import os
import json
import tempfile
import unittest
from unittest.mock import patch

import src.mcp.server as mcp_server


class TestMcpServer(unittest.TestCase):
    @patch("src.mcp.server.run_nobel_pipeline")
    def test_orchestrate_all_success_contract(self, mock_run):
        # 伪造一个最小 run_log.json，包含 summary 和 artifacts
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
        tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".json")
        try:
            json.dump(run_log, tmp)
            tmp.flush()
            tmp.close()
            mock_run.return_value = tmp.name

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
                os.unlink(tmp.name)
            except Exception:
                pass

    @patch("src.mcp.server.run_nobel_pipeline", side_effect=RuntimeError("boom"))
    def test_orchestrate_all_pipeline_exception(self, _mock_run):
        result = mcp_server.orchestrate_all({})
        self.assertEqual(result.get("schema_version"), "1.0")
        self.assertEqual(result.get("summary"), {})
        self.assertEqual(result.get("artifacts"), {})
        self.assertIsInstance(result.get("errors"), list)
        self.assertTrue(any(e.get("code") == "E_ORCHESTRATE_FAIL" for e in result["errors"]))

    @patch("src.mcp.server.run_nobel_pipeline")
    def test_orchestrate_all_load_log_fail(self, mock_run):
        # 返回一个不存在的路径，触发 E_LOAD_LOG_FAIL
        mock_run.return_value = "/nonexistent/path/run_log.json"
        result = mcp_server.orchestrate_all({})
        self.assertEqual(result.get("schema_version"), "1.0")
        self.assertEqual(result.get("summary"), {})
        self.assertEqual(result.get("artifacts"), {})
        self.assertTrue(any(e.get("code") == "E_LOAD_LOG_FAIL" for e in result.get("errors", [])))


if __name__ == "__main__":
    unittest.main()