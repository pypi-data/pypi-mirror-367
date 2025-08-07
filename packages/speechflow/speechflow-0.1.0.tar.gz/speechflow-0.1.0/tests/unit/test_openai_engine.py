"""Unit tests for OpenAI TTS engine."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import os
import io
import wave

from speechflow.engines.openai import OpenAIEngine
from speechflow.core.exceptions import ConfigurationError, TTSError


class TestOpenAIEngine:
    """Test cases for OpenAIEngine."""
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_init_with_api_key(self, mock_openai_class):
        """Test initialization with API key."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        engine = OpenAIEngine(api_key="test-key")
        
        mock_openai_class.assert_called_once_with(api_key="test-key")
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIEngine(api_key="")
        
        assert "OpenAI API key is required" in str(exc_info.value)
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_init_with_custom_voice(self, mock_openai_class):
        """Test initialization with custom voice."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        engine = OpenAIEngine(api_key="test-key")
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_init_with_invalid_voice(self, mock_openai_class):
        """Test initialization with invalid voice raises error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIEngine(api_key="test-key", voice="InvalidVoice")
        
        assert "Unsupported voice" in str(exc_info.value)
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_init_with_custom_model(self, mock_openai_class):
        """Test initialization with custom model."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        engine = OpenAIEngine(api_key="test-key", model="tts-1-hd")
        assert engine.model == "tts-1-hd"
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_init_with_default_model(self, mock_openai_class):
        """Test initialization uses default model when not specified."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        engine = OpenAIEngine(api_key="test-key")
        assert engine.model == OpenAIEngine.DEFAULT_MODEL
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_synthesize_success(self, mock_openai_class):
        """Test successful speech synthesis."""
        # Create test WAV data
        sample_rate = 24000
        duration = 1.0
        samples = int(sample_rate * duration)
        audio_data = np.random.randint(-32768, 32767, samples, dtype=np.int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        wav_bytes = wav_buffer.getvalue()
        
        # Setup mock
        mock_response = Mock()
        mock_response.read.return_value = wav_bytes
        
        mock_client = Mock()
        mock_client.audio.speech.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Test synthesis
        engine = OpenAIEngine(api_key="test-key")
        audio = engine.synthesize("Hello world")
        
        assert audio.sample_rate == sample_rate
        assert audio.channels == 1
        assert audio.format == "wav"
        assert len(audio.data) == samples
        
        # Verify API was called correctly
        mock_client.audio.speech.create.assert_called_once_with(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input="Hello world",
            speed=1.0,
            response_format="wav"
        )
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_synthesize_with_different_voice(self, mock_openai_class):
        """Test synthesis with different voice parameter."""
        # Create test WAV data
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(np.zeros(24000, dtype=np.int16).tobytes())
        wav_bytes = wav_buffer.getvalue()
        
        # Setup mock
        mock_response = Mock()
        mock_response.read.return_value = wav_bytes
        
        mock_client = Mock()
        mock_client.audio.speech.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Test synthesis with different voice
        engine = OpenAIEngine(api_key="test-key")
        audio = engine.synthesize("Hello", voice="echo")
        
        # Verify the API was called with correct voice
        mock_client.audio.speech.create.assert_called_once_with(
            model="gpt-4o-mini-tts",
            voice="echo",
            input="Hello",
            speed=1.0,
            response_format="wav"
        )
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_synthesize_error(self, mock_openai_class):
        """Test synthesis error handling."""
        mock_client = Mock()
        mock_client.audio.speech.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        engine = OpenAIEngine(api_key="test-key")
        
        with pytest.raises(TTSError) as exc_info:
            engine.synthesize("Hello")
        
        assert "OpenAI TTS synthesis failed" in str(exc_info.value)
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_stream_real_streaming(self, mock_openai_class):
        """Test real streaming with PCM format."""
        # Create test PCM data (3 seconds at 24kHz)
        sample_rate = 24000
        duration = 3.0
        total_samples = int(sample_rate * duration)
        pcm_data = np.random.randint(-32768, 32767, total_samples, dtype=np.int16).tobytes()
        
        # Mock streaming response
        class MockStreamResponse:
            def __init__(self, data):
                self.data = data
                
            def iter_bytes(self, chunk_size):
                """Yield data in chunks."""
                for i in range(0, len(self.data), chunk_size):
                    yield self.data[i:i + chunk_size]
        
        mock_response = MockStreamResponse(pcm_data)
        
        mock_client = Mock()
        mock_client.audio.speech.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Test streaming
        engine = OpenAIEngine(api_key="test-key")
        chunks = list(engine.stream("Hello"))
        
        # Should have multiple chunks (3 chunks for 3 seconds)
        assert len(chunks) >= 3
        
        # Each chunk should be properly formatted
        for chunk in chunks[:-1]:  # All but last chunk
            assert chunk.sample_rate == 24000
            assert chunk.channels == 1
            assert chunk.format == "pcm"
            assert len(chunk.data) == 24000  # 1 second of audio
        
        # Verify API was called with PCM format
        mock_client.audio.speech.create.assert_called_once_with(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input="Hello",
            speed=1.0,
            response_format="pcm"
        )
    
    @patch('speechflow.engines.openai.OpenAI')
    def test_stream_error(self, mock_openai_class):
        """Test streaming error handling."""
        mock_client = Mock()
        mock_client.audio.speech.create.side_effect = Exception("Streaming Error")
        mock_openai_class.return_value = mock_client
        
        engine = OpenAIEngine(api_key="test-key")
        
        with pytest.raises(TTSError) as exc_info:
            list(engine.stream("Hello"))
        
        assert "OpenAI TTS streaming failed" in str(exc_info.value)
    
    def test_supported_voices(self):
        """Test that all supported voices are defined."""
        expected_voices = ["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]
        
        for voice in expected_voices:
            assert voice in OpenAIEngine.SUPPORTED_VOICES