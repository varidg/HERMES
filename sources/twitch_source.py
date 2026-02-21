"""
sources/twitch_source.py
-------------------------
Fetches the latest VOD from a Twitch streamer via the Helix API.
"""

import requests
from models.pipeline_state import PipelineState
from sources.base_source import BaseSource

TWITCH_BASE = "https://api.twitch.tv/helix"
TWITCH_AUTH = "https://id.twitch.tv/oauth2/token"


class TwitchSource(BaseSource):
    name = "TwitchSource"

    def __init__(self, client_id: str, client_secret: str, streamer_login: str) -> None:
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.streamer_login = streamer_login
        self._token: str = ""

    def _get_token(self) -> str:
        if self._token:
            return self._token
        resp = requests.post(
            TWITCH_AUTH,
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            timeout=15,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def _headers(self) -> dict:
        return {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {self._get_token()}",
        }

    def _get_user_id(self) -> tuple[str, str]:
        resp = requests.get(
            f"{TWITCH_BASE}/users",
            params={"login": self.streamer_login},
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        user = resp.json()["data"][0]
        return user["id"], user["display_name"]

    def _get_latest_vod(self, user_id: str) -> dict:
        resp = requests.get(
            f"{TWITCH_BASE}/videos",
            params={"user_id": user_id, "type": "archive", "first": 1},
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        videos = resp.json()["data"]
        if not videos:
            raise ValueError(f"No VODs found for streamer: {self.streamer_login}")
        return videos[0]

    def fetch(self, state: PipelineState) -> PipelineState:
        self.log.info(f"Fetching latest Twitch VOD for: {self.streamer_login}")
        user_id, display_name = self._get_user_id()
        vod = self._get_latest_vod(user_id)

        state.source_name   = display_name
        state.content_id    = vod["id"]
        state.content_title = vod["title"]
        state.content_url   = vod["url"]
        state.content_meta  = {
            "duration": vod.get("duration"),
            "view_count": vod.get("view_count"),
            "created_at": vod.get("created_at"),
            "streamer_login": self.streamer_login,
        }

        self.log.info(f"Found VOD: '{vod['title']}' → {vod['url']}")
        return state
