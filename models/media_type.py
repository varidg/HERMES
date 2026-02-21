"""
models/media_type.py
--------------------
Enum of all supported media source types.
Adding a new source = adding a value here + a new source file.
"""

from enum import Enum


class MediaType(str, Enum):
    YOUTUBE = "youtube"
    TWITCH  = "twitch"
    REDDIT  = "reddit"
    PODCAST = "podcast"
    ARTICLE = "article"
