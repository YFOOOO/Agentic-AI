import os
import json
import tempfile
import unittest
import types
import importlib
from unittest.mock import patch


# 模块级辅助函数：_load_server_with_mock
def _load_server_with_mock(mock_run_func):
    import types
    import importlib
    from unittest.mock import patch

    # 用真正的"模块对象"更稳妥，避免某些导入路径对非模块对象敏感
    dummy = types.ModuleType("orchestrator")
    dummy.run_nobel_pipeline = mock_run_func

    with patch.dict('sys.modules', {
        'src.mcp.orchestrator': dummy,   # 覆盖 src 路径
        'mcp.orchestrator': dummy,       # 覆盖回退路径
    }):
        if 'src.mcp.server' in importlib.sys.modules:
            del importlib.sys.modules['src.mcp.server']
        return importlib.import_module('src.mcp.server')


class TestMcpServer(unittest.TestCase):
    def test_orchestrator_config_snapshot_env_keys_consistent(self):
        import os, json, importlib

        prev = {
            "NOBEL_LLM_MODEL": os.environ.get("NOBEL_LLM_MODEL"),
            "NOBEL_LLM_MAX_TOKENS": os.environ.get("NOBEL_LLM_MAX_TOKENS"), 
            "NOBEL_LLM_TEMPERATURE": os.environ.get("NOBEL_LLM_TEMPERATURE"),
            "NOBEL_THEME": os.environ.get("NOBEL_THEME"),
        }
        os.environ["NOBEL_LLM_MODEL"] = "provider:model"
        os.environ["NOBEL_LLM_MAX_TOKENS"] = "512"
        os.environ["NOBEL_LLM_TEMPERATURE"] = "0.3"
        os.environ["NOBEL_THEME"] = "主题"

        try:
            run_dir = "artifacts/nobel/test_config_snapshot_env_keys_consistent"
            os.makedirs(run_dir, exist_ok=True)
            run_log = {"summary": {"artifacts": {"run_dir": run_dir}, "agent_run_dir": run_dir}}
            orchestrator = importlib.import_module("src.mcp.orchestrator")
            path = orchestrator._save_run_config_snapshot(run_log)
            self.assertTrue(path and os.path.exists(path))
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            env = data.get("env", {})
            self.assertEqual(env.get("NOBEL_LLM_MODEL"), os.environ["NOBEL_LLM_MODEL"])
            self.assertEqual(env.get("NOBEL_LLM_MAX_TOKENS"), os.environ["NOBEL_LLM_MAX_TOKENS"])
            self.assertEqual(env.get("NOBEL_LLM_TEMPERATURE"), os.environ["NOBEL_LLM_TEMPERATURE"])
            self.assertEqual(env.get("NOBEL_THEME"), os.environ["NOBEL_THEME"])
        finally:
            for k, v in prev.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_orchestrate_all_force_string_zero_does_not_set_env(self):
        import os, json, tempfile

        prev = os.environ.get("NOBEL_FORCE_RECOMPUTE")
        if prev is not None:
            os.environ.pop("NOBEL_FORCE_RECOMPUTE", None)

        def mock_run():
            fd, path = tempfile.mkstemp(suffix=".json")
            os.close(fd)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"summary": {"artifacts": {}}}, f)
            # 验证：字符串 "0" 不应设置环境变量
            assert os.environ.get("NOBEL_FORCE_RECOMPUTE") is None
            return path

        server = _load_server_with_mock(mock_run)
        try:
            payload = {"force": "0"}
            result = server.orchestrate_all(payload)
            self.assertIsInstance(result, dict)
        finally:
            if prev is None:
                os.environ.pop("NOBEL_FORCE_RECOMPUTE", None)
            else:
                os.environ["NOBEL_FORCE_RECOMPUTE"] = prev

    def test_orchestrate_all_max_tokens_non_numeric_does_not_set_env(self):
        import os, json, tempfile

        prev = os.environ.get("NOBEL_LLM_MAX_TOKENS")
        if prev is not None:
            os.environ.pop("NOBEL_LLM_MAX_TOKENS", None)

        def mock_run():
            fd, path = tempfile.mkstemp(suffix=".json")
            os.close(fd)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"summary": {"artifacts": {}}}, f)
            # 验证：列表这种非数值类型不应写入环境
            assert os.environ.get("NOBEL_LLM_MAX_TOKENS") is None
            return path

        server = _load_server_with_mock(mock_run)
        try:
            payload = {"max_tokens": ["not", "numeric"]}
            result = server.orchestrate_all(payload)
            self.assertIsInstance(result, dict)
        finally:
            if prev is None:
                os.environ.pop("NOBEL_LLM_MAX_TOKENS", None)
            else:
                os.environ["NOBEL_LLM_MAX_TOKENS"] = prev

    def test_orchestrate_all_temperature_non_numeric_does_not_set_env(self):
        import os, json, tempfile

        prev = os.environ.get("NOBEL_LLM_TEMPERATURE")
        if prev is not None:
            os.environ.pop("NOBEL_LLM_TEMPERATURE", None)

        def mock_run():
            fd, path = tempfile.mkstemp(suffix=".json")
            os.close(fd)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"summary": {"artifacts": {}}}, f)
            # 验证：非数值类型不应写入环境变量
            assert os.environ.get("NOBEL_LLM_TEMPERATURE") is None
            return path

        server = _load_server_with_mock(mock_run)
        try:
            payload = {"temperature": ["not", "numeric"]}
            result = server.orchestrate_all(payload)
            self.assertIsInstance(result, dict)
        finally:
            if prev is None:
                os.environ.pop("NOBEL_LLM_TEMPERATURE", None)
            else:
                os.environ["NOBEL_LLM_TEMPERATURE"] = prev