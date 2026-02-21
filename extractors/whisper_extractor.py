"""
extractors/whisper_extractor.py
--------------------------------
Transcribes audio content (podcasts) using OpenAI Whisper API.
Downloads the audio file to a temp location, then transcribes.
"""

import os
import tempfile
import requests
from openai import OpenAI

from models.pipeline_state import PipelineState
from models.media_type import MediaType
from extractors.base_extractor import BaseExtractor


class WhisperExtractor(BaseExtractor):
    name = "WhisperExtractor"

    def __init__(self, api_key: str) -> None:
        super().__init__()
        self.client = OpenAI(api_key=api_key)

    def can_handle(self, state: PipelineState) -> bool:
        return state.media_type == MediaType.PODCAST

    def extract(self, state: PipelineState) -> str:
        audio_url = state.content_meta.get("audio_url", "")
        if not audio_url:
            raise ValueError("No audio_url found in content_meta for Whisper extraction")

        self.log.info(f"Downloading audio for Whisper transcription: {audio_url}")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
            resp = requests.get(audio_url, stream=True, timeout=120)
            resp.raise_for_status()
            for chunk in resp.iter_content(chunk_size=8192):
                tmp.write(chunk)

        try:
            self.log.info(f"Transcribing with Whisper — file: {tmp_path}")
            with open(tmp_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                )
            text = transcription.text
            self.log.info(f"Whisper transcription complete — {len(text)} characters")
            return text
        finally:
            os.unlink(tmp_path)
