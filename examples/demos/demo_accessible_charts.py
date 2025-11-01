#!/usr/bin/env python3
"""
无障碍友好图表演示
使用真实诺贝尔奖数据展示色彩无障碍功能
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analysis.enhanced_viz import EnhancedVizAgent
from analysis.accessibility_checker import AccessibilityChecker


def create_accessible_nobel_charts():
    """创建无障碍友好的诺贝尔奖图表"""
    print("🎨 创建无障碍友好的诺贝尔奖图表...")
    
    # 加载诺贝尔奖数据
    data_path = "data/nobel/laureates_prizes.csv"
    if not Path(data_path).exists():
        print(f"❌ 数据文件不存在: {data_path}")
        return False
    
    df = pd.read_csv(data_path)
    print(f"📊 加载数据: {len(df)} 条记录")
    
    # 初始化可视化代理
    viz_agent = EnhancedVizAgent("outputs/figures/accessible_figures")
    checker = AccessibilityChecker()
    
    # 1. 创建无障碍友好的分类统计图
    print("\n1. 创建分类统计图（无障碍友好）...")
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    
    # 使用Wong色盲友好调色板
    fig1 = viz_agent.create_interactive_bar_chart(
        category_counts,
        x_col='category',
        y_col='count',
        color_col='category',
        title='诺贝尔奖各类别获奖数量（色盲友好版）',
        use_accessible_colors=True,
        theme='academic'
    )
    
    saved1 = viz_agent.save_chart(fig1, 'accessible_categories', ['html', 'png'])
    print(f"   保存文件: {list(saved1.keys())}")
    
    # 验证颜色无障碍性
    colors_used = viz_agent.get_accessible_colors(len(category_counts), 'wong')
    validation = viz_agent.validate_chart_accessibility(colors_used)
    print(f"   无障碍性验证: {'✅ 通过' if validation['overall_accessible'] else '❌ 需改进'}")
    
    # 2. 创建高对比度主题图表
    print("\n2. 创建高对比度主题图表...")
    fig2 = viz_agent.create_interactive_bar_chart(
        category_counts,
        x_col='category',
        y_col='count',
        color_col='category',
        title='诺贝尔奖各类别获奖数量（高对比度版）',
        use_accessible_colors=True,
        theme='high_contrast'
    )
    
    saved2 = viz_agent.save_chart(fig2, 'high_contrast_categories', ['html', 'png'])
    print(f"   保存文件: {list(saved2.keys())}")
    
    # 3. 创建商务主题图表
    print("\n3. 创建商务主题图表...")
    fig3 = viz_agent.create_interactive_bar_chart(
        category_counts,
        x_col='category',
        y_col='count',
        color_col='category',
        title='诺贝尔奖各类别获奖数量（商务主题）',
        use_accessible_colors=True,
        theme='business'
    )
    
    saved3 = viz_agent.save_chart(fig3, 'business_categories', ['html', 'png'])
    print(f"   保存文件: {list(saved3.keys())}")
    
    # 4. 展示色盲模拟效果
    print("\n4. 色盲模拟分析...")
    wong_colors = checker.get_colorblind_safe_palette('wong', 6)
    print(f"   原始Wong调色板: {wong_colors}")
    
    for cb_type in ['protanopia', 'deuteranopia', 'tritanopia']:
        simulated = [checker.simulate_colorblindness(color, cb_type) for color in wong_colors]
        print(f"   {cb_type}模拟: {simulated}")
    
    # 5. 对比度分析报告
    print("\n5. 对比度分析报告...")
    themes = ['academic', 'business', 'high_contrast']
    
    for theme_name in themes:
        theme_colors = checker.get_theme_colors(theme_name)
        contrast = checker.calculate_contrast_ratio(
            theme_colors['text'], 
            theme_colors['background']
        )
        wcag_result = checker.check_wcag_compliance(
            theme_colors['text'], 
            theme_colors['background']
        )
        
        print(f"   {theme_name} 主题:")
        print(f"     文字/背景对比度: {contrast:.2f}")
        print(f"     WCAG AA合规: {'✅ 通过' if wcag_result['passes'] else '❌ 不通过'}")
    
    return True


def compare_accessibility_palettes():
    """比较不同调色板的无障碍性"""
    print("\n🔍 比较不同调色板的无障碍性...")
    
    checker = AccessibilityChecker()
    
    # 测试不同调色板
    palettes = {
        'wong': '色盲友好（推荐）',
        'viridis': '科学可视化标准',
        'tol_bright': 'Tol明亮调色板',
        'default_plotly': ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
    }
    
    print("\n调色板无障碍性对比:")
    print("-" * 60)
    
    for palette_name, description in palettes.items():
        if palette_name == 'default_plotly':
            colors = description  # 直接使用颜色列表
        else:
            colors = checker.get_colorblind_safe_palette(palette_name, 6)
        
        analysis = checker.analyze_palette_accessibility(colors)
        
        # 计算通过率
        sufficient_contrasts = sum(1 for pair in analysis['pairwise_contrasts'] 
                                 if pair['sufficient_contrast'])
        total_pairs = len(analysis['pairwise_contrasts'])
        pass_rate = (sufficient_contrasts / total_pairs * 100) if total_pairs > 0 else 0
        
        print(f"{palette_name:15} | {str(description):20} | 对比度通过率: {pass_rate:.1f}%")
        if analysis['recommendations']:
            print(f"{'':15} | {'建议:':20} | {analysis['recommendations'][0]}")
        print("-" * 60)


def main():
    """主函数"""
    print("=" * 70)
    print("🎯 无障碍友好图表演示")
    print("=" * 70)
    
    try:
        # 创建无障碍图表
        if create_accessible_nobel_charts():
            print("\n✅ 无障碍图表创建成功")
        else:
            print("\n❌ 无障碍图表创建失败")
            return False
        
        # 比较调色板
        compare_accessibility_palettes()
        
        print("\n" + "=" * 70)
        print("🎉 无障碍功能演示完成！")
        print("\n📁 生成的文件位置: outputs/figures/accessible_figures/")
        print("💡 建议: 在浏览器中打开HTML文件查看交互效果")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)