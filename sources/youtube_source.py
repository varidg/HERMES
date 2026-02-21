"""
sources/youtube_source.py
--------------------------
Fetches the latest video from a YouTube channel via the Data API v3.
"""

import requests
from models.pipeline_state import PipelineState
from sources.base_source import BaseSource

YOUTUBE_BASE = "https://youtube.googleapis.com/youtube/v3"


class YouTubeSource(BaseSource):
    name = "YouTubeSource"

    def __init__(self, api_key: str, channel_id: str) -> None:
        super().__init__()
        self.api_key = api_key
        self.channel_id = channel_id

    def _get_uploads_playlist(self) -> str:
        resp = requests.get(
            f"{YOUTUBE_BASE}/channels",
            params={"part": "contentDetails", "id": self.channel_id, "key": self.api_key},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _get_latest_video(self, playlist_id: str) -> tuple[str, str, str]:
        resp = requests.get(
            f"{YOUTUBE_BASE}/playlistItems",
            params={"part": "snippet", "playlistId": playlist_id, "maxResults": 1, "key": self.api_key},
            timeout=15,
        )
        resp.raise_for_status()
        snippet = resp.json()["items"][0]["snippet"]
        video_id = snippet["resourceId"]["videoId"]
        return video_id, snippet["title"], snippet.get("channelTitle", "")

    def fetch(self, state: PipelineState) -> PipelineState:
        self.log.info(f"Fetching latest YouTube video for channel: {self.channel_id}")
        playlist_id = self._get_uploads_playlist()
        video_id, title, channel_name = self._get_latest_video(playlist_id)

        state.source_name  = channel_name
        state.content_id   = video_id
        state.content_title = title
        state.content_url  = f"https://www.youtube.com/watch?v={video_id}"
        state.content_meta = {"playlist_id": playlist_id, "channel_id": self.channel_id}

        self.log.info(f"Found: '{title}' → {state.content_url}")
        return state
