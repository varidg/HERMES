# MIDAS
### Media Ingestion, Distillation & Agentic Summary System

MIDAS is a fully agentic, plug-and-play media intelligence pipeline.
It ingests content from any source, distils it with AI, and broadcasts
highlights to Discord — automatically, every day.

---

## Architecture

```
                          ┌─────────────────────────────┐
                          │        SchedulerAgent        │
                          │   fires pipeline.trigger     │
                          └────────────┬────────────────┘
                                       │
                          ┌────────────▼────────────────┐
                          │       SourceRouterAgent      │
                          │  routes to correct source    │
                          └──┬──────┬──────┬──────┬─────┘
                             │      │      │      │
                   ┌─────────▼─┐ ┌──▼───┐ ┌▼────┐ ┌▼──────────┐
                   │  YouTube  │ │Twitch│ │Reddit│ │  Podcast  │
                   │  Source   │ │Source│ │Source│ │  Source   │
                   └─────────┬─┘ └──┬───┘ └┬────┘ └┬──────────┘
                             │      │      │       │
                          ┌──▼──────▼──────▼───────▼──┐
                          │        ExtractorAgent      │
                          │  transcript/scrape/whisper │
                          └────────────┬───────────────┘
                                       │
                          ┌────────────▼────────────────┐
                          │         SummaryAgent         │
                          │      Google Gemini LLM       │
                          └────────────┬────────────────┘
                                       │
                          ┌────────────▼────────────────┐
                          │        NotifierAgent         │
                          │         → Discord            │
                          └─────────────────────────────┘
```

## Directory Structure

```
MIDAS/
├── main.py                        ← entry point
├── orchestrator.py                ← wires all agents + env config
├── requirements.txt
├── .env.example
├── README.md
│
├── config/
│   ├── __init__.py
│   └── settings.py                ← all config loaded from .env
│
├── bus/
│   ├── __init__.py
│   ├── message_bus.py             ← pub/sub event bus
│   └── events.py                  ← all event name constants
│
├── models/
│   ├── __init__.py
│   ├── pipeline_state.py          ← shared state dataclass
│   └── media_type.py              ← MediaType enum
│
├── sources/                       ← pluggable media ingestors
│   ├── __init__.py
│   ├── base_source.py             ← abstract source interface
│   ├── youtube_source.py          ← YouTube Data API v3
│   ├── twitch_source.py           ← Twitch Helix API (latest VOD)
│   ├── reddit_source.py           ← Reddit API (top post)
│   ├── podcast_source.py          ← RSS feed parser
│   └── article_source.py          ← web article scraper
│
├── extractors/                    ← content → raw text
│   ├── __init__.py
│   ├── base_extractor.py          ← abstract extractor interface
│   ├── kome_extractor.py          ← video transcript via kome.ai
│   ├── whisper_extractor.py       ← audio → text via OpenAI Whisper
│   └── scraper_extractor.py       ← HTML → text via BeautifulSoup
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              ← abstract base all agents inherit
│   ├── scheduler_agent.py         ← fires trigger on cron schedule
│   ├── source_router_agent.py     ← routes pipeline to correct source
│   ├── extractor_agent.py         ← picks and runs correct extractor
│   ├── summary_agent.py           ← Gemini summarisation
│   └── notifier_agent.py          ← Discord webhook posting
│
├── notifiers/
│   ├── __init__.py
│   ├── base_notifier.py           ← abstract notifier interface
│   └── discord_notifier.py        ← Discord webhook implementation
│
└── utils/
    ├── __init__.py
    └── logger.py                  ← centralised logging
```

## Supported Sources

| Source   | What it fetches                        | Extractor used     |
|----------|----------------------------------------|--------------------|
| YouTube  | Latest video from a channel            | kome.ai transcript |
| Twitch   | Latest VOD from a streamer             | kome.ai / Whisper  |
| Reddit   | Top post + top comments from subreddit | Scraper            |
| Podcast  | Latest episode from RSS feed           | Whisper (audio)    |
| Article  | Latest post from a blog/Substack       | Scraper            |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env    # fill in your keys
python main.py --now    # run immediately
python main.py          # wait for scheduled time
```

## Adding a New Source

1. Create `sources/mysource_source.py` extending `BaseSource`
2. Add `MediaType.MYSOURCE` to `models/media_type.py`
3. Register it in `sources/__init__.py`
4. Add it to `SourceRouterAgent`'s registry

No other files need to change.
