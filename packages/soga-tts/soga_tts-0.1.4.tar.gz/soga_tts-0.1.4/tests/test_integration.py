import pytest
from unittest.mock import patch, MagicMock
from soga_tts.fixed_duration_tts import soga_tts, TTSPrecisionError, TTSGenerationError
from soga_tts.my_tts import raw_text_to_speech_tool


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow_with_mocked_dependencies(self):
        """测试完整工作流程（模拟依赖）"""
        # 模拟TTS函数返回固定路径
        def mock_tts(text):
            return f"/tmp/audio_{hash(text)}.mp3"
        
        # 模拟LLM函数返回标准格式
        def mock_llm(_prompt):
            return '''```json
[
    {
        "version": 1,
        "text": "Short version",
        "length": 10
    },
    {
        "version": 2,
        "text": "Medium length version with more content",
        "length": 30
    }
]
```'''
        
        # 模拟音频时长获取
        with patch('librosa.get_duration', return_value=9.5):
            result_text, result_audio, result_duration = soga_tts(
                text="Test integration",
                target_duration=10.0,
                tts_function=mock_tts,
                llm_function=mock_llm,
                tolerance_pct=5.0,
                max_rounds=2
            )
            
            assert result_text == "Test integration"
            assert result_audio is not None
            assert result_duration == 9.5

    def test_edge_cases_empty_text(self):
        """测试边缘情况：空文本时抛出精度异常"""
        def mock_tts(text):
            return f"/tmp/audio_{hash(text)}.mp3"
        
        with patch('librosa.get_duration', return_value=0.1):
            with pytest.raises(TTSPrecisionError) as exc_info:
                soga_tts(
                    text="",
                    target_duration=1.0,
                    tts_function=mock_tts,
                    tolerance_pct=10.0
                )
            
            error = exc_info.value
            assert error.target_duration == 1.0
            assert error.achieved_duration == 0.1
            assert error.error_pct == 90.0

    def test_edge_cases_very_short_duration(self):
        """测试边缘情况：极短目标时长"""
        def mock_tts(text):
            return f"/tmp/audio_{hash(text)}.mp3"
        
        with patch('librosa.get_duration', return_value=0.5):
            result_text, result_audio, result_duration = soga_tts(
                text="Hi",
                target_duration=0.5,
                tts_function=mock_tts,
                tolerance_pct=20.0
            )
            
            assert result_text == "Hi"
            assert result_duration == 0.5

    def test_edge_cases_very_long_duration(self):
        """测试边缘情况：极长目标时长"""
        def mock_tts(text):
            return f"/tmp/audio_{hash(text)}.mp3"
        
        def mock_llm(_prompt):
            return '''```json
[
    {
        "version": 1,
        "text": "This is a very long text that should take much more time to speak and contains many detailed descriptions and explanations to fill the required duration",
        "length": 150
    }
]
```'''
        
        with patch('librosa.get_duration', return_value=30.0):
            result_text, result_audio, result_duration = soga_tts(
                text="Short",
                target_duration=30.0,
                tts_function=mock_tts,
                llm_function=mock_llm,
                tolerance_pct=10.0
            )
            
            assert result_duration == 30.0

    def test_tts_function_failure(self):
        """测试TTS函数失败时抛出TTSGenerationError"""
        def failing_tts(_text):
            return None  # 模拟失败
        
        with pytest.raises(TTSGenerationError):
            soga_tts(
                text="Test failure",
                target_duration=5.0,
                tts_function=failing_tts,
                tolerance_pct=5.0
            )

    def test_audio_scaling_integration(self):
        """测试音频缩放集成"""
        def mock_tts(text):
            return f"/tmp/audio_{hash(text)}.mp3"
        
        # 模拟成功的音频缩放
        with patch('librosa.get_duration', return_value=8.0):
            with patch('librosa.load', return_value=([1, 2, 3, 4], 1000)):
                with patch('librosa.effects.time_stretch', return_value=[1, 2, 3, 4, 5]):
                    with patch('soundfile.write'):
                        result_text, result_audio, result_duration = soga_tts(
                            text="Scale test",
                            target_duration=10.0,
                            tts_function=mock_tts,
                            tolerance_pct=5.0,
                            force_exact_duration=True,
                            max_rounds=1
                        )
                        
                        assert result_duration == 10.0  # 应该被缩放到精确时长

    def test_zero_tolerance(self):
        """测试零容差的情况"""
        def mock_tts(text):
            return f"/tmp/audio_{hash(text)}.mp3"
        
        with patch('librosa.get_duration', return_value=10.0):  # 完全匹配
            result_text, result_audio, result_duration = soga_tts(
                text="Perfect match",
                target_duration=10.0,
                tts_function=mock_tts,
                tolerance_pct=0.0
            )
            
            assert result_duration == 10.0

    def test_max_rounds_reached(self):
        """测试达到最大回合数的情况"""
        def mock_tts(text):
            return f"/tmp/audio_{hash(text)}.mp3"
        
        def mock_llm(_prompt):
            return '''```json
[
    {
        "version": 1,
        "text": "Different version that still doesn't match well",
        "length": 25
    }
]
```'''
        
        with patch('librosa.get_duration', return_value=5.0):  # 始终不匹配
            with pytest.raises(TTSPrecisionError) as exc_info:
                soga_tts(
                    text="Max rounds test",
                    target_duration=10.0,
                    tts_function=mock_tts,
                    llm_function=mock_llm,
                    tolerance_pct=1.0,  # 很严格的容差
                    max_rounds=2
                )
            
            error = exc_info.value
            assert error.target_duration == 10.0
            assert error.achieved_duration == 5.0
            assert error.error_pct == 50.0

    def test_real_tts_function_mock(self):
        """测试使用真实TTS函数的模拟"""
        # 完全模拟edge_tts的行为
        with patch('soga_tts.my_tts.edge_tts.Communicate') as mock_communicate:
            mock_instance = MagicMock()
            mock_communicate.return_value = mock_instance
            
            with patch('asyncio.get_running_loop', side_effect=RuntimeError):
                with patch('asyncio.new_event_loop') as mock_new_loop:
                    with patch('asyncio.set_event_loop'):
                        mock_loop = MagicMock()
                        mock_new_loop.return_value = mock_loop
                        
                        with patch('librosa.get_duration', return_value=8.0):
                            result_text, result_audio, result_duration = soga_tts(
                                text="Real TTS test",
                                target_duration=8.0,
                                tts_function=raw_text_to_speech_tool,
                                tolerance_pct=5.0
                            )
                            
                            assert result_text == "Real TTS test"
                            assert result_duration == 8.0
