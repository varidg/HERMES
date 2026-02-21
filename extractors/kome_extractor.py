"""
extractors/kome_extractor.py
-----------------------------
Fetches transcripts for YouTube and Twitch VOD URLs via kome.ai.
"""

import requests
from models.pipeline_state import PipelineState
from models.media_type import MediaType
from extractors.base_extractor import BaseExtractor

KOME_URL = "https://kome.ai/api/transcript"


class KomeExtractor(BaseExtractor):
    name = "KomeExtractor"

    def can_handle(self, state: PipelineState) -> bool:
        return state.media_type in (MediaType.YOUTUBE, MediaType.TWITCH)

    def extract(self, state: PipelineState) -> str:
        self.log.info(f"Fetching transcript via kome.ai for: {state.content_url}")
        resp = requests.post(
            KOME_URL,
            json={"video_id": state.content_url, "format": True},
            headers={"content-type": "application/json", "origin": "https://kome.ai"},
            timeout=90,
        )
        resp.raise_for_status()
        transcript = resp.json().get("transcript", "")

        if not transcript:
            raise ValueError(f"Empty transcript returned for: {state.content_url}")

        self.log.info(f"Transcript fetched — {len(transcript)} characters")
        return transcript
