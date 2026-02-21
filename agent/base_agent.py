"""
agents/base_agent.py
--------------------
Abstract base class every MIDAS agent must inherit from.
Handles auto-subscription and safe error wrapping.
"""

from abc import ABC, abstractmethod
from bus.message_bus import MessageBus
from bus.events import Events
from utils.logger import get_logger


class BaseAgent(ABC):
    name: str = "BaseAgent"
    input_events: list[str] = []
    output_events: list[str] = []

    def __init__(self, bus: MessageBus) -> None:
        self.bus = bus
        self.log = get_logger(self.name)
        self._register()

    def _register(self) -> None:
        for event in self.input_events:
            self.bus.subscribe(event, self._safe_handle)
            self.log.info(f"Subscribed to → '{event}'")

    def _safe_handle(self, payload: dict) -> None:
        try:
            self.handle(payload)
        except Exception as exc:
            self.log.error(f"Error in {self.name}: {exc}", exc_info=True)
            self.bus.publish(Events.PIPELINE_ERROR, {
                "agent": self.name,
                "error": str(exc),
                "payload": payload,
            })

    @abstractmethod
    def handle(self, payload: dict) -> None:
        ...

    def publish(self, event: str, payload: dict) -> None:
        self.log.info(f"Publishing → '{event}'")
        self.bus.publish(event, payload)
