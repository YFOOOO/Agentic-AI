"""
错误处理框架集成验证脚本

测试统一错误处理框架在实际使用场景中的表现，验证用户友好性和功能完整性。
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mcp.exceptions import (
    ErrorHandler, ConfigurationError, LLMError, 
    AgentError, FileIOError, ValidationError,
    NetworkError, DataProcessingError
)


class TestErrorHandlingIntegration:
    """错误处理框架集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.error_handler = ErrorHandler("integration_test")
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_configuration_error_user_friendly(self):
        """测试配置错误的用户友好性"""
        error = ConfigurationError(
            "API密钥未配置",
            config_key="OPENAI_API_KEY",
            suggestions=[
                "在.env文件中设置OPENAI_API_KEY",
                "检查环境变量是否正确加载",
                "参考文档中的配置示例"
            ]
        )
        
        # 验证错误信息结构
        error_dict = error.to_dict()
        assert error_dict["category"] == "configuration"
        assert error_dict["severity"] == "high"
        assert "API密钥未配置" in error_dict["message"]
        assert len(error_dict["suggestions"]) == 3
        
        # 验证用户友好的消息
        user_message = error.get_user_message()
        assert "[CONFIGURATION]" in user_message
        assert "建议解决方案:" in user_message
        assert "在.env文件中设置" in user_message
        
        print("✅ 配置错误用户友好性测试通过")
        print(f"错误消息: {user_message}")
    
    def test_llm_error_with_context(self):
        """测试LLM错误的上下文信息"""
        error = LLMError(
            "模型调用失败",
            provider="openai",
            model="gpt-4",
            suggestions=[
                "检查API密钥是否有效",
                "验证网络连接",
                "尝试使用其他模型"
            ]
        )
        
        # 使用错误处理器处理
        response = self.error_handler.create_error_response(error)
        
        assert response["success"] is False
        assert response["error"]["category"] == "llm"
        assert response["error"]["details"]["provider"] == "openai"
        assert response["error"]["details"]["model"] == "gpt-4"
        
        print("✅ LLM错误上下文信息测试通过")
        print(f"错误详情: {response['error']['details']}")
    
    def test_file_io_error_with_suggestions(self):
        """测试文件IO错误的建议信息"""
        non_existent_file = "/path/to/nonexistent/file.txt"
        
        error = FileIOError(
            f"无法读取文件: {non_existent_file}",
            file_path=non_existent_file,
            operation="read"
        )
        
        error_dict = error.to_dict()
        assert error_dict["category"] == "file_io"
        assert error_dict["details"]["file_path"] == non_existent_file
        assert error_dict["details"]["operation"] == "read"
        assert "检查文件路径" in str(error_dict["suggestions"])
        
        print("✅ 文件IO错误建议信息测试通过")
        print(f"建议: {error_dict['suggestions']}")
    
    def test_agent_error_with_task_context(self):
        """测试代理错误的任务上下文"""
        task_id = "test_task_123"
        agent_name = "TestAgent"
        
        error = AgentError(
            "代理执行超时",
            agent_name=agent_name,
            task_id=task_id,
            suggestions=[
                "增加超时时间设置",
                "检查输入数据格式",
                "查看代理日志获取详细信息"
            ]
        )
        
        # 测试错误处理器的上下文处理
        context = {"user_id": "user_123", "session_id": "session_456"}
        response = self.error_handler.handle_error(error, context=context, reraise=False)
        
        assert response["category"] == "agent"
        assert response["details"]["agent_name"] == agent_name
        assert response["details"]["task_id"] == task_id
        assert response["context"]["user_id"] == "user_123"
        
        print("✅ 代理错误任务上下文测试通过")
        print(f"上下文: {response['context']}")
    
    def test_network_error_retry_suggestions(self):
        """测试网络错误的重试建议"""
        error = NetworkError(
            "连接超时",
            url="https://api.example.com/data",
            status_code=408,
            suggestions=[
                "检查网络连接状态",
                "稍后重试请求",
                "联系服务提供商"
            ]
        )
        
        user_message = error.get_user_message()
        assert "[NETWORK]" in user_message
        assert "连接超时" in user_message
        assert "稍后重试" in user_message
        
        print("✅ 网络错误重试建议测试通过")
        print(f"用户消息: {user_message}")
    
    def test_validation_error_field_specific(self):
        """测试验证错误的字段特定信息"""
        error = ValidationError(
            "邮箱格式不正确",
            field="email",
            suggestions=[
                "确保邮箱包含@符号",
                "检查邮箱域名格式",
                "参考: user@example.com"
            ]
        )
        
        error_dict = error.to_dict()
        assert error_dict["severity"] == "low"  # 验证错误通常是低严重程度
        assert error_dict["details"]["field"] == "email"
        assert "邮箱格式不正确" in error_dict["message"]
        
        print("✅ 验证错误字段特定信息测试通过")
        print(f"字段: {error_dict['details']['field']}")
    
    def test_error_handler_logging(self):
        """测试错误处理器的日志记录"""
        import logging
        from io import StringIO
        
        # 创建字符串流来捕获日志
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        # 配置错误处理器的日志
        self.error_handler.logger.addHandler(handler)
        self.error_handler.logger.setLevel(logging.INFO)
        
        # 创建不同严重程度的错误
        low_error = ValidationError("轻微验证错误")
        high_error = ConfigurationError("严重配置错误")
        
        # 处理错误（不重新抛出）
        self.error_handler.handle_error(low_error, reraise=False)
        self.error_handler.handle_error(high_error, reraise=False)
        
        # 检查日志内容
        log_content = log_stream.getvalue()
        assert "轻微验证错误" in log_content
        assert "严重配置错误" in log_content
        
        print("✅ 错误处理器日志记录测试通过")
        print(f"日志内容预览: {log_content[:100]}...")
    
    def test_standard_exception_conversion(self):
        """测试标准异常的转换"""
        # 测试文件不存在错误
        file_error = FileNotFoundError("No such file or directory: test.txt")
        response = self.error_handler.handle_error(file_error, reraise=False)
        
        assert response["category"] == "file_io"
        assert "文件路径" in str(response["suggestions"])
        
        # 测试值错误
        value_error = ValueError("Invalid input format")
        response = self.error_handler.handle_error(value_error, reraise=False)
        
        assert response["category"] == "validation"
        assert response["severity"] == "low"
        
        # 测试连接错误
        conn_error = ConnectionError("Connection refused")
        response = self.error_handler.handle_error(conn_error, reraise=False)
        
        assert response["category"] == "network"
        assert "网络连接" in str(response["suggestions"])
        
        print("✅ 标准异常转换测试通过")
        print(f"转换示例: FileNotFoundError -> {response['category']}")
    
    def test_error_chain_handling(self):
        """测试错误链处理"""
        try:
            # 模拟嵌套错误场景
            try:
                raise ValueError("原始数据格式错误")
            except ValueError as e:
                raise DataProcessingError("数据处理失败") from e
        except DataProcessingError as final_error:
            response = self.error_handler.handle_error(final_error, reraise=False)
            
            assert response["category"] == "data_processing"
            assert "数据处理失败" in response["message"]
            
            print("✅ 错误链处理测试通过")
            print(f"最终错误类别: {response['category']}")
    
    def test_error_severity_mapping(self):
        """测试错误严重程度映射"""
        errors_and_severities = [
            (ValidationError("验证错误"), "low"),
            (NetworkError("网络错误"), "medium"),
            (ConfigurationError("配置错误"), "high"),
            (AgentError("代理错误"), "medium"),
        ]
        
        for error, expected_severity in errors_and_severities:
            error_dict = error.to_dict()
            assert error_dict["severity"] == expected_severity
            
        print("✅ 错误严重程度映射测试通过")
        print("验证了4种错误类型的严重程度映射")
    
    def test_multilingual_error_messages(self):
        """测试多语言错误消息"""
        # 测试中文错误消息
        error = ConfigurationError(
            "配置文件缺失",
            suggestions=[
                "创建.env配置文件",
                "检查文件权限设置"
            ]
        )
        
        user_message = error.get_user_message()
        assert "配置文件缺失" in user_message
        assert "建议解决方案:" in user_message
        assert "创建.env配置文件" in user_message
        
        print("✅ 多语言错误消息测试通过")
        print(f"中文消息示例: {user_message.split('建议解决方案:')[0].strip()}")


def run_integration_tests():
    """运行集成测试并生成报告"""
    print("🧪 开始错误处理框架集成验证...")
    print("=" * 60)
    
    test_instance = TestErrorHandlingIntegration()
    test_instance.setup_method()
    
    test_methods = [
        test_instance.test_configuration_error_user_friendly,
        test_instance.test_llm_error_with_context,
        test_instance.test_file_io_error_with_suggestions,
        test_instance.test_agent_error_with_task_context,
        test_instance.test_network_error_retry_suggestions,
        test_instance.test_validation_error_field_specific,
        test_instance.test_error_handler_logging,
        test_instance.test_standard_exception_conversion,
        test_instance.test_error_chain_handling,
        test_instance.test_error_severity_mapping,
        test_instance.test_multilingual_error_messages,
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__} 失败: {e}")
            failed += 1
    
    test_instance.teardown_method()
    
    print("=" * 60)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有错误处理集成测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)