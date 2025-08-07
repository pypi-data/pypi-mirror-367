import pytest
import os
import json
from unittest.mock import patch, MagicMock
from soga_tts.fixed_duration_tts import DirectTTSGenerator, soga_tts, TTSGenerationError, TTSPrecisionError


class TestDirectTTSGenerator:
    """测试DirectTTSGenerator类"""
    
    def test_init(self, mock_tts_function, mock_llm_function):
        """测试初始化"""
        generator = DirectTTSGenerator(mock_tts_function, mock_llm_function)
        assert generator.tts_function == mock_tts_function
        assert generator.llm_function == mock_llm_function

    def test_get_audio_duration_success(self):
        """测试成功获取音频时长"""
        generator = DirectTTSGenerator(None, None)
        
        with patch('librosa.get_duration', return_value=5.5):
            duration = generator.get_audio_duration("/test/path.mp3")
            assert duration == 5.5

    def test_get_audio_duration_fallback(self):
        """测试音频时长获取的fallback逻辑"""
        generator = DirectTTSGenerator(None, None)
        
        with patch('librosa.get_duration', side_effect=[Exception(), 3.2]):
            duration = generator.get_audio_duration("/test/path.mp3")
            assert duration == 3.2

    def test_get_audio_duration_failure(self):
        """测试音频时长获取失败"""
        generator = DirectTTSGenerator(None, None)
        
        with patch('librosa.get_duration', side_effect=Exception()):
            duration = generator.get_audio_duration("/test/path.mp3")
            assert duration is None

    @patch('librosa.load')
    @patch('librosa.effects.time_stretch')
    @patch('soundfile.write')
    def test_scale_audio_to_duration_success(self, mock_sf_write, mock_time_stretch, mock_load):
        """测试音频缩放成功"""
        generator = DirectTTSGenerator(None, None)
        
        # 模拟librosa.load返回
        mock_audio = [1, 2, 3, 4]  # 4个样本
        mock_sr = 1000  # 1000 Hz
        mock_load.return_value = (mock_audio, mock_sr)
        
        # 模拟时间拉伸
        mock_scaled_audio = [1, 2, 3, 4, 5, 6]
        mock_time_stretch.return_value = mock_scaled_audio
        
        # 模拟验证新时长
        with patch.object(generator, 'get_audio_duration', return_value=2.0):
            result = generator.scale_audio_to_duration("/test/input.mp3", 2.0)
            
            assert result == "/test/input_scaled.mp3"
            mock_load.assert_called_once_with("/test/input.mp3", sr=None)
            mock_sf_write.assert_called_once()

    def test_scale_audio_to_duration_failure(self):
        """测试音频缩放失败"""
        generator = DirectTTSGenerator(None, None)
        
        with patch('librosa.load', side_effect=Exception("Load failed")):
            result = generator.scale_audio_to_duration("/test/input.mp3", 2.0)
            assert result is None

    def test_round_0_direct_test_success(self, mock_tts_function):
        """测试第0回合直接测试成功"""
        generator = DirectTTSGenerator(mock_tts_function, None)
        
        with patch.object(generator, 'get_audio_duration', return_value=5.0):
            result = generator.round_0_direct_test("test text", 5.0)
            
            assert result['success'] is True
            assert result['text'] == "test text"
            assert result['duration'] == 5.0
            assert result['error_pct'] == 0.0

    def test_round_0_direct_test_failure(self, mock_tts_function):
        """测试第0回合直接测试失败"""
        generator = DirectTTSGenerator(mock_tts_function, None)
        
        with patch.object(generator, 'get_audio_duration', return_value=None):
            result = generator.round_0_direct_test("test text", 5.0)
            
            assert result['success'] is False

    def test_extract_variants_success(self):
        """测试成功提取变体"""
        generator = DirectTTSGenerator(None, None)
        
        response = '''```json
[
    {"version": 1, "text": "Short text", "length": 10},
    {"version": 2, "text": "Medium length text", "length": 20}
]
```'''
        
        variants = generator.extract_variants(response)
        assert len(variants) == 2
        assert variants[0] == "Short text"
        assert variants[1] == "Medium length text"

    def test_extract_variants_no_json(self):
        """测试无JSON内容的响应"""
        generator = DirectTTSGenerator(None, None)
        
        response = "No JSON content here"
        variants = generator.extract_variants(response)
        assert variants == []

    def test_extract_variants_invalid_json(self):
        """测试无效JSON"""
        generator = DirectTTSGenerator(None, None)
        
        response = '''```json
invalid json content
```'''
        
        variants = generator.extract_variants(response)
        assert variants == []

    def test_find_best_result_success(self):
        """测试找到最佳结果"""
        generator = DirectTTSGenerator(None, None)
        
        results = [
            {'error_pct': 5.0, 'text': 'text1'},
            {'error_pct': 2.0, 'text': 'text2'},
            {'error_pct': 8.0, 'text': 'text3'}
        ]
        
        best = generator.find_best_result(results)
        assert best['error_pct'] == 2.0
        assert best['text'] == 'text2'

    def test_find_best_result_empty(self):
        """测试空结果列表"""
        generator = DirectTTSGenerator(None, None)
        
        best = generator.find_best_result([])
        assert best is None

    def test_test_all_variants(self, mock_tts_function):
        """测试并行测试所有变体"""
        generator = DirectTTSGenerator(mock_tts_function, None)
        
        variants = ["text1", "text2"]
        target_duration = 5.0
        
        with patch.object(generator, 'get_audio_duration', return_value=4.5):
            results = generator.test_all_variants(variants, target_duration)
            
            assert len(results) == 2
            for result in results:
                assert 'text' in result
                assert 'duration' in result
                assert 'error_pct' in result

    def test_generate_linear_variants_success(self, mock_tts_function, mock_llm_function):
        """测试生成线性变体成功"""
        generator = DirectTTSGenerator(mock_tts_function, mock_llm_function)
        
        with patch.object(generator, 'extract_variants', return_value=["variant1", "variant2"]):
            with patch.object(generator, 'test_all_variants', return_value=[
                {'error_pct': 3.0, 'text': 'variant1'},
                {'error_pct': 7.0, 'text': 'variant2'}
            ]):
                result = generator.generate_linear_variants(
                    "original text", 10.0, 8.0, 1
                )
                
                assert result['success'] is True
                assert result['best_result']['error_pct'] == 3.0

    def test_generate_linear_variants_no_variants(self, mock_tts_function, mock_llm_function):
        """测试未生成变体的情况"""
        generator = DirectTTSGenerator(mock_tts_function, mock_llm_function)
        
        with patch.object(generator, 'extract_variants', return_value=[]):
            result = generator.generate_linear_variants(
                "original text", 10.0, 8.0, 1
            )
            
            assert result['success'] is False

    def test_generate_speech_direct_success(self, mock_tts_function, mock_llm_function):
        """测试第0回合直接成功"""
        generator = DirectTTSGenerator(mock_tts_function, mock_llm_function)
        
        with patch.object(generator, 'round_0_direct_test', return_value={
            'success': True,
            'error_pct': 2.0,  # 小于3.0的容差
            'text': 'original text',
            'audio_path': '/test/audio.mp3',
            'duration': 10.0
        }):
            text, audio_path, duration = generator.generate_speech(
                "original text", 10.0, tolerance_pct=3.0
            )
            
            assert text == "original text"
            assert audio_path == "/test/audio.mp3"
            assert duration == 10.0

    def test_generate_speech_round_0_failure(self, mock_tts_function, mock_llm_function):
        """测试第0回合失败时抛出TTSGenerationError"""
        generator = DirectTTSGenerator(mock_tts_function, mock_llm_function)
        
        with patch.object(generator, 'round_0_direct_test', return_value={'success': False}):
            with pytest.raises(TTSGenerationError) as exc_info:
                generator.generate_speech("original text", 10.0)
            
            assert "第0回合TTS生成失败" in str(exc_info.value)

    def test_generate_speech_multiple_rounds(self, mock_tts_function, mock_llm_function):
        """测试多回合处理"""
        generator = DirectTTSGenerator(mock_tts_function, mock_llm_function)
        
        # 第0回合不达标
        round0_result = {
            'success': True,
            'error_pct': 10.0,  # 超过容差
            'text': 'original text',
            'audio_path': '/test/audio.mp3',
            'duration': 8.0
        }
        
        # 第1回合达标
        round1_result = {
            'success': True,
            'best_result': {
                'error_pct': 2.0,  # 在容差内
                'text': 'improved text',
                'audio_path': '/test/audio2.mp3',
                'duration': 9.8
            }
        }
        
        with patch.object(generator, 'round_0_direct_test', return_value=round0_result):
            with patch.object(generator, 'generate_linear_variants', return_value=round1_result):
                text, audio_path, duration = generator.generate_speech(
                    "original text", 10.0, tolerance_pct=3.0, max_rounds=3
                )
                
                assert text == "improved text"
                assert audio_path == "/test/audio2.mp3"
                assert duration == 9.8

    def test_generate_speech_with_audio_scaling(self, mock_tts_function, mock_llm_function):
        """测试带音频缩放的生成"""
        generator = DirectTTSGenerator(mock_tts_function, mock_llm_function)
        
        round0_result = {
            'success': True,
            'error_pct': 10.0,
            'text': 'original text',
            'audio_path': '/test/audio.mp3',
            'duration': 8.0
        }
        
        with patch.object(generator, 'round_0_direct_test', return_value=round0_result):
            with patch.object(generator, 'generate_linear_variants', return_value={'success': False}):
                with patch.object(generator, 'scale_audio_to_duration', return_value='/test/scaled.mp3'):
                    text, audio_path, duration = generator.generate_speech(
                        "original text", 10.0, force_exact_duration=True, max_rounds=1
                    )
                    
                    assert text == "original text"
                    assert audio_path == "/test/scaled.mp3"
                    assert duration == 10.0


