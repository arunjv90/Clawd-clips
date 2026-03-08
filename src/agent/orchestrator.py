"""
Main agent orchestrator — the Claude-powered brain of Clawd-clips.

Run this module to start the agent loop:
    python -m src.agent.orchestrator
"""

import json
import os
import time
from typing import Any

import anthropic
import structlog

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.tools import TOOLS

log = structlog.get_logger()


def handle_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """
    Dispatch tool calls to the appropriate handler modules.
    Replace the stubs here with real implementations as each module is built.
    """
    log.info("tool_call", tool=tool_name, input=tool_input)

    if tool_name == "get_trending_topics":
        # TODO: import and call src.trends.aggregator.get_trending_topics
        return json.dumps({"trends": [], "message": "Trend monitor not yet implemented"})

    elif tool_name == "get_past_performance":
        # TODO: import and call src.analytics.collector.get_past_performance
        return json.dumps({"posts": [], "message": "Analytics not yet implemented"})

    elif tool_name == "search_meme_templates":
        # TODO: import and call src.content.template_renderer.search_templates
        return json.dumps({"templates": [], "message": "Template search not yet implemented"})

    elif tool_name == "generate_meme":
        # TODO: import and call src.content pipeline
        return json.dumps({"content_id": None, "message": "Content generator not yet implemented"})

    elif tool_name == "schedule_post":
        # TODO: import and call src.publisher.queue.schedule_post
        return json.dumps({"status": "queued", "message": "Publisher not yet implemented"})

    elif tool_name == "reject_content":
        log.info("content_rejected", content_id=tool_input.get("content_id"), reason=tool_input.get("reason"))
        return json.dumps({"status": "rejected"})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def run_agent_cycle() -> None:
    """Run one full decision cycle: trends → content → review → queue."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages: list[dict] = [
        {
            "role": "user",
            "content": (
                "Run your content cycle. Check trends, decide what to post, generate memes, "
                "review them, and queue the good ones. Think through your decisions."
            ),
        }
    ]

    log.info("agent_cycle_start")

    # Agentic loop — keep going until the model stops calling tools
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        log.info("agent_response", stop_reason=response.stop_reason, usage=response.usage.model_dump())

        # Collect any text the agent outputs (its reasoning)
        for block in response.content:
            if block.type == "text":
                log.info("agent_reasoning", text=block.text)

        if response.stop_reason == "end_turn":
            log.info("agent_cycle_complete")
            break

        if response.stop_reason != "tool_use":
            log.warning("unexpected_stop_reason", reason=response.stop_reason)
            break

        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = handle_tool_call(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # Append assistant turn + tool results to message history
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})


def main() -> None:
    import structlog
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(
        getattr(__import__("logging"), os.environ.get("LOG_LEVEL", "INFO"))
    ))

    log.info("clawd_clips_start")

    dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"
    if dry_run:
        log.info("dry_run_mode", note="Set DRY_RUN=false to actually post")

    run_agent_cycle()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
