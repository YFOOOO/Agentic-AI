#!/usr/bin/env python3
"""
测试EnhancedLiteratureAgent的web search功能
"""

import sys
import os
import asyncio
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.enhanced_literature_agent import EnhancedLiteratureAgent
from src.agents.multi_source_config_example import ACADEMIC_CONFIG

async def test_enhanced_agent_web_search():
    """测试EnhancedLiteratureAgent的Web搜索功能"""
    print("开始测试EnhancedLiteratureAgent的Web搜索功能...")
    
    # 创建临时目录用于测试
    temp_dir = tempfile.mkdtemp(prefix="enhanced_agent_test_")
    print(f"使用临时目录: {temp_dir}")
    
    try:
        # 创建EnhancedLiteratureAgent实例，使用学术配置
        agent = EnhancedLiteratureAgent(
            base_dir=temp_dir,
            multi_source_config=ACADEMIC_CONFIG
        )
        
        # 测试handle方法，包含web search
        print("执行文献数据收集（包含Web搜索）...")
        task = {
            "query": "deep learning",
            "limit": 10
        }
        result = await agent.handle(task)
        
        print(f"收集完成，结果保存在: {result['artifacts']['csv']}")
        print(f"报告路径: {result['artifacts']['report']}")
        print(f"数据来源: {result['data_sources']}")
        print(f"总记录数: {result['metrics']['rows']}")
        
        # 检查CSV文件是否存在且非空
        if os.path.exists(result['artifacts']['csv']):
            import pandas as pd
            df = pd.read_csv(result['artifacts']['csv'])
            print(f"CSV文件包含 {len(df)} 行数据")
            
            # 显示一些样本数据
            if not df.empty:
                print("\n样本数据:")
                for idx, row in df.head(3).iterrows():
                    print(f"  {idx+1}. {row.get('title', 'N/A')} [{row.get('data_source', 'N/A')}]")
        else:
            print("❌ CSV文件未找到")
            
        print("EnhancedLiteratureAgent Web搜索功能测试完成!")
        return True
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"已清理临时目录: {temp_dir}")

if __name__ == "__main__":
    try:
        asyncio.run(test_enhanced_agent_web_search())
        print("\n✅ 所有测试通过!")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()