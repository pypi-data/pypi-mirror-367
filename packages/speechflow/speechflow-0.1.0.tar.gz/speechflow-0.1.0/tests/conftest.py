"""pytest configuration and fixtures."""

import pytest
import numpy as np
from unittest.mock import Mock

from speechflow.core.base import AudioData


@pytest.fixture
def sample_audio_data():
    """Create sample audio data for testing."""
    # 1 second of 440Hz sine wave at 44100Hz sample rate
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440.0
    audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    return AudioData(
        data=audio,
        sample_rate=sample_rate,
        channels=1,
        format="pcm"
    )


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-123"


@pytest.fixture
def mock_genai_client(mocker):
    """Mock Google GenAI client."""
    mock_client = Mock()
    mock_genai = mocker.patch("speechflow.engines.gemini.genai")
    mock_genai.Client.return_value = mock_client
    return mock_client


@pytest.fixture
def mock_openai_client(mocker):
    """Mock OpenAI client."""
    mock_client = Mock()
    mock_openai = mocker.patch("speechflow.engines.openai.OpenAI")
    mock_openai.return_value = mock_client
    return mock_client