import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from soga_tts.my_tts import raw_text_to_speech_tool


class TestRawTextToSpeechTool:
    """测试raw_text_to_speech_tool函数"""
    
    @patch('soga_tts.my_tts.edge_tts')
    def test_file_name_generation(self, mock_edge_tts):
        """测试文件名生成逻辑"""
        text = "Hello world! This is a test."
        expected_prefix = "audio_for_Hello world This is a test"
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop'):
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    result = raw_text_to_speech_tool(text)
                    
                    assert result.startswith(f"/tmp/{expected_prefix}")
                    assert result.endswith(".mp3")

    @patch('soga_tts.my_tts.edge_tts')
    def test_special_characters_in_text(self, mock_edge_tts):
        """测试特殊字符处理"""
        text = "Hello@#$%^&*(){}[]|\\:;\"'<>?,./"
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop'):
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    result = raw_text_to_speech_tool(text)
                    
                    # 确保特殊字符被过滤掉
                    assert "Hello" in result
                    assert "@" not in result
                    assert "#" not in result

    @patch('soga_tts.my_tts.edge_tts')
    def test_long_text_truncation(self, mock_edge_tts):
        """测试长文本截断"""
        long_text = "a" * 100  # 100个字符的文本
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop'):
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    result = raw_text_to_speech_tool(long_text)
                    
                    # 文件名应该被截断为50字符
                    file_name = os.path.basename(result)
                    # 减去 "audio_for_" (10个字符) 和 ".mp3" (4个字符)
                    expected_max_length = 10 + 50 + 4
                    assert len(file_name) <= expected_max_length

    @patch('soga_tts.my_tts.edge_tts')
    def test_edge_tts_communication(self, mock_edge_tts):
        """测试edge_tts的通信设置"""
        text = "Test communication"
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop'):
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    # 模拟事件循环执行异步函数
                    def mock_run_until_complete(coro):
                        # 模拟运行协程，只需要模拟执行保存操作
                        return None
                    mock_loop.run_until_complete = mock_run_until_complete
                    
                    result = raw_text_to_speech_tool(text)
                    
                    # 验证返回了正确的文件路径
                    assert result.startswith("/tmp/audio_for_")
                    assert result.endswith(".mp3")
                    assert "Test communication" in result or "Test_communication" in result

    @patch('soga_tts.my_tts.edge_tts')
    def test_asyncio_event_loop_handling_new_loop(self, mock_edge_tts):
        """测试在没有运行事件循环时创建新循环"""
        text = "Test new loop"
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop') as mock_set_loop:
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    raw_text_to_speech_tool(text)
                    
                    # 验证新事件循环被创建和设置
                    mock_new_loop.assert_called_once()
                    mock_set_loop.assert_called_once_with(mock_loop)
                    mock_loop.run_until_complete.assert_called_once()

    @patch('soga_tts.my_tts.edge_tts')
    def test_asyncio_event_loop_handling_existing_loop(self, mock_edge_tts):
        """测试在已有事件循环时的处理"""
        text = "Test existing loop"
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        mock_loop = MagicMock()
        with patch('asyncio.get_running_loop', return_value=mock_loop):
            
            raw_text_to_speech_tool(text)
            
            # 验证使用现有循环
            mock_loop.run_until_complete.assert_called_once()

    @patch('soga_tts.my_tts.edge_tts')
    def test_file_path_structure(self, mock_edge_tts):
        """测试文件路径结构"""
        text = "Path test"
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop'):
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    result = raw_text_to_speech_tool(text)
                    
                    # 验证路径结构
                    assert result.startswith("/tmp/")
                    assert result.endswith(".mp3")
                    assert "audio_for_" in result

    @patch('soga_tts.my_tts.edge_tts')
    def test_empty_text(self, mock_edge_tts):
        """测试空文本处理"""
        text = ""
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop'):
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    result = raw_text_to_speech_tool(text)
                    
                    # 空文本应该也能正常处理
                    assert result.startswith("/tmp/audio_for_")
                    assert result.endswith(".mp3")

    @patch('soga_tts.my_tts.edge_tts')
    def test_whitespace_only_text(self, mock_edge_tts):
        """测试仅空白字符的文本处理"""
        text = "   \n\t   "
        
        mock_communicate = MagicMock()
        mock_edge_tts.Communicate.return_value = mock_communicate
        mock_communicate.save = AsyncMock()
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError):
            with patch('asyncio.new_event_loop') as mock_new_loop:
                with patch('asyncio.set_event_loop'):
                    mock_loop = MagicMock()
                    mock_new_loop.return_value = mock_loop
                    
                    result = raw_text_to_speech_tool(text)
                    
                    # 应该生成有效的文件路径
                    assert result.startswith("/tmp/audio_for_")
                    assert result.endswith(".mp3")
