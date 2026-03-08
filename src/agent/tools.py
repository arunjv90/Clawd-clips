"""Tool definitions for the Claude agent orchestrator."""

from typing import Any

# Tool schemas passed to the Anthropic API
TOOLS = [
    {
        "name": "get_trending_topics",
        "description": (
            "Fetch current trending topics from Reddit, Twitter/X, and Google Trends. "
            "Returns a ranked list of trends with context about why they're trending."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Max number of trends to return (default 20)",
                    "default": 20,
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["reddit", "twitter", "google", "news"]},
                    "description": "Which sources to pull from (default: all)",
                },
            },
        },
    },
    {
        "name": "get_past_performance",
        "description": (
            "Get engagement stats for recent posts to understand what's working. "
            "Returns metrics like likes, shares, reach, and comments."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "How many days of history to return (default 7)",
                    "default": 7,
                },
                "platform": {
                    "type": "string",
                    "enum": ["instagram", "twitter", "tiktok", "reddit", "all"],
                    "description": "Which platform to get stats for (default: all)",
                },
            },
        },
    },
    {
        "name": "search_meme_templates",
        "description": "Search the local meme template library for formats that fit a trend.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g. 'comparison', 'reaction', 'distracted')",
                },
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "generate_meme",
        "description": (
            "Generate a meme image and captions for a given trend and format. "
            "Returns a content package ready for review."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "trend": {
                    "type": "string",
                    "description": "The trend or topic to make the meme about",
                },
                "template_id": {
                    "type": "string",
                    "description": "ID of the meme template to use (from search_meme_templates)",
                },
                "concept": {
                    "type": "string",
                    "description": "Brief description of the meme concept / what the joke is",
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["instagram", "twitter", "tiktok", "reddit"]},
                    "description": "Which platforms to generate captions for",
                },
            },
            "required": ["trend", "concept", "platforms"],
        },
    },
    {
        "name": "schedule_post",
        "description": "Add approved content to the posting queue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content_id": {
                    "type": "string",
                    "description": "ID of the generated content to post",
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Platforms to post to",
                },
                "post_at": {
                    "type": "string",
                    "description": "ISO 8601 datetime to post (optional — agent will pick optimal time if omitted)",
                },
            },
            "required": ["content_id", "platforms"],
        },
    },
    {
        "name": "reject_content",
        "description": "Reject generated content with a reason. It won't be posted.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content_id": {"type": "string"},
                "reason": {
                    "type": "string",
                    "description": "Why this content is being rejected",
                },
            },
            "required": ["content_id", "reason"],
        },
    },
]
