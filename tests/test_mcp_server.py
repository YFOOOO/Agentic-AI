import os
import json
import tempfile
import unittest
import types
import importlib
from unittest.mock import patch

import src.mcp.server as mcp_server


def _load_server_with_mock(mock_run_func):
    """
    在导入 src.mcp.server 之前，注入一个假的 src.mcp.orchestrator，
    其内只提供 run_nobel_pipeline=mock_run_func，避免真实依赖被导入。
    """
    dummy_orchestrator = types.SimpleNamespace(run_nobel_pipeline=mock_run_func)
    with patch.dict('sys.modules', {'src.mcp.orchestrator': dummy_orchestrator}):
        # 保险：若之前已导入过 server，则删除以强制重新导入
        if 'src.mcp.server' in importlib.sys.modules:
            del importlib.sys.modules['src.mcp.server']
        return importlib.import_module('src.mcp.server')


class TestMcpServer(unittest.TestCase):
    def test_orchestrate_all_success_contract(self):
        # 伪造最小 run_log.json，包含 summary/artifacts
        run_log = {
            "summary": {
                "ok": True,
                "run_id": "123456",
                "agent_run_dir": "artifacts/nobel/runs/123456",
                "artifacts": {
                    "draft_published": "artifacts/nobel/draft.md",
                    "draft_md_agent": "artifacts/nobel/runs/123456/draft_agent.md",
                    "thresholds_path": "artifacts/nobel/eval_thresholds.json",
                },
            }
        }
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(run_log, f, ensure_ascii=False)
            mcp_server = _load_server_with_mock(lambda: path)
            payload = {"theme": "测试主题", "thresholds_path": "artifacts/nobel/eval_thresholds.json"}
            result = mcp_server.orchestrate_all(payload)

            # 顶层契约
            self.assertEqual(result.get("schema_version"), "1.0")
            self.assertIsInstance(result.get("summary"), dict)
            self.assertIsInstance(result.get("artifacts"), dict)
            self.assertIsInstance(result.get("errors"), list)
            # 成功路径
            self.assertTrue(result["summary"].get("ok"))
            self.assertIn("draft_published", result["artifacts"])
            self.assertIn("draft_md_agent", result["artifacts"])
            self.assertEqual(result["errors"], [])
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass

    def test_orchestrate_all_pipeline_exception(self):
        mcp_server = _load_server_with_mock(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        result = mcp_server.orchestrate_all({})
        self.assertEqual(result.get("schema_version"), "1.0")
        self.assertEqual(result.get("summary"), {})
        self.assertEqual(result.get("artifacts"), {})
        self.assertIsInstance(result.get("errors"), list)
        self.assertTrue(any(e.get("code") == "E_ORCHESTRATE_FAIL" for e in result["errors"]))

    def test_orchestrate_all_load_log_fail(self):
        mcp_server = _load_server_with_mock(lambda: "/nonexistent/path/run_log.json")
        result = mcp_server.orchestrate_all({})
        self.assertEqual(result.get("schema_version"), "1.0")
        self.assertEqual(result.get("summary"), {})
        self.assertEqual(result.get("artifacts"), {})
        self.assertTrue(any(e.get("code") == "E_LOAD_LOG_FAIL" for e in result.get("errors", [])))


if __name__ == "__main__":
    unittest.main()