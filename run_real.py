"""
Real run — uses claude_agent_sdk which authenticates via Claude Code's own auth.

The meme pipeline tools are exposed as MCP tools so the real Claude model
can reason about trends, pick concepts, generate images, and queue posts.

Usage:
    DRY_RUN=true env -u CLAUDECODE python run_real.py
"""

import anyio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    SystemMessage,
)

from src.agent.prompts import SYSTEM_PROMPT


# ── MCP tool definitions wired to the real pipeline modules ───────────────────

@tool(
    "get_trending_ai_topics",
    "Fetch currently trending AI/internet topics that could make good memes. "
    "Returns topics with meme potential scores, freshness, and context.",
    {"limit": int, "pillar_filter": str},
)
async def get_trending_ai_topics(args):
    from src.trends.stub import get_trending_topics
    result = get_trending_topics(
        limit=args.get("limit", 10),
        pillar_filter=args.get("pillar_filter", "any"),
    )
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


@tool(
    "get_past_performance",
    "Retrieve engagement data for recent posts to inform content decisions.",
    {"days": int},
)
async def get_past_performance(args):
    return {"content": [{"type": "text", "text": json.dumps({
        "note": "No posting history yet — this is the first run.",
        "posts": [],
        "recommendation": "Start with highest-confidence concepts; build baseline data.",
    })}]}


@tool(
    "search_meme_templates",
    "Search available meme templates by keyword. Returns template metadata.",
    {"query": str, "limit": int},
)
async def search_meme_templates(args):
    from src.content.templates import search_templates
    results = search_templates(query=args.get("query", ""), limit=args.get("limit", 5))
    return {"content": [{"type": "text", "text": json.dumps({"templates": results}, indent=2)}]}


@tool(
    "generate_meme",
    "Generate a meme image from a concept. Renders a real PNG to output/. "
    "Returns content_id, image_path, and text zone content.",
    {"topic": str, "pillar": str, "concept": str, "template_id": str, "platforms": list},
)
async def generate_meme(args):
    from src.content.generator import generate_meme as _gen
    result = _gen(
        topic=args["topic"],
        pillar=args["pillar"],
        concept=args["concept"],
        template_id=args.get("template_id"),
        platforms=args.get("platforms", ["instagram", "twitter"]),
    )
    print(f"\n  ✓ Generated: {result['image_path']} [{result['template_used']}]", flush=True)
    print(f"    Text: {result['text_zones']}", flush=True)
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


@tool(
    "schedule_post",
    "Queue a generated meme for posting on one or more platforms.",
    {"content_id": str, "platforms": list, "priority": str},
)
async def schedule_post(args):
    from src.publisher.queue import schedule_post as _q
    result = _q(
        content_id=args["content_id"],
        platforms=args.get("platforms", ["instagram", "twitter"]),
        priority=args.get("priority", "normal"),
    )
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


@tool(
    "reject_content",
    "Mark generated content as rejected. Optionally include notes for a retry.",
    {"content_id": str, "reason": str, "retry_with_notes": str},
)
async def reject_content_tool(args):
    from src.content.generator import reject_content
    result = reject_content(
        content_id=args["content_id"],
        reason=args["reason"],
        retry_with_notes=args.get("retry_with_notes"),
    )
    print(f"\n  ✗ Rejected {args['content_id']}: {args['reason']}", flush=True)
    return {"content": [{"type": "text", "text": json.dumps(result)}]}


# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"

    print("=" * 60, flush=True)
    print("CLAWD-CLIPS — REAL RUN (claude_agent_sdk)", flush=True)
    print(f"  DRY_RUN : {dry_run}", flush=True)
    print("=" * 60, flush=True)

    server = create_sdk_mcp_server("clawd-tools", tools=[
        get_trending_ai_topics,
        get_past_performance,
        search_meme_templates,
        generate_meme,
        schedule_post,
        reject_content_tool,
    ])

    prompt = (
        "Run your content cycle. Check what's trending, pick the strongest 1-2 meme concepts, "
        "generate the memes, review them critically, and queue the ones that pass. "
        "Think out loud as you go — I want to see your reasoning for every decision."
    )

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"clawd": server},
        permission_mode="dontAsk",
    )

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, SystemMessage):
                print(f"\n[SESSION {message.subtype}]", flush=True)
            elif isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        print(f"\n[CLAWD] {block.text}", flush=True)
            elif isinstance(message, ResultMessage):
                print(f"\n{'='*60}", flush=True)
                print("[CYCLE COMPLETE]", flush=True)
                if message.result:
                    print(message.result, flush=True)
                print("=" * 60, flush=True)
    except Exception as e:
        # The SDK raises on cleanup after ResultMessage is received — that's ok
        if "ResultMessage" not in str(e) and "exit code" not in str(e).lower():
            raise

    # Print queue summary
    from src.publisher.queue import get_queue
    queue = get_queue()
    new_queue = [e for e in queue if e.get("queued_at", "") > "2026-03-08T10:30"]
    print(f"\nNew posts queued this cycle: {len(new_queue)}", flush=True)
    for entry in new_queue:
        print(f"  • {entry['content_id']} — {entry.get('template', '?')} — {entry['platforms']}", flush=True)
    if new_queue:
        print(f"  Images in output/", flush=True)


if __name__ == "__main__":
    anyio.run(main)
