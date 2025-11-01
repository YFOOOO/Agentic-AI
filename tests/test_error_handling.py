"""
错误处理框架测试模块

测试统一异常处理系统的各种功能和场景
"""

import pytest
import logging
from datetime import datetime
from unittest.mock import Mock, patch

from src.mcp.exceptions import (
    MCPError, ValidationError, ConfigurationError, NetworkError,
    LLMError, FileIOError, DataProcessingError, AgentError,
    ErrorSeverity, ErrorCategory, ErrorHandler, handle_mcp_error
)


class TestMCPError:
    """测试MCP基础异常类"""
    
    def test_basic_error_creation(self):
        """测试基础错误创建"""
        error = MCPError("Test error message")
        
        assert error.message == "Test error message"
        assert error.category == ErrorCategory.SYSTEM
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.details == {}
        assert error.suggestions == []
        assert error.error_code == "SYSTEM_ERROR"
        assert isinstance(error.timestamp, datetime)
    
    def test_custom_error_creation(self):
        """测试自定义错误创建"""
        details = {"key": "value"}
        suggestions = ["Try this", "Or that"]
        
        error = MCPError(
            "Custom error",
            category=ErrorCategory.LLM,
            severity=ErrorSeverity.HIGH,
            details=details,
            suggestions=suggestions,
            error_code="CUSTOM_001"
        )
        
        assert error.message == "Custom error"
        assert error.category == ErrorCategory.LLM
        assert error.severity == ErrorSeverity.HIGH
        assert error.details == details
        assert error.suggestions == suggestions
        assert error.error_code == "CUSTOM_001"
    
    def test_to_dict(self):
        """测试转换为字典"""
        error = MCPError(
            "Test message",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details={"field": "name"},
            suggestions=["Check input"]
        )
        
        result = error.to_dict()
        
        assert result["message"] == "Test message"
        assert result["category"] == "validation"
        assert result["severity"] == "low"
        assert result["details"] == {"field": "name"}
        assert result["suggestions"] == ["Check input"]
        assert "timestamp" in result
    
    def test_get_user_message_without_suggestions(self):
        """测试无建议的用户消息"""
        error = MCPError("Test error", category=ErrorCategory.NETWORK)
        message = error.get_user_message()
        
        assert message == "[NETWORK] Test error"
    
    def test_get_user_message_with_suggestions(self):
        """测试有建议的用户消息"""
        error = MCPError(
            "Test error",
            category=ErrorCategory.LLM,
            suggestions=["Suggestion 1", "Suggestion 2"]
        )
        message = error.get_user_message()
        
        expected = "[LLM] Test error\n建议解决方案:\n  • Suggestion 1\n  • Suggestion 2"
        assert message == expected


class TestSpecificErrors:
    """测试特定类型的错误"""
    
    def test_validation_error(self):
        """测试验证错误"""
        error = ValidationError("Invalid input", field="email")
        
        assert error.category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.LOW
        assert error.details["field"] == "email"
    
    def test_configuration_error(self):
        """测试配置错误"""
        error = ConfigurationError("Missing API key", config_key="OPENAI_API_KEY")
        
        assert error.category == ErrorCategory.CONFIGURATION
        assert error.severity == ErrorSeverity.HIGH
        assert error.details["config_key"] == "OPENAI_API_KEY"
        assert len(error.suggestions) > 0
    
    def test_network_error(self):
        """测试网络错误"""
        error = NetworkError(
            "Connection failed",
            url="https://api.example.com",
            status_code=500
        )
        
        assert error.category == ErrorCategory.NETWORK
        assert error.details["url"] == "https://api.example.com"
        assert error.details["status_code"] == 500
    
    def test_llm_error(self):
        """测试LLM错误"""
        error = LLMError(
            "Model not found",
            provider="openai",
            model="gpt-4"
        )
        
        assert error.category == ErrorCategory.LLM
        assert error.details["provider"] == "openai"
        assert error.details["model"] == "gpt-4"
    
    def test_file_io_error(self):
        """测试文件IO错误"""
        error = FileIOError(
            "File not found",
            file_path="/path/to/file.txt",
            operation="read"
        )
        
        assert error.category == ErrorCategory.FILE_IO
        assert error.details["file_path"] == "/path/to/file.txt"
        assert error.details["operation"] == "read"
    
    def test_data_processing_error(self):
        """测试数据处理错误"""
        error = DataProcessingError("Invalid CSV format", data_type="csv")
        
        assert error.category == ErrorCategory.DATA_PROCESSING
        assert error.details["data_type"] == "csv"
    
    def test_agent_error(self):
        """测试代理错误"""
        error = AgentError(
            "Agent execution failed",
            agent_name="WritingAgent",
            task_id="task_123"
        )
        
        assert error.category == ErrorCategory.AGENT
        assert error.details["agent_name"] == "WritingAgent"
        assert error.details["task_id"] == "task_123"


