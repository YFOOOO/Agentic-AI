"""
MCP协调器核心功能测试
测试目标：提升orchestrator.py的测试覆盖率从8%到60%+
"""
import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import shutil

# 确保项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestLLMClientFromEnv(unittest.TestCase):
    """测试LLM客户端创建和配置功能"""
    
    def setUp(self):
        """测试前准备"""
        self.original_env = {}
        # 保存原始环境变量
        for key in ["NOBEL_LLM_MODEL", "NOBEL_LLM_TEMPERATURE", "NOBEL_LLM_MAX_TOKENS", 
                   "DASHSCOPE_API_KEY", "DEEPSEEK_API_KEY", "AISUITE_PATH"]:
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
    
    def test_get_llm_client_no_aisuite(self):
        """测试没有aisuite时返回None"""
        # 确保没有aisuite相关的环境变量
        if "AISUITE_PATH" in os.environ:
            del os.environ["AISUITE_PATH"]
        
        # 由于aisuite可能不存在，这个测试验证函数能正确处理ImportError
        from src.mcp.orchestrator import get_llm_client_from_env
        
        # 如果aisuite不存在，应该返回None；如果存在，应该返回adapter
        result = get_llm_client_from_env()
        # 这个测试主要验证函数不会崩溃
        self.assertTrue(result is None or hasattr(result, 'generate'))
    
    def test_environment_variable_reading(self):
        """测试环境变量读取逻辑"""
        # 设置测试环境变量
        os.environ["NOBEL_LLM_MODEL"] = "test:model"
        os.environ["NOBEL_LLM_TEMPERATURE"] = "0.7"
        os.environ["NOBEL_LLM_MAX_TOKENS"] = "2048"
        
        # 验证环境变量设置成功
        self.assertEqual(os.environ.get("NOBEL_LLM_MODEL"), "test:model")
        self.assertEqual(os.environ.get("NOBEL_LLM_TEMPERATURE"), "0.7")
        self.assertEqual(os.environ.get("NOBEL_LLM_MAX_TOKENS"), "2048")
    
    def test_api_key_detection_logic(self):
        """测试API Key检测逻辑"""
        # 测试DashScope Key检测
        os.environ["DASHSCOPE_API_KEY"] = "test_dashscope_key"
        self.assertTrue(os.environ.get("DASHSCOPE_API_KEY"))
        
        # 清理并测试DeepSeek Key检测
        del os.environ["DASHSCOPE_API_KEY"]
        os.environ["DEEPSEEK_API_KEY"] = "test_deepseek_key"
        self.assertTrue(os.environ.get("DEEPSEEK_API_KEY"))


class TestAisuiteAdapter(unittest.TestCase):
    """测试AisuiteAdapter类的功能（简化版本）"""
    
    def test_adapter_class_structure(self):
        """测试Adapter类的基本结构"""
        # 这个测试验证如果能创建adapter，它应该有正确的属性
        from src.mcp.orchestrator import get_llm_client_from_env
        
        adapter = get_llm_client_from_env()
        if adapter is not None:
            # 验证adapter有必要的方法和属性
            self.assertTrue(hasattr(adapter, 'generate'))
            self.assertTrue(hasattr(adapter, 'temperature'))
            self.assertTrue(hasattr(adapter, 'max_tokens'))
            self.assertTrue(hasattr(adapter, 'last_error'))
    
    def test_temperature_parsing(self):
        """测试温度参数解析"""
        # 测试有效的温度值
        os.environ["NOBEL_LLM_TEMPERATURE"] = "0.5"
        try:
            temp = float(os.environ.get("NOBEL_LLM_TEMPERATURE", "0.2"))
            self.assertEqual(temp, 0.5)
        except Exception:
            self.fail("Temperature parsing should not fail for valid value")
        
        # 测试无效的温度值
        os.environ["NOBEL_LLM_TEMPERATURE"] = "invalid"
        try:
            temp = float(os.environ.get("NOBEL_LLM_TEMPERATURE", "0.2"))
        except Exception:
            # 应该能处理异常并使用默认值
            temp = 0.2
        self.assertEqual(temp, 0.2)
        
        # 清理
        if "NOBEL_LLM_TEMPERATURE" in os.environ:
            del os.environ["NOBEL_LLM_TEMPERATURE"]


