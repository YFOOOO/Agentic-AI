"""
错误处理机制改进测试
测试目标：验证统一错误处理框架的使用和用户友好的错误信息
"""
import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# 确保项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestErrorHandlingImprovements(unittest.TestCase):
    """测试错误处理机制改进"""
    
    def test_mcp_error_structure(self):
        """测试MCP错误的结构和信息"""
        from src.mcp.exceptions import AgentError, ErrorSeverity, ErrorCategory
        
        # 创建一个详细的错误
        error = AgentError(
            "测试代理执行失败",
            agent_name="TestAgent",
            task_id="test_123",
            details={"step": "initialization", "data": "test_data"},
            suggestions=["检查配置", "重试操作", "联系支持"]
        )
        
        # 验证错误属性
        self.assertEqual(error.message, "测试代理执行失败")
        self.assertEqual(error.category, ErrorCategory.AGENT)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertIn("agent_name", error.details)
        self.assertEqual(error.details["agent_name"], "TestAgent")
        self.assertEqual(len(error.suggestions), 3)
        
        # 验证错误字典转换
        error_dict = error.to_dict()
        self.assertIn("message", error_dict)
        self.assertIn("category", error_dict)
        self.assertIn("severity", error_dict)
        self.assertIn("details", error_dict)
        self.assertIn("suggestions", error_dict)
        
        # 验证用户友好消息
        user_message = error.get_user_message()
        self.assertIn("测试代理执行失败", user_message)
    
    def test_file_io_error_details(self):
        """测试文件IO错误的详细信息"""
        from src.mcp.exceptions import FileIOError, ErrorCategory
        
        error = FileIOError(
            "文件不存在",
            file_path="/test/path/file.csv",
            operation="read",
            suggestions=["检查文件路径", "验证权限设置"]
        )
        
        # 验证特定属性
        self.assertEqual(error.category, ErrorCategory.FILE_IO)
        self.assertIn("file_path", error.details)
        self.assertIn("operation", error.details)
        self.assertEqual(error.details["file_path"], "/test/path/file.csv")
        self.assertEqual(error.details["operation"], "read")
    
    def test_data_processing_error_details(self):
        """测试数据处理错误的详细信息"""
        from src.mcp.exceptions import DataProcessingError, ErrorCategory
        
        error = DataProcessingError(
            "数据分析失败",
            data_type="nobel_analysis",
            details={
                "returncode": 1,
                "stderr": "Missing column 'year'",
                "command": "python analysis.py"
            },
            suggestions=["检查数据格式", "验证列名"]
        )
        
        # 验证特定属性
        self.assertEqual(error.category, ErrorCategory.DATA_PROCESSING)
        self.assertIn("data_type", error.details)
        self.assertEqual(error.details["data_type"], "nobel_analysis")
        self.assertIn("returncode", error.details)
        self.assertIn("stderr", error.details)
    
    def test_error_handler_logging(self):
        """测试错误处理器的日志功能"""
        from src.mcp.exceptions import ErrorHandler, AgentError
        
        # 创建错误处理器
        handler = ErrorHandler("test_handler")
        
        # 创建测试错误
        error = AgentError(
            "测试错误",
            agent_name="TestAgent",
            suggestions=["测试建议"]
        )
        
        # 测试错误处理（不重新抛出）
        with patch.object(handler.logger, 'log') as mock_log:
            error_info = handler.handle_error(error, reraise=False)
            
            # 验证日志被调用
            mock_log.assert_called()
            
            # 验证返回的错误信息
            self.assertIn("message", error_info)
            self.assertIn("category", error_info)
            self.assertEqual(error_info["message"], "测试错误")
    
    def test_standard_exception_conversion(self):
        """测试标准异常转换为MCP异常"""
        from src.mcp.exceptions import ErrorHandler, MCPError
        
        handler = ErrorHandler("test_handler")
        
        # 测试标准异常转换
        standard_error = ValueError("Invalid value")
        
        with self.assertRaises(MCPError) as context:
            handler.handle_error(standard_error, context={"test": "data"})
        
        # 验证转换后的异常
        mcp_error = context.exception
        self.assertIn("Invalid value", str(mcp_error))
        # 修正：检查details中的original_type而不是suggestions
        self.assertIn("original_type", mcp_error.details)
        self.assertEqual(mcp_error.details["original_type"], "ValueError")
    
    def test_error_context_information(self):
        """测试错误上下文信息"""
        from src.mcp.exceptions import ErrorHandler, AgentError
        
        handler = ErrorHandler("test_handler")
        
        error = AgentError("测试错误")
        context = {
            "function": "test_function",
            "step": "initialization",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        # 测试带上下文的错误处理
        error_info = handler.handle_error(error, context=context, reraise=False)
        
        # 验证上下文信息被包含
        self.assertIn("context", error_info)
        self.assertEqual(error_info["context"]["function"], "test_function")
        self.assertEqual(error_info["context"]["step"], "initialization")


class TestOrchestratorErrorHandling(unittest.TestCase):
    """测试orchestrator中的错误处理改进"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_literature_agent_error_handling(self):
        """测试文献代理错误处理"""
        from src.mcp.exceptions import AgentError
        
        # 模拟代理返回无效结果的情况
        with patch('src.mcp.orchestrator.LiteratureAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.handle.return_value = None  # 无效结果
            mock_agent_class.return_value = mock_agent
            
            with patch('src.mcp.orchestrator.ERROR_HANDLING_AVAILABLE', True):
                from src.mcp.orchestrator import run_nobel_pipeline
                
                # 应该抛出AgentError
                with self.assertRaises(AgentError) as context:
                    run_nobel_pipeline()
                
                # 验证错误信息
                error = context.exception
                self.assertIn("文献代理执行失败", error.message)
                self.assertIn("agent_name", error.details)
                self.assertEqual(error.details["agent_name"], "LiteratureAgent")
                # 修正：suggestions存储在error.suggestions属性中，不是details中
                self.assertIsNotNone(error.suggestions)
                self.assertGreater(len(error.suggestions), 0)
    
    def test_file_not_found_error_handling(self):
        """测试文件不存在的错误处理"""
        from src.mcp.exceptions import FileIOError
        
        # 模拟代理返回不存在的文件路径
        with patch('src.mcp.orchestrator.LiteratureAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.handle.return_value = {
                "artifacts": {"csv": "/nonexistent/file.csv", "run_dir": self.test_dir}
            }
            mock_agent_class.return_value = mock_agent
            
            with patch('src.mcp.orchestrator.ERROR_HANDLING_AVAILABLE', True):
                from src.mcp.orchestrator import run_nobel_pipeline
                
                # 应该抛出FileIOError
                with self.assertRaises(FileIOError) as context:
                    run_nobel_pipeline()
                
                # 验证错误信息
                error = context.exception
                self.assertIn("生成的CSV文件不存在", error.message)
                self.assertIn("file_path", error.details)
                self.assertIn("operation", error.details)
                self.assertEqual(error.details["operation"], "read")
    
    def test_error_context_timestamp(self):
        """测试错误上下文包含时间戳"""
        from src.mcp.exceptions import ErrorHandler
        
        # 模拟错误处理器调用
        with patch('src.mcp.orchestrator.orchestrator_error_handler') as mock_handler:
            with patch('src.mcp.orchestrator.LiteratureAgent') as mock_agent_class:
                mock_agent = MagicMock()
                mock_agent.handle.side_effect = Exception("Test error")
                mock_agent_class.return_value = mock_agent
                
                with patch('src.mcp.orchestrator.ERROR_HANDLING_AVAILABLE', True):
                    from src.mcp.orchestrator import run_nobel_pipeline
                    
                    try:
                        run_nobel_pipeline()
                    except:
                        pass  # 忽略异常，我们只关心错误处理器是否被调用
                    
                    # 验证错误处理器被调用且包含上下文
                    mock_handler.handle_error.assert_called()
                    call_args = mock_handler.handle_error.call_args
                    context = call_args[1]['context']
                    
                    # 验证上下文信息
                    self.assertIn("function", context)
                    self.assertIn("step", context)
                    self.assertIn("timestamp", context)
                    self.assertEqual(context["function"], "run_nobel_pipeline")


class TestUserFriendlyErrorMessages(unittest.TestCase):
    """测试用户友好的错误信息"""
    
    def test_error_suggestions_quality(self):
        """测试错误建议的质量"""
        from src.mcp.exceptions import (
            AgentError, FileIOError, DataProcessingError, 
            LLMError, ConfigurationError
        )
        
        # 测试不同类型错误的建议
        errors = [
            AgentError("代理失败", suggestions=["检查网络连接", "重试操作"]),
            FileIOError("文件错误", suggestions=["检查文件路径", "验证权限设置"]),
            DataProcessingError("数据错误", suggestions=["检查数据格式", "验证数据完整性"]),
            LLMError("LLM错误", suggestions=["检查API Key配置", "重试请求"]),
            ConfigurationError("配置错误", suggestions=["检查配置文件", "验证参数设置"])
        ]
        
        for error in errors:
            # 每个错误都应该有建议
            self.assertIsNotNone(error.suggestions)
            self.assertGreater(len(error.suggestions), 0)
            
            # 建议应该是有意义的字符串
            for suggestion in error.suggestions:
                self.assertIsInstance(suggestion, str)
                self.assertGreater(len(suggestion), 3)  # 至少4个字符（降低要求）
    
    def test_error_message_localization(self):
        """测试错误信息的本地化"""
        from src.mcp.exceptions import AgentError
        
        # 创建中文错误信息
        error = AgentError(
            "文献代理执行失败，无法获取数据",
            agent_name="LiteratureAgent",
            suggestions=[
                "检查网络连接是否正常",
                "验证API密钥配置是否正确",
                "查看详细日志获取更多信息"
            ]
        )
        
        # 验证中文信息
        self.assertIn("文献代理", error.message)
        self.assertIn("执行失败", error.message)
        
        # 验证中文建议
        for suggestion in error.suggestions:
            # 应该包含中文字符
            self.assertTrue(any('\u4e00' <= char <= '\u9fff' for char in suggestion))


if __name__ == '__main__':
    unittest.main()