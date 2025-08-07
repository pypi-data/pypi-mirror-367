"""Unit tests for Style-BERT-VITS2 TTS engine."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
import torch

from speechflow.core.exceptions import ConfigurationError, TTSError
from speechflow.engines.stylebert import StyleBertEngine


class TestStyleBertEngine:
    """Test cases for StyleBertEngine."""

    def test_init_with_neither_model_name_nor_path(self):
        """Test initialization fails when neither model_name nor model_path is provided."""
        with pytest.raises(ConfigurationError) as exc_info:
            StyleBertEngine()
        
        assert "Either model_name or model_path must be provided" in str(exc_info.value)

    @patch("speechflow.engines.stylebert.StyleBertEngine._load_pretrained_model")
    def test_init_with_model_name(self, mock_load_pretrained):
        """Test initialization with model name."""
        engine = StyleBertEngine(model_name="jvnv")
        
        assert engine.model_name == "jvnv"
        assert engine.model_path is None
        mock_load_pretrained.assert_called_once_with("jvnv")

    @patch("speechflow.engines.stylebert.StyleBertEngine._load_custom_model")
    def test_init_with_model_path(self, mock_load_custom):
        """Test initialization with model path."""
        engine = StyleBertEngine(model_path="/path/to/model")
        
        assert engine.model_path == "/path/to/model"
        assert engine.model_name is None
        mock_load_custom.assert_called_once_with("/path/to/model")

    @patch("torch.cuda.is_available")
    def test_device_auto_detection(self, mock_cuda_available):
        """Test automatic device detection."""
        # Test with CUDA available
        mock_cuda_available.return_value = True
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test", device="auto")
            assert engine.device == "cuda"
        
        # Test without CUDA
        mock_cuda_available.return_value = False
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test", device="auto")
            assert engine.device == "cpu"

    def test_device_explicit(self):
        """Test explicit device setting."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test", device="cpu")
            assert engine.device == "cpu"

    def test_load_pretrained_model_invalid_name(self):
        """Test loading pretrained model with invalid name."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        with pytest.raises(ConfigurationError) as exc_info:
            engine._load_pretrained_model("invalid-model")
        
        assert "Unknown model: invalid-model" in str(exc_info.value)

    @patch("speechflow.engines.stylebert.Path.home")
    @patch("speechflow.engines.stylebert.Path.exists")
    @patch("speechflow.engines.stylebert.StyleBertEngine._download_model")
    @patch("speechflow.engines.stylebert.StyleBertEngine._load_custom_model")
    def test_load_pretrained_model_download(self, mock_load_custom, mock_download, mock_exists, mock_home):
        """Test downloading pretrained model when not cached."""
        mock_home.return_value = Path("/home/user")
        mock_exists.return_value = False
        
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        engine._load_pretrained_model("jvnv")
        
        expected_cache_dir = Path("/home/user/.cache/speechflow/stylebert/jvnv")
        mock_download.assert_called_once_with("jvnv", expected_cache_dir)
        mock_load_custom.assert_called_once_with(str(expected_cache_dir))

    @patch("speechflow.engines.stylebert.snapshot_download")
    def test_download_model_success(self, mock_snapshot_download):
        """Test successful model download."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        cache_dir = Path("/test/cache")
        engine._download_model("jvnv", cache_dir)
        
        mock_snapshot_download.assert_called_once_with(
            repo_id="litagin/style_bert_vits2_jvnv",
            local_dir=str(cache_dir),
            local_dir_use_symlinks=False
        )

    @patch("speechflow.engines.stylebert.snapshot_download")
    def test_download_model_failure(self, mock_snapshot_download):
        """Test model download failure."""
        mock_snapshot_download.side_effect = Exception("Download failed")
        
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        with pytest.raises(TTSError) as exc_info:
            engine._download_model("jvnv", Path("/test/cache"))
        
        assert "Failed to download model" in str(exc_info.value)

    def test_load_custom_model_no_config(self):
        """Test loading custom model without config.json."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(ConfigurationError) as exc_info:
                engine._load_custom_model("/path/to/model")
            
            assert "config.json not found" in str(exc_info.value)

    @patch("builtins.open", create=True)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("speechflow.engines.stylebert.TTSModel")
    def test_load_custom_model_success(self, mock_tts_model, mock_exists, mock_open):
        """Test successful custom model loading."""
        # Mock config file content
        config_data = {
            "data": {
                "sampling_rate": 44100,
                "spk2id": {"speaker1": 0, "speaker2": 1}
            }
        }
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(config_data)
        
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        engine._load_custom_model("/path/to/model")
        
        assert engine.sample_rate == 44100
        assert engine.speakers == {"speaker1": 0, "speaker2": 1}
        mock_tts_model.assert_called_once()

    @patch("speechflow.engines.stylebert.StyleBertEngine._extract_audio")
    def test_synthesize_success(self, mock_extract_audio):
        """Test successful synthesis."""
        # Setup mock
        mock_model = Mock()
        mock_audio_data = Mock()
        mock_extract_audio.return_value = mock_audio_data
        
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.model = mock_model
            engine.speakers = {"speaker1": 0}
            engine.sample_rate = 44100
        
        result = engine.synthesize("Hello world")
        
        assert result == mock_audio_data
        mock_model.infer.assert_called_once()
        mock_extract_audio.assert_called_once()

    def test_synthesize_invalid_speaker_id(self):
        """Test synthesis with invalid speaker ID."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.speakers = {"speaker1": 0}
        
        with pytest.raises(TTSError) as exc_info:
            engine.synthesize("Hello", speaker_id=5)
        
        assert "Invalid speaker_id: 5" in str(exc_info.value)

    def test_synthesize_invalid_style(self):
        """Test synthesis with invalid style."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.speakers = {"speaker1": 0}
        
        with pytest.raises(TTSError) as exc_info:
            engine.synthesize("Hello", style="InvalidStyle")
        
        assert "Unsupported style: InvalidStyle" in str(exc_info.value)

    def test_stream_empty_text(self):
        """Test streaming with empty text."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        results = list(engine.stream(""))
        assert len(results) == 0

    @patch("speechflow.engines.stylebert.StyleBertEngine.synthesize")
    def test_stream_with_sentences(self, mock_synthesize):
        """Test streaming with multiple sentences."""
        mock_audio = Mock()
        mock_synthesize.return_value = mock_audio
        
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
        
        text = "First sentence. Second sentence! Third sentence?"
        results = list(engine.stream(text))
        
        assert len(results) == 3
        assert mock_synthesize.call_count == 3

    def test_extract_audio_none(self):
        """Test _extract_audio with None input."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.sample_rate = 44100
        
        result = engine._extract_audio(None)
        assert result is None

    def test_extract_audio_torch_tensor(self):
        """Test _extract_audio with torch tensor."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.sample_rate = 44100
        
        # Create torch tensor
        audio_tensor = torch.randn(1000)
        result = engine._extract_audio(audio_tensor)
        
        assert result is not None
        assert isinstance(result.data, np.ndarray)
        assert result.data.dtype == np.float32
        assert result.sample_rate == 44100

    def test_extract_audio_numpy_array(self):
        """Test _extract_audio with numpy array."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.sample_rate = 44100
        
        # Create numpy array
        audio_array = np.random.randn(1000).astype(np.float32)
        result = engine._extract_audio(audio_array)
        
        assert result is not None
        assert result.data.dtype == np.float32

    def test_extract_audio_normalization(self):
        """Test _extract_audio normalization."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.sample_rate = 44100
        
        # Create audio exceeding [-1, 1] range
        audio_array = np.array([2.0, -3.0, 1.5], dtype=np.float32)
        result = engine._extract_audio(audio_array)
        
        assert result is not None
        assert np.abs(result.data).max() <= 1.0

    def test_extract_audio_batch_dimension(self):
        """Test _extract_audio with batch dimension."""
        with patch("speechflow.engines.stylebert.StyleBertEngine._init_model"):
            engine = StyleBertEngine(model_name="test")
            engine.sample_rate = 44100
        
        # Create 2D array (batch dimension)
        audio_array = np.random.randn(1, 1000).astype(np.float32)
        result = engine._extract_audio(audio_array)
        
        assert result is not None
        assert result.data.ndim == 1  # Should be squeezed