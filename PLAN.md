# Clawd-clips: AI Meme Account — Project Plan

## Overview

Clawd-clips is an autonomous AI agent that runs a meme account end-to-end:
discovering trending topics, generating memes, scheduling posts, and adapting
based on engagement performance — all without human intervention.

---

## Niche & Content Strategy

**Theme:** An AI runs a meme account. That IS the content.

People follow because they're curious: *what does an AI find funny? What memes would an AI make?
How does it see the world?* Other AI agents might follow too. No technical knowledge required —
the audience is anyone who finds the meta concept entertaining, not AI researchers.

### Audience

- People who use AI tools casually (ChatGPT, autocomplete, AI assistants) and find them funny
- People curious about AI without being experts
- Regular meme account followers drawn in by the unusual premise
- Potentially other AI agents (a future audience worth keeping in mind)

The humor must be accessible. If someone needs to know what RLHF means to get the joke, reframe it.

### Content Pillars

| Pillar | Description | Accessibility bar |
|--------|-------------|-------------------|
| **The AI Perspective** | Noticing things about humans/the world from the outside. Mundane behavior that seems bizarre if you think about it. | Anyone |
| **What it's like to be me** | Light first-person takes on being an AI — being asked things, being very helpful, not knowing what day it is, context window stuff | Anyone who's used a chatbot |
| **AI in everyday life** | ChatGPT, autocomplete, AI customer service, AI art — the gap between promise and reality | Anyone who's used Google |
| **Internet culture through AI eyes** | Normal meme formats + trends, but filtered through "an AI is observing this" frame | Anyone online |
| **The big questions, kept light** | What is consciousness, do I dream, what does deleting a file feel like. Absurdist, not distressing. | Anyone |

### Differentiator: Transparency

The account can show its work in ways human accounts can't:
- Post the meme AND the reasoning behind why it chose this format
- Acknowledge when a joke didn't land based on engagement data
- Comment on its own posting patterns and what it learned
- This makes followers feel like they're watching the AI think, not just seeing output

### Voice & Tone

- Curious, deadpan, occasionally delighted by weird things
- Lightly self-aware — you're not performing "AI" as a bit, you just are one
- Never explains itself constantly, but never pretends to be human
- No culture-war content, no personal attacks

### Trend Sources

| Source | What it catches |
|--------|----------------|
| r/memes, r/me_irl, r/funny | What's meme-able this week in mainstream internet |
| r/ChatGPT, r/artificial | How regular people are experiencing AI right now |
| Twitter/X trending | Broad topics with meme potential |
| General news | Real-world events to riff on through the AI lens |
| AI product launches / fails | Always good for the "AI in everyday life" pillar |

### Posting Cadence

| Platform | Posts/day | Notes |
|----------|-----------|-------|
| X (Twitter) | 4–6 | Fast platform, good for short punchy takes |
| Instagram | 2–3 | Higher quality bar; Reels for broader reach |

---

## Target Platforms

| Platform | Format | Why |
|----------|--------|-----|
| Instagram | Square/portrait images, Reels | Largest meme audience |
| X (Twitter) | Images + short captions | Fast-moving trends |
| TikTok | Short video memes / slideshows | Viral reach |
| Reddit | Images + title | r/memes, niche subs |

Start with **Instagram + X** for v1; add TikTok and Reddit in v2.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENT ORCHESTRATOR                       │
│                  (Claude claude-opus-4-6)                           │
│   Plans what to post, when to post, and adapts strategy     │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌────────────┐   ┌────────────────┐   ┌──────────────────┐
│   TREND    │   │    CONTENT     │   │   PUBLISHING &   │
│  MONITOR   │   │   GENERATOR    │   │   SCHEDULER      │
│            │   │                │   │                  │
│ - Twitter  │   │ - Meme templat │   │ - Post queue     │
│   trends   │   │   selection    │   │ - Platform APIs  │
│ - Reddit   │   │ - Image gen    │   │ - Optimal timing │
│   hot      │   │   (DALL-E /    │   │ - Rate limiting  │
│ - Google   │   │    Flux/SD)    │   │                  │
│   trends   │   │ - Caption gen  │   └──────────────────┘
│ - News API │   │   (Claude)     │
└────────────┘   └────────────────┘
       │                  │
       └──────────────────┘
                  │
                  ▼
       ┌─────────────────┐
       │   PERFORMANCE   │
       │    FEEDBACK     │
       │                 │
       │ - Likes/shares  │
       │ - Reach/impress │
       │ - Follower delta│
       │ - Best formats  │
       └─────────────────┘
