"""
专业图表模板库
提供多种预设的专业图表样式和配置，适用于不同场景
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path


class ChartTemplateLibrary:
    """专业图表模板库"""
    
    def __init__(self):
        """初始化模板库"""
        self.templates = self._init_templates()
        self.color_palettes = self._init_color_palettes()
        self.font_configs = self._init_font_configs()
        self.layout_presets = self._init_layout_presets()
    
    def _init_templates(self) -> Dict[str, Dict]:
        """初始化图表模板"""
        return {
            'academic': {
                'name': '学术论文',
                'description': '适用于学术论文和科研报告的简洁专业风格',
                'color_palette': 'academic_blue',
                'font_family': 'Times New Roman',
                'font_size': 12,
                'background_color': 'white',
                'grid_color': '#E5E5E5',
                'line_width': 2,
                'marker_size': 8,
                'show_legend': True,
                'legend_position': 'top',
                'margin': {'l': 60, 'r': 60, 't': 80, 'b': 60}
            },
            'business': {
                'name': '商业报告',
                'description': '适用于商业演示和企业报告的现代专业风格',
                'color_palette': 'business_modern',
                'font_family': 'Arial',
                'font_size': 14,
                'background_color': '#FAFAFA',
                'grid_color': '#DDDDDD',
                'line_width': 3,
                'marker_size': 10,
                'show_legend': True,
                'legend_position': 'right',
                'margin': {'l': 80, 'r': 100, 't': 100, 'b': 80}
            },
            'presentation': {
                'name': '演示文稿',
                'description': '适用于PPT演示和会议展示的大字体清晰风格',
                'color_palette': 'presentation_bold',
                'font_family': 'Helvetica',
                'font_size': 16,
                'background_color': 'white',
                'grid_color': '#F0F0F0',
                'line_width': 4,
                'marker_size': 12,
                'show_legend': True,
                'legend_position': 'bottom',
                'margin': {'l': 100, 'r': 100, 't': 120, 'b': 100}
            },
            'scientific': {
                'name': '科学研究',
                'description': '适用于科学研究和数据分析的精确风格',
                'color_palette': 'scientific_precise',
                'font_family': 'Computer Modern',
                'font_size': 11,
                'background_color': 'white',
                'grid_color': '#CCCCCC',
                'line_width': 1.5,
                'marker_size': 6,
                'show_legend': True,
                'legend_position': 'top',
                'margin': {'l': 70, 'r': 70, 't': 90, 'b': 70}
            },
            'media': {
                'name': '新闻媒体',
                'description': '适用于新闻报道和媒体发布的醒目风格',
                'color_palette': 'media_vibrant',
                'font_family': 'Open Sans',
                'font_size': 13,
                'background_color': '#F8F9FA',
                'grid_color': '#DEE2E6',
                'line_width': 3,
                'marker_size': 9,
                'show_legend': True,
                'legend_position': 'top',
                'margin': {'l': 70, 'r': 70, 't': 100, 'b': 80}
            },
            'minimal': {
                'name': '极简风格',
                'description': '极简设计风格，突出数据本身',
                'color_palette': 'minimal_gray',
                'font_family': 'Roboto',
                'font_size': 12,
                'background_color': 'white',
                'grid_color': '#F5F5F5',
                'line_width': 2,
                'marker_size': 7,
                'show_legend': False,
                'legend_position': 'none',
                'margin': {'l': 50, 'r': 50, 't': 60, 'b': 50}
            },
            'dark': {
                'name': '深色主题',
                'description': '深色背景主题，适合现代界面展示',
                'color_palette': 'dark_neon',
                'font_family': 'Segoe UI',
                'font_size': 13,
                'background_color': '#1E1E1E',
                'grid_color': '#404040',
                'line_width': 2.5,
                'marker_size': 8,
                'show_legend': True,
                'legend_position': 'top',
                'margin': {'l': 70, 'r': 70, 't': 90, 'b': 70}
            },
            'infographic': {
                'name': '信息图表',
                'description': '适用于信息图表和数据故事的创意风格',
                'color_palette': 'infographic_creative',
                'font_family': 'Lato',
                'font_size': 14,
                'background_color': '#FFFFFF',
                'grid_color': '#E8E8E8',
                'line_width': 3,
                'marker_size': 11,
                'show_legend': True,
                'legend_position': 'right',
                'margin': {'l': 80, 'r': 120, 't': 100, 'b': 80}
            }
        }
    
    def _init_color_palettes(self) -> Dict[str, List[str]]:
        """初始化配色方案"""
        return {
            'academic_blue': [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ],
            'business_modern': [
                '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83',
                '#1B998B', '#ED217C', '#FF6B35', '#004E89', '#7209B7'
            ],
            'presentation_bold': [
                '#E63946', '#F77F00', '#FCBF49', '#06D6A0', '#118AB2',
                '#073B4C', '#FFD166', '#EF476F', '#06FFA5', '#4ECDC4'
            ],
            'scientific_precise': [
                '#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087',
                '#f95d6a', '#ff7c43', '#ffa600', '#488f31', '#de425b'
            ],
            'media_vibrant': [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
            ],
            'minimal_gray': [
                '#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7',
                '#ECF0F1', '#3498DB', '#E74C3C', '#F39C12', '#27AE60'
            ],
            'dark_neon': [
                '#00D9FF', '#FF0080', '#00FF88', '#FFD700', '#FF4500',
                '#8A2BE2', '#00CED1', '#FF1493', '#32CD32', '#FF6347'
            ],
            'infographic_creative': [
                '#FF6B9D', '#C44569', '#F8B500', '#6C5CE7', '#00B894',
                '#FDCB6E', '#E17055', '#74B9FF', '#A29BFE', '#FD79A8'
            ]
        }
    
    def _init_font_configs(self) -> Dict[str, Dict]:
        """初始化字体配置"""
        return {
            'title': {
                'academic': {'size': 16, 'weight': 'bold', 'color': '#2C3E50'},
                'business': {'size': 18, 'weight': 'bold', 'color': '#2E86AB'},
                'presentation': {'size': 24, 'weight': 'bold', 'color': '#E63946'},
                'scientific': {'size': 14, 'weight': 'bold', 'color': '#003f5c'},
                'media': {'size': 20, 'weight': 'bold', 'color': '#FF6B6B'},
                'minimal': {'size': 16, 'weight': 'normal', 'color': '#2C3E50'},
                'dark': {'size': 18, 'weight': 'bold', 'color': '#FFFFFF'},
                'infographic': {'size': 22, 'weight': 'bold', 'color': '#FF6B9D'}
            },
            'axis': {
                'academic': {'size': 12, 'weight': 'normal', 'color': '#34495E'},
                'business': {'size': 12, 'weight': 'normal', 'color': '#2C3E50'},
                'presentation': {'size': 14, 'weight': 'normal', 'color': '#2C3E50'},
                'scientific': {'size': 10, 'weight': 'normal', 'color': '#2f4b7c'},
                'media': {'size': 12, 'weight': 'normal', 'color': '#2C3E50'},
                'minimal': {'size': 11, 'weight': 'normal', 'color': '#7F8C8D'},
                'dark': {'size': 12, 'weight': 'normal', 'color': '#CCCCCC'},
                'infographic': {'size': 13, 'weight': 'normal', 'color': '#2C3E50'}
            },
            'legend': {
                'academic': {'size': 11, 'weight': 'normal', 'color': '#34495E'},
                'business': {'size': 12, 'weight': 'normal', 'color': '#2C3E50'},
                'presentation': {'size': 14, 'weight': 'normal', 'color': '#2C3E50'},
                'scientific': {'size': 10, 'weight': 'normal', 'color': '#2f4b7c'},
                'media': {'size': 11, 'weight': 'normal', 'color': '#2C3E50'},
                'minimal': {'size': 10, 'weight': 'normal', 'color': '#7F8C8D'},
                'dark': {'size': 11, 'weight': 'normal', 'color': '#CCCCCC'},
                'infographic': {'size': 12, 'weight': 'normal', 'color': '#2C3E50'}
            }
        }
    
    def _init_layout_presets(self) -> Dict[str, Dict]:
        """初始化布局预设"""
        return {
            'academic': {
                'showgrid': True,
                'gridwidth': 1,
                'zeroline': True,
                'zerolinewidth': 1,
                'showline': True,
                'linewidth': 1,
                'mirror': True
            },
            'business': {
                'showgrid': True,
                'gridwidth': 1,
                'zeroline': False,
                'showline': True,
                'linewidth': 2,
                'mirror': False
            },
            'presentation': {
                'showgrid': True,
                'gridwidth': 2,
                'zeroline': False,
                'showline': True,
                'linewidth': 3,
                'mirror': False
            },
            'scientific': {
                'showgrid': True,
                'gridwidth': 0.5,
                'zeroline': True,
                'zerolinewidth': 0.5,
                'showline': True,
                'linewidth': 1,
                'mirror': True
            },
            'media': {
                'showgrid': True,
                'gridwidth': 1,
                'zeroline': False,
                'showline': True,
                'linewidth': 2,
                'mirror': False
            },
            'minimal': {
                'showgrid': False,
                'zeroline': False,
                'showline': True,
                'linewidth': 1,
                'mirror': False
            },
            'dark': {
                'showgrid': True,
                'gridwidth': 1,
                'zeroline': False,
                'showline': True,
                'linewidth': 1,
                'mirror': False
            },
            'infographic': {
                'showgrid': True,
                'gridwidth': 1,
                'zeroline': False,
                'showline': True,
                'linewidth': 2,
                'mirror': False
            }
        }
    
    def get_template(self, template_name: str) -> Dict:
        """
        获取指定模板配置
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板配置字典
        """
        if template_name not in self.templates:
            raise ValueError(f"模板 '{template_name}' 不存在。可用模板: {list(self.templates.keys())}")
        
        return self.templates[template_name].copy()
    
    def get_color_palette(self, palette_name: str) -> List[str]:
        """
        获取指定配色方案
        
        Args:
            palette_name: 配色方案名称
            
        Returns:
            颜色列表
        """
        if palette_name not in self.color_palettes:
            raise ValueError(f"配色方案 '{palette_name}' 不存在。可用方案: {list(self.color_palettes.keys())}")
        
        return self.color_palettes[palette_name].copy()
    
    def list_templates(self) -> Dict[str, str]:
        """
        列出所有可用模板
        
        Returns:
            模板名称和描述的字典
        """
        return {name: config['description'] for name, config in self.templates.items()}
    
    def list_color_palettes(self) -> Dict[str, List[str]]:
        """
        列出所有可用配色方案
        
        Returns:
            配色方案字典
        """
        return self.color_palettes.copy()
    
    def apply_template_to_figure(self, fig: go.Figure, template_name: str, 
                               title: str = None, custom_colors: List[str] = None) -> go.Figure:
        """
        将模板应用到图表
        
        Args:
            fig: Plotly图表对象
            template_name: 模板名称
            title: 自定义标题
            custom_colors: 自定义颜色列表
            
        Returns:
            应用模板后的图表
        """
        template = self.get_template(template_name)
        
        # 获取配色方案
        colors = custom_colors or self.get_color_palette(template['color_palette'])
        
        # 获取字体配置
        title_font = self.font_configs['title'][template_name]
        axis_font = self.font_configs['axis'][template_name]
        legend_font = self.font_configs['legend'][template_name]
        
        # 获取布局预设
        layout_preset = self.layout_presets[template_name]
        
        # 应用颜色
        if hasattr(fig, 'data') and fig.data:
            for i, trace in enumerate(fig.data):
                color_idx = i % len(colors)
                if hasattr(trace, 'marker'):
                    trace.marker.color = colors[color_idx]
                elif hasattr(trace, 'line'):
                    trace.line.color = colors[color_idx]
                    trace.line.width = template['line_width']
        
        # 应用布局
        fig.update_layout(
            # 背景和网格
            plot_bgcolor=template['background_color'],
            paper_bgcolor=template['background_color'],
            
            # 标题
            title=dict(
                text=title or fig.layout.title.text,
                font=dict(
                    family=template['font_family'],
                    size=title_font['size'],
                    color=title_font['color']
                ),
                x=0.5,
                xanchor='center'
            ),
            
            # 字体
            font=dict(
                family=template['font_family'],
                size=template['font_size'],
                color=axis_font['color']
            ),
            
            # 图例
            showlegend=template['show_legend'],
            legend=dict(
                font=dict(
                    family=template['font_family'],
                    size=legend_font['size'],
                    color=legend_font['color']
                ),
                bgcolor='rgba(255,255,255,0.8)' if template_name != 'dark' else 'rgba(0,0,0,0.8)',
                bordercolor='rgba(0,0,0,0.2)' if template_name != 'dark' else 'rgba(255,255,255,0.2)',
                borderwidth=1
            ),
            
            # 边距
            margin=template['margin']
        )
        
        # 设置图例位置
        if template['legend_position'] == 'top':
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        elif template['legend_position'] == 'bottom':
            fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
        elif template['legend_position'] == 'right':
            fig.update_layout(legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1.02))
        elif template['legend_position'] == 'left':
            fig.update_layout(legend=dict(yanchor="middle", y=0.5, xanchor="right", x=-0.02))
        
        # 应用坐标轴样式
        axis_style = dict(
            gridcolor=template['grid_color'],
            linecolor=axis_font['color'],
            tickfont=dict(
                family=template['font_family'],
                size=axis_font['size'],
                color=axis_font['color']
            ),
            title=dict(
                font=dict(
                    family=template['font_family'],
                    size=axis_font['size'] + 1,
                    color=axis_font['color']
                )
            ),
            **layout_preset
        )
        
        fig.update_xaxes(**axis_style)
        fig.update_yaxes(**axis_style)
        
        return fig
    
    def create_template_preview(self, template_name: str) -> go.Figure:
        """
        创建模板预览图
        
        Args:
            template_name: 模板名称
            
        Returns:
            预览图表
        """
        # 创建示例数据
        import pandas as pd
        sample_data = pd.DataFrame({
            'Category': ['A', 'B', 'C', 'D', 'E'],
            'Value': [23, 45, 56, 78, 32]
        })
        
        # 创建基础柱状图
        fig = px.bar(sample_data, x='Category', y='Value', 
                    title=f'{self.templates[template_name]["name"]} 模板预览')
        
        # 应用模板
        fig = self.apply_template_to_figure(fig, template_name)
        
        return fig
    
    def save_custom_template(self, template_name: str, template_config: Dict, 
                           file_path: Optional[str] = None) -> None:
        """
        保存自定义模板
        
        Args:
            template_name: 模板名称
            template_config: 模板配置
            file_path: 保存路径（可选）
        """
        self.templates[template_name] = template_config
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({template_name: template_config}, f, ensure_ascii=False, indent=2)
    
    def load_custom_template(self, file_path: str) -> None:
        """
        加载自定义模板
        
        Args:
            file_path: 模板文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            custom_templates = json.load(f)
            self.templates.update(custom_templates)


def demo_template_library():
    """演示模板库功能"""
    print("=== 专业图表模板库演示 ===\n")
    
    # 初始化模板库
    template_lib = ChartTemplateLibrary()
    
    print("1. 可用模板列表:")
    templates = template_lib.list_templates()
    for name, desc in templates.items():
        print(f"  - {name}: {desc}")
    
    print("\n2. 可用配色方案:")
    palettes = template_lib.list_color_palettes()
    for name, colors in palettes.items():
        print(f"  - {name}: {colors[:3]}... (共{len(colors)}种颜色)")
    
    print("\n3. 模板配置示例 (academic):")
    academic_template = template_lib.get_template('academic')
    for key, value in academic_template.items():
        print(f"  {key}: {value}")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    demo_template_library()