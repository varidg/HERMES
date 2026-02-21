"""
notifiers/discord_notifier.py
------------------------------
Posts messages to a Discord channel via webhook.
Handles Discord's 2000 character message limit by chunking long messages.
"""

from discord_webhook import DiscordWebhook
from notifiers.base_notifier import BaseNotifier

MAX_DISCORD_LENGTH = 1900  # leave buffer below Discord's 2000 char limit


class DiscordNotifier(BaseNotifier):
    name = "DiscordNotifier"

    def __init__(self, webhook_url: str) -> None:
        super().__init__()
        self.webhook_url = webhook_url

    def _chunks(self, text: str) -> list[str]:
        """Split text into Discord-safe chunks."""
        return [text[i: i + MAX_DISCORD_LENGTH] for i in range(0, len(text), MAX_DISCORD_LENGTH)]

    def send(self, message: str) -> int:
        chunks = self._chunks(message)
        last_status = 0

        for i, chunk in enumerate(chunks, 1):
            self.log.info(f"Sending Discord chunk {i}/{len(chunks)} ({len(chunk)} chars)")
            webhook = DiscordWebhook(url=self.webhook_url, content=chunk)
            resp = webhook.execute()
            last_status = resp.status_code

        self.log.info(f"Discord delivery complete — final status: {last_status}")
        return last_status
