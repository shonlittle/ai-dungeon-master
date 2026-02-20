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
        # OpenRouter text-to-speech endpoint
        self.api_url = "https://openrouter.ai/api/v1/audio/speech"
        # Use real TTS API when available, fallback to mock if it fails
        self.use_mock = False  # Set to True to use mock audio for testing

        if self.api_key:
            logger.info(
                f"✓ Voice provider initialized with API key (first 10 chars: {self.api_key[:10]}...)"
            )
        else:
            logger.warning("✗ No API key found, voice will use mock audio")

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
        Make HTTP request to text-to-speech API.

        Uses OpenRouter's TTS endpoint which supports multiple models.
        """
        try:
            logger.info(f"Calling TTS API for text: {len(text)} chars")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Try OpenRouter's TTS endpoint
            payload = {
                "model": "openai/tts-1",
                "input": text,
                "voice": "alloy",
            }

            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(self.api_url, json=payload, headers=headers)
                resp.raise_for_status()
                # Response should be binary audio data
                audio_bytes = resp.content
                logger.info(
                    f"Successfully got audio from TTS API ({len(audio_bytes)} bytes)"
                )
                return base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"TTS API call failed: {e}. Falling back to mock audio.")
            return self._get_mock_audio()

    @staticmethod
    def _get_mock_audio() -> str:
        """
        Return mock audio data for testing.

        Creates a valid WAV file with 1 second of simple beeping tones.
        This allows you to test audio without a real API key.
        Change AUDIBLE_MOCK = False to get silent audio instead.
        """
        import math

        AUDIBLE_MOCK = True  # Set to False for silent audio
        SAMPLE_RATE = 44100
        DURATION = 1  # seconds
        FREQUENCY = 800  # Hz (frequency of beep tone)

        # Generate audio data
        num_samples = SAMPLE_RATE * DURATION
        audio_data = bytearray()

        for i in range(num_samples):
            if AUDIBLE_MOCK:
                # Create a simple beeping sound
                sample = int(
                    32767 * 0.3 * math.sin(2 * math.pi * FREQUENCY * i / SAMPLE_RATE)
                )
            else:
                # Silent audio
                sample = 0

            # Convert to 16-bit signed integer (little-endian)
            audio_data.extend(sample.to_bytes(2, "little", signed=True))

        # WAV header for the generated audio
        riff_header = b"RIFF"
        wav_size = 36 + len(audio_data)  # File size - 8
        riff_header += wav_size.to_bytes(4, "little")

        # WAVE format
        format_chunk = b"WAVEfmt "
        format_chunk += (16).to_bytes(4, "little")  # Subchunk size
        format_chunk += (1).to_bytes(2, "little")  # Audio format (PCM)
        format_chunk += (1).to_bytes(2, "little")  # Number of channels (mono)
        format_chunk += SAMPLE_RATE.to_bytes(4, "little")  # Sample rate
        format_chunk += (SAMPLE_RATE * 2).to_bytes(4, "little")  # Byte rate
        format_chunk += (2).to_bytes(2, "little")  # Block align
        format_chunk += (16).to_bytes(2, "little")  # Bits per sample

        # Data chunk
        data_chunk = b"data"
        data_chunk += len(audio_data).to_bytes(4, "little")
        data_chunk += audio_data

        wav_data = riff_header + format_chunk + data_chunk
        return base64.b64encode(wav_data).decode("utf-8")


# Create singleton instance
voice = VoiceProvider()
