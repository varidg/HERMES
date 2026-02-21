"""
sources/podcast_source.py
--------------------------
Fetches the latest episode from a podcast RSS feed via feedparser.
The audio URL is stored so WhisperExtractor can transcribe it.
"""

import feedparser
from models.pipeline_state import PipelineState
from sources.base_source import BaseSource


class PodcastSource(BaseSource):
    name = "PodcastSource"

    def __init__(self, rss_url: str) -> None:
        super().__init__()
        self.rss_url = rss_url

    def fetch(self, state: PipelineState) -> PipelineState:
        self.log.info(f"Parsing podcast RSS: {self.rss_url}")
        feed = feedparser.parse(self.rss_url)

        if not feed.entries:
            raise ValueError(f"No entries found in RSS feed: {self.rss_url}")

        ep = feed.entries[0]
        podcast_name = feed.feed.get("title", "Unknown Podcast")

        # Find the audio enclosure URL
        audio_url = ""
        for enc in ep.get("enclosures", []):
            if "audio" in enc.get("type", ""):
                audio_url = enc.get("href", "")
                break

        if not audio_url:
            raise ValueError(f"No audio enclosure found in episode: {ep.get('title')}")

        state.source_name   = podcast_name
        state.content_id    = ep.get("id", ep.get("link", ""))
        state.content_title = ep.get("title", "Untitled Episode")
        state.content_url   = ep.get("link", audio_url)
        state.content_meta  = {
            "audio_url": audio_url,         # WhisperExtractor reads this
            "published": ep.get("published", ""),
            "duration": ep.get("itunes_duration", ""),
            "summary": ep.get("summary", ""),
        }

        self.log.info(f"Found episode: '{state.content_title}' from {podcast_name}")
        return state
