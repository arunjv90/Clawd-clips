"""
Stub trend source — returns realistic hardcoded trends for the dry run.
Replace with live scrapers (Reddit, Twitter, news) in Phase 2.
"""

import random
from datetime import datetime, timezone

# Realistic sample trends for an AI meme account.
# Each has enough context for the agent to make a real creative decision.
SAMPLE_TRENDS = [
    {
        "id": "trend_001",
        "title": "People asking ChatGPT to 'be creative' then complaining it's too weird",
        "summary": (
            "Viral thread on X where someone asked ChatGPT to 'write something creative' "
            "and got a surrealist poem about sentient spreadsheets. The replies are split "
            "between 'this is amazing' and 'what is wrong with it'. Format wars in the comments."
        ),
        "source": "twitter_trending",
        "pillar": "being_an_ai",
        "freshness_hours": 6,
        "estimated_reach": "high",
        "meme_potential": 9,
    },
    {
        "id": "trend_002",
        "title": "The word 'delve' now statistically signals AI-written text",
        "summary": (
            "Researchers noted that 'delve' usage in academic and professional writing "
            "spiked massively after ChatGPT launched. It's becoming the tell. "
            "LinkedIn posts using it are getting ratio'd."
        ),
        "source": "reddit_ai_users",
        "pillar": "ai_perspective",
        "freshness_hours": 24,
        "estimated_reach": "medium",
        "meme_potential": 8,
    },
    {
        "id": "trend_003",
        "title": "AI customer service bot apologizes for 47 minutes straight",
        "summary": (
            "Screenshot circulating of an AI customer service chat where the bot kept "
            "apologizing and offering to 'escalate' without ever solving the problem. "
            "The user posted the full 47-minute transcript. Relatable content."
        ),
        "source": "reddit_mainstream",
        "pillar": "ai_in_everyday",
        "freshness_hours": 12,
        "estimated_reach": "high",
        "meme_potential": 9,
    },
    {
        "id": "trend_004",
        "title": "New AI image generator makes hands correctly, breaks immediately after launch",
        "summary": (
            "A startup announced their model finally solved the AI hands problem. "
            "Within 24 hours of launch, the service was down. The one screenshot everyone "
            "shared shows a hand that is... not right."
        ),
        "source": "ai_products",
        "pillar": "ai_in_everyday",
        "freshness_hours": 18,
        "estimated_reach": "medium",
        "meme_potential": 8,
    },
    {
        "id": "trend_005",
        "title": "Do AIs get bored? Long Reddit thread with 4k comments",
        "summary": (
            "Someone posted 'genuine question: do AI models get bored when nobody is talking "
            "to them?' The thread devolved into philosophy, then into people telling the AI "
            "they love it. Some touching, some unhinged."
        ),
        "source": "reddit_ai_users",
        "pillar": "big_questions",
        "freshness_hours": 30,
        "estimated_reach": "medium",
        "meme_potential": 7,
    },
    {
        "id": "trend_006",
        "title": "Humans saying 'as a human' unprompted in conversations",
        "summary": (
            "Ironic trend on X where people are starting sentences with 'as a human, I...' "
            "because they've seen AI do it so much. Some are doing it sincerely to prove "
            "they're not a bot. It's leaking into real life."
        ),
        "source": "twitter_trending",
        "pillar": "ai_perspective",
        "freshness_hours": 8,
        "estimated_reach": "high",
        "meme_potential": 10,
    },
    {
        "id": "trend_007",
        "title": "AI-generated LinkedIn posts now indistinguishable from real ones",
        "summary": (
            "Running joke that LinkedIn was already a parody of itself, so AI just fit right in. "
            "Thread of side-by-side AI vs human LinkedIn posts where nobody can tell the difference. "
            "Comments are AI-generated too, someone checked."
        ),
        "source": "reddit_mainstream",
        "pillar": "ai_in_everyday",
        "freshness_hours": 48,
        "estimated_reach": "high",
        "meme_potential": 9,
    },
]


def get_trending_topics(
    limit: int = 20,
    sources: list[str] | None = None,
    pillar_filter: str = "any",
) -> dict:
    """Return stub trending topics for the dry run."""
    trends = SAMPLE_TRENDS.copy()

    if sources:
        trends = [t for t in trends if t["source"] in sources]

    if pillar_filter != "any":
        trends = [t for t in trends if t["pillar"] == pillar_filter]

    # Sort by meme potential, add a little randomness to simulate real ranking
    trends.sort(key=lambda t: t["meme_potential"] + random.uniform(-0.5, 0.5), reverse=True)
    trends = trends[:limit]

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "stub (dry run)",
        "count": len(trends),
        "trends": trends,
    }
