"""Unit tests for Gemini TTS engine."""

import pytest
from unittest.mock import Mock, patch
import numpy as np
import os

from speechflow.engines.gemini import GeminiEngine
from speechflow.core.exceptions import ConfigurationError, TTSError


class TestGeminiEngine:
    """Test cases for GeminiEngine."""
    
    def test_init_with_api_key(self, mock_genai_client):
        """Test initialization with API key."""
        engine = GeminiEngine(api_key="test-key")
        
        # API key should be properly set
        assert mock_genai_client.call_count == 1
    
    def test_init_without_api_key(self, mock_genai_client):
        """Test initialization without API key raises error."""
        with pytest.raises(ConfigurationError) as exc_info:
            GeminiEngine(api_key="")
        
        assert "Gemini API key is required" in str(exc_info.value)
    
    def test_init_with_custom_voice(self, mock_genai_client):
        """Test initialization with custom voice."""
        engine = GeminiEngine(api_key="test-key")
    
    def test_init_with_invalid_api_key_type(self, mock_genai_client):
        """Test initialization with invalid API key type raises error."""
        with pytest.raises(ConfigurationError) as exc_info:
            GeminiEngine(api_key=None)
        
        assert "Gemini API key is required" in str(exc_info.value)
    
    def test_synthesize_success(self, mock_genai_client):
        """Test successful speech synthesis."""
        # Setup mock response
        mock_part = Mock()
        mock_part.inline_data.data = np.zeros(48000, dtype=np.int16).tobytes()
        mock_part.inline_data.mime_type = "audio/L16;codec=pcm;rate=24000"
        
        mock_content = Mock()
        mock_content.parts = [mock_part]
        
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        
        mock_genai_client.models.generate_content.return_value = mock_response
        
        # Test synthesis
        engine = GeminiEngine(api_key="test-key")
        audio = engine.synthesize("Hello world")
        
        assert audio.sample_rate == 24000
        assert audio.channels == 1
        assert audio.format == "pcm"
        assert len(audio.data) == 48000
    
    def test_synthesize_with_different_voice(self, mock_genai_client):
        """Test synthesis with different voice parameter."""
        # Setup mock
        mock_part = Mock()
        mock_part.inline_data.data = np.zeros(24000, dtype=np.int16).tobytes()
        mock_part.inline_data.mime_type = "audio/L16;codec=pcm;rate=24000"
        
        mock_content = Mock()
        mock_content.parts = [mock_part]
        
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        
        mock_genai_client.models.generate_content.return_value = mock_response
        
        # Test synthesis with different voice
        engine = GeminiEngine(api_key="test-key")
        audio = engine.synthesize("Hello", voice="Fenrir")
        
        # Verify the API was called with correct voice
        call_args = mock_genai_client.models.generate_content.call_args
        config = call_args.kwargs["config"]
        voice_name = config.speech_config.voice_config.prebuilt_voice_config.voice_name
        assert voice_name == "Fenrir"
    
    def test_synthesize_no_candidates(self, mock_genai_client):
        """Test synthesis failure when no candidates returned."""
        mock_response = Mock()
        mock_response.candidates = []
        
        mock_genai_client.models.generate_content.return_value = mock_response
        
        engine = GeminiEngine(api_key="test-key")
        
        with pytest.raises(TTSError) as exc_info:
            engine.synthesize("Hello")
        
        assert "No candidates in response" in str(exc_info.value)
    
    def test_supported_voices(self):
        """Test that all supported voices are defined."""
        expected_voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]
        
        for voice in expected_voices:
            assert voice in GeminiEngine.SUPPORTED_VOICES
    
    def test_init_with_custom_model(self, mock_genai_client):
        """Test initialization with custom model."""
        engine = GeminiEngine(api_key="test-key", model="gemini-2.5-pro-preview-tts")
        assert engine.model == "gemini-2.5-pro-preview-tts"
    
    def test_init_with_default_model(self, mock_genai_client):
        """Test initialization uses default model when not specified."""
        engine = GeminiEngine(api_key="test-key")
        assert engine.model == GeminiEngine.DEFAULT_MODEL