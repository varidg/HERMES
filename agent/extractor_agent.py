"""
agents/extractor_agent.py
--------------------------
ExtractorAgent
Listens for source.ready events, auto-selects the correct extractor
based on media_type (using extractor.can_handle()), runs it,
and publishes content.extracted.

Adding a new extractor = registering it here. No extractor knows about others.
"""

from bus.message_bus import MessageBus
from bus.events import Events
from agents.base_agent import BaseAgent
from models.pipeline_state import PipelineState
from extractors.base_extractor import BaseExtractor


class ExtractorAgent(BaseAgent):
    name = "ExtractorAgent"
    input_events = [Events.SOURCE_READY]
    output_events = [Events.CONTENT_EXTRACTED]

    def __init__(self, bus: MessageBus, extractors: list[BaseExtractor]) -> None:
        super().__init__(bus)
        self.extractors = extractors
        self.log.info(f"Registered extractors: {[e.name for e in extractors]}")

    def handle(self, payload: dict) -> None:
        state: PipelineState = payload["state"]

        # Find the first extractor that can handle this media type
        extractor = next((e for e in self.extractors if e.can_handle(state)), None)

        if not extractor:
            raise ValueError(
                f"No extractor can handle media_type: {state.media_type.value}. "
                f"Available: {[e.name for e in self.extractors]}"
            )

        self.log.info(f"Selected extractor: {extractor.name} for {state.media_type.value}")
        raw_text = extractor.extract(state)

        state.raw_text = raw_text
        state.extractor_used = extractor.name

        self.publish(Events.CONTENT_EXTRACTED, {"state": state})
