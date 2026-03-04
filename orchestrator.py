"""
orchestrator.py
---------------
HERMES Orchestrator — the single place that:
  1. Reads all config from Settings
  2. Instantiates all sources, extractors, notifiers, and agents
  3. Wires them to the shared MessageBus
  4. Starts the SchedulerAgent

No agents, source, or extractor knows about any other.
All communication is via the MessageBus.
"""

from bus import MessageBus
from config import Settings
from models.media_type import MediaType

from sources import (
    YouTubeSource, TwitchSource, RedditSource,
    PodcastSource, ArticleSource,
)
from extractors import KomeExtractor, WhisperExtractor, ScraperExtractor
from notifiers import DiscordNotifier

from agents import (
    SchedulerAgent,
    SourceRouterAgent,
    ExtractorAgent,
    SummaryAgent,
    NotifierAgent,
)
from utils.logger import get_logger

log = get_logger("Orchestrator")


class Orchestrator:
    def __init__(self) -> None:
        self.cfg = Settings()
        self.bus = MessageBus()

        log.info("=" * 60)
        log.info("  HERMES — Hybrid Extraction & Relay for Media, Enrichment & Summary")
        log.info("=" * 60)
        log.info(f"Active sources: {[s.value for s in self.cfg.ACTIVE_SOURCES]}")

        # ── Sources ──────────────────────────────────────────────────────────
        available_sources: dict[MediaType, object] = {}

        if MediaType.YOUTUBE in self.cfg.ACTIVE_SOURCES:
            available_sources[MediaType.YOUTUBE] = YouTubeSource(
                api_key=self.cfg.YOUTUBE_API_KEY,
                channel_id=self.cfg.YOUTUBE_CHANNEL_ID,
            )

        if MediaType.TWITCH in self.cfg.ACTIVE_SOURCES:
            available_sources[MediaType.TWITCH] = TwitchSource(
                client_id=self.cfg.TWITCH_CLIENT_ID,
                client_secret=self.cfg.TWITCH_CLIENT_SECRET,
                streamer_login=self.cfg.TWITCH_STREAMER_LOGIN,
            )

        if MediaType.REDDIT in self.cfg.ACTIVE_SOURCES:
            available_sources[MediaType.REDDIT] = RedditSource(
                client_id=self.cfg.REDDIT_CLIENT_ID,
                client_secret=self.cfg.REDDIT_CLIENT_SECRET,
                user_agent=self.cfg.REDDIT_USER_AGENT,
                subreddit=self.cfg.REDDIT_SUBREDDIT,
            )

        if MediaType.PODCAST in self.cfg.ACTIVE_SOURCES:
            available_sources[MediaType.PODCAST] = PodcastSource(
                rss_url=self.cfg.PODCAST_RSS_URL,
            )

        if MediaType.ARTICLE in self.cfg.ACTIVE_SOURCES:
            available_sources[MediaType.ARTICLE] = ArticleSource(
                rss_url=self.cfg.ARTICLE_RSS_URL,
            )

        # ── Extractors ───────────────────────────────────────────────────────
        extractors = [
            KomeExtractor(),
            WhisperExtractor(api_key=self.cfg.OPENAI_API_KEY),
            ScraperExtractor(),
        ]

        # ── Notifiers ────────────────────────────────────────────────────────
        notifiers = [
            DiscordNotifier(webhook_url=self.cfg.DISCORD_WEBHOOK_URL),
        ]

        # ── Agents (order of instantiation doesn't matter — bus handles it) ─
        self.scheduler = SchedulerAgent(
            bus=self.bus,
            run_time=self.cfg.SCHEDULE_TIME,
            active_sources=self.cfg.ACTIVE_SOURCES,
        )
        self.source_router = SourceRouterAgent(bus=self.bus, sources=available_sources)
        self.extractor     = ExtractorAgent(bus=self.bus, extractors=extractors)
        self.summary       = SummaryAgent(bus=self.bus, api_key=self.cfg.GEMINI_API_KEY)
        self.notifier      = NotifierAgent(bus=self.bus, notifiers=notifiers)

        log.info("All agents, sources, and extractors registered.")

    def start(self, run_now: bool = False) -> None:
        self.scheduler.start(run_now=run_now)
