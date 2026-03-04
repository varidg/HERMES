"""
config/settings.py
------------------
Single place where all environment variables are loaded and validated.
Imported by the Orchestrator — agents receive only what they need.
"""

import os
from dotenv import load_dotenv
from models.media_type import MediaType

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Required environment variable missing: {key}")
    return val


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


class Settings:
    # ── Schedule ───────────────────────────────────────────────────────────────
    SCHEDULE_TIME: str = _optional("SCHEDULE_TIME", "15:00")

    # ── Active sources ─────────────────────────────────────────────────────────
    _raw_sources = _optional("ACTIVE_SOURCES", "youtube")
    ACTIVE_SOURCES: list[MediaType] = [
        MediaType(s.strip()) for s in _raw_sources.split(",") if s.strip()
    ]

    # ── YouTube ────────────────────────────────────────────────────────────────
    YOUTUBE_API_KEY:    str = _optional("YOUTUBE_API_KEY")
    YOUTUBE_CHANNEL_ID: str = _optional("YOUTUBE_CHANNEL_ID")

    # ── Twitch ─────────────────────────────────────────────────────────────────
    TWITCH_CLIENT_ID:     str = _optional("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET: str = _optional("TWITCH_CLIENT_SECRET")
    TWITCH_STREAMER_LOGIN: str = _optional("TWITCH_STREAMER_LOGIN")

    # ── Reddit ─────────────────────────────────────────────────────────────────
    REDDIT_CLIENT_ID:     str = _optional("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = _optional("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT:    str = _optional("REDDIT_USER_AGENT", "HERMES/1.0")
    REDDIT_SUBREDDIT:     str = _optional("REDDIT_SUBREDDIT", "technology")

    # ── Podcast ────────────────────────────────────────────────────────────────
    PODCAST_RSS_URL: str = _optional("PODCAST_RSS_URL")

    # ── Article ────────────────────────────────────────────────────────────────
    ARTICLE_RSS_URL: str = _optional("ARTICLE_RSS_URL")

    # ── AI ─────────────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = _optional("GEMINI_API_KEY")
    OPENAI_API_KEY: str = _optional("OPENAI_API_KEY")

    # ── Discord ────────────────────────────────────────────────────────────────
    DISCORD_WEBHOOK_URL: str = _optional("DISCORD_WEBHOOK_URL")
