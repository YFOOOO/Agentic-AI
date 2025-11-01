"""
带图说的图表演示程序
展示自动图说生成功能在实际图表中的应用
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.analysis.enhanced_viz import EnhancedVizAgent


def create_demo_charts():
    """创建演示图表"""
    print("=== 创建带图说的演示图表 ===\n")
    
    # 创建输出目录
    output_dir = Path("outputs/figures/caption_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化增强可视化代理
    viz_agent = EnhancedVizAgent()
    
    # 1. 诺贝尔奖各类别分布（中文图说）
    print("1. 创建诺贝尔奖各类别分布图（中文图说）...")
    nobel_data = pd.DataFrame({
        'category': ['物理学', '化学', '生理学或医学', '文学', '和平奖', '经济学'],
        'count': [224, 189, 225, 118, 140, 93],
        'description': ['研究物质和能量', '研究物质组成', '研究生命科学', '文学创作', '促进世界和平', '经济学研究']
    })
    
    fig1 = viz_agent.create_interactive_bar_chart(
        df=nobel_data,
        x_col='category',
        y_col='count',
        title='诺贝尔奖各类别获奖人数分布（1901-2023）',
        auto_caption=True,
        caption_style='academic',
        theme='academic'
    )
    
    # 保存图表
    fig1.write_html(str(output_dir / "nobel_categories_zh.html"))
    fig1.write_image(str(output_dir / "nobel_categories_zh.png"), width=1000, height=600)
    print("✓ 中文图说图表已保存")
    
    # 2. 年度趋势图（英文图说）
    print("\n2. 创建年度趋势图（英文图说）...")
    viz_agent.set_caption_language('en')
    
    # 创建年度数据
    years = list(range(2010, 2024))
    annual_data = pd.DataFrame({
        'year': years,
        'awards': [12, 11, 13, 14, 12, 15, 13, 14, 16, 15, 12, 10, 14, 13],
        'category': ['Total'] * len(years)
    })
    
    # 创建折线图（使用柱状图模拟，因为我们主要有柱状图方法）
    fig2 = viz_agent.create_interactive_bar_chart(
        df=annual_data,
        x_col='year',
        y_col='awards',
        title='Nobel Prize Awards by Year (2010-2023)',
        auto_caption=True,
        caption_style='standard',
        theme='business'
    )
    
    # 保存图表
    fig2.write_html(str(output_dir / "nobel_annual_en.html"))
    fig2.write_image(str(output_dir / "nobel_annual_en.png"), width=1000, height=600)
    print("✓ 英文图说图表已保存")
    
    # 3. 不同风格的图说对比
    print("\n3. 创建不同风格图说对比...")
    viz_agent.set_caption_language('zh')
    
    # 创建简单数据用于对比
    comparison_data = pd.DataFrame({
        'region': ['欧洲', '北美', '亚洲', '其他'],
        'count': [156, 89, 45, 23]
    })
    
    styles = [
        ('standard', '标准风格'),
        ('academic', '学术风格'),
        ('brief', '简洁风格')
    ]
    
    for style, style_name in styles:
        print(f"  创建{style_name}图说...")
        
        fig = viz_agent.create_interactive_bar_chart(
            df=comparison_data,
            x_col='region',
            y_col='count',
            title=f'诺贝尔奖获奖者地区分布 - {style_name}',
            auto_caption=True,
            caption_style=style,
            theme='high_contrast' if style == 'academic' else 'academic'
        )
        
        # 保存图表
        fig.write_html(str(output_dir / f"nobel_regions_{style}.html"))
        fig.write_image(str(output_dir / f"nobel_regions_{style}.png"), width=1000, height=600)
        print(f"✓ {style_name}图表已保存")
    
    # 4. 展示图说内容
    print("\n4. 图说内容展示:")
    
    # 生成不同风格的图说进行对比
    for style, style_name in styles:
        caption = viz_agent.generate_chart_caption(
            df=comparison_data,
            chart_type='bar_chart',
            title='诺贝尔奖获奖者地区分布',
            value_col='count',
            category_col='region',
            style=style
        )
        print(f"  {style_name}: {caption}")
    
    print(f"\n✅ 所有演示图表已保存到: {output_dir}")
    
    # 列出生成的文件
    print("\n📁 生成的文件:")
    for file in sorted(output_dir.glob("*")):
        print(f"  - {file.name}")


def demonstrate_multilingual_captions():
    """演示多语言图说功能"""
    print("\n=== 多语言图说演示 ===")
    
    # 创建测试数据
    data = pd.DataFrame({
        'field': ['AI', 'Robotics', 'Quantum', 'Biotech', 'Space'],
        'investment': [1200, 800, 600, 900, 400]  # 单位：百万美元
    })
    
    viz_agent = EnhancedVizAgent()
    
    # 中文图说
    viz_agent.set_caption_language('zh')
    caption_zh = viz_agent.generate_chart_caption(
        df=data,
        chart_type='bar_chart',
        title='科技领域投资分布',
        value_col='investment',
        category_col='field',
        style='standard'
    )
    
    # 英文图说
    viz_agent.set_caption_language('en')
    caption_en = viz_agent.generate_chart_caption(
        df=data,
        chart_type='bar_chart',
        title='Technology Investment Distribution',
        value_col='investment',
        category_col='field',
        style='standard'
    )
    
    print("中文图说:")
    print(f"  {caption_zh}")
    print("\n英文图说:")
    print(f"  {caption_en}")
    
    print("\n✅ 多语言图说演示完成")


def analyze_caption_features():
    """分析图说功能特性"""
    print("\n=== 图说功能特性分析 ===")
    
    # 创建包含异常值的数据
    np.random.seed(42)
    data_with_outliers = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'],
        'value': [100, 95, 105, 300, 98]  # C是异常值
    })
    
    viz_agent = EnhancedVizAgent()
    viz_agent.set_caption_language('zh')
    
    # 生成包含异常值分析的图说
    caption = viz_agent.generate_chart_caption(
        df=data_with_outliers,
        chart_type='bar_chart',
        title='包含异常值的数据分布',
        value_col='value',
        category_col='category',
        style='academic'
    )
    
    print("异常值检测图说:")
    print(f"  {caption}")
    
    # 创建趋势数据
    trend_data = pd.DataFrame({
        'month': range(1, 13),
        'sales': [100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320]
    })
    
    # 生成趋势分析图说
    caption_trend = viz_agent.generate_chart_caption(
        df=trend_data,
        chart_type='line_chart',
        title='月度销售趋势',
        value_col='sales',
        time_col='month',
        style='standard'
    )
    
    print("\n趋势分析图说:")
    print(f"  {caption_trend}")
    
    print("\n✅ 图说功能特性分析完成")


def main():
    """主函数"""
    print("🎯 开始图说自动生成演示...\n")
    
    try:
        create_demo_charts()
        demonstrate_multilingual_captions()
        analyze_caption_features()
        
        print("\n🎉 图说自动生成演示完成！")
        print("\n📊 功能特点总结:")
        print("  ✓ 支持中英文双语图说生成")
        print("  ✓ 提供标准、学术、简洁三种风格")
        print("  ✓ 自动统计分析和异常值检测")
        print("  ✓ 智能趋势识别和描述")
        print("  ✓ 与可视化图表无缝集成")
        print("  ✓ 支持多种图表类型")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        raise


if __name__ == "__main__":
    main()