class TestSogaTTSFunction:
    """测试soga_tts主入口函数"""
    
    def test_soga_tts_with_defaults(self, mock_tts_function):
        """测试使用默认参数的soga_tts函数"""
        with patch('soga_tts.fixed_duration_tts.DirectTTSGenerator') as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_speech.return_value = ("result text", "/audio.mp3", 10.0)
            
            result = soga_tts("test text", 10.0, tts_function=mock_tts_function)
            
            assert result == ("result text", "/audio.mp3", 10.0)
            mock_generator_class.assert_called_once_with(
                tts_function=mock_tts_function,
                llm_function=None
            )

    def test_soga_tts_with_custom_params(self, mock_tts_function, mock_llm_function):
        """测试使用自定义参数的soga_tts函数"""
        with patch('soga_tts.fixed_duration_tts.DirectTTSGenerator') as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_speech.return_value = ("result text", "/audio.mp3", 10.0)
            
            result = soga_tts(
                "test text", 
                10.0,
                tts_function=mock_tts_function,
                llm_function=mock_llm_function,
                tolerance_pct=5.0,
                max_rounds=5,
                force_exact_duration=False
            )
            
            assert result == ("result text", "/audio.mp3", 10.0)
            mock_generator.generate_speech.assert_called_once_with(
                text="test text",
                target_duration=10.0,
                tolerance_pct=5.0,
                max_rounds=5,
                force_exact_duration=False
            )
