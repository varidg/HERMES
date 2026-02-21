"""
extractors/scraper_extractor.py
--------------------------------
Extracts readable text from web pages (articles, Substack, blogs).
Also handles Reddit posts where raw_text is pre-populated in content_meta.
Uses BeautifulSoup with lxml for fast, clean extraction.
"""

import requests
from bs4 import BeautifulSoup

from models.pipeline_state import PipelineState
from models.media_type import MediaType
from extractors.base_extractor import BaseExtractor

HEADERS = {
    "User-Agent": "MIDAS/1.0 (Media Intelligence Pipeline; content research bot)"
}


class ScraperExtractor(BaseExtractor):
    name = "ScraperExtractor"

    def can_handle(self, state: PipelineState) -> bool:
        return state.media_type in (MediaType.ARTICLE, MediaType.REDDIT)

    def extract(self, state: PipelineState) -> str:
        # Reddit pre-populates raw_text in content_meta — no scraping needed
        if state.media_type == MediaType.REDDIT:
            raw = state.content_meta.get("raw_text", "")
            if raw:
                self.log.info(f"Using pre-extracted Reddit text — {len(raw)} characters")
                return raw

        self.log.info(f"Scraping article: {state.content_url}")
        resp = requests.get(state.content_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove boilerplate elements
        for tag in soup(["script", "style", "nav", "header", "footer",
                          "aside", "form", "button", "iframe", "noscript"]):
            tag.decompose()

        # Try to find main content block
        content = (
            soup.find("article")
            or soup.find("main")
            or soup.find(class_=lambda c: c and any(
                k in c for k in ["post-content", "article-body", "entry-content", "prose"]
            ))
            or soup.find("body")
        )

        text = content.get_text(separator="\n", strip=True) if content else ""

        if not text:
            raise ValueError(f"Could not extract text from: {state.content_url}")

        self.log.info(f"Scraped {len(text)} characters from {state.content_url}")
        return text
