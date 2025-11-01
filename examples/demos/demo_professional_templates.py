"""
专业图表模板演示
展示不同模板的视觉效果和应用场景
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from pathlib import Path
from src.analysis.enhanced_viz import EnhancedVizAgent
from src.analysis.chart_templates import ChartTemplateLibrary


def create_sample_data():
    """创建演示数据"""
    # 诺贝尔奖数据样本
    nobel_data = pd.DataFrame({
        'Category': ['物理学', '化学', '生理学或医学', '文学', '和平奖', '经济学'],
        'Awards': [225, 189, 224, 118, 104, 89],
        'Region': ['欧洲', '北美', '欧洲', '欧洲', '全球', '北美']
    })
    
    # 年度趋势数据
    trend_data = pd.DataFrame({
        'Year': list(range(2015, 2024)),
        'Publications': [1200, 1350, 1480, 1620, 1750, 1890, 2020, 2180, 2350],
        'Citations': [15000, 17200, 19800, 22500, 25800, 29200, 32800, 36500, 40200]
    })
    
    return nobel_data, trend_data


def demo_all_templates():
    """演示所有专业模板"""
    print("=== 专业图表模板演示 ===\n")
    
    # 创建输出目录
    output_dir = Path("outputs/figures/professional_templates")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化组件
    viz_agent = EnhancedVizAgent(output_dir=str(output_dir))
    template_lib = ChartTemplateLibrary()
    
    # 获取演示数据
    nobel_data, trend_data = create_sample_data()
    
    # 获取所有模板
    templates = template_lib.list_templates()
    
    print("1. 创建各种专业模板的柱状图:")
    
    # 为每个模板创建图表
    for template_name, description in templates.items():
        print(f"  正在创建 {template_name} 模板图表...")
        
        try:
            # 创建柱状图
            fig = viz_agent.create_interactive_bar_chart(
                df=nobel_data,
                x_col='Category',
                y_col='Awards',
                title=f'诺贝尔奖各类别获奖数量 - {description}',
                template=template_name,
                auto_caption=True,
                caption_style='standard',
                caption_language='zh'
            )
            
            # 保存图表
            filename = f"nobel_awards_{template_name}"
            saved_files = viz_agent.save_chart(fig, filename, formats=['html', 'png'])
            
            print(f"    ✓ {template_name} 模板图表已保存: {list(saved_files.keys())}")
            
        except Exception as e:
            print(f"    ✗ {template_name} 模板创建失败: {e}")
    
    print("\n2. 创建模板预览图:")
    
    # 创建模板预览
    preview_templates = ['academic', 'business', 'presentation', 'dark']
    for template_name in preview_templates:
        try:
            preview_fig = template_lib.create_template_preview(template_name)
            filename = f"template_preview_{template_name}"
            saved_files = viz_agent.save_chart(preview_fig, filename, formats=['html'])
            print(f"  ✓ {template_name} 预览图已保存")
        except Exception as e:
            print(f"  ✗ {template_name} 预览图创建失败: {e}")
    
    print("\n3. 创建对比展示:")
    
    # 创建同一数据的不同模板对比
    comparison_templates = ['academic', 'business', 'presentation', 'minimal']
    
    for i, template_name in enumerate(comparison_templates):
        try:
            fig = viz_agent.create_interactive_bar_chart(
                df=nobel_data.head(4),  # 只显示前4个类别
                x_col='Category',
                y_col='Awards',
                title=f'模板对比 - {template_name.title()} 风格',
                template=template_name,
                auto_caption=False  # 关闭自动图说以便对比
            )
            
            filename = f"comparison_{i+1}_{template_name}"
            viz_agent.save_chart(fig, filename, formats=['html'])
            print(f"  ✓ 对比图 {i+1} ({template_name}) 已保存")
            
        except Exception as e:
            print(f"  ✗ 对比图 {template_name} 创建失败: {e}")
    
    return output_dir


def demo_template_features():
    """演示模板特色功能"""
    print("\n=== 模板特色功能演示 ===\n")
    
    output_dir = Path("outputs/figures/template_features")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    viz_agent = EnhancedVizAgent(output_dir=str(output_dir))
    nobel_data, trend_data = create_sample_data()
    
    print("1. 自定义颜色演示:")
    
    # 自定义颜色方案
    custom_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    fig_custom = viz_agent.create_interactive_bar_chart(
        df=nobel_data,
        x_col='Category',
        y_col='Awards',
        color_col='Region',
        title='诺贝尔奖分布 - 自定义配色方案',
        template='infographic',
        custom_colors=custom_colors,
        auto_caption=True,
        caption_style='brief'
    )
    
    viz_agent.save_chart(fig_custom, "custom_colors_demo", formats=['html', 'png'])
    print("  ✓ 自定义颜色演示图已保存")
    
    print("\n2. 多语言图说演示:")
    
    # 中文图说
    fig_zh = viz_agent.create_interactive_bar_chart(
        df=nobel_data.head(4),
        x_col='Category',
        y_col='Awards',
        title='诺贝尔奖统计 - 中文图说',
        template='media',
        auto_caption=True,
        caption_style='academic',
        caption_language='zh'
    )
    
    viz_agent.save_chart(fig_zh, "multilingual_zh", formats=['html'])
    
    # 英文图说
    viz_agent.set_caption_language('en')
    fig_en = viz_agent.create_interactive_bar_chart(
        df=nobel_data.head(4),
        x_col='Category',
        y_col='Awards',
        title='Nobel Prize Statistics - English Caption',
        template='scientific',
        auto_caption=True,
        caption_style='academic',
        caption_language='en'
    )
    
    viz_agent.save_chart(fig_en, "multilingual_en", formats=['html'])
    print("  ✓ 多语言图说演示图已保存")
    
    print("\n3. 不同图说风格演示:")
    
    # 重置为中文
    viz_agent.set_caption_language('zh')
    
    caption_styles = ['standard', 'academic', 'brief']
    for style in caption_styles:
        fig = viz_agent.create_interactive_bar_chart(
            df=nobel_data.head(4),
            x_col='Category',
            y_col='Awards',
            title=f'诺贝尔奖统计 - {style.title()} 风格图说',
            template='business',
            auto_caption=True,
            caption_style=style
        )
        
        viz_agent.save_chart(fig, f"caption_style_{style}", formats=['html'])
        print(f"  ✓ {style} 风格图说演示图已保存")
    
    return output_dir


def demo_template_comparison():
    """创建模板对比总览"""
    print("\n=== 模板对比总览 ===\n")
    
    template_lib = ChartTemplateLibrary()
    
    # 显示模板信息
    templates = template_lib.list_templates()
    palettes = template_lib.list_color_palettes()
    
    print("可用专业模板总览:")
    print("-" * 80)
    print(f"{'模板名称':<15} {'描述':<35} {'配色方案':<20}")
    print("-" * 80)
    
    for name, desc in templates.items():
        template_config = template_lib.get_template(name)
        palette_name = template_config['color_palette']
        print(f"{name:<15} {desc:<35} {palette_name:<20}")
    
    print("-" * 80)
    print(f"总计: {len(templates)} 个专业模板, {len(palettes)} 种配色方案")
    
    print("\n模板特性对比:")
    print("-" * 100)
    print(f"{'模板':<12} {'字体':<15} {'字号':<6} {'背景':<10} {'图例位置':<8} {'适用场景':<20}")
    print("-" * 100)
    
    for name in templates.keys():
        config = template_lib.get_template(name)
        font_family = config['font_family'][:12] + "..." if len(config['font_family']) > 12 else config['font_family']
        
        print(f"{name:<12} {font_family:<15} {config['font_size']:<6} "
              f"{config['background_color']:<10} {config['legend_position']:<8} "
              f"{templates[name][:18]+'...' if len(templates[name]) > 18 else templates[name]:<20}")
    
    print("-" * 100)


def main():
    """主演示函数"""
    print("🎨 专业图表模板库完整演示\n")
    
    try:
        # 1. 演示所有模板
        template_dir = demo_all_templates()
        
        # 2. 演示特色功能
        feature_dir = demo_template_features()
        
        # 3. 显示对比信息
        demo_template_comparison()
        
        print(f"\n🎉 演示完成！")
        print(f"📁 模板演示文件保存在: {template_dir}")
        print(f"📁 特色功能演示文件保存在: {feature_dir}")
        
        print(f"\n📊 生成的文件包括:")
        print(f"  - 8种专业模板的柱状图 (HTML + PNG)")
        print(f"  - 4种模板预览图 (HTML)")
        print(f"  - 4种模板对比图 (HTML)")
        print(f"  - 自定义颜色演示 (HTML + PNG)")
        print(f"  - 多语言图说演示 (HTML)")
        print(f"  - 3种图说风格演示 (HTML)")
        
        print(f"\n💡 使用建议:")
        print(f"  - academic: 学术论文、科研报告")
        print(f"  - business: 商业演示、企业报告")
        print(f"  - presentation: PPT演示、会议展示")
        print(f"  - scientific: 科学研究、数据分析")
        print(f"  - media: 新闻报道、媒体发布")
        print(f"  - minimal: 极简设计、突出数据")
        print(f"  - dark: 现代界面、深色主题")
        print(f"  - infographic: 信息图表、数据故事")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 专业图表模板库演示成功完成！")
    else:
        print("\n❌ 演示过程中出现问题，请检查错误信息。")