"""Unit tests for Kokoro TTS engine."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import torch

from speechflow.engines.kokoro import KokoroEngine
from speechflow.core.exceptions import ConfigurationError, TTSError


class TestKokoroEngine:
    """Test cases for KokoroEngine."""
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_init_with_default_lang(self, mock_pipeline_class):
        """Test initialization with default language code."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        engine = KokoroEngine()
        
        assert engine.lang_code == "a"  # Default American English
        mock_pipeline_class.assert_called_once_with(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cuda")
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_init_with_custom_lang(self, mock_pipeline_class):
        """Test initialization with custom language code."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        engine = KokoroEngine(lang_code="j")
        
        assert engine.lang_code == "j"
        mock_pipeline_class.assert_called_once_with(lang_code="j", repo_id="hexgrad/Kokoro-82M", device="cuda")
    
    def test_init_with_invalid_lang(self):
        """Test initialization with invalid language code."""
        with pytest.raises(ConfigurationError) as exc_info:
            KokoroEngine(lang_code="x")
        
        assert "Unsupported language code" in str(exc_info.value)
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_init_pipeline_failure(self, mock_pipeline_class):
        """Test handling of pipeline initialization failure."""
        mock_pipeline_class.side_effect = Exception("Pipeline init failed")
        
        with pytest.raises(ConfigurationError) as exc_info:
            KokoroEngine()
        
        assert "Failed to initialize Kokoro pipeline" in str(exc_info.value)
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_synthesize_success(self, mock_pipeline_class):
        """Test successful speech synthesis."""
        # Setup mock pipeline
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create mock audio data
        audio_data = np.random.randn(24000).astype(np.float32) * 0.5
        
        # Mock generator output
        mock_pipeline.return_value = [
            ("graphemes", "phonemes", audio_data)
        ]
        
        engine = KokoroEngine()
        result = engine.synthesize("Hello world")
        
        # Verify pipeline was called correctly
        mock_pipeline.assert_called_once_with(
            "Hello world",
            voice="af_heart",
            speed=1.0,
            split_pattern=r'\n+'
        )
        
        # Verify result
        assert result.sample_rate == 24000
        assert result.channels == 1
        assert result.format == "pcm"
        assert isinstance(result.data, np.ndarray)
        assert result.data.dtype == np.float32
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_synthesize_with_custom_params(self, mock_pipeline_class):
        """Test synthesis with custom voice and speed."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        audio_data = np.random.randn(24000).astype(np.float32)
        mock_pipeline.return_value = [("g", "p", audio_data)]
        
        engine = KokoroEngine()
        result = engine.synthesize("Test", voice="am_michael", speed=1.5)
        
        mock_pipeline.assert_called_once_with(
            "Test",
            voice="am_michael",
            speed=1.5,
            split_pattern=r'\n+'
        )
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_synthesize_with_invalid_voice(self, mock_pipeline_class):
        """Test synthesis with invalid voice raises error."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        engine = KokoroEngine()
        
        with pytest.raises(ConfigurationError) as exc_info:
            engine.synthesize("Test", voice="invalid_voice")
        
        assert "Unsupported voice" in str(exc_info.value)
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_synthesize_with_torch_tensor(self, mock_pipeline_class):
        """Test synthesis when Kokoro returns torch tensors."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create torch tensor
        audio_tensor = torch.randn(24000)
        mock_pipeline.return_value = [("g", "p", audio_tensor)]
        
        engine = KokoroEngine()
        result = engine.synthesize("Test")
        
        # Should convert to numpy
        assert isinstance(result.data, np.ndarray)
        assert result.data.dtype == np.float32
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_synthesize_normalization(self, mock_pipeline_class):
        """Test audio normalization when values exceed [-1, 1]."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create audio data exceeding normal range
        audio_data = np.random.randn(24000).astype(np.float32) * 2.0
        mock_pipeline.return_value = [("g", "p", audio_data)]
        
        engine = KokoroEngine()
        result = engine.synthesize("Test")
        
        # Should be normalized to [-1, 1]
        assert np.abs(result.data).max() <= 1.0
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_synthesize_multiple_chunks(self, mock_pipeline_class):
        """Test synthesis with multiple audio chunks."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create multiple chunks
        chunk1 = np.random.randn(12000).astype(np.float32) * 0.5
        chunk2 = np.random.randn(12000).astype(np.float32) * 0.5
        
        mock_pipeline.return_value = [
            ("g1", "p1", chunk1),
            ("g2", "p2", chunk2)
        ]
        
        engine = KokoroEngine()
        result = engine.synthesize("Test")
        
        # Should concatenate chunks
        assert len(result.data) == 24000
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_synthesize_no_audio_generated(self, mock_pipeline_class):
        """Test synthesis when no audio is generated."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Return empty generator
        mock_pipeline.return_value = []
        
        engine = KokoroEngine()
        
        with pytest.raises(TTSError) as exc_info:
            engine.synthesize("Test")
        
        assert "No audio data generated" in str(exc_info.value)
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_stream_success(self, mock_pipeline_class):
        """Test successful streaming synthesis."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create chunks
        chunks = [
            np.random.randn(12000).astype(np.float32) * 0.5,
            np.random.randn(12000).astype(np.float32) * 0.5
        ]
        
        mock_pipeline.return_value = [
            ("g1", "p1", chunks[0]),
            ("g2", "p2", chunks[1])
        ]
        
        engine = KokoroEngine()
        stream = engine.stream("Test")
        
        # Collect all chunks
        results = list(stream)
        
        assert len(results) == 2
        for i, result in enumerate(results):
            assert result.sample_rate == 24000
            assert result.channels == 1
            assert result.format == "pcm"
            assert len(result.data) == 12000
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_stream_with_exception(self, mock_pipeline_class):
        """Test streaming when an exception occurs."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        def generator():
            yield ("g", "p", np.zeros(1000))
            raise Exception("Stream error")
        
        mock_pipeline.return_value = generator()
        
        engine = KokoroEngine()
        stream = engine.stream("Test")
        
        # First chunk should work
        first = next(stream)
        assert first is not None
        
        # Second should raise wrapped exception
        with pytest.raises(TTSError) as exc_info:
            next(stream)
        
        assert "Kokoro TTS streaming failed" in str(exc_info.value)
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_extract_audio_with_valid_data(self, mock_pipeline_class):
        """Test _extract_audio with valid data."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        engine = KokoroEngine()
        
        # Test with numpy array
        audio_np = np.random.randn(1000).astype(np.float32) * 0.5
        result = engine._extract_audio(("graphemes", "phonemes", audio_np))
        
        assert result is not None
        assert result.sample_rate == 24000
        assert result.channels == 1
        assert result.format == "pcm"
        assert np.array_equal(result.data, audio_np)
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_extract_audio_with_torch_tensor(self, mock_pipeline_class):
        """Test _extract_audio with torch tensor."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        engine = KokoroEngine()
        
        # Test with torch tensor
        audio_tensor = torch.randn(1000)
        result = engine._extract_audio(("g", "p", audio_tensor))
        
        assert result is not None
        assert isinstance(result.data, np.ndarray)
        assert result.data.dtype == np.float32
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_extract_audio_with_invalid_data(self, mock_pipeline_class):
        """Test _extract_audio with invalid data."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        engine = KokoroEngine()
        
        # Test with None
        assert engine._extract_audio(None) is None
        
        # Test with empty tuple
        assert engine._extract_audio(()) is None
        
        # Test with wrong tuple length
        assert engine._extract_audio(("g", "p")) is None
        
        # Test with None audio
        assert engine._extract_audio(("g", "p", None)) is None
    
    @patch('speechflow.engines.kokoro.KPipeline')
    def test_extract_audio_normalization(self, mock_pipeline_class):
        """Test _extract_audio normalization."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        
        engine = KokoroEngine()
        
        # Test with audio exceeding [-1, 1] range
        audio_np = np.array([2.0, -3.0, 1.5], dtype=np.float32)
        result = engine._extract_audio(("g", "p", audio_np))
        
        assert result is not None
        assert np.abs(result.data).max() <= 1.0
        # Check that ratios are preserved
        assert np.allclose(result.data, audio_np / 3.0)