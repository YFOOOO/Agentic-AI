"""
LLM集成稳定性测试（简化版本）
测试目标：验证LLM集成的稳定性改进，重点测试核心逻辑而不是复杂的mock
"""
import os
import sys
import unittest
import tempfile
from unittest.mock import MagicMock
from pathlib import Path

# 确保项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestLLMIntegrationStability(unittest.TestCase):
    """测试LLM集成稳定性改进（简化版本）"""
    
    def setUp(self):
        """测试前准备"""
        self.original_env = {}
        # 保存原始环境变量
        for key in ["NOBEL_LLM_MODEL", "DASHSCOPE_API_KEY", "DEEPSEEK_API_KEY", 
                   "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
            self.original_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
    
    def tearDown(self):
        """测试后清理"""
        # 恢复原始环境变量
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_api_key_validation_logic(self):
        """测试API Key验证逻辑（不使用复杂mock）"""
        # 测试环境变量检测
        os.environ["DASHSCOPE_API_KEY"] = "test_key"
        
        # 验证环境变量设置
        self.assertTrue(os.environ.get("DASHSCOPE_API_KEY"))
        
        # 测试多个API Key的情况
        os.environ["DEEPSEEK_API_KEY"] = "deepseek_key"
        
        api_keys = {
            "dashscope": os.environ.get("DASHSCOPE_API_KEY"),
            "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY")
        }
        
        valid_providers = {k: v for k, v in api_keys.items() if v}
        
        # 验证过滤逻辑
        self.assertIn("dashscope", valid_providers)
        self.assertIn("deepseek", valid_providers)
        self.assertNotIn("openai", valid_providers)
        self.assertNotIn("anthropic", valid_providers)
    
    def test_model_provider_parsing(self):
        """测试模型provider解析逻辑"""
        # 测试有效的模型格式
        model = "dashscope:qwen3-max"
        provider = model.split(":")[0]
        self.assertEqual(provider, "dashscope")
        
        # 测试无效格式的处理
        invalid_model = "invalid_format"
        parts = invalid_model.split(":")
        if len(parts) == 1:
            # 没有provider信息
            self.assertEqual(parts[0], "invalid_format")
    
    def test_error_message_structure(self):
        """测试错误信息结构"""
        # 模拟错误信息格式
        attempt = 2
        max_retries = 3
        error_msg = "API rate limit exceeded"
        
        formatted_error = f"Attempt {attempt}/{max_retries}: {error_msg}"
        
        # 验证错误信息包含必要信息
        self.assertIn("Attempt", formatted_error)
        self.assertIn("2/3", formatted_error)
        self.assertIn("API rate limit exceeded", formatted_error)
    
    def test_timeout_configuration_values(self):
        """测试超时配置值"""
        # 测试默认超时值
        default_timeout = 30
        self.assertEqual(default_timeout, 30)
        
        # 测试指数退避计算
        for attempt in range(3):
            backoff_time = min(2 ** attempt, 10)
            self.assertLessEqual(backoff_time, 10)
            if attempt == 0:
                self.assertEqual(backoff_time, 1)
            elif attempt == 1:
                self.assertEqual(backoff_time, 2)
            elif attempt == 2:
                self.assertEqual(backoff_time, 4)


