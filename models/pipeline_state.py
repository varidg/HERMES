"""
models/pipeline_state.py
------------------------
The shared state dataclass that flows through the entire pipeline.
Each agents receives it, enriches its relevant fields, and passes it on.
"""

from dataclasses import dataclass, field
from datetime import datetime
from models.media_type import MediaType


@dataclass
class PipelineState:
    # ── Set by SchedulerAgent ──────────────────────────────────────────────────
    triggered_at: datetime = field(default_factory=datetime.now)
    media_type: MediaType  = MediaType.YOUTUBE   # which source to run

    # ── Set by Source agents ───────────────────────────────────────────────────
    source_name: str  = ""     # human label e.g. "Linus Tech Tips"
    content_url: str  = ""     # canonical URL to the content
    content_id: str   = ""     # platform-specific ID (video_id, post_id, etc.)
    content_title: str = ""    # title of the piece of content
    content_meta: dict = field(default_factory=dict)  # extra platform metadata

    # ── Set by ExtractorAgent ─────────────────────────────────────────────────
    raw_text: str     = ""     # full extracted text (transcript / article body)
    extractor_used: str = ""   # which extractor was used

    # ── Set by SummaryAgent ───────────────────────────────────────────────────
    summary: str      = ""

    # ── Set by NotifierAgent ──────────────────────────────────────────────────
    notification_sent: bool = False
    notification_status_code: int = 0

    def to_dict(self) -> dict:
        return {
            "triggered_at": self.triggered_at.isoformat(),
            "media_type": self.media_type.value,
            "source_name": self.source_name,
            "content_title": self.content_title,
            "content_url": self.content_url,
            "raw_text_length": len(self.raw_text),
            "extractor_used": self.extractor_used,
            "summary_length": len(self.summary),
            "notification_sent": self.notification_sent,
            "notification_status_code": self.notification_status_code,
        }
