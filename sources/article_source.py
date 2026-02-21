"""
sources/article_source.py
--------------------------
Fetches the latest article from a blog/Substack RSS feed.
Stores the article URL so ScraperExtractor can extract the full text.
"""

import feedparser
from models.pipeline_state import PipelineState
from sources.base_source import BaseSource


class ArticleSource(BaseSource):
    name = "ArticleSource"

    def __init__(self, rss_url: str) -> None:
        super().__init__()
        self.rss_url = rss_url

    def fetch(self, state: PipelineState) -> PipelineState:
        self.log.info(f"Parsing article RSS: {self.rss_url}")
        feed = feedparser.parse(self.rss_url)

        if not feed.entries:
            raise ValueError(f"No entries found in RSS feed: {self.rss_url}")

        article = feed.entries[0]
        blog_name = feed.feed.get("title", "Unknown Blog")

        state.source_name   = blog_name
        state.content_id    = article.get("id", article.get("link", ""))
        state.content_title = article.get("title", "Untitled Article")
        state.content_url   = article.get("link", "")
        state.content_meta  = {
            "published": article.get("published", ""),
            "author": article.get("author", ""),
            "tags": [t.term for t in article.get("tags", [])],
        }

        self.log.info(f"Found article: '{state.content_title}' from {blog_name}")
        return state