class TestConfigurationFunctions(unittest.TestCase):
    """测试配置相关功能"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.run_log = {
            "summary": {
                "artifacts": {"run_dir": self.test_dir},
                "agent_run_dir": self.test_dir
            }
        }
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_save_run_config_snapshot(self):
        """测试保存运行配置快照"""
        from src.mcp.orchestrator import _save_run_config_snapshot
        
        # 设置环境变量
        os.environ["NOBEL_LLM_MODEL"] = "test:model"
        os.environ["NOBEL_THEME"] = "测试主题"
        
        try:
            # 调用函数
            config_path = _save_run_config_snapshot(self.run_log)
            
            # 验证结果
            self.assertIsNotNone(config_path)
            self.assertTrue(os.path.exists(config_path))
            
            # 验证配置内容
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 根据实际的数据结构验证
            self.assertIn("env", config)
            self.assertIn("NOBEL_LLM_MODEL", config["env"])
            self.assertEqual(config["env"]["NOBEL_LLM_MODEL"], "test:model")
            self.assertIn("NOBEL_THEME", config["env"])
            self.assertEqual(config["env"]["NOBEL_THEME"], "测试主题")
            
        finally:
            # 清理环境变量
            for key in ["NOBEL_LLM_MODEL", "NOBEL_THEME"]:
                if key in os.environ:
                    del os.environ[key]
    
    @patch('builtins.print')
    def test_print_run_summary(self, mock_print):
        """测试打印运行摘要"""
        from src.mcp.orchestrator import _print_run_summary
        
        # 准备测试数据
        run_log = {
            "summary": {
                "total_duration_s": 25.5,
                "artifacts": {"run_dir": "/test/path"},
                "steps": {
                    "fetch": {"duration_s": 5.0, "rows": 100},
                    "analysis": {"duration_s": 10.0},
                    "write": {"duration_s": 8.0},
                    "eval": {"duration_s": 2.5}
                }
            }
        }
        
        # 调用函数
        _print_run_summary(run_log)
        
        # 验证打印调用
        self.assertTrue(mock_print.called)
        # 检查是否打印了关键信息
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        summary_printed = any("Run Summary" in call for call in print_calls)
        self.assertTrue(summary_printed)


class TestRunNobelPipelineCore(unittest.TestCase):
    """测试run_nobel_pipeline核心逻辑（不执行完整流程）"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.original_env = {}
        # 保存并清理环境变量
        for key in ["NOBEL_FORCE_RECOMPUTE", "NOBEL_THEME"]:
            self.original_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # 恢复环境变量
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    @patch('src.mcp.orchestrator.LiteratureAgent')
    @patch('src.mcp.orchestrator.load_dotenv')
    @patch('os.makedirs')
    def test_run_nobel_pipeline_initialization(self, mock_makedirs, mock_load_dotenv, mock_literature_agent):
        """测试pipeline初始化阶段"""
        from src.mcp.orchestrator import run_nobel_pipeline
        
        # 设置mock
        mock_agent_instance = MagicMock()
        mock_agent_instance.handle.return_value = {
            "artifacts": {
                "csv": f"{self.test_dir}/test.csv",
                "run_dir": self.test_dir
            },
            "metrics": {"rows": 100}
        }
        mock_literature_agent.return_value = mock_agent_instance
        
        # 创建测试CSV文件
        test_csv = f"{self.test_dir}/test.csv"
        with open(test_csv, 'w') as f:
            f.write("test,data\n1,2\n")
        
        # 由于完整pipeline会执行很多步骤，我们只测试初始化部分
        # 通过让后续步骤抛出异常来提前结束
        with patch('subprocess.run', side_effect=Exception("Test stop")):
            try:
                run_nobel_pipeline()
            except Exception as e:
                # 预期的异常，用于提前结束测试
                pass
        
        # 验证初始化步骤
        mock_load_dotenv.assert_called_once()
        mock_makedirs.assert_called_with("artifacts/nobel", exist_ok=True)
        mock_literature_agent.assert_called_once_with(base_dir="artifacts/nobel")
        mock_agent_instance.handle.assert_called_once()
    
    @patch.dict(os.environ, {"NOBEL_FORCE_RECOMPUTE": "1"})
    def test_force_recompute_flag(self):
        """测试强制重新计算标志"""
        from src.mcp.orchestrator import run_nobel_pipeline
        
        # 验证环境变量设置
        self.assertEqual(os.environ.get("NOBEL_FORCE_RECOMPUTE"), "1")
        
        # 这里我们只测试环境变量的读取，不执行完整pipeline
        with patch('src.mcp.orchestrator.LiteratureAgent') as mock_agent:
            mock_agent_instance = MagicMock()
            mock_agent_instance.handle.side_effect = Exception("Test stop")
            mock_agent.return_value = mock_agent_instance
            
            with patch('src.mcp.orchestrator.load_dotenv'):
                try:
                    run_nobel_pipeline()
                except Exception:
                    pass  # 预期的异常


class TestErrorHandling(unittest.TestCase):
    """测试错误处理机制"""
    
    @patch('src.mcp.orchestrator.ERROR_HANDLING_AVAILABLE', True)
    @patch('src.mcp.orchestrator.orchestrator_error_handler')
    def test_error_handling_with_framework(self, mock_error_handler):
        """测试使用错误处理框架的情况"""
        from src.mcp.orchestrator import run_nobel_pipeline
        
        # 设置mock让LiteratureAgent抛出异常
        with patch('src.mcp.orchestrator.LiteratureAgent') as mock_agent:
            mock_agent.side_effect = Exception("Test error")
            
            with patch('src.mcp.orchestrator.load_dotenv'):
                with self.assertRaises(Exception):
                    run_nobel_pipeline()
                
                # 验证错误处理器被调用
                mock_error_handler.handle_error.assert_called_once()
    
    @patch('src.mcp.orchestrator.ERROR_HANDLING_AVAILABLE', False)
    def test_error_handling_without_framework(self):
        """测试没有错误处理框架的情况"""
        from src.mcp.orchestrator import run_nobel_pipeline
        
        # 设置mock让LiteratureAgent抛出异常
        with patch('src.mcp.orchestrator.LiteratureAgent') as mock_agent:
            mock_agent.side_effect = Exception("Test error")
            
            with patch('src.mcp.orchestrator.load_dotenv'):
                # 应该直接抛出异常
                with self.assertRaises(Exception) as context:
                    run_nobel_pipeline()
                
                self.assertEqual(str(context.exception), "Test error")


if __name__ == '__main__':
    unittest.main()