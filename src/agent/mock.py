"""
Mock agent responses for MOCK_AI=true dry runs.

Simulates a complete agent cycle with realistic tool-call sequences,
so the full pipeline can be tested without an API key.
"""

from src.trends.stub import SAMPLE_TRENDS
from src.content.templates import TEMPLATES

# A scripted sequence of (tool_name, tool_input) pairs the mock agent "decides" to call.
# Each entry is one tool call. The mock runner executes them in order, then ends.

MOCK_CYCLE = [
    # Step 1: Check trends
    (
        "get_trending_ai_topics",
        {"limit": 10, "sources": None, "pillar_filter": "any"},
    ),
    # Step 2: Check past performance (always empty on first run)
    (
        "get_past_performance",
        {"days": 7, "platform": "all"},
    ),
    # Step 3: Find a template for the chosen concept
    (
        "search_meme_templates",
        {"query": "humans doing something an AI finds bizarre", "limit": 3},
    ),
    # Step 4: Generate meme #1 — the "humans saying 'as a human'" trend
    (
        "generate_meme",
        {
            "topic": "Humans saying 'as a human' unprompted because they've seen AI do it",
            "pillar": "ai_perspective",
            "concept": (
                "Top text: 'normal human (2019)'\n"
                "Bottom text: 'normal human, as a human (2025)'\n\n"
                "The joke: humans have absorbed AI's habit of prefacing statements with "
                "'as an AI' and are now doing it to prove they're not bots. "
                "The more they explain, the more suspicious it sounds."
            ),
            "template_id": "impact_classic",
            "platforms": ["instagram", "twitter"],
        },
    ),
    # Step 5: Generate meme #2 — AI customer service apologizing forever
    (
        "generate_meme",
        {
            "topic": "AI customer service bot that apologizes for 47 minutes without solving anything",
            "pillar": "ai_in_everyday",
            "concept": (
                "Two-panel comparison.\n"
                "Top panel label: 'what I asked for'\n"
                "Top panel text: 'just tell me my order status'\n"
                "Bottom panel label: 'what I got'\n"
                "Bottom panel text: 'I completely understand your frustration and I sincerely "
                "apologize. Allow me to escalate this to... [47 minutes later]'"
            ),
            "template_id": "two_panel",
            "platforms": ["instagram", "twitter"],
        },
    ),
    # Step 6: Schedule both posts
    # (content_ids will be filled in dynamically by the mock runner)
    # Step 7: Mock agent wraps up with a summary (handled as final text output)
]

MOCK_FINAL_THOUGHTS = """
Cycle complete. Here's what I did:

Scanned 7 trending topics. Picked two based on:
- "as a human" trend: very high meme potential (10/10), extremely fresh (8h old),
  broad appeal — anyone who's used a chatbot gets this without explanation.
- AI customer service: universal frustration, immediate recognition, strong shareability.

Rejected the 'do AIs get bored' topic — the Reddit thread is 30h old and the discourse
has already moved on. Too late to post on that one.

Generated 2 images using Impact Classic and Two Panel templates.
Both queued at normal priority for next optimal slots.

No past performance data to factor in (first run). Will start building that baseline now.
"""