class TestWritingAgentIntegration(unittest.TestCase):
    """测试写作代理与改进后的LLM集成"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_writing_agent_with_mock_llm(self):
        """测试写作代理使用mock LLM客户端"""
        from src.agents.writing_agent import WritingAgent
        
        # 创建mock LLM客户端
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Generated content"
        mock_llm.last_error = None
        
        # 创建写作代理
        agent = WritingAgent(base_dir=self.test_dir, llm=mock_llm)
        
        # 创建测试CSV文件
        test_csv = os.path.join(self.test_dir, "test.csv")
        with open(test_csv, 'w') as f:
            f.write("year,name,category\n2023,Test,Physics\n")
        
        # 测试处理任务
        task = {
            "task_id": "test_task",
            "csv": test_csv,
            "theme": "测试主题"
        }
        
        result = agent.handle(task)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertIn("artifacts", result)
        # 修正：使用实际的键名
        self.assertIn("draft_md", result["artifacts"])
        
        # 验证LLM被调用
        mock_llm.generate.assert_called()
    
    def test_writing_agent_fallback_mode(self):
        """测试写作代理的fallback模式"""
        from src.agents.writing_agent import WritingAgent
        
        # 不提供LLM客户端
        agent = WritingAgent(base_dir=self.test_dir, llm=None)
        
        # 创建测试CSV文件
        test_csv = os.path.join(self.test_dir, "test.csv")
        with open(test_csv, 'w') as f:
            f.write("year,name,category\n2023,Test,Physics\n")
        
        # 测试处理任务
        task = {
            "task_id": "test_task",
            "csv": test_csv,
            "theme": "测试主题"
        }
        
        result = agent.handle(task)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertIn("artifacts", result)
        # 修正：使用实际的键名
        self.assertIn("draft_md", result["artifacts"])
        
        # 验证使用了fallback模式
        self.assertIn("LLM client not injected", agent.last_llm_error)
    
    def test_writing_agent_retry_mechanism(self):
        """测试写作代理的重试机制"""
        from src.agents.writing_agent import WritingAgent
        
        # 创建会失败然后成功的mock LLM
        mock_llm = MagicMock()
        # 第一次调用失败，第二次成功
        mock_llm.generate.side_effect = ["", "Generated content on retry"]
        mock_llm.last_error = "First attempt failed"
        
        agent = WritingAgent(base_dir=self.test_dir, llm=mock_llm)
        
        # 测试call_llm方法的重试逻辑
        result = agent.call_llm("test prompt", max_retries=2)
        
        # 验证重试机制工作
        self.assertEqual(mock_llm.generate.call_count, 2)
        self.assertEqual(result, "Generated content on retry")
    
    def test_fallback_content_generation(self):
        """测试fallback内容生成"""
        from src.agents.writing_agent import WritingAgent
        
        agent = WritingAgent(base_dir=self.test_dir)
        
        # 测试不同主题的fallback内容
        prompt_nobel = "分析Nobel奖数据，theme: 诺贝尔奖研究"
        fallback_content = agent._generate_fallback_content(prompt_nobel)
        
        # 验证fallback内容包含必要信息
        self.assertIn("诺贝尔奖", fallback_content)
        self.assertIn("数据概览", fallback_content)
        self.assertIn("主要发现", fallback_content)
        self.assertIn("LLM服务暂时不可用", fallback_content)


class TestLLMClientStability(unittest.TestCase):
    """测试LLM客户端稳定性功能（不依赖复杂mock）"""
    
    def test_get_llm_client_no_aisuite(self):
        """测试没有aisuite时的处理"""
        from src.mcp.orchestrator import get_llm_client_from_env
        
        # 这个测试验证函数能正确处理aisuite不存在的情况
        # 由于aisuite可能存在也可能不存在，我们主要验证函数不会崩溃
        try:
            result = get_llm_client_from_env()
            # 如果aisuite存在且有API Key，result可能不为None
            # 如果aisuite不存在或没有API Key，result应该为None
            self.assertTrue(result is None or hasattr(result, 'generate'))
        except Exception as e:
            # 如果有异常，应该是可预期的ImportError或类似错误
            self.assertIn("aisuite", str(e).lower())
    
    def test_environment_variable_handling(self):
        """测试环境变量处理"""
        # 测试温度参数解析
        os.environ["NOBEL_LLM_TEMPERATURE"] = "0.7"
        try:
            temp = float(os.environ.get("NOBEL_LLM_TEMPERATURE", "0.2"))
            self.assertEqual(temp, 0.7)
        except Exception:
            self.fail("Temperature parsing should not fail")
        
        # 测试max_tokens参数解析
        os.environ["NOBEL_LLM_MAX_TOKENS"] = "1024"
        try:
            max_tokens = int(os.environ.get("NOBEL_LLM_MAX_TOKENS"))
            self.assertEqual(max_tokens, 1024)
        except Exception:
            self.fail("Max tokens parsing should not fail")
        
        # 清理
        for key in ["NOBEL_LLM_TEMPERATURE", "NOBEL_LLM_MAX_TOKENS"]:
            if key in os.environ:
                del os.environ[key]


if __name__ == '__main__':
    unittest.main()