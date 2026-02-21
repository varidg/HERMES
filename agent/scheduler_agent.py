"""
agents/scheduler_agent.py
--------------------------
Fires pipeline.trigger events on a daily cron schedule.
One trigger is fired per active source, so each runs independently.
"""

import schedule
import time
import threading
from datetime import datetime

from bus.message_bus import MessageBus
from bus.events import Events
from agents.base_agent import BaseAgent
from models.pipeline_state import PipelineState
from models.media_type import MediaType


class SchedulerAgent(BaseAgent):
    name = "SchedulerAgent"
    input_events = []
    output_events = [Events.PIPELINE_TRIGGER]

    def __init__(self, bus: MessageBus, run_time: str, active_sources: list[MediaType]) -> None:
        super().__init__(bus)
        self.run_time = run_time
        self.active_sources = active_sources

    def handle(self, payload: dict) -> None:
        pass  # source agent — no inbound events

    def _fire(self) -> None:
        self.log.info(f"Trigger fired at {datetime.now().strftime('%H:%M:%S')} for {len(self.active_sources)} source(s)")
        for media_type in self.active_sources:
            state = PipelineState(triggered_at=datetime.now(), media_type=media_type)
            self.log.info(f"  → Triggering pipeline for source: {media_type.value}")
            self.publish(Events.PIPELINE_TRIGGER, {"state": state})

    def start(self, run_now: bool = False) -> None:
        if run_now:
            self.log.info("run_now=True — firing all pipelines immediately")
            self._fire()

        schedule.every().day.at(self.run_time).do(self._fire)
        self.log.info(f"Scheduled daily at {self.run_time} for sources: {[s.value for s in self.active_sources]}")

        def _loop():
            while True:
                schedule.run_pending()
                time.sleep(30)

        threading.Thread(target=_loop, daemon=True, name="SchedulerThread").start()
