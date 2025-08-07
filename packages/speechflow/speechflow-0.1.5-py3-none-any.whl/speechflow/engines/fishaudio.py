from typing import Iterator, Literal, cast

import numpy as np
from fish_audio_sdk import ReferenceAudio, Session, TTSRequest

from ..core.base import AudioData, TTSEngineBase
from ..core.exceptions import ConfigurationError, StreamingError, TTSError


class FishAudioTTSEngine(TTSEngineBase):
    """FishAudio TTS engine implementation."""

    SUPPORTED_MODELS = [
        "s1",
        "s1-mini",
        "speech-1.6",
        "speech-1.5",
        "agent-x0",
    ]

    def __init__(self, api_key: str):
        """Initialize FishAudio TTS engine.

        Args:
            api_key: FishAudio API key

        Raises:
            ConfigurationError: If api_key is not provided
        """
        super().__init__()

        if not api_key:
            raise ConfigurationError("FishAudio API key is required")

        # Create client with API key
        self.session = Session(apikey=api_key)
        self.sample_rate = 44100  # Default sample rate

    def get(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Synthesize speech from text using FishAudio TTS.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        response_iterator = self.stream(text, model=model, voice=voice)
        audio_bytes = b""
        for audio_data in response_iterator:
            audio_bytes += audio_data.data.tobytes()

        return AudioData(
            data=np.frombuffer(audio_bytes, dtype=np.int16),
            sample_rate=self.sample_rate,
            channels=1,  # Default to mono
            format="pcm",
        )

    async def aget(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> AudioData:
        """Asynchronously synthesize speech from text using FishAudio TTS.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Returns:
            AudioData containing the synthesized speech
        """
        raise NotImplementedError("Asynchronous synthesis is not implemented for FishAudioTTSEngine")

    def stream(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
    ) -> Iterator[AudioData]:
        """Stream synthesized speech in chunks.

        Args:
            text: Text to synthesize
            model: Optional model name
            voice: Optional voice name

        Yields:
            AudioData chunks
        """

        if model not in self.SUPPORTED_MODELS:
            model = self.SUPPORTED_MODELS[0]

        try:
            response_iterator = self.session.tts(
                backend=cast(Literal["speech-1.5", "speech-1.6", "agent-x0", "s1", "s1-mini"], model),
                request=TTSRequest(
                    text=text,
                    reference_id=voice,
                    format="pcm",
                    sample_rate=self.sample_rate,
                ),
            )

            # Iterate through all responses
            for response in response_iterator:
                if response is None:
                    continue

                audio_data = self._extract_audio(response)
                if audio_data:
                    yield audio_data

        except RuntimeError as e:
            if "Generator did not stop" in str(e):
                # This error can occur at the end of the stream, which is normal
                pass
            else:
                raise StreamingError(f"FishAudio streaming error: {str(e)}")
        except Exception as e:
            raise TTSError(f"FishAudio TTS error: {str(e)}")

    def _extract_audio(self, response: bytes) -> AudioData | None:
        """Extract AudioData from FishAudio response.

        Args:
            response: bytes response from the TTS service

        Returns:
            AudioData if audio content is found, None otherwise
        """

        audio_bytes = response

        # Parse audio format from MIME type (e.g., "audio/L16;codec=pcm;rate=24000")
        sample_rate = self.sample_rate  # Default (FishAudio default)
        channels = 1  # Default to mono

        # Skip empty byte arrays
        if len(audio_bytes) == 0:
            return None

        # Ensure byte count is even
        if len(audio_bytes) % 2 != 0:
            audio_bytes = audio_bytes[:-1]  # Remove last byte

        # Skip if only 1 byte remains
        if len(audio_bytes) == 0:
            return None

        # Test endianness - try both little-endian and big-endian
        audio_data_le = np.frombuffer(audio_bytes, dtype="<i2")  # Little-endian int16
        audio_data_be = np.frombuffer(audio_bytes, dtype=">i2")  # Big-endian int16

        # Check which has more reasonable range
        if audio_data_le.size > 0 and audio_data_be.size > 0:
            le_max = np.abs(audio_data_le).max()
            be_max = np.abs(audio_data_be).max()

            # The one with smaller max value is more likely correct
            # However, if too small (<100), it might be silence
            if be_max < le_max and be_max > 100 and be_max < 20000:
                audio_data = audio_data_be
            elif le_max < be_max and le_max > 100 and le_max < 20000:
                audio_data = audio_data_le
            else:
                # If neither is reasonable, choose the one with smaller max
                if be_max < le_max:
                    audio_data = audio_data_be
                else:
                    audio_data = audio_data_le
        else:
            return None

        # Normalize to float32 [-1, 1]
        audio_data = audio_data.astype(np.float32) / 32767.0

        return AudioData(data=audio_data, sample_rate=sample_rate, channels=channels, format="pcm")
