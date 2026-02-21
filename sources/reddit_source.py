"""
sources/reddit_source.py
-------------------------
Fetches the top post of the day from a subreddit via PRAW.
Includes top comments for richer summarisation context.
"""

import praw
from models.pipeline_state import PipelineState
from sources.base_source import BaseSource


class RedditSource(BaseSource):
    name = "RedditSource"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        subreddit: str,
        top_comments: int = 10,
    ) -> None:
        super().__init__()
        self.subreddit = subreddit
        self.top_comments = top_comments
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

    def fetch(self, state: PipelineState) -> PipelineState:
        self.log.info(f"Fetching top post from r/{self.subreddit}")
        sub = self.reddit.subreddit(self.subreddit)
        post = next(sub.top(time_filter="day", limit=1))

        # Build a rich text blob: title + selftext + top comments
        lines = [f"Title: {post.title}"]
        if post.selftext:
            lines.append(f"\nPost body:\n{post.selftext}")

        post.comments.replace_more(limit=0)
        top = post.comments.list()[: self.top_comments]
        if top:
            lines.append("\nTop comments:")
            for i, c in enumerate(top, 1):
                lines.append(f"{i}. {c.body[:500]}")

        # Store raw text in content_meta so ExtractorAgent can pass it through
        combined = "\n".join(lines)

        state.source_name   = f"r/{self.subreddit}"
        state.content_id    = post.id
        state.content_title = post.title
        state.content_url   = f"https://reddit.com{post.permalink}"
        state.content_meta  = {
            "raw_text": combined,   # pre-extracted — no separate extractor needed
            "score": post.score,
            "num_comments": post.num_comments,
            "author": str(post.author),
        }

        self.log.info(f"Found post: '{post.title}' (score: {post.score})")
        return state
