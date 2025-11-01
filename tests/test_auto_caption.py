"""
图说自动生成功能测试
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.analysis.auto_caption import AutoCaptionGenerator
from src.analysis.enhanced_viz import EnhancedVizAgent


def test_auto_caption_basic():
    """测试基础图说生成功能"""
    print("=== 测试基础图说生成功能 ===")
    
    # 创建测试数据
    np.random.seed(42)
    test_data = pd.DataFrame({
        'category': ['Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace', 'Economics'],
        'count': [45, 38, 52, 23, 31, 28],
        'year': [2020, 2021, 2022, 2023, 2024, 2025]
    })
    
    # 测试中文图说生成
    caption_gen_zh = AutoCaptionGenerator(language='zh')
    
    caption_zh = caption_gen_zh.generate_caption(
        df=test_data,
        chart_type='bar_chart',
        title='诺贝尔奖各类别获奖数量',
        value_col='count',
        category_col='category',
        style='standard'
    )
    
    print(f"✓ 中文柱状图说: {caption_zh}")
    assert len(caption_zh) > 0, "中文图说生成失败"
    
    # 测试英文图说生成
    caption_gen_en = AutoCaptionGenerator(language='en')
    
    caption_en = caption_gen_en.generate_caption(
        df=test_data,
        chart_type='bar_chart',
        title='Nobel Prize Categories',
        value_col='count',
        category_col='category',
        style='standard'
    )
    
    print(f"✓ 英文柱状图说: {caption_en}")
    assert len(caption_en) > 0, "英文图说生成失败"
    
    print("✓ 基础图说生成功能测试通过\n")


def test_statistical_analysis():
    """测试统计分析功能"""
    print("=== 测试统计分析功能 ===")
    
    # 创建测试数据
    np.random.seed(42)
    test_data = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'] * 20,
        'value': np.random.normal(100, 20, 100)
    })
    
    caption_gen = AutoCaptionGenerator(language='zh')
    
    # 测试统计分析
    stats = caption_gen.analyze_data_statistics(test_data, 'value', 'category')
    
    print(f"✓ 数据总数: {stats['count']}")
    print(f"✓ 平均值: {stats['mean']:.2f}")
    print(f"✓ 标准差: {stats['std']:.2f}")
    print(f"✓ 最高类别: {stats['top_category']}")
    print(f"✓ 异常值数量: {stats['outliers_count']}")
    
    assert stats['count'] == 100, "数据计数错误"
    assert 'top_category' in stats, "缺少最高类别信息"
    assert 'outliers_count' in stats, "缺少异常值信息"
    
    print("✓ 统计分析功能测试通过\n")


def test_trend_detection():
    """测试趋势检测功能"""
    print("=== 测试趋势检测功能 ===")
    
    # 创建上升趋势数据
    dates = pd.date_range('2020-01-01', periods=12, freq='M')
    trend_data = pd.DataFrame({
        'date': dates,
        'value': np.arange(12) * 2 + np.random.normal(0, 1, 12)
    })
    
    caption_gen = AutoCaptionGenerator(language='zh')
    
    # 测试趋势检测
    trends = caption_gen.detect_trends(trend_data, 'value', 'date')
    
    print(f"✓ 趋势方向: {trends.get('direction', 'unknown')}")
    print(f"✓ 变化幅度: {trends.get('change_percentage', 0):.1f}%")
    print(f"✓ 峰值数量: {len(trends.get('peaks', []))}")
    print(f"✓ 谷值数量: {len(trends.get('valleys', []))}")
    
    assert 'direction' in trends, "缺少趋势方向信息"
    assert trends['direction'] in ['increasing', 'decreasing', 'stable'], "趋势方向值错误"
    
    print("✓ 趋势检测功能测试通过\n")


def test_enhanced_viz_integration():
    """测试与EnhancedVizAgent的集成"""
    print("=== 测试与EnhancedVizAgent的集成 ===")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'category': ['Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace'],
        'count': [45, 38, 52, 23, 31]
    })
    
    # 初始化增强可视化代理
    viz_agent = EnhancedVizAgent()
    
    # 测试图说生成
    caption = viz_agent.generate_chart_caption(
        df=test_data,
        chart_type='bar_chart',
        title='诺贝尔奖分布',
        value_col='count',
        category_col='category'
    )
    
    print(f"✓ 集成图说生成: {caption}")
    assert len(caption) > 0, "集成图说生成失败"
    
    # 测试语言切换
    viz_agent.set_caption_language('en')
    caption_en = viz_agent.generate_chart_caption(
        df=test_data,
        chart_type='bar_chart',
        title='Nobel Prize Distribution',
        value_col='count',
        category_col='category'
    )
    
    print(f"✓ 英文图说生成: {caption_en}")
    assert len(caption_en) > 0, "英文图说生成失败"
    
    print("✓ EnhancedVizAgent集成测试通过\n")


def test_chart_with_caption():
    """测试带图说的图表生成"""
    print("=== 测试带图说的图表生成 ===")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'category': ['Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace'],
        'count': [45, 38, 52, 23, 31]
    })
    
    # 初始化增强可视化代理
    viz_agent = EnhancedVizAgent()
    
    # 创建带图说的柱状图
    fig = viz_agent.create_interactive_bar_chart(
        df=test_data,
        x_col='category',
        y_col='count',
        title='诺贝尔奖各类别分布',
        auto_caption=True,
        caption_style='standard'
    )
    
    print("✓ 带图说的柱状图创建成功")
    
    # 检查图表是否包含注释（图说）
    annotations = fig.layout.annotations
    has_caption = any(ann.text and len(ann.text) > 20 for ann in annotations) if annotations else False
    
    assert has_caption, "图表缺少图说注释"
    print("✓ 图表包含图说注释")
    
    # 保存图表进行验证
    output_dir = Path("artifacts/nobel/caption_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存HTML格式
    html_path = output_dir / "bar_chart_with_caption.html"
    fig.write_html(str(html_path))
    print(f"✓ 图表已保存: {html_path}")
    
    print("✓ 带图说的图表生成测试通过\n")


def test_multiple_styles():
    """测试多种图说风格"""
    print("=== 测试多种图说风格 ===")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'],
        'value': [100, 85, 120, 65, 95]
    })
    
    caption_gen = AutoCaptionGenerator(language='zh')
    
    styles = ['standard', 'academic', 'brief']
    
    for style in styles:
        caption = caption_gen.generate_caption(
            df=test_data,
            chart_type='bar_chart',
            title='测试数据',
            value_col='value',
            category_col='category',
            style=style
        )
        
        print(f"✓ {style}风格图说: {caption}")
        assert len(caption) > 0, f"{style}风格图说生成失败"
    
    print("✓ 多种图说风格测试通过\n")


def cleanup_test_files():
    """清理测试文件"""
    print("=== 清理测试文件 ===")
    
    test_dir = Path("artifacts/nobel/caption_test")
    if test_dir.exists():
        for file in test_dir.glob("*"):
            if file.is_file():
                file.unlink()
        print("✓ 测试文件清理完成")


def main():
    """运行所有测试"""
    print("开始图说自动生成功能测试...\n")
    
    try:
        test_auto_caption_basic()
        test_statistical_analysis()
        test_trend_detection()
        test_enhanced_viz_integration()
        test_chart_with_caption()
        test_multiple_styles()
        
        print("🎉 所有图说自动生成功能测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise
    
    finally:
        cleanup_test_files()


if __name__ == "__main__":
    main()