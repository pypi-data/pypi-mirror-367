"""Unit tests for AudioData class."""

import pytest
import numpy as np

from speechflow.core.base import AudioData


class TestAudioData:
    """Test cases for AudioData class."""
    
    def test_audio_data_creation(self):
        """Test creating AudioData instance."""
        data = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        audio = AudioData(
            data=data,
            sample_rate=44100,
            channels=1,
            format="wav"
        )
        
        assert np.array_equal(audio.data, data)
        assert audio.sample_rate == 44100
        assert audio.channels == 1
        assert audio.format == "wav"
    
    def test_duration_calculation(self):
        """Test duration property calculation."""
        # 1 second of audio at 44100Hz
        data = np.zeros(44100, dtype=np.float32)
        audio = AudioData(
            data=data,
            sample_rate=44100,
            channels=1
        )
        
        assert audio.duration == pytest.approx(1.0)
    
    def test_duration_with_different_sample_rates(self):
        """Test duration calculation with various sample rates."""
        test_cases = [
            (24000, 48000, 0.5),   # 24000 samples at 48kHz = 0.5s
            (16000, 16000, 1.0),   # 16000 samples at 16kHz = 1.0s
            (8000, 8000, 1.0),     # 8000 samples at 8kHz = 1.0s
        ]
        
        for num_samples, sample_rate, expected_duration in test_cases:
            data = np.zeros(num_samples, dtype=np.float32)
            audio = AudioData(
                data=data,
                sample_rate=sample_rate,
                channels=1
            )
            assert audio.duration == pytest.approx(expected_duration)