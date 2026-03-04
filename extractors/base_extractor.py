"""
extractors/base_extractor.py
-----------------------------
Abstract interface every extractor must implement.
An extractor's job: given a populated PipelineState,
return raw_text extracted from the content.
"""

from abc import ABC, abstractmethod
from models.pipeline_state import PipelineState
from utils.logger import get_logger


class BaseExtractor(ABC):
    name: str = "BaseExtractor"

    def __init__(self) -> None:
        self.log = get_logger(self.name)

    @abstractmethod
    def can_handle(self, state: PipelineState) -> bool:
        """Return True if this extractor can handle the given state."""
        ...

    @abstractmethod
    def extract(self, state: PipelineState) -> str:
        """Extract and return raw text from the content."""
        ...
