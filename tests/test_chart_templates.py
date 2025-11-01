"""
测试专业图表模板库功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import pandas as pd
from src.analysis.chart_templates import ChartTemplateLibrary
from src.analysis.enhanced_viz import EnhancedVizAgent


def test_template_library_basic():
    """测试模板库基本功能"""
    print("=== 测试模板库基本功能 ===")
    
    # 初始化模板库
    template_lib = ChartTemplateLibrary()
    
    # 测试模板列表
    templates = template_lib.list_templates()
    print(f"✓ 可用模板数量: {len(templates)}")
    for name, desc in templates.items():
        print(f"  - {name}: {desc}")
    
    # 测试配色方案
    palettes = template_lib.list_color_palettes()
    print(f"\n✓ 可用配色方案数量: {len(palettes)}")
    for name, colors in palettes.items():
        print(f"  - {name}: {len(colors)} 种颜色")
    
    # 测试获取特定模板
    academic_template = template_lib.get_template('academic')
    print(f"\n✓ 学术模板配置: {academic_template['name']}")
    print(f"  字体: {academic_template['font_family']}")
    print(f"  配色: {academic_template['color_palette']}")
    
    # 测试获取配色方案
    academic_colors = template_lib.get_color_palette('academic_blue')
    print(f"\n✓ 学术蓝配色方案: {academic_colors[:3]}... (共{len(academic_colors)}种)")
    
    print("✓ 模板库基本功能测试通过\n")


def test_template_preview():
    """测试模板预览功能"""
    print("=== 测试模板预览功能 ===")
    
    template_lib = ChartTemplateLibrary()
    
    # 测试几个主要模板的预览
    test_templates = ['academic', 'business', 'presentation', 'dark']
    
    for template_name in test_templates:
        try:
            fig = template_lib.create_template_preview(template_name)
            print(f"✓ {template_name} 模板预览创建成功")
            
            # 验证图表属性
            assert fig.layout.title.text is not None
            assert len(fig.data) > 0
            
        except Exception as e:
            print(f"✗ {template_name} 模板预览创建失败: {e}")
            return False
    
    print("✓ 模板预览功能测试通过\n")
    return True


def test_enhanced_viz_integration():
    """测试与EnhancedVizAgent的集成"""
    print("=== 测试与EnhancedVizAgent集成 ===")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'Category': ['产品A', '产品B', '产品C', '产品D', '产品E'],
        'Sales': [120, 95, 180, 75, 160],
        'Region': ['北区', '南区', '东区', '西区', '中区']
    })
    
    # 初始化增强可视化代理
    viz_agent = EnhancedVizAgent(output_dir="artifacts/template_test")
    
    # 测试模板列表功能
    templates = viz_agent.list_available_templates()
    print(f"✓ 集成模板数量: {len(templates)}")
    
    # 测试获取模板颜色
    business_colors = viz_agent.get_template_colors('business')
    print(f"✓ 商业模板颜色: {business_colors[:3]}...")
    
    # 测试模板预览
    preview_fig = viz_agent.create_template_preview('presentation')
    print("✓ 演示模板预览创建成功")
    
    # 测试创建带模板的图表
    chart_with_template = viz_agent.create_interactive_bar_chart(
        df=test_data,
        x_col='Category',
        y_col='Sales',
        title='产品销售数据 - 商业模板',
        template='business',
        auto_caption=True,
        caption_style='academic'
    )
    print("✓ 带商业模板的柱状图创建成功")
    
    # 验证图表属性
    assert chart_with_template.layout.title.text is not None
    assert len(chart_with_template.data) > 0
    
    print("✓ EnhancedVizAgent集成测试通过\n")
    return True


def test_template_application():
    """测试模板应用功能"""
    print("=== 测试模板应用功能 ===")
    
    import plotly.express as px
    
    # 创建基础图表
    test_data = pd.DataFrame({
        'x': ['A', 'B', 'C', 'D'],
        'y': [1, 3, 2, 4]
    })
    
    base_fig = px.bar(test_data, x='x', y='y', title='基础图表')
    
    # 初始化模板库
    template_lib = ChartTemplateLibrary()
    
    # 测试不同模板的应用
    test_templates = ['academic', 'business', 'minimal', 'dark']
    
    for template_name in test_templates:
        try:
            # 应用模板
            styled_fig = template_lib.apply_template_to_figure(
                base_fig, 
                template_name, 
                title=f'{template_name.title()} 风格图表'
            )
            
            print(f"✓ {template_name} 模板应用成功")
            
            # 验证模板应用效果
            template_config = template_lib.get_template(template_name)
            
            # 检查标题
            assert styled_fig.layout.title.text is not None
            
            # 检查字体
            assert styled_fig.layout.font.family == template_config['font_family']
            
            # 检查背景色
            assert styled_fig.layout.plot_bgcolor == template_config['background_color']
            
        except Exception as e:
            print(f"✗ {template_name} 模板应用失败: {e}")
            return False
    
    print("✓ 模板应用功能测试通过\n")
    return True


def test_custom_colors():
    """测试自定义颜色功能"""
    print("=== 测试自定义颜色功能 ===")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'Category': ['A', 'B', 'C'],
        'Value': [10, 20, 15],
        'Group': ['G1', 'G2', 'G1']
    })
    
    # 自定义颜色
    custom_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    viz_agent = EnhancedVizAgent()
    
    # 创建带自定义颜色的图表
    fig = viz_agent.create_interactive_bar_chart(
        df=test_data,
        x_col='Category',
        y_col='Value',
        color_col='Group',
        title='自定义颜色测试',
        template='presentation',
        custom_colors=custom_colors
    )
    
    print("✓ 自定义颜色图表创建成功")
    
    # 验证颜色应用
    assert len(fig.data) > 0
    
    print("✓ 自定义颜色功能测试通过\n")
    return True


def run_all_tests():
    """运行所有测试"""
    print("开始专业图表模板库测试...\n")
    
    tests = [
        test_template_library_basic,
        test_template_preview,
        test_enhanced_viz_integration,
        test_template_application,
        test_custom_colors
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            result = test_func()
            if result is not False:
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test_func.__name__} 失败: {e}\n")
    
    print(f"=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！专业图表模板库功能正常")
    else:
        print("⚠️  部分测试失败，请检查相关功能")
    
    return passed == total


if __name__ == "__main__":
    run_all_tests()