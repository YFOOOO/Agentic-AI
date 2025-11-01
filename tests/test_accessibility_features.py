#!/usr/bin/env python3
"""
测试色彩无障碍检查功能
验证无障碍友好的图表生成和颜色方案
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.analysis.accessibility_checker import AccessibilityChecker
from src.analysis.enhanced_viz import EnhancedVizAgent


def test_accessibility_checker():
    """测试无障碍检查器的基本功能"""
    print("🔍 测试无障碍检查器基本功能...")
    
    checker = AccessibilityChecker()
    
    # 1. 测试对比度计算
    print("\n1. 对比度检查测试:")
    test_cases = [
        ('#000000', '#FFFFFF', '黑白对比'),
        ('#FF0000', '#FFFFFF', '红白对比'),
        ('#0072B2', '#FFFFFF', '蓝白对比'),
        ('#FFFF00', '#FFFFFF', '黄白对比（低对比度）')
    ]
    
    for fg, bg, desc in test_cases:
        result = checker.check_wcag_compliance(fg, bg)
        status = "✅ 通过" if result['passes'] else "❌ 不通过"
        print(f"  {desc}: {result['contrast_ratio']:.2f} {status}")
    
    # 2. 测试色盲友好调色板
    print("\n2. 色盲友好调色板测试:")
    palettes = ['wong', 'viridis', 'tol_bright']
    for palette in palettes:
        colors = checker.get_colorblind_safe_palette(palette, 5)
        print(f"  {palette}: {colors[:3]}...")  # 只显示前3个颜色
    
    # 3. 测试色盲模拟
    print("\n3. 色盲模拟测试:")
    test_color = '#FF0000'
    print(f"  原始颜色: {test_color}")
    for cb_type in ['protanopia', 'deuteranopia', 'tritanopia']:
        simulated = checker.simulate_colorblindness(test_color, cb_type)
        print(f"  {cb_type}: {simulated}")
    
    # 4. 测试调色板分析
    print("\n4. 调色板无障碍性分析:")
    test_palette = ['#FF0000', '#00FF00', '#0000FF']
    analysis = checker.analyze_palette_accessibility(test_palette)
    print(f"  测试调色板: {test_palette}")
    print(f"  对比度不足的颜色对: {len([p for p in analysis['pairwise_contrasts'] if not p['sufficient_contrast']])}")
    print(f"  建议数量: {len(analysis['recommendations'])}")
    
    return True


def test_enhanced_viz_accessibility():
    """测试增强可视化代理的无障碍功能"""
    print("\n🎨 测试增强可视化代理无障碍功能...")
    
    # 创建测试数据
    np.random.seed(42)
    test_data = pd.DataFrame({
        'category': ['Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace', 'Economics'],
        'count': np.random.randint(10, 100, 6),
        'year': np.random.choice(range(2000, 2024), 6)
    })
    
    # 初始化增强可视化代理
    viz_agent = EnhancedVizAgent("test_accessibility_figures")
    
    # 1. 测试无障碍颜色获取
    print("\n1. 无障碍颜色获取测试:")
    colors = viz_agent.get_accessible_colors(6, 'wong')
    print(f"  Wong调色板 (6色): {colors}")
    
    # 2. 测试颜色验证
    print("\n2. 颜色无障碍性验证:")
    validation = viz_agent.validate_chart_accessibility(colors)
    print(f"  整体无障碍性: {'✅ 通过' if validation['overall_accessible'] else '❌ 不通过'}")
    print(f"  对比度检查通过率: {sum(1 for r in validation['contrast_results'] if r['passes_wcag'])}/{len(validation['contrast_results'])}")
    
    # 3. 测试无障碍友好图表生成
    print("\n3. 无障碍友好图表生成测试:")
    
    # 创建无障碍友好的柱状图
    fig = viz_agent.create_interactive_bar_chart(
        test_data, 
        x_col='category', 
        y_col='count',
        color_col='category',
        title='Nobel Prize Categories (Accessible)',
        use_accessible_colors=True,
        theme='academic'
    )
    
    # 保存图表
    saved_files = viz_agent.save_chart(fig, 'accessible_bar_chart', ['html', 'png'])
    print(f"  保存的文件: {list(saved_files.keys())}")
    
    # 4. 测试不同主题
    print("\n4. 不同主题测试:")
    themes = ['academic', 'business', 'high_contrast']
    for theme in themes:
        fig_themed = viz_agent.create_interactive_bar_chart(
            test_data, 
            x_col='category', 
            y_col='count',
            title=f'Theme: {theme}',
            use_accessible_colors=True,
            theme=theme
        )
        saved = viz_agent.save_chart(fig_themed, f'theme_{theme}', ['html'])
        print(f"  {theme} 主题: {list(saved.keys())}")
    
    return True


def test_colorblind_simulation():
    """测试色盲模拟功能"""
    print("\n👁️ 测试色盲模拟功能...")
    
    checker = AccessibilityChecker()
    viz_agent = EnhancedVizAgent("test_colorblind_figures")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'],
        'value': [25, 35, 20, 20]
    })
    
    # 测试不同调色板在色盲模拟下的效果
    palettes = ['wong', 'viridis', 'tol_bright']
    colorblind_types = ['protanopia', 'deuteranopia', 'tritanopia']
    
    print("\n色盲模拟结果:")
    for palette in palettes:
        colors = checker.get_colorblind_safe_palette(palette, 4)
        print(f"\n  {palette} 调色板:")
        print(f"    原始: {colors}")
        
        for cb_type in colorblind_types:
            simulated = [checker.simulate_colorblindness(color, cb_type) for color in colors]
            print(f"    {cb_type}: {simulated}")
    
    return True


def test_performance():
    """测试无障碍功能的性能"""
    print("\n⚡ 测试无障碍功能性能...")
    
    import time
    
    checker = AccessibilityChecker()
    
    # 测试大量颜色的处理性能
    start_time = time.time()
    
    # 生成100个随机颜色并检查无障碍性
    colors = []
    for i in range(100):
        r, g, b = np.random.randint(0, 256, 3)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append(hex_color)
    
    # 分析调色板
    analysis = checker.analyze_palette_accessibility(colors[:10])  # 只分析前10个以节省时间
    
    end_time = time.time()
    
    print(f"  处理100个颜色用时: {end_time - start_time:.3f}秒")
    print(f"  分析结果: {len(analysis['pairwise_contrasts'])} 个颜色对")
    
    return True


def cleanup_test_files():
    """清理测试文件"""
    print("\n🧹 清理测试文件...")
    
    test_dirs = ['test_accessibility_figures', 'test_colorblind_figures']
    
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            import shutil
            shutil.rmtree(test_dir)
            print(f"  已删除: {test_dir}")


def main():
    """主测试函数"""
    print("=" * 60)
    print("🎯 色彩无障碍检查功能测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        tests = [
            test_accessibility_checker,
            test_enhanced_viz_accessibility,
            test_colorblind_simulation,
            test_performance
        ]
        
        passed_tests = 0
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_func.__name__} 通过")
                else:
                    print(f"❌ {test_func.__name__} 失败")
            except Exception as e:
                print(f"❌ {test_func.__name__} 出错: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {passed_tests}/{len(tests)} 通过")
        
        if passed_tests == len(tests):
            print("🎉 所有无障碍功能测试通过！")
            return True
        else:
            print("⚠️ 部分测试失败，请检查实现")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False
    
    finally:
        # 清理测试文件
        cleanup_test_files()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)