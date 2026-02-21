"""
notifiers/base_notifier.py
---------------------------
Abstract interface every notifier must implement.
Adding a new output channel = a new file extending this class.
"""

from abc import ABC, abstractmethod
from utils.logger import get_logger


class BaseNotifier(ABC):
    name: str = "BaseNotifier"

    def __init__(self) -> None:
        self.log = get_logger(self.name)

    @abstractmethod
    def send(self, message: str) -> int:
        """Send the message. Return the HTTP status code."""
        ...
