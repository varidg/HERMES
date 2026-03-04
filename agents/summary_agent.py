"""
agents/summary_agent.py
------------------------
SummaryAgent
Listens for content.extracted, sends raw_text to Google Gemini
with a media-type-aware prompt, and publishes summary.ready.
"""

import google.generativeai as genai

from bus.message_bus import MessageBus
from bus.events import Events
from agents.base_agent import BaseAgent
from models.pipeline_state import PipelineState
from models.media_type import MediaType

# Tailored prompts per media type for better summaries
PROMPTS: dict[MediaType, str] = {
    MediaType.YOUTUBE: (
        "Summarise this YouTube video transcript. Structure your response as:\n"
        "1. TITLE & DATE\n2. KEY POINTS (plain text bullets, no symbols)\n3. SUMMARY\n"
        "Keep under 2000 characters. No markdown, no special characters."
    ),
    MediaType.TWITCH: (
        "Summarise this Twitch stream transcript. Structure your response as:\n"
        "1. STREAM TITLE & DATE\n2. HIGHLIGHTS (what happened, key moments)\n3. SUMMARY\n"
        "Keep under 2000 characters. No markdown, no special characters."
    ),
    MediaType.REDDIT: (
        "Summarise this Reddit post and its top comments. Structure your response as:\n"
        "1. POST TITLE & SUBREDDIT\n2. KEY DISCUSSION POINTS\n3. COMMUNITY SENTIMENT\n"
        "Keep under 2000 characters. No markdown, no special characters."
    ),
    MediaType.PODCAST: (
        "Summarise this podcast episode transcript. Structure your response as:\n"
        "1. EPISODE TITLE & SHOW\n2. KEY TOPICS DISCUSSED\n3. SUMMARY & TAKEAWAYS\n"
        "Keep under 2000 characters. No markdown, no special characters."
    ),
    MediaType.ARTICLE: (
        "Summarise this article or blog post. Structure your response as:\n"
        "1. ARTICLE TITLE & SOURCE\n2. KEY ARGUMENTS & POINTS\n3. CONCLUSION\n"
        "Keep under 2000 characters. No markdown, no special characters."
    ),
}


class SummaryAgent(BaseAgent):
    name = "SummaryAgent"
    input_events = [Events.CONTENT_EXTRACTED]
    output_events = [Events.SUMMARY_READY]

    def __init__(self, bus: MessageBus, api_key: str, model_name: str = "gemini-2.0-flash") -> None:
        super().__init__(bus)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def handle(self, payload: dict) -> None:
        state: PipelineState = payload["state"]

        prompt_intro = PROMPTS.get(state.media_type, PROMPTS[MediaType.ARTICLE])
        prompt = f"{prompt_intro}\n\nContent:\n\n{state.raw_text}"

        self.log.info(f"Summarising {state.media_type.value} content with {self.model_name}")
        response = self.model.generate_content(prompt)
        summary = response.text.strip()

        if not summary:
            raise ValueError("Gemini returned an empty summary")

        state.summary = summary
        self.log.info(f"Summary complete — {len(summary)} characters")
        self.publish(Events.SUMMARY_READY, {"state": state})
