"""
agents/source_router_agent.py
------------------------------
SourceRouterAgent
Listens for pipeline.trigger events, looks at state.media_type,
delegates to the correct registered BaseSource, then publishes source.ready.

Adding a new source = registering it in the Orchestrator.
No source knows about any other source.
"""

from bus.message_bus import MessageBus
from bus.events import Events
from agents.base_agent import BaseAgent
from models.pipeline_state import PipelineState
from models.media_type import MediaType
from sources.base_source import BaseSource


class SourceRouterAgent(BaseAgent):
    name = "SourceRouterAgent"
    input_events = [Events.PIPELINE_TRIGGER]
    output_events = [Events.SOURCE_READY]

    def __init__(self, bus: MessageBus, sources: dict[MediaType, BaseSource]) -> None:
        super().__init__(bus)
        self.sources = sources
        self.log.info(f"Registered sources: {[k.value for k in sources]}")

    def handle(self, payload: dict) -> None:
        state: PipelineState = payload["state"]
        media_type = state.media_type

        source = self.sources.get(media_type)
        if not source:
            raise ValueError(f"No source registered for media type: {media_type.value}")

        self.log.info(f"Routing {media_type.value} → {source.name}")
        state = source.fetch(state)
        self.publish(Events.SOURCE_READY, {"state": state})
