"""
测试多源数据集成功能

验证EnhancedLiteratureAgent与MultiSourceManager的集成，
确保能够正确地从多个数据源收集和合并数据。
"""

import os
import sys
import asyncio
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, '/Users/yf/Documents/Github_repository/Agentic-AI')

from src.agents.enhanced_literature_agent import EnhancedLiteratureAgent
from src.agents.multi_source_config_example import ACADEMIC_CONFIG


def test_multi_source_integration():
    """测试多源数据集成功能"""
    print("=== 多源数据集成功能测试 ===")
    
    # 创建测试输出目录
    test_output_dir = "test_output/multi_source"
    os.makedirs(test_output_dir, exist_ok=True)
    
    # 初始化增强版文献代理，使用学术配置
    agent = EnhancedLiteratureAgent(
        base_dir=test_output_dir,
        multi_source_config=ACADEMIC_CONFIG
    )
    
    # 定义测试任务
    task = {
        "task_id": "multi_source_test_001",
        "query": "machine learning",
        "limit": 30
    }
    
    # 执行任务
    print(f"开始执行任务: {task['task_id']}")
    print(f"搜索查询: {task['query']}")
    
    try:
        # 运行异步任务
        result = asyncio.run(agent.handle(task))
        
        # 验证结果
        print("\n任务执行完成，验证结果...")
        
        # 检查返回结果结构
        assert "type" in result, "结果缺少type字段"
        assert result["type"] == "literature_collect", f"结果类型错误: {result['type']}"
        
        assert "task_id" in result, "结果缺少task_id字段"
        assert result["task_id"] == task["task_id"], f"任务ID不匹配: {result['task_id']}"
        
        # 检查artifacts
        assert "artifacts" in result, "结果缺少artifacts字段"
        artifacts = result["artifacts"]
        
        assert "csv" in artifacts, "artifacts缺少csv字段"
        assert "report" in artifacts, "artifacts缺少report字段"
        assert "run_dir" in artifacts, "artifacts缺少run_dir字段"
        
        # 检查文件是否存在
        assert os.path.exists(artifacts["csv"]), f"CSV文件不存在: {artifacts['csv']}"
        assert os.path.exists(artifacts["report"]), f"报告文件不存在: {artifacts['report']}"
        
        # 检查metrics
        assert "metrics" in result, "结果缺少metrics字段"
        metrics = result["metrics"]
        
        assert "rows" in metrics, "metrics缺少rows字段"
        assert "data_sources" in metrics, "metrics缺少data_sources字段"
        
        # 检查使用的数据源
        data_sources = result["data_sources"]
        assert "nobel_prize" in data_sources, "应包含nobel_prize数据源"
        assert len(data_sources) >= 2, f"应至少使用2个数据源，实际使用: {data_sources}"
        
        # 检查CSV文件内容
        df = pd.read_csv(artifacts["csv"])
        assert len(df) == metrics["rows"], f"CSV行数与metrics不匹配: {len(df)} vs {metrics['rows']}"
        
        # 检查数据源列
        assert "data_source" in df.columns, "CSV缺少data_source列"
        csv_sources = df["data_source"].unique().tolist()
        for source in data_sources:
            assert source in csv_sources, f"CSV中缺少数据源: {source}"
        
        print(f"\n✅ 测试通过!")
        print(f"   - 总记录数: {metrics['rows']}")
        print(f"   - 使用数据源: {', '.join(data_sources)}")
        print(f"   - CSV文件: {artifacts['csv']}")
        print(f"   - 报告文件: {artifacts['report']}")
        
        # 显示部分数据
        print("\n数据源分布:")
        if "source_distribution" in metrics:
            for source, count in metrics["source_distribution"].items():
                print(f"   - {source}: {count} 条记录")
        
        print("\n前5条记录预览:")
        print(df.head()[['title', 'data_source']].to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n=== 向后兼容性测试 ===")
    
    # 创建测试输出目录
    test_output_dir = "test_output/compatibility"
    os.makedirs(test_output_dir, exist_ok=True)
    
    # 使用别名初始化（不启用多源数据）
    from src.agents.enhanced_literature_agent import LiteratureAgent
    agent = LiteratureAgent(base_dir=test_output_dir)
    
    # 定义简单任务（无查询）
    task = {
        "task_id": "compatibility_test_001"
    }
    
    try:
        # 运行异步任务
        result = asyncio.run(agent.handle(task))
        
        # 验证结果
        assert "type" in result, "结果缺少type字段"
        assert result["type"] == "literature_collect", f"结果类型错误: {result['type']}"
        
        # 检查数据源
        data_sources = result["data_sources"]
        assert data_sources == ["nobel_prize"], f"向后兼容性测试失败，应只包含nobel_prize数据源: {data_sources}"
        
        print(f"✅ 向后兼容性测试通过!")
        print(f"   - 使用数据源: {', '.join(data_sources)}")
        print(f"   - 总记录数: {result['metrics']['rows']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 向后兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("开始多源数据集成功能测试...")
    
    # 测试多源数据集成
    success1 = test_multi_source_integration()
    
    # 测试向后兼容性
    success2 = test_backward_compatibility()
    
    if success1 and success2:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print("\n💥 部分测试失败!")
        return 1


if __name__ == "__main__":
    exit(main())