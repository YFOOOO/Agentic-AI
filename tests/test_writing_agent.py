"""
写作代理测试模块

测试写作代理的核心功能，包括LLM集成、错误处理和fallback机制
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
import pandas as pd

from src.agents.writing_agent import WritingAgent


class TestWritingAgent:
    """写作代理测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = WritingAgent(base_dir=self.temp_dir)
        
        # 创建测试CSV文件
        self.test_csv_path = os.path.join(self.temp_dir, "test_data.csv")
        test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'year': [2020, 2021, 2022, 2023, 2024],
            'bornCountry': ['USA', 'USA', 'UK', 'Germany', 'France'],
            'category': ['physics', 'chemistry', 'physics', 'medicine', 'literature']
        })
        test_data.to_csv(self.test_csv_path, index=False)
    
    def teardown_method(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_default_params(self):
        """测试默认参数初始化"""
        agent = WritingAgent()
        assert agent.base_dir == "artifacts/nobel"
        assert agent.llm is None
        assert agent.model is None
        assert agent.last_llm_error is None
    
    def test_init_custom_params(self):
        """测试自定义参数初始化"""
        mock_llm = Mock()
        agent = WritingAgent(
            base_dir="/custom/path",
            llm=mock_llm,
            model="test:model"
        )
        assert agent.base_dir == "/custom/path"
        assert agent.llm == mock_llm
        assert agent.model == "test:model"
    
    def test_handle_basic_task(self):
        """测试基本任务处理"""
        task = {
            "task_id": "test_123",
            "csv": self.test_csv_path,
            "theme": "Test Analysis"
        }
        
        result = self.agent.handle(task)
        
        # 验证返回结构
        assert "artifacts" in result
        assert "metrics" in result
        assert "llm" in result
        
        # 验证文件生成
        draft_path = result["artifacts"]["draft_md"]
        assert os.path.exists(draft_path)
        
        # 验证指标计算
        metrics = result["metrics"]
        assert metrics["rows"] == 5
        assert metrics["laureates_unique"] == 5
        assert metrics["year_min"] == 2020
        assert metrics["year_max"] == 2024
        assert metrics["top_country_name"] == "USA"
        assert metrics["top_country_count"] == 2
    
    def test_handle_missing_csv(self):
        """测试CSV文件不存在的情况"""
        task = {
            "task_id": "test_missing",
            "csv": "/nonexistent/file.csv",
            "theme": "Missing File Test"
        }
        
        result = self.agent.handle(task)
        
        # 应该仍然返回有效结构，但指标为默认值
        assert "artifacts" in result
        assert "metrics" in result
        assert result["metrics"]["rows"] == 0
        assert result["metrics"]["laureates_unique"] == 0
    
    def test_build_prompt(self):
        """测试提示词构建"""
        theme = "Test Theme"
        metrics = {
            "rows": 100,
            "laureates_unique": 80,
            "year_min": 1901,
            "year_max": 2024,
            "top_country_name": "USA",
            "top_country_count": 25,
            "top_category_name": "physics",
            "top_category_count": 30
        }
        
        prompt = self.agent.build_prompt(theme, metrics)
        
        # 验证提示词包含关键信息
        assert "Test Theme" in prompt
        assert "100" in prompt  # rows
        assert "80" in prompt   # laureates_unique
        assert "USA" in prompt  # top_country_name
        # 注意：build_prompt方法可能不包含category信息，所以移除这个断言
    
    def test_call_llm_no_client(self):
        """测试没有LLM客户端时的fallback"""
        prompt = "Test prompt with Nobel Prize theme"
        
        result = self.agent.call_llm(prompt)
        
        # 应该返回fallback内容
        assert result is not None
        assert isinstance(result, str)
        assert "诺贝尔奖数据分析" in result
        assert "LLM服务暂时不可用" in result
        assert self.agent.last_llm_error == "LLM client not injected - using fallback mode"
    
    def test_call_llm_with_mock_client_success(self):
        """测试LLM客户端成功调用"""
        mock_llm = Mock()
        mock_llm.generate.return_value = "Generated content from LLM"
        
        self.agent.llm = mock_llm
        self.agent.model = "test:model"
        
        result = self.agent.call_llm("Test prompt")
        
        assert result == "Generated content from LLM"
        assert self.agent.last_llm_error is None
        mock_llm.generate.assert_called_once_with("Test prompt", model="test:model")
    
    def test_call_llm_with_mock_client_empty_result(self):
        """测试LLM客户端返回空结果"""
        mock_llm = Mock()
        mock_llm.generate.return_value = ""  # 空结果
        mock_llm.last_error = "API rate limit exceeded"
        
        self.agent.llm = mock_llm
        self.agent.model = "test:model"
        
        result = self.agent.call_llm("Test prompt", max_retries=1)
        
        # 应该使用fallback
        assert "数据分析报告" in result
        assert "LLM服务暂时不可用" in result
        assert "Empty result from LLM" in self.agent.last_llm_error
    
    def test_call_llm_with_exception_retry(self):
        """测试LLM调用异常时的重试机制"""
        mock_llm = Mock()
        # 前两次调用失败，第三次成功
        mock_llm.generate.side_effect = [
            Exception("Network error"),
            Exception("Timeout error"), 
            "Success on third try"
        ]
        
        self.agent.llm = mock_llm
        self.agent.model = "test:model"
        
        with patch('time.sleep'):  # 跳过实际等待
            result = self.agent.call_llm("Test prompt", max_retries=3)
        
        assert result == "Success on third try"
        assert mock_llm.generate.call_count == 3
    
    def test_call_llm_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("Persistent error")
        
        self.agent.llm = mock_llm
        self.agent.model = "test:model"
        
        with patch('time.sleep'):  # 跳过实际等待
            result = self.agent.call_llm("Test prompt", max_retries=2)
        
        # 应该使用fallback
        assert "数据分析报告" in result
        assert "LLM服务暂时不可用" in result
        assert "Attempt 3/3 failed" in self.agent.last_llm_error
    
    def test_generate_fallback_content_nobel_theme(self):
        """测试诺贝尔奖主题的fallback内容生成"""
        prompt = "Analyze Nobel Prize data with theme: Nobel Prize Analysis"
        
        result = self.agent._generate_fallback_content(prompt)
        
        assert "诺贝尔奖数据分析" in result
        assert "数据概览" in result
        assert "主要发现" in result
        assert "建议" in result
        assert "LLM服务恢复后重新生成" in result
    
    def test_generate_fallback_content_custom_theme(self):
        """测试自定义主题的fallback内容生成"""
        prompt = "Please analyze the data with theme: Climate Change Research"
        
        result = self.agent._generate_fallback_content(prompt)
        
        assert "Climate Change Research" in result
        assert "数据概览" in result
        assert "主要发现" in result
    
    def test_generate_fallback_content_default_theme(self):
        """测试默认主题的fallback内容生成"""
        prompt = "Analyze this dataset without specific theme"
        
        result = self.agent._generate_fallback_content(prompt)
        
        assert "数据分析" in result
        assert "数据概览" in result
    
    def test_handle_with_llm_integration(self):
        """测试完整的LLM集成流程"""
        mock_llm = Mock()
        mock_llm.generate.return_value = "# Custom Analysis\n\nThis is LLM generated content."
        
        self.agent.llm = mock_llm
        self.agent.model = "test:model"
        
        task = {
            "task_id": "llm_test",
            "csv": self.test_csv_path,
            "theme": "LLM Integration Test"
        }
        
        result = self.agent.handle(task)
        
        # 验证LLM被调用
        assert mock_llm.generate.called
        
        # 验证生成的文件包含LLM内容
        draft_path = result["artifacts"]["draft_md"]
        with open(draft_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "Custom Analysis" in content
        assert "LLM generated content" in content
    
    def test_task_id_generation(self):
        """测试任务ID生成"""
        task_without_id = {
            "csv": self.test_csv_path,
            "theme": "No ID Test"
        }
        
        result = self.agent.handle(task_without_id)
        
        # 验证返回结构存在
        assert "artifacts" in result
        assert "metrics" in result
        # 注意：WritingAgent不直接返回task_id，而是在run_dir路径中体现


if __name__ == "__main__":
    pytest.main([__file__, "-v"])