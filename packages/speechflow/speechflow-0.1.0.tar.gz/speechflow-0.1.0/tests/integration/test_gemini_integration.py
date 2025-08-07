"""Integration tests for Gemini TTS engine."""

import pytest
import os

from speechflow import TTSEngine, EngineType
from speechflow.core.exceptions import ConfigurationError


@pytest.mark.integration
class TestGeminiIntegration:
    """Integration tests for Gemini engine."""
    
    @pytest.fixture
    def has_api_key(self):
        """Check if Gemini API key is available."""
        return bool(os.getenv("SPEECHFLOW_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY"))
    
    def test_engine_creation(self, has_api_key):
        """Test creating Gemini engine through factory."""
        if not has_api_key:
            pytest.skip("Gemini API key not available")
        
        engine = TTSEngine(EngineType.GEMINI)
        assert engine is not None
    
    def test_simple_synthesis(self, has_api_key):
        """Test simple text synthesis."""
        if not has_api_key:
            pytest.skip("Gemini API key not available")
        
        engine = TTSEngine(EngineType.GEMINI)
        audio = engine.synthesize("Hello, this is a test.")
        
        assert audio is not None
        assert audio.sample_rate > 0
        assert len(audio.data) > 0
        assert audio.duration > 0
    
    def test_voice_switching(self, has_api_key):
        """Test synthesis with different voices."""
        if not has_api_key:
            pytest.skip("Gemini API key not available")
        
        engine = TTSEngine(EngineType.GEMINI)
        
        # Test a few voices
        test_voices = ["Kore", "Puck", "Fenrir"]
        
        for voice in test_voices:
            audio = engine.synthesize(f"Testing {voice} voice", voice=voice)
            assert audio is not None
            assert len(audio.data) > 0