class TestErrorHandler:
    """测试错误处理器"""
    
    def setup_method(self):
        """测试前准备"""
        self.handler = ErrorHandler("test_logger")
    
    def test_handle_mcp_error(self):
        """测试处理MCP错误"""
        error = ValidationError("Test validation error")
        context = {"user_id": "123"}
        
        with pytest.raises(ValidationError):
            self.handler.handle_error(error, context=context)
    
    def test_handle_mcp_error_no_reraise(self):
        """测试处理MCP错误不重新抛出"""
        error = LLMError("Test LLM error")
        context = {"model": "gpt-4"}
        
        result = self.handler.handle_error(error, context=context, reraise=False)
        
        assert result["message"] == "Test LLM error"
        assert result["category"] == "llm"
        assert result["context"] == context
    
    def test_handle_standard_exception(self):
        """测试处理标准异常"""
        error = ValueError("Invalid value")
        
        with pytest.raises(MCPError) as exc_info:
            self.handler.handle_error(error)
        
        mcp_error = exc_info.value
        assert mcp_error.category == ErrorCategory.SYSTEM
        assert "Invalid value" in str(mcp_error)
    
    def test_handle_file_not_found_error(self):
        """测试处理文件未找到错误"""
        error = FileNotFoundError("File not found")
        
        result = self.handler.handle_error(error, reraise=False)
        
        assert result["category"] == "file_io"
        assert "文件路径" in str(result["suggestions"])
    
    def test_handle_connection_error(self):
        """测试处理连接错误"""
        error = ConnectionError("Connection failed")
        
        result = self.handler.handle_error(error, reraise=False)
        
        assert result["category"] == "network"
        assert "网络连接" in str(result["suggestions"])
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        error = ValidationError("Invalid input")
        
        response = self.handler.create_error_response(error)
        
        assert response["success"] is False
        assert "error" in response
        assert response["error"]["message"] == "Invalid input"
        assert response["error"]["category"] == "validation"
    
    def test_create_error_response_with_traceback(self):
        """测试创建包含堆栈跟踪的错误响应"""
        error = ValueError("Standard error")
        
        response = self.handler.create_error_response(error, include_traceback=True)
        
        assert response["success"] is False
        assert "traceback" in response["error"]
    
    @patch('logging.getLogger')
    def test_logger_setup(self, mock_get_logger):
        """测试日志记录器设置"""
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        
        handler = ErrorHandler("test")
        
        mock_logger.addHandler.assert_called_once()
        mock_logger.setLevel.assert_called_once_with(logging.INFO)


class TestErrorDecorator:
    """测试错误处理装饰器"""
    
    def test_decorator_success(self):
        """测试装饰器成功情况"""
        @handle_mcp_error
        def test_function():
            return {"result": "success"}
        
        result = test_function()
        assert result == {"result": "success"}
    
    def test_decorator_with_mcp_error(self):
        """测试装饰器处理MCP错误"""
        @handle_mcp_error
        def test_function():
            raise ValidationError("Test error")
        
        result = test_function()
        
        assert result["success"] is False
        assert result["error"]["message"] == "Test error"
        assert result["error"]["category"] == "validation"
    
    def test_decorator_with_standard_error(self):
        """测试装饰器处理标准错误"""
        @handle_mcp_error
        def test_function():
            raise ValueError("Standard error")
        
        result = test_function()
        
        assert result["success"] is False
        assert "Standard error" in result["error"]["message"]


class TestErrorIntegration:
    """测试错误处理集成场景"""
    
    def test_error_chain(self):
        """测试错误链处理"""
        try:
            # 模拟嵌套错误场景
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise LLMError("LLM processing failed") from e
        except LLMError as llm_error:
            handler = ErrorHandler()
            result = handler.handle_error(llm_error, reraise=False)
            
            assert result["category"] == "llm"
            assert result["message"] == "LLM processing failed"
    
    def test_context_preservation(self):
        """测试上下文信息保存"""
        error = AgentError(
            "Agent failed",
            agent_name="TestAgent",
            task_id="task_456"
        )
        
        context = {
            "user_id": "user_123",
            "session_id": "session_789"
        }
        
        handler = ErrorHandler()
        result = handler.handle_error(error, context=context, reraise=False)
        
        assert result["context"]["user_id"] == "user_123"
        assert result["context"]["session_id"] == "session_789"
        assert result["details"]["agent_name"] == "TestAgent"
        assert result["details"]["task_id"] == "task_456"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])