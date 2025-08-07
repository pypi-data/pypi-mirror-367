"""Unit tests for TTSEngineBase class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from speechflow.core.base import TTSEngineBase, AudioData


class MockTTSEngine(TTSEngineBase):
    """Mock TTS engine for testing base class functionality."""
    
    def synthesize(self, text: str, **kwargs) -> AudioData:
        """Mock synthesize method."""
        # Return mock audio data
        data = np.zeros(44100, dtype=np.float32)  # 1 second of silence
        return AudioData(
            data=data,
            sample_rate=44100,
            channels=1,
            format="wav"
        )
    
    def stream(self, text: str, **kwargs):
        """Mock stream method."""
        # Yield mock audio chunks
        chunk_size = 4410  # 0.1 second chunks
        data = np.zeros(44100, dtype=np.float32)
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            yield AudioData(
                data=chunk,
                sample_rate=44100,
                channels=1,
                format="wav"
            )


class TestTTSEngineBase:
    """Test cases for TTSEngineBase class."""
    
    def test_speak_without_save(self):
        """Test speak method without saving to file."""
        engine = MockTTSEngine()
        
        with patch.object(engine, '_play_audio') as mock_play:
            engine.speak("Hello world")
            
            # Verify audio was played
            mock_play.assert_called_once()
            audio_data = mock_play.call_args[0][0]
            assert isinstance(audio_data, AudioData)
            assert len(audio_data.data) == 44100
    
    def test_speak_with_save(self):
        """Test speak method with save_path option."""
        engine = MockTTSEngine()
        
        with patch.object(engine, '_play_audio') as mock_play, \
             patch.object(engine, '_save_audio') as mock_save:
            
            engine.speak("Hello world", save_path="output.wav")
            
            # Verify audio was played
            mock_play.assert_called_once()
            
            # Verify audio was saved
            mock_save.assert_called_once()
            save_args = mock_save.call_args
            assert save_args[0][1] == "output.wav"
            assert isinstance(save_args[0][0], AudioData)
    
    def test_speak_synthesize_once(self):
        """Test that synthesize is called only once when saving."""
        engine = MockTTSEngine()
        
        with patch.object(engine, 'synthesize', wraps=engine.synthesize) as mock_synth, \
             patch.object(engine, '_play_audio'), \
             patch.object(engine, '_save_audio'):
            
            engine.speak("Hello world", save_path="output.wav")
            
            # Verify synthesize was called only once
            mock_synth.assert_called_once_with("Hello world")
    
    def test_speak_with_kwargs(self):
        """Test speak method passes kwargs to synthesize."""
        engine = MockTTSEngine()
        
        with patch.object(engine, 'synthesize', wraps=engine.synthesize) as mock_synth, \
             patch.object(engine, '_play_audio'):
            
            engine.speak("Hello", voice="custom_voice", speed=1.5)
            
            # Verify kwargs were passed to synthesize
            mock_synth.assert_called_once_with("Hello", voice="custom_voice", speed=1.5)
    
    def test_save_to_file(self):
        """Test save_to_file method."""
        engine = MockTTSEngine()
        
        with patch.object(engine, '_save_audio') as mock_save:
            engine.save_to_file("Test text", "test.wav")
            
            # Verify save was called
            mock_save.assert_called_once()
            save_args = mock_save.call_args
            assert save_args[0][1] == "test.wav"
            assert isinstance(save_args[0][0], AudioData)
    
    @patch('speechflow.audio.writer.AudioWriter')
    def test_save_audio_implementation(self, mock_writer_class):
        """Test _save_audio method implementation."""
        engine = MockTTSEngine()
        mock_writer = Mock()
        mock_writer_class.return_value = mock_writer
        
        audio = AudioData(
            data=np.zeros(100, dtype=np.float32),
            sample_rate=44100,
            channels=1
        )
        
        engine._save_audio(audio, "test.wav")
        
        # Verify AudioWriter was used correctly
        mock_writer_class.assert_called_once()
        mock_writer.save.assert_called_once_with(audio, "test.wav")
    
    @patch('speechflow.audio.player.AudioPlayer')
    def test_play_audio_implementation(self, mock_player_class):
        """Test _play_audio method implementation."""
        engine = MockTTSEngine()
        mock_player = Mock()
        mock_player_class.return_value = mock_player
        
        audio = AudioData(
            data=np.zeros(100, dtype=np.float32),
            sample_rate=44100,
            channels=1
        )
        
        engine._play_audio(audio)
        
        # Verify AudioPlayer was used correctly
        mock_player_class.assert_called_once()
        mock_player.play.assert_called_once_with(audio)