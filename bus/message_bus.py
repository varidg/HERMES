"""
bus/message_bus.py
------------------
Lightweight synchronous pub/sub bus.
All inter-agents communication flows through here.
No agents imports or calls any other agents directly.
"""

from collections import defaultdict
from typing import Any, Callable


class MessageBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable[[dict], None]) -> None:
        self._subscribers[event].append(handler)

    def publish(self, event: str, payload: dict[str, Any] | None = None) -> None:
        payload = payload or {}
        for handler in self._subscribers.get(event, []):
            handler(payload)
