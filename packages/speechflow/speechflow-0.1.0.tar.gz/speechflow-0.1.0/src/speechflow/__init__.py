from .audio import AudioPlayer, AudioWriter
from .core import AudioData, AudioProcessingError, EngineNotFoundError, TTSEngineBase, TTSError
from .engines import FishAudioTTSEngine, GeminiTTSEngine, KokoroTTSEngine, OpenAITTSEngine, StyleBertTTSEngine

__version__ = "0.1.0"

__all__ = [
    # Core
    "TTSEngineBase",
    "AudioData",
    # Exceptions
    "TTSError",
    "EngineNotFoundError",
    "AudioProcessingError",
    # Audio components
    "AudioPlayer",
    "AudioWriter",
    # Engines
    "FishAudioTTSEngine",
    "GeminiTTSEngine",
    "KokoroTTSEngine",
    "OpenAITTSEngine",
    "StyleBertTTSEngine",
]
