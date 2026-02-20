"""Adapter for Grok Voice TTS API calls."""

import base64
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class VoiceProvider:
    """Interface to Grok Voice for text-to-speech narration."""

    def __init__(self):
        """Initialize voice provider with API credentials."""
        self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("XAI_API_KEY")
        # TODO: Replace with actual Grok Voice endpoint
        self.api_url = "https://api.x.ai/v1/audio/speech"

    async def generate_voice(self, text: str) -> str:
        """
        Generate audio narration from text.

        Args:
            text: Text to convert to speech

        Returns:
            Base64-encoded audio data (mp3)
        """
        if not self.api_key:
            # Return mock audio for testing
            return self._get_mock_audio()

        return await self._call_voice_api(text)

    async def _call_voice_api(self, text: str) -> str:
        """
        Make HTTP request to Grok Voice API.

        TODO: Implement actual Grok Voice API call.
        Expected payload structure:
        {
            "text": "...",
            "voice": "alloy",  # or other voice
            "model": "grok-voice-1"
        }

        Expected response:
        Binary audio data (mp3 format)
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "text": text,
                "voice": "alloy",
                "model": "grok-voice-1",  # Placeholder model name
            }

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(self.api_url, json=payload, headers=headers)
                resp.raise_for_status()
                # Assuming response is binary audio data
                audio_bytes = resp.content
                return base64.b64encode(audio_bytes).decode("utf-8")
        except Exception:
            # Fallback to mock if real API fails
            return self._get_mock_audio()

    @staticmethod
    def _get_mock_audio() -> str:
        """
        Return mock audio data for testing.

        Creates a simple silent MP3 frame (about 1 second of silence).
        """
        # Minimal valid MP3 header (MPEG-1 Layer III, 44.1kHz, 128kbps)
        # This creates a short silent audio file for testing
        mp3_frame = (
            b"\xff\xfb\x90\x00"  # MP3 sync word + MPEG1 Layer3 128kbps
            b"\x00" * 118  # Padding to complete frame
        )
        # Create multiple frames for ~1 second of audio
        mock_mp3 = mp3_frame * 40  # Approximately 1 second
        return base64.b64encode(mock_mp3).decode("utf-8")


# Create singleton instance
voice = VoiceProvider()
