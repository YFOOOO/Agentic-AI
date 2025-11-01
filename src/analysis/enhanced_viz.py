"""
增强的图表优化专家模块
集成 Plotly 支持交互式图表生成，同时保持与现有 Altair 代码的兼容性
"""

import os
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, Optional, Union, List
import json
from .accessibility_checker import AccessibilityChecker
from .auto_caption import AutoCaptionGenerator
from .chart_templates import ChartTemplateLibrary


class EnhancedVizAgent:
    """增强的可视化代理，集成Plotly支持交互式图表和无障碍检查"""
    
    def __init__(self, output_dir: str = "enhanced_figures"):
        from pathlib import Path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.accessibility_checker = AccessibilityChecker()
        self.caption_generator = AutoCaptionGenerator(language='zh')
        self.template_library = ChartTemplateLibrary()
        
        # 默认配置
        self.default_config = {
            'theme': 'plotly_white',
            'color_palette': 'wong',  # 使用色盲友好的Wong配色
            'width': 800,
            'height': 600,
            'font_family': 'Arial',
            'font_size': 12,
            'show_accessibility_info': True,
            'use_accessible_colors': True,
            'auto_caption': True,
            'caption_style': 'standard',
            'caption_language': 'zh',
            'template': None,  # 新增：专业模板选择
            'custom_colors': None  # 新增：自定义颜色
        }
        
        self.supported_formats = ["html", "png", "svg", "pdf", "json"]
        
    def save_chart(self, chart: Union[alt.Chart, go.Figure], 
                   filename: str, 
                   formats: List[str] = ["html"]) -> Dict[str, str]:
        """
        保存图表到多种格式
        
        Args:
            chart: Altair Chart 或 Plotly Figure 对象
            filename: 文件名（不含扩展名）
            formats: 要保存的格式列表
            
        Returns:
            Dict[str, str]: 格式到文件路径的映射
        """
        os.makedirs(self.output_dir, exist_ok=True)
        saved_files = {}
        
        for fmt in formats:
            if fmt not in self.supported_formats:
                print(f"Warning: Unsupported format {fmt}")
                continue
                
            filepath = os.path.join(self.output_dir, f"{filename}.{fmt}")
            
            try:
                if isinstance(chart, alt.Chart):
                    # Altair 图表
                    if fmt == "html":
                        chart.save(filepath)
                    else:
                        print(f"Warning: Altair chart only supports HTML export")
                        continue
                        
                elif isinstance(chart, go.Figure):
                    # Plotly 图表
                    if fmt == "html":
                        chart.write_html(filepath)
                    elif fmt == "png":
                        chart.write_image(filepath, format="png")
                    elif fmt == "svg":
                        chart.write_image(filepath, format="svg")
                    elif fmt == "pdf":
                        chart.write_image(filepath, format="pdf")
                    elif fmt == "json":
                        chart.write_json(filepath)
                        
                saved_files[fmt] = filepath
                print(f"Chart saved: {filepath}")
                
            except Exception as e:
                print(f"Error saving {fmt} format: {e}")
                
        return saved_files

    def get_accessible_colors(self, num_colors: int, palette_name: str = None) -> List[str]:
        """
        获取无障碍友好的颜色方案
        
        Args:
            num_colors: 需要的颜色数量
            palette_name: 调色板名称，如果为None则使用默认配置
            
        Returns:
            颜色列表
        """
        if palette_name is None:
            palette_name = self.default_config['color_palette']
        
        return self.accessibility_checker.get_colorblind_safe_palette(
            palette_name, num_colors
        )
    
    def validate_chart_accessibility(self, colors: List[str], 
                                   background_color: str = '#FFFFFF') -> Dict:
        """
        验证图表的无障碍性
        
        Args:
            colors: 图表使用的颜色列表
            background_color: 背景颜色
            
        Returns:
            无障碍性分析结果
        """
        # 分析调色板
        palette_analysis = self.accessibility_checker.analyze_palette_accessibility(colors)
        
        # 检查与背景的对比度
        contrast_results = []
        for color in colors:
            contrast = self.accessibility_checker.check_wcag_compliance(
                color, background_color, text_size='large', level='AA'
            )
            contrast_results.append({
                'color': color,
                'contrast_ratio': contrast['contrast_ratio'],
                'passes_wcag': contrast['passes']
            })
        
        return {
            'palette_analysis': palette_analysis,
            'contrast_results': contrast_results,
            'overall_accessible': all(result['passes_wcag'] for result in contrast_results)
        }
    
    def generate_chart_caption(self, df: pd.DataFrame, 
                              chart_type: str,
                              title: str = "",
                              value_col: str = None,
                              category_col: str = None,
                              time_col: str = None,
                              style: str = None,
                              language: str = None) -> str:
        """
        生成图表说明
        
        Args:
            df: 数据框
            chart_type: 图表类型
            title: 图表标题
            value_col: 数值列名
            category_col: 分类列名
            time_col: 时间列名
            style: 说明风格
            language: 语言设置
            
        Returns:
            图表说明文字
        """
        # 使用配置中的默认值
        style = style or self.default_config.get('caption_style', 'standard')
        language = language or self.default_config.get('caption_language', 'zh')
        
        # 如果语言设置改变，重新初始化生成器
        if self.caption_generator.language != language:
            self.caption_generator = AutoCaptionGenerator(language=language)
        
        return self.caption_generator.generate_caption(
            df=df,
            chart_type=chart_type,
            title=title,
            value_col=value_col,
            category_col=category_col,
            time_col=time_col,
            style=style
        )
    
    def add_caption_to_figure(self, fig, caption: str, position: str = 'bottom') -> None:
        """
        为图表添加说明文字
        
        Args:
            fig: Plotly图表对象
            caption: 说明文字
            position: 位置 ('bottom', 'top')
        """
        if position == 'bottom':
            # 在图表底部添加注释
            fig.add_annotation(
                text=caption,
                xref="paper", yref="paper",
                x=0.5, y=-0.15,
                showarrow=False,
                font=dict(size=10, color="gray"),
                align="center",
                width=800,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="lightgray",
                borderwidth=1
            )
            # 调整布局以留出空间
            fig.update_layout(margin=dict(b=100))
        elif position == 'top':
            # 在图表顶部添加注释
            fig.add_annotation(
                text=caption,
                xref="paper", yref="paper",
                x=0.5, y=1.1,
                showarrow=False,
                font=dict(size=10, color="gray"),
                align="center",
                width=800,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="lightgray",
                borderwidth=1
            )
            # 调整布局以留出空间
            fig.update_layout(margin=dict(t=100))
    
    def set_caption_language(self, language: str) -> None:
        """
        设置图说语言
        
        Args:
            language: 语言代码 ('zh', 'en')
        """
        self.default_config['caption_language'] = language
        self.caption_generator = AutoCaptionGenerator(language=language)
    
    def list_available_templates(self) -> Dict[str, str]:
        """
        列出所有可用的专业模板
        
        Returns:
            模板名称和描述的字典
        """
        return self.template_library.list_templates()
    
    def get_template_colors(self, template_name: str) -> List[str]:
        """
        获取指定模板的配色方案
        
        Args:
            template_name: 模板名称
            
        Returns:
            颜色列表
        """
        template = self.template_library.get_template(template_name)
        return self.template_library.get_color_palette(template['color_palette'])
    
    def apply_professional_template(self, fig: go.Figure, template_name: str, 
                                  title: str = None, custom_colors: List[str] = None) -> go.Figure:
        """
        应用专业模板到图表
        
        Args:
            fig: Plotly图表对象
            template_name: 模板名称
            title: 自定义标题
            custom_colors: 自定义颜色列表
            
        Returns:
            应用模板后的图表
        """
        return self.template_library.apply_template_to_figure(fig, template_name, title, custom_colors)
    
    def create_template_preview(self, template_name: str) -> go.Figure:
        """
        创建模板预览图
        
        Args:
            template_name: 模板名称
            
        Returns:
            预览图表
        """
        return self.template_library.create_template_preview(template_name)

    def apply_accessible_theme(self, fig, theme_name: str = 'academic') -> go.Figure:
        """
        应用无障碍友好的主题
        
        Args:
            fig: Plotly图表对象
            theme_name: 主题名称
            
        Returns:
            应用主题后的图表对象
        """
        theme_colors = self.accessibility_checker.get_theme_colors(theme_name)
        
        fig.update_layout(
            plot_bgcolor=theme_colors['background'],
            paper_bgcolor=theme_colors['background'],
            font=dict(
                family=self.default_config['font_family'],
                size=self.default_config['font_size'],
                color=theme_colors['text']
            ),
            title=dict(
                font=dict(
                    size=self.default_config['font_size'] + 4,
                    color=theme_colors['text']
                )
            ),
            xaxis=dict(
                gridcolor='rgba(128,128,128,0.2)',
                linecolor=theme_colors['text']
            ),
            yaxis=dict(
                gridcolor='rgba(128,128,128,0.2)',
                linecolor=theme_colors['text']
            )
        )
        
        return fig

    def create_interactive_bar_chart(self, df: pd.DataFrame, 
                                   x_col: str, y_col: str, 
                                   title: str = "",
                                   color_col: Optional[str] = None,
                                   top_n: Optional[int] = None,
                                   use_accessible_colors: bool = True,
                                   theme: str = 'academic',
                                   auto_caption: bool = None,
                                   caption_style: str = None,
                                   caption_position: str = 'bottom',
                                   template: str = None,
                                   custom_colors: List[str] = None) -> go.Figure:
        """创建交互式柱状图（支持无障碍友好配色）"""
        
        # 使用默认配置
        use_accessible_colors = use_accessible_colors if use_accessible_colors is not None else self.default_config.get('use_accessible_colors', True)
        theme = theme or self.default_config.get('theme', 'academic')
        auto_caption = auto_caption if auto_caption is not None else self.default_config.get('auto_caption', True)
        caption_style = caption_style or self.default_config.get('caption_style', 'standard')
        template = template or self.default_config.get('template')
        custom_colors = custom_colors or self.default_config.get('custom_colors')
        
        # 数据预处理
        if top_n:
            df = df.nlargest(top_n, y_col)
            
        # 创建图表
        if color_col and use_accessible_colors:
            # 获取唯一值数量以确定需要的颜色数
            unique_colors = df[color_col].nunique()
            accessible_colors = custom_colors or self.get_accessible_colors(unique_colors)
            
            fig = px.bar(
                df, 
                x=y_col, 
                y=x_col, 
                orientation='h',
                color=color_col,
                title=title,
                hover_data=[x_col, y_col],
                color_discrete_sequence=accessible_colors
            )
        else:
            fig = px.bar(
                df, 
                x=y_col, 
                y=x_col, 
                orientation='h',
                color=color_col if color_col else y_col,
                title=title,
                hover_data=[x_col, y_col],
                color_continuous_scale="viridis"
            )
        
        # 应用专业模板（优先级高于无障碍主题）
        if template:
            fig = self.apply_professional_template(fig, template, title, custom_colors)
        elif use_accessible_colors:
            # 应用无障碍主题
            fig = self.apply_accessible_theme(fig, theme)
        
        # 优化布局（如果没有应用专业模板）
        if not template:
            fig.update_layout(
                title_font_size=16,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                height=max(400, len(df) * 25),  # 动态高度
                margin=dict(l=150, r=50, t=80, b=50),
                hovermode='closest'
            )
        else:
            # 专业模板下的基本布局调整
            fig.update_layout(
                height=max(400, len(df) * 25),  # 动态高度
                hovermode='closest'
            )
        
        # 排序 y 轴
        fig.update_yaxes(categoryorder="total ascending")
        
        # 生成并添加图说
        if auto_caption:
            caption = self.generate_chart_caption(
                df=df,
                chart_type='bar_chart',
                title=title,
                value_col=y_col,
                category_col=x_col,
                style=caption_style
            )
            self.add_caption_to_figure(fig, caption, caption_position)
        
        return fig

    def create_interactive_line_chart(self, df: pd.DataFrame,
                                    x_col: str, y_col: str,
                                    title: str = "",
                                    group_col: Optional[str] = None) -> go.Figure:
        """创建交互式折线图"""
        
        if group_col:
            fig = px.line(
                df, 
                x=x_col, 
                y=y_col, 
                color=group_col,
                title=title,
                markers=True,
                hover_data=[x_col, y_col, group_col]
            )
        else:
            fig = px.line(
                df, 
                x=x_col, 
                y=y_col, 
                title=title,
                markers=True,
                hover_data=[x_col, y_col]
            )
        
        # 优化布局
        fig.update_layout(
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            height=500,
            hovermode='x unified'
        )
        
        return fig

    def create_interactive_area_chart(self, df: pd.DataFrame,
                                    x_col: str, y_col: str,
                                    group_col: str,
                                    title: str = "",
                                    normalize: bool = False) -> go.Figure:
        """创建交互式面积图"""
        
        if normalize:
            # 计算归一化数据
            pivot_df = df.pivot_table(
                index=x_col, 
                columns=group_col, 
                values=y_col, 
                fill_value=0
            )
            # 按行归一化
            pivot_df = pivot_df.div(pivot_df.sum(axis=1), axis=0)
            
            fig = go.Figure()
            
            for col in pivot_df.columns:
                fig.add_trace(go.Scatter(
                    x=pivot_df.index,
                    y=pivot_df[col],
                    mode='lines',
                    stackgroup='one',
                    groupnorm='percent',
                    name=str(col),
                    hovertemplate=f'<b>{col}</b><br>' +
                                f'{x_col}: %{{x}}<br>' +
                                f'占比: %{{y:.1%}}<extra></extra>'
                ))
        else:
            fig = px.area(
                df, 
                x=x_col, 
                y=y_col, 
                color=group_col,
                title=title,
                hover_data=[x_col, y_col, group_col]
            )
        
        # 优化布局
        fig.update_layout(
            title=title,
            title_font_size=16,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            height=500,
            hovermode='x unified'
        )
        
        return fig

    def create_enhanced_nobel_charts(self, df: pd.DataFrame, 
                                   top_n: int = 15) -> Dict[str, go.Figure]:
        """
        为诺贝尔奖数据创建增强的交互式图表集合
        
        Args:
            df: 诺贝尔奖数据DataFrame
            top_n: 显示前N个国家
            
        Returns:
            Dict[str, go.Figure]: 图表名称到图表对象的映射
        """
        charts = {}
        
        # 1. 交互式国家分布柱状图
        country_counts = (
            df.groupby("bornCountry")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(top_n)
        )
        
        charts["countries_interactive"] = self.create_interactive_bar_chart(
            country_counts,
            x_col="bornCountry",
            y_col="count",
            title=f"诺贝尔奖获奖者出生国家分布 Top {top_n}（交互式）",
            top_n=None  # 已经预处理了
        )
        
        # 2. 交互式年度趋势图
        yearly_counts = (
            df.groupby("year")
            .size()
            .reset_index(name="count")
            .sort_values("year")
        )
        
        charts["yearly_trend_interactive"] = self.create_interactive_line_chart(
            yearly_counts,
            x_col="year",
            y_col="count",
            title="年度获奖人数趋势（交互式）"
        )
        
        # 3. 交互式学科分布面积图
        category_yearly = (
            df.groupby(["year", "category"])
            .size()
            .reset_index(name="count")
            .sort_values(["year", "category"])
        )
        
        charts["category_stacked_interactive"] = self.create_interactive_area_chart(
            category_yearly,
            x_col="year",
            y_col="count",
            group_col="category",
            title="按奖项类别的年度占比（归一化，交互式）",
            normalize=True
        )
        
        # 4. 新增：国家-学科热力图
        country_category = (
            df.groupby(["bornCountry", "category"])
            .size()
            .reset_index(name="count")
        )
        
        # 只显示获奖人数较多的国家
        top_countries = country_counts.head(10)["bornCountry"].tolist()
        country_category_filtered = country_category[
            country_category["bornCountry"].isin(top_countries)
        ]
        
        pivot_heatmap = country_category_filtered.pivot(
            index="bornCountry", 
            columns="category", 
            values="count"
        ).fillna(0)
        
        charts["country_category_heatmap"] = go.Figure(data=go.Heatmap(
            z=pivot_heatmap.values,
            x=pivot_heatmap.columns,
            y=pivot_heatmap.index,
            colorscale='Viridis',
            hovertemplate='国家: %{y}<br>学科: %{x}<br>获奖人数: %{z}<extra></extra>'
        ))
        
        charts["country_category_heatmap"].update_layout(
            title="主要国家按学科获奖分布热力图",
            title_font_size=16,
            xaxis_title="奖项类别",
            yaxis_title="出生国家",
            height=400
        )
        
        return charts


def demo_enhanced_viz():
    """演示增强图表功能"""
    # 模拟数据
    import numpy as np
    
    np.random.seed(42)
    countries = ["美国", "英国", "德国", "法国", "日本", "瑞典", "俄国", "意大利"]
    categories = ["物理学", "化学", "生理学或医学", "文学", "和平", "经济学"]
    years = list(range(1901, 2024))
    
    # 生成模拟数据
    data = []
    for _ in range(1000):
        data.append({
            "bornCountry": np.random.choice(countries, p=[0.3, 0.15, 0.12, 0.1, 0.08, 0.07, 0.06, 0.12]),
            "category": np.random.choice(categories),
            "year": np.random.choice(years)
        })
    
    df = pd.DataFrame(data)
    
    # 创建增强图表
    viz_agent = EnhancedVizAgent("demo_figures")
    charts = viz_agent.create_enhanced_nobel_charts(df)
    
    # 保存所有图表
    for name, chart in charts.items():
        viz_agent.save_chart(chart, name, formats=["html", "png"])
    
    print(f"Demo charts saved to demo_figures/")


if __name__ == "__main__":
    demo_enhanced_viz()