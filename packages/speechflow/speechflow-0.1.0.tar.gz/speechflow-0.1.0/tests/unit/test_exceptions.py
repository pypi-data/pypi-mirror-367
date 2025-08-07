"""Unit tests for custom exceptions."""

import pytest

from speechflow.core.exceptions import (
    TTSError,
    ConfigurationError,
    StreamingError,
    AudioProcessingError,
    EngineNotFoundError
)


class TestExceptions:
    """Test cases for custom exceptions."""
    
    def test_tts_error(self):
        """Test TTSError exception."""
        with pytest.raises(TTSError) as exc_info:
            raise TTSError("Test TTS error")
        
        assert str(exc_info.value) == "Test TTS error"
        assert isinstance(exc_info.value, Exception)
    
    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Invalid configuration")
        
        assert str(exc_info.value) == "Invalid configuration"
        assert isinstance(exc_info.value, TTSError)
    
    def test_streaming_error(self):
        """Test StreamingError exception."""
        with pytest.raises(StreamingError) as exc_info:
            raise StreamingError("Stream failed")
        
        assert str(exc_info.value) == "Stream failed"
        assert isinstance(exc_info.value, TTSError)
    
    def test_audio_processing_error(self):
        """Test AudioProcessingError exception."""
        with pytest.raises(AudioProcessingError) as exc_info:
            raise AudioProcessingError("Audio processing failed")
        
        assert str(exc_info.value) == "Audio processing failed"
        assert isinstance(exc_info.value, TTSError)
    
    def test_engine_not_found_error(self):
        """Test EngineNotFoundError exception."""
        with pytest.raises(EngineNotFoundError) as exc_info:
            raise EngineNotFoundError("Engine not found")
        
        assert str(exc_info.value) == "Engine not found"
        assert isinstance(exc_info.value, TTSError)
    
    def test_exception_hierarchy(self):
        """Test that all custom exceptions inherit from TTSError."""
        exceptions = [
            ConfigurationError("test"),
            StreamingError("test"),
            AudioProcessingError("test"),
            EngineNotFoundError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, TTSError)