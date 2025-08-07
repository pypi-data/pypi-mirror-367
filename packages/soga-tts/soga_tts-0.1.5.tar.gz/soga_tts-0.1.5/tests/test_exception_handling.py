#!/usr/bin/env python3
"""
测试异常处理功能
"""

from soga_tts.fixed_duration_tts import DirectTTSGenerator, TTSPrecisionError, TTSGenerationError


class TestExceptionClasses:
    """测试异常类的基本功能"""
    
    def test_tts_precision_error_creation(self):
        """测试TTSPrecisionError异常的创建和属性"""
        target_duration = 10.0
        achieved_duration = 12.5
        error_pct = abs(achieved_duration - target_duration) / target_duration * 100
        message = f"TTSPrecisionError: achieved {achieved_duration:.2f}s vs target {target_duration:.2f}s (error: {error_pct:.1f}%)"
        
        error = TTSPrecisionError(message, achieved_duration, target_duration, error_pct)
        
        assert error.target_duration == target_duration
        assert error.achieved_duration == achieved_duration
        assert error.error_pct == 25.0
        
        # 测试字符串表示
        error_str = str(error)
        assert "TTSPrecisionError" in error_str
        assert "25.0%" in error_str
    
    def test_tts_generation_error_creation(self):
        """测试TTSGenerationError异常的创建"""
        message = "Failed to generate speech"
        error = TTSGenerationError(message)
        
        assert str(error) == message
        assert isinstance(error, Exception)
    
    def test_error_percentage_calculation(self):
        """测试误差百分比计算的边界情况"""
        # 测试正向偏差
        target_duration = 10.0
        achieved_duration = 11.0
        error_pct = abs(achieved_duration - target_duration) / target_duration * 100
        message = "Error test"
        error1 = TTSPrecisionError(message, achieved_duration, target_duration, error_pct)
        assert error1.error_pct == 10.0
        
        # 测试负向偏差
        achieved_duration = 9.0
        error_pct = abs(achieved_duration - target_duration) / target_duration * 100
        error2 = TTSPrecisionError(message, achieved_duration, target_duration, error_pct)
        assert error2.error_pct == 10.0
        
        # 测试零偏差
        achieved_duration = 10.0
        error_pct = abs(achieved_duration - target_duration) / target_duration * 100
        error3 = TTSPrecisionError(message, achieved_duration, target_duration, error_pct)
        assert error3.error_pct == 0.0
        
        # 测试小数精度
        achieved_duration = 10.05
        error_pct = abs(achieved_duration - target_duration) / target_duration * 100
        error4 = TTSPrecisionError(message, achieved_duration, target_duration, error_pct)
        assert abs(error4.error_pct - 0.5) < 0.001


class TestExceptionIntegration:
    """测试异常的集成功能"""
    
    def test_generator_initialization(self):
        """测试生成器可以正常初始化"""
        def dummy_tts(_text):
            return "dummy_audio.wav"
            
        def dummy_llm(text):
            return text
            
        generator = DirectTTSGenerator(dummy_tts, dummy_llm)
        assert generator is not None
        assert generator.tts_function is dummy_tts
        assert generator.llm_function is dummy_llm