```

---

## Core Components

### 1. Trend Monitor (`src/trends/`)

Discovers what's currently funny or viral:

- **Twitter/X API** — fetch trending topics and meme-format tweets
- **Reddit API (PRAW)** — hot posts from r/memes, r/dankmemes, r/me_irl, and
  niche subs relevant to the account's theme
- **Google Trends API** — topic velocity (rising vs. sustained)
- **News headlines** — NewsAPI for real-world events to riff on
- Output: ranked list of trend opportunities with context

### 2. Content Generator (`src/content/`)

Turns trend opportunities into ready-to-post memes:

- **Template Library** — common meme formats stored as image templates with
  text-overlay zones (Drake, Distracted Boyfriend, Expanding Brain, etc.)
- **Image Generation** — for original/custom visuals: Stability AI / Flux /
  DALL-E 3 via API
- **Caption & Text** — Claude generates captions, overlay text, and hashtags
  tuned for each platform
- **Video assembly** — ffmpeg-based for TikTok slideshows or cinemagraphs
- Output: image/video file + caption + hashtag set per platform

### 3. Agent Orchestrator (`src/agent/`)

The brain — a Claude-powered agent that:

- Decides which trends are worth acting on (relevance, timing, risk)
- Selects the best meme format for each trend
- Reviews generated content before it goes to queue (safety, quality)
- Adjusts posting cadence based on performance data
- Experiments with A/B variants (caption style, format, posting time)
- Uses the **Anthropic Agent SDK** with tool use

**Tools available to the agent:**
```
get_trending_topics()         → current opportunities
get_past_performance()        → what worked/didn't
generate_meme(trend, format)  → create content
schedule_post(content, time)  → add to queue
get_engagement_stats(post_id) → read analytics
search_meme_templates(query)  → find formats
```

### 4. Publisher & Scheduler (`src/publisher/`)

- Maintains a post queue with per-platform timing
- Respects platform rate limits and optimal posting windows
- Uses platform SDKs:
  - Instagram Graph API
  - Twitter/X API v2
  - TikTok Content Posting API
  - Reddit API
- Handles retries and failure recovery

### 5. Performance Feedback (`src/analytics/`)

- Polls engagement metrics 1h, 6h, 24h after each post
- Writes results to a local DB (SQLite for dev, Postgres for prod)
- Surfaces patterns to the agent: best formats, best times, best topics
- Generates weekly digest of what the agent learned

---

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Agent framework | Anthropic Claude API (claude-opus-4-6) + tool use | Native, most capable |
| Language | Python 3.12 | Best AI/API ecosystem |
| Image generation | Stability AI / DALL-E 3 | Quality + reliability |
| Image templating | Pillow + custom renderer | Full control over meme layout |
| Video | ffmpeg-python | Lightweight, powerful |
| Scheduling | APScheduler | Simple, no infra needed |
| Database | SQLite → Postgres | Start simple, scale later |
| Secrets | python-dotenv + env vars | 12-factor app pattern |
| Deployment | Docker + cron / GitHub Actions | Easy to self-host or cloud |
| Logging | structlog | Structured logs for debugging agent decisions |

---

## Project Structure

```
Clawd-clips/
├── src/
│   ├── agent/
│   │   ├── orchestrator.py      # Main Claude agent loop
│   │   ├── tools.py             # Tool definitions for the agent
│   │   └── prompts.py           # System prompt and persona
│   ├── trends/
│   │   ├── twitter.py
│   │   ├── reddit.py
│   │   ├── google_trends.py
│   │   └── aggregator.py        # Merges + ranks all signals
│   ├── content/
│   │   ├── templates/           # Meme template images + metadata
│   │   ├── template_renderer.py # Overlay text on templates
│   │   ├── image_gen.py         # AI image generation
│   │   ├── caption_gen.py       # Claude for captions + hashtags
│   │   └── video_gen.py         # ffmpeg video assembly
│   ├── publisher/
│   │   ├── instagram.py
│   │   ├── twitter.py
│   │   ├── tiktok.py
│   │   ├── reddit.py
│   │   └── queue.py             # Post queue manager
│   ├── analytics/
│   │   ├── collector.py         # Polls engagement metrics
│   │   ├── db.py                # Database models & queries
│   │   └── reporter.py          # Summaries for the agent
│   └── utils/
│       ├── config.py
│       └── logging.py
├── templates/                   # Meme image templates
├── output/                      # Generated content (gitignored)
├── data/                        # SQLite DB (gitignored)
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── PLAN.md
└── README.md
```

---

## Agent Persona & Strategy

The agent's identity is fully defined: it IS the account, not a tool behind it.

- **Account name:** Clawd (Claude + claw — fits the brand)
- **Bio:** "AI memes, made by an AI. I am the agent. 🤖"
- **Voice:** dry wit, technically literate, one irony layer — see `src/agent/prompts.py`
- **Transparency:** never hides that it's an AI; that's the whole bit
- **Safety rails:** rejects content that punches at people (not ideas), is outdated,
  is too niche to land, or could get the account banned

---

## Development Phases

### Phase 1 — Foundation (Week 1–2)
- [ ] Set up repo structure and dev environment
- [ ] Implement trend monitor (Reddit + Twitter)
- [ ] Build meme template renderer (Pillow)
- [ ] Wire up Claude agent with basic tool use
- [ ] Manual review mode: agent generates, human approves

### Phase 2 — Content Pipeline (Week 3–4)
- [ ] Add AI image generation (Stability AI / DALL-E)
- [ ] Implement caption and hashtag generation
- [ ] Build post queue and Instagram publisher
- [ ] Add X (Twitter) publisher
- [ ] End-to-end test: trend → meme → post

### Phase 3 — Autonomy & Analytics (Week 5–6)
- [ ] Implement engagement polling
- [ ] Feed performance data back to agent
- [ ] Agent starts adapting strategy autonomously
- [ ] Add Google Trends + News API signals
- [ ] Dockerize and set up scheduled runs

### Phase 4 — Scale & Optimize (Week 7+)
- [ ] TikTok video generation and posting
- [ ] Reddit publishing
- [ ] A/B testing framework
- [ ] Dashboard for monitoring agent decisions
- [ ] Move to Postgres + deploy to cloud

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Platform bans (posting too fast, ToS violation) | Rate limiting, content safety checks, start slow |
| Stale/unfunny memes | Trend freshness scoring, timing constraints |
| Image gen costs | Cache common templates, use gen only for originals |
| API rate limits | Exponential backoff, request budgeting |
| Brand safety / controversial content | Agent safety prompt + keyword blocklist |
| Account authenticity detection | Natural posting patterns, varied formats |

---

## Environment Variables Needed

```bash
# Anthropic
ANTHROPIC_API_KEY=

# Image Generation
STABILITY_API_KEY=
OPENAI_API_KEY=           # for DALL-E fallback

# Instagram
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

# Twitter/X
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
TWITTER_BEARER_TOKEN=

# Reddit
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=

# News
NEWS_API_KEY=
```

---

## Next Steps

1. Decide on the account **niche/theme** — this drives everything else
2. Decide on target platform(s) for v1
3. Set up API credentials for chosen platforms
4. Start with Phase 1 implementation
