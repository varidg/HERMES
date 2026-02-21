"""
agents/notifier_agent.py
-------------------------
NotifierAgent
Listens for summary.ready, formats the final message with source metadata,
delegates to the registered notifier(s), and publishes pipeline.complete.
Also listens for pipeline.error to log failures gracefully.
"""

from bus.message_bus import MessageBus
from bus.events import Events
from agents.base_agent import BaseAgent
from models.pipeline_state import PipelineState
from notifiers.base_notifier import BaseNotifier


class NotifierAgent(BaseAgent):
    name = "NotifierAgent"
    input_events = [Events.SUMMARY_READY, Events.PIPELINE_ERROR]
    output_events = [Events.PIPELINE_COMPLETE]

    def __init__(self, bus: MessageBus, notifiers: list[BaseNotifier]) -> None:
        super().__init__(bus)
        self.notifiers = notifiers
        self.log.info(f"Registered notifiers: {[n.name for n in notifiers]}")

    def _format_message(self, state: PipelineState) -> str:
        source_line = f"Source: {state.source_name} [{state.media_type.value.upper()}]"
        url_line = f"URL: {state.content_url}"
        divider = "-" * 40
        return f"{source_line}\n{url_line}\n{divider}\n{state.summary}"

    def handle(self, payload: dict) -> None:
        # Pipeline error path
        if Events.PIPELINE_ERROR in str(payload.get("_event", "")) or "error" in payload:
            agent = payload.get("agent", "unknown")
            error = payload.get("error", "unknown error")
            self.log.error(f"Pipeline error reported by '{agent}': {error}")
            # Notify Discord about the failure too
            error_msg = f"[MIDAS ERROR] Pipeline failed in {agent}: {error}"
            for notifier in self.notifiers:
                try:
                    notifier.send(error_msg)
                except Exception as e:
                    self.log.error(f"Failed to send error notification via {notifier.name}: {e}")
            return

        # Success path
        state: PipelineState = payload["state"]
        message = self._format_message(state)

        for notifier in self.notifiers:
            try:
                status = notifier.send(message)
                self.log.info(f"{notifier.name} → status {status}")
                state.notification_sent = True
                state.notification_status_code = status
            except Exception as e:
                self.log.error(f"Notifier {notifier.name} failed: {e}")

        self.publish(Events.PIPELINE_COMPLETE, {"state": state})
        self.log.info(f"Pipeline complete for '{state.content_title}'")
        self.log.info(f"Final state: {state.to_dict()}")
