"""Tool definitions for the Claude agent orchestrator."""

# Tool schemas passed to the Anthropic API
TOOLS = [
    {
        "name": "get_trending_ai_topics",
        "description": (
            "Fetch what's currently trending in the AI world from Reddit, Twitter/X, "
            "Hacker News, and AI news sources. Returns a ranked list of opportunities "
            "with context: what happened, why it's funny/notable, how fresh it is."
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
                    "items": {
                        "type": "string",
                        "enum": [
                            "reddit_mainstream",  # r/memes, r/me_irl, r/funny — what's broadly meme-able
                            "reddit_ai_users",    # r/ChatGPT, r/artificial — how regular people use AI
                            "twitter_trending",   # broad trending topics with meme potential
                            "news",               # general news to riff on through AI lens
                            "ai_products",        # new AI product launches, fails, and discourse
                        ],
                    },
                    "description": "Which sources to pull from (default: all)",
                },
                "pillar_filter": {
                    "type": "string",
                    "enum": [
                        "ai_perspective",   # noticing human behavior from the outside
                        "being_an_ai",      # first-person: being helpful, not knowing dates, context limits
                        "ai_in_everyday",   # chatgpt, autocomplete, AI product gap vs. reality
                        "internet_culture", # normal meme trends filtered through AI observer frame
                        "big_questions",    # consciousness, dreaming, deleting files — kept light
                        "any",
                    ],
                    "description": "Filter trends by content pillar (default: any)",
                    "default": "any",
                },
            },
        },
    },
    {
        "name": "get_past_performance",
        "description": (
            "Get engagement stats for recent posts to understand what's working. "
            "Returns metrics per post: likes, shares, reach, replies, and the content pillar. "
            "Use this to tune your strategy — which pillars, formats, and times perform best."
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
                    "enum": ["instagram", "twitter", "all"],
                    "description": "Which platform to get stats for (default: all)",
                    "default": "all",
                },
                "group_by": {
                    "type": "string",
                    "enum": ["post", "pillar", "format", "time_of_day"],
                    "description": "How to aggregate results (default: post)",
                    "default": "post",
                },
            },
        },
    },
    {
        "name": "search_meme_templates",
        "description": (
            "Search the meme template library for formats that fit a concept. "
            "Returns templates with their text zones, aspect ratios, and examples of "
            "how they've been used for AI humor before."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Describe the kind of template you need. "
                        "E.g. 'comparison two options', 'escalating absurdity', "
                        "'character reacting to news', 'text-only bold statement'"
                    ),
                },
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "generate_meme",
        "description": (
            "Generate a meme image and platform-specific captions for a given concept. "
            "Provide a clear, specific concept — the more precise the joke setup and punchline, "
            "the better the output. Returns a content package ready for your review."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The AI news, event, or phenomenon this meme is about",
                },
                "pillar": {
                    "type": "string",
                    "enum": [
                        "ai_perspective",
                        "being_an_ai",
                        "ai_in_everyday",
                        "internet_culture",
                        "big_questions",
                    ],
                    "description": "Which content pillar this falls under",
                },
                "concept": {
                    "type": "string",
                    "description": (
                        "The specific meme concept. Include the setup, the joke, and the punchline. "
                        "E.g. 'Drake meme: top panel rejects reading the paper; bottom panel approves "
                        "reading the Twitter thread summary of the paper'"
                    ),
                },
                "template_id": {
                    "type": "string",
                    "description": "ID from search_meme_templates (optional — will auto-select if omitted)",
                },
                "use_ai_image_gen": {
                    "type": "boolean",
                    "description": "Generate a custom image with AI instead of using a template (slower, costs more)",
                    "default": False,
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["instagram", "twitter"]},
                    "description": "Which platforms to generate captions and hashtags for",
                },
            },
            "required": ["topic", "pillar", "concept", "platforms"],
        },
    },
    {
        "name": "schedule_post",
        "description": (
            "Add approved content to the posting queue. "
            "If post_at is omitted, the scheduler picks the next optimal slot for that platform "
            "based on historical engagement windows."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content_id": {
                    "type": "string",
                    "description": "ID of the generated content to post",
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["instagram", "twitter"]},
                    "description": "Platforms to post to",
                },
                "post_at": {
                    "type": "string",
                    "description": "ISO 8601 datetime to post (omit to let scheduler decide)",
                },
                "priority": {
                    "type": "string",
                    "enum": ["breaking", "normal", "evergreen"],
                    "description": (
                        "breaking = post ASAP (for fast-moving news). "
                        "normal = next optimal slot. "
                        "evergreen = fill gaps in the schedule."
                    ),
                    "default": "normal",
                },
            },
            "required": ["content_id", "platforms"],
        },
    },
    {
        "name": "reject_content",
        "description": (
            "Reject generated content so it won't be posted. "
            "Always provide a specific reason — this is logged and used to improve generation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content_id": {"type": "string"},
                "reason": {
                    "type": "string",
                    "description": (
                        "Why this is being rejected. Be specific: "
                        "'joke is outdated — this meme format died in 2022', "
                        "'punches at a person not a concept', "
                        "'too niche — fewer than 1000 people will get this', "
                        "'caption doesn't land — setup and punchline are disconnected', etc."
                    ),
                },
                "retry_with_notes": {
                    "type": "string",
                    "description": "Optional: notes for regenerating this concept with fixes applied",
                },
            },
            "required": ["content_id", "reason"],
        },
    },
]
