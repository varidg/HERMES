"""
sources/base_source.py
----------------------
Abstract interface every source must implement.
A source's job: given config, return a populated PipelineState
with source_name, content_url, content_id, content_title, content_meta filled in.
"""

from abc import ABC, abstractmethod
from models.pipeline_state import PipelineState
from utils.logger import get_logger


class BaseSource(ABC):
    name: str = "BaseSource"

    def __init__(self) -> None:
        self.log = get_logger(self.name)

    @abstractmethod
    def fetch(self, state: PipelineState) -> PipelineState:
        """
        Fetch metadata for the latest piece of content.
        Populate state fields: source_name, content_url, content_id,
        content_title, content_meta.
        Return the enriched state.
        """
        ...
