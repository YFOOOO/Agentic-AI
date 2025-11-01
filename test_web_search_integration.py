#!/usr/bin/env python3
"""
测试web search功能集成
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.integrations.web_search import WebSearchSource
from src.integrations import SearchResult

async def test_web_search():
    """测试Web搜索功能"""
    print("开始测试Web搜索功能...")
    
    # 创建Web搜索源实例
    config = {
        "timeout": 30,
        "max_retries": 3,
        "engines": ["semantic_scholar", "arxiv"]
    }
    
    web_search = WebSearchSource(config)
    
    # 验证配置
    print("验证配置...")
    assert web_search.validate_config(), "配置验证失败"
    print("✓ 配置验证通过")
    
    # 测试健康检查
    print("执行健康检查...")
    health_status = await web_search.health_check()
    print(f"✓ 健康检查状态: {health_status}")
    
    # 测试搜索功能
    print("执行搜索测试...")
    query = "machine learning"
    results = await web_search.search(query, limit=5)
    
    print(f"搜索 '{query}' 得到 {len(results)} 条结果:")
    for i, result in enumerate(results[:3]):  # 显示前3条结果
        print(f"  {i+1}. {result.title} ({result.source})")
        print(f"     作者: {', '.join(result.authors[:3])}")
        print(f"     摘要: {result.abstract[:100]}..." if result.abstract else "     摘要: N/A")
        print(f"     URL: {result.url}")
        print()
    
    # 测试根据ID获取详情
    if results:
        print("测试根据ID获取详情...")
        first_result = results[0]
        if hasattr(first_result, 'metadata') and first_result.metadata:
            if 'arxiv_id' in first_result.metadata:
                detail_result = await web_search.get_by_id(first_result.metadata['arxiv_id'])
                if detail_result:
                    print(f"✓ 成功获取arXiv ID {first_result.metadata['arxiv_id']} 的详情")
                else:
                    print(f"⚠ 未能获取arXiv ID {first_result.metadata['arxiv_id']} 的详情")
            elif 'doi' in first_result.metadata and first_result.metadata['doi']:
                detail_result = await web_search.get_by_id(first_result.metadata['doi'])
                if detail_result:
                    print(f"✓ 成功获取DOI {first_result.metadata['doi']} 的详情")
                else:
                    print(f"⚠ 未能获取DOI {first_result.metadata['doi']} 的详情")
    
    print("Web搜索功能测试完成!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_web_search())
        print("\n✅ 所有测试通过!")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()