"""Adapter for Grok Voice TTS API calls."""

import base64
import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class VoiceProvider:
    """Interface to Grok Voice for text-to-speech narration."""

    def __init__(self):
        """Initialize voice provider with API credentials."""
        self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("XAI_API_KEY")
        # TODO: Replace with actual Grok Voice endpoint
        # Current placeholder: https://api.x.ai/v1/audio/speech
        # Note: Grok Voice TTS integration is pending endpoint availability
        self.api_url = "https://api.x.ai/v1/audio/speech"
        self.use_mock = True  # Set to False when real Grok Voice endpoint is available

    async def generate_voice(self, text: str) -> str:
        """
        Generate audio narration from text.

        Args:
            text: Text to convert to speech

        Returns:
            Base64-encoded audio data (WAV format)
        """
        if not self.api_key:
            logger.warning("No API key found, using mock audio")
            return self._get_mock_audio()

        if self.use_mock:
            logger.info("Mock audio mode (Grok Voice endpoint not yet integrated)")
            return self._get_mock_audio()

        return await self._call_voice_api(text)

    async def _call_voice_api(self, text: str) -> str:
        """
        Make HTTP request to Grok Voice API.

        TODO: Implement actual Grok Voice API call.
        Expected payload structure:
        {
            "text": "...",
            "voice": "alloy",  # or other voice options
            "model": "grok-voice-1"  # or appropriate model name
        }

        Expected response:
        Binary audio data (mp3 or WAV format)

        To integrate real Grok Voice:
        1. Confirm the correct API endpoint with Grok/xAI
        2. Update self.api_url with the real endpoint
        3. Set self.use_mock = False in __init__
        4. Test the integration
        """
        try:
            logger.info(f"Calling Grok Voice API for text: {len(text)} chars")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "text": text,
                "voice": "alloy",
                "model": "grok-voice-1",
            }

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(self.api_url, json=payload, headers=headers)
                resp.raise_for_status()
                # Assuming response is binary audio data
                audio_bytes = resp.content
                logger.info(
                    f"Successfully got audio from Grok Voice API ({len(audio_bytes)} bytes)"
                )
                return base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            logger.error(
                f"Grok Voice API call failed: {e}. Falling back to mock audio."
            )
            return self._get_mock_audio()

    @staticmethod
    def _get_mock_audio() -> str:
        """
        Return mock audio data for testing.

        Creates a valid WAV file with 1 second of silence.
        WAV format is more reliable for testing across browsers.
        """
        # WAV header for 1 second of silence at 44.1kHz, 16-bit mono
        # RIFF header
        riff_header = b"RIFF"
        wav_size = 36 + 44100 * 2  # File size - 8
        riff_header += wav_size.to_bytes(4, "little")

        # WAVE format
        format_chunk = b"WAVEfmt "
        format_chunk += (16).to_bytes(4, "little")  # Subchunk size
        format_chunk += (1).to_bytes(2, "little")  # Audio format (PCM)
        format_chunk += (1).to_bytes(2, "little")  # Number of channels (mono)
        format_chunk += (44100).to_bytes(4, "little")  # Sample rate
        format_chunk += (88200).to_bytes(4, "little")  # Byte rate (44100 * 2)
        format_chunk += (2).to_bytes(2, "little")  # Block align
        format_chunk += (16).to_bytes(2, "little")  # Bits per sample

        # Data chunk with silence (zeros)
        data_chunk = b"data"
        data_chunk += (44100 * 2).to_bytes(4, "little")  # Data size
        data_chunk += b"\x00" * (44100 * 2)  # 1 second of silence

        wav_data = riff_header + format_chunk + data_chunk
        return base64.b64encode(wav_data).decode("utf-8")


# Create singleton instance
voice = VoiceProvider()
