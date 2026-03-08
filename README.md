# Clawd-clips

An autonomous AI agent that runs a meme account end-to-end — discovering
trends, generating memes, posting to social media, and learning from engagement
performance, all without human intervention.

## How it works

```
Trending topics → Claude agent → Meme generation → Post queue → Platforms
                       ↑                                              │
                       └──────── Engagement analytics ───────────────┘
```

1. **Trend Monitor** scrapes Reddit, Twitter/X, Google Trends, and news
   headlines to find what's funny right now
2. **Agent Orchestrator** (Claude claude-opus-4-6) decides which trends to act on,
   picks the best meme format, and reviews content before posting
3. **Content Generator** renders meme templates or generates original images,
   then writes captions and hashtags tuned for each platform
4. **Publisher** queues posts and sends them to Instagram, X, TikTok, and Reddit
   at optimal times
5. **Analytics** polls engagement after each post and feeds results back to the
   agent so it improves over time

## Docs

- [Full project plan](PLAN.md) — architecture, tech stack, phases, risks

## Setup

```bash
cp .env.example .env
# fill in your API keys
pip install -r requirements.txt
python -m src.agent.orchestrator
```

## Status

Early planning phase. See [PLAN.md](PLAN.md) for the full roadmap.
