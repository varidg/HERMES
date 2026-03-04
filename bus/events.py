"""
bus/events.py
-------------
All event name constants used across the HERMES pipeline.
Using constants prevents typos and makes the event graph easy to audit.

Event flow:
    PIPELINE_TRIGGER
        └─► SOURCE_READY
                └─► CONTENT_EXTRACTED
                        └─► SUMMARY_READY
                                └─► PIPELINE_COMPLETE
    (any stage) ─► PIPELINE_ERROR
"""


class Events:
    # ── Lifecycle ──────────────────────────────────────────────────────────────
    PIPELINE_TRIGGER   = "pipeline.trigger"      # SchedulerAgent fires this
    PIPELINE_COMPLETE  = "pipeline.complete"      # NotifierAgent fires this
    PIPELINE_ERROR     = "pipeline.error"         # any agents fires on failure

    # ── Source stage ──────────────────────────────────────────────────────────
    SOURCE_READY       = "source.ready"           # SourceRouterAgent fires this

    # ── Extraction stage ──────────────────────────────────────────────────────
    CONTENT_EXTRACTED  = "content.extracted"      # ExtractorAgent fires this

    # ── Summary stage ─────────────────────────────────────────────────────────
    SUMMARY_READY      = "summary.ready"          # SummaryAgent fires this
