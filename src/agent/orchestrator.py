"""
Main agent orchestrator — the Claude-powered brain of Clawd-clips.

Run this module to start the agent loop:
    python -m src.agent.orchestrator

Environment variables:
    ANTHROPIC_API_KEY   — required for live mode
    DRY_RUN=true        — queue posts but don't actually publish (default: true)
    MOCK_AI=true        — use scripted mock responses instead of real Claude API
                          (useful for testing the pipeline without an API key)
"""

import json
import logging
import os
from typing import Any

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.tools import TOOLS


def handle_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Dispatch tool calls to the appropriate handler modules."""
    print(f"\n  → {tool_name}({', '.join(f'{k}={repr(v)[:60]}' for k, v in tool_input.items())})")

    if tool_name == "get_trending_ai_topics":
        from src.trends.stub import get_trending_topics
        result = get_trending_topics(
            limit=tool_input.get("limit", 20),
            sources=tool_input.get("sources"),
            pillar_filter=tool_input.get("pillar_filter", "any"),
        )
        return json.dumps(result)

    elif tool_name == "get_past_performance":
        return json.dumps({
            "note": "No posting history yet — this is the first run.",
            "posts": [],
            "recommendation": "Start with highest-confidence concepts; build baseline data.",
        })

    elif tool_name == "search_meme_templates":
        from src.content.templates import search_templates
        results = search_templates(
            query=tool_input["query"],
            limit=tool_input.get("limit", 5),
        )
        return json.dumps({"templates": results})

    elif tool_name == "generate_meme":
        from src.content.generator import generate_meme
        result = generate_meme(
            topic=tool_input["topic"],
            pillar=tool_input["pillar"],
            concept=tool_input["concept"],
            template_id=tool_input.get("template_id"),
            platforms=tool_input.get("platforms", ["instagram", "twitter"]),
        )
        print(f"     ✓ Generated: {result['image_path']} [{result['template_used']}]")
        print(f"     Text: {result['text_zones']}")
        return json.dumps(result)

    elif tool_name == "schedule_post":
        from src.publisher.queue import schedule_post
        result = schedule_post(
            content_id=tool_input["content_id"],
            platforms=tool_input["platforms"],
            post_at=tool_input.get("post_at"),
            priority=tool_input.get("priority", "normal"),
        )
        return json.dumps(result)

    elif tool_name == "reject_content":
        from src.content.generator import reject_content
        result = reject_content(
            content_id=tool_input["content_id"],
            reason=tool_input["reason"],
            retry_with_notes=tool_input.get("retry_with_notes"),
        )
        print(f"     ✗ Rejected: {tool_input['reason']}")
        return json.dumps(result)

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def run_mock_cycle() -> None:
    """Run a scripted mock agent cycle — no API key needed."""
    from src.agent.mock import MOCK_CYCLE, MOCK_FINAL_THOUGHTS

    print("\n[MODE: MOCK — scripted agent decisions, real content generation]\n")

    generated_content_ids = []

    for i, (tool_name, tool_input) in enumerate(MOCK_CYCLE, 1):
        print(f"[Step {i}/{len(MOCK_CYCLE)}]", end="")
        raw = handle_tool_call(tool_name, tool_input)
        result = json.loads(raw)

        # Collect generated content IDs and immediately schedule them
        if tool_name == "generate_meme" and "content_id" in result:
            content_id = result["content_id"]
            generated_content_ids.append(content_id)
            print(f"\n[Step {i}b] Scheduling {content_id}")
            handle_tool_call("schedule_post", {
                "content_id": content_id,
                "platforms": tool_input.get("platforms", ["instagram", "twitter"]),
                "priority": "normal",
            })

    print("\n[AGENT SUMMARY]")
    print(MOCK_FINAL_THOUGHTS)
    print("\n✓ Mock cycle complete.")
    print(f"  Generated {len(generated_content_ids)} meme(s): {generated_content_ids}")
    print("  Images saved to output/")
    print("  Queue saved to output/queue.json")


def run_agent_cycle() -> None:
    """Run one full live decision cycle using the Claude API."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages: list[dict] = [
        {
            "role": "user",
            "content": (
                "Run your content cycle. Check what's trending, decide which ones are worth "
                "posting about, generate 1-2 memes, review them critically, and queue the ones "
                "that pass. Think out loud as you go — I want to see your reasoning."
            ),
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        print(f"\n[AGENT stop_reason={response.stop_reason}]")

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print("\n[AGENT THINKING]")
                print(block.text)

        if response.stop_reason == "end_turn":
            print("\n✓ Agent cycle complete.")
            break

        if response.stop_reason != "tool_use":
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = handle_tool_call(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})


def main() -> None:
    logging.basicConfig(
        level=getattr(logging, os.environ.get("LOG_LEVEL", "WARNING")),
        format="%(levelname)s %(name)s %(message)s",
    )

    dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"
    mock_ai = os.environ.get("MOCK_AI", "false").lower() == "true"

    print("=" * 60)
    print("CLAWD-CLIPS")
    print(f"  DRY_RUN : {dry_run}")
    print(f"  MOCK_AI : {mock_ai}")
    print("=" * 60)

    if mock_ai:
        run_mock_cycle()
    else:
        if "ANTHROPIC_API_KEY" not in os.environ:
            print("\nERROR: ANTHROPIC_API_KEY not set.")
            print("  Set it in .env or export it, then re-run.")
            print("  For a no-key demo: MOCK_AI=true python -m src.agent.orchestrator")
            raise SystemExit(1)
        run_agent_cycle()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
