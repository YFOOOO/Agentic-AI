"""
图说自动生成模块
基于数据分析自动生成图表描述和洞察
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
import re
from datetime import datetime


class AutoCaptionGenerator:
    """图说自动生成器"""
    
    def __init__(self, language: str = 'zh'):
        """
        初始化图说生成器
        
        Args:
            language: 语言设置 ('zh' 中文, 'en' 英文)
        """
        self.language = language
        self.templates = self._init_templates()
        self.statistical_terms = self._init_statistical_terms()
    
    def _init_templates(self) -> Dict[str, Dict[str, str]]:
        """初始化图说模板"""
        return {
            'zh': {
                'bar_chart': "该柱状图展示了{title}的分布情况。{insights}",
                'line_chart': "该折线图显示了{title}随时间的变化趋势。{insights}",
                'area_chart': "该面积图展现了{title}的累积变化。{insights}",
                'heatmap': "该热力图展示了{title}的相关性分布。{insights}",
                'pie_chart': "该饼图显示了{title}的构成比例。{insights}",
                'scatter': "该散点图展示了{title}之间的关系。{insights}",
                'histogram': "该直方图显示了{title}的频率分布。{insights}"
            },
            'en': {
                'bar_chart': "This bar chart shows the distribution of {title}. {insights}",
                'line_chart': "This line chart displays the trend of {title} over time. {insights}",
                'area_chart': "This area chart presents the cumulative changes of {title}. {insights}",
                'heatmap': "This heatmap shows the correlation distribution of {title}. {insights}",
                'pie_chart': "This pie chart displays the composition of {title}. {insights}",
                'scatter': "This scatter plot shows the relationship between {title}. {insights}",
                'histogram': "This histogram shows the frequency distribution of {title}. {insights}"
            }
        }
    
    def _init_statistical_terms(self) -> Dict[str, Dict[str, str]]:
        """初始化统计术语"""
        return {
            'zh': {
                'highest': '最高',
                'lowest': '最低',
                'average': '平均',
                'median': '中位数',
                'total': '总计',
                'increasing': '呈上升趋势',
                'decreasing': '呈下降趋势',
                'stable': '保持稳定',
                'peak': '峰值',
                'valley': '谷值',
                'outlier': '异常值',
                'correlation': '相关性',
                'distribution': '分布',
                'concentration': '集中',
                'dispersion': '分散'
            },
            'en': {
                'highest': 'highest',
                'lowest': 'lowest',
                'average': 'average',
                'median': 'median',
                'total': 'total',
                'increasing': 'shows an increasing trend',
                'decreasing': 'shows a decreasing trend',
                'stable': 'remains stable',
                'peak': 'peak',
                'valley': 'valley',
                'outlier': 'outlier',
                'correlation': 'correlation',
                'distribution': 'distribution',
                'concentration': 'concentration',
                'dispersion': 'dispersion'
            }
        }
    
    def analyze_data_statistics(self, df: pd.DataFrame, 
                              value_col: str, 
                              category_col: str = None) -> Dict:
        """
        分析数据的基本统计信息
        
        Args:
            df: 数据框
            value_col: 数值列名
            category_col: 分类列名
            
        Returns:
            统计分析结果
        """
        stats = {}
        
        # 基本统计信息
        values = df[value_col].dropna()
        stats['count'] = len(values)
        stats['sum'] = values.sum()
        stats['mean'] = values.mean()
        stats['median'] = values.median()
        stats['std'] = values.std()
        stats['min'] = values.min()
        stats['max'] = values.max()
        stats['range'] = stats['max'] - stats['min']
        
        # 分位数
        stats['q25'] = values.quantile(0.25)
        stats['q75'] = values.quantile(0.75)
        stats['iqr'] = stats['q75'] - stats['q25']
        
        # 异常值检测（IQR方法）
        lower_bound = stats['q25'] - 1.5 * stats['iqr']
        upper_bound = stats['q75'] + 1.5 * stats['iqr']
        outliers = values[(values < lower_bound) | (values > upper_bound)]
        stats['outliers_count'] = len(outliers)
        stats['outliers_percentage'] = (len(outliers) / len(values)) * 100
        
        # 分类统计（如果有分类列）
        if category_col and category_col in df.columns:
            category_stats = df.groupby(category_col)[value_col].agg([
                'count', 'sum', 'mean', 'min', 'max'
            ]).round(2)
            
            stats['category_stats'] = category_stats.to_dict('index')
            stats['top_category'] = category_stats['sum'].idxmax()
            stats['bottom_category'] = category_stats['sum'].idxmin()
            stats['most_frequent_category'] = category_stats['count'].idxmax()
        
        return stats
    
    def detect_trends(self, df: pd.DataFrame, 
                     value_col: str, 
                     time_col: str = None) -> Dict:
        """
        检测数据趋势
        
        Args:
            df: 数据框
            value_col: 数值列名
            time_col: 时间列名
            
        Returns:
            趋势分析结果
        """
        trends = {}
        
        if time_col and time_col in df.columns:
            # 按时间排序
            df_sorted = df.sort_values(time_col)
            values = df_sorted[value_col].dropna()
            
            if len(values) > 1:
                # 计算趋势斜率
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]
                
                # 判断趋势方向
                if slope > 0.1:
                    trends['direction'] = 'increasing'
                elif slope < -0.1:
                    trends['direction'] = 'decreasing'
                else:
                    trends['direction'] = 'stable'
                
                trends['slope'] = slope
                trends['start_value'] = values.iloc[0]
                trends['end_value'] = values.iloc[-1]
                trends['change'] = trends['end_value'] - trends['start_value']
                trends['change_percentage'] = (trends['change'] / trends['start_value']) * 100
                
                # 寻找峰值和谷值
                peaks = []
                valleys = []
                for i in range(1, len(values) - 1):
                    if values.iloc[i] > values.iloc[i-1] and values.iloc[i] > values.iloc[i+1]:
                        peaks.append((i, values.iloc[i]))
                    elif values.iloc[i] < values.iloc[i-1] and values.iloc[i] < values.iloc[i+1]:
                        valleys.append((i, values.iloc[i]))
                
                trends['peaks'] = peaks
                trends['valleys'] = valleys
        
        return trends
    
    def generate_insights(self, stats: Dict, trends: Dict = None, 
                         chart_type: str = 'bar_chart') -> List[str]:
        """
        生成数据洞察
        
        Args:
            stats: 统计信息
            trends: 趋势信息
            chart_type: 图表类型
            
        Returns:
            洞察列表
        """
        insights = []
        terms = self.statistical_terms[self.language]
        
        # 基本统计洞察
        if 'category_stats' in stats:
            top_cat = stats['top_category']
            bottom_cat = stats['bottom_category']
            
            if self.language == 'zh':
                insights.append(f"其中{top_cat}的数值{terms['highest']}，达到{stats['category_stats'][top_cat]['sum']:.1f}")
                insights.append(f"{bottom_cat}的数值{terms['lowest']}，为{stats['category_stats'][bottom_cat]['sum']:.1f}")
            else:
                insights.append(f"{top_cat} has the {terms['highest']} value at {stats['category_stats'][top_cat]['sum']:.1f}")
                insights.append(f"{bottom_cat} has the {terms['lowest']} value at {stats['category_stats'][bottom_cat]['sum']:.1f}")
        
        # 异常值洞察
        if stats['outliers_count'] > 0:
            if self.language == 'zh':
                insights.append(f"数据中存在{stats['outliers_count']}个{terms['outlier']}，占总数的{stats['outliers_percentage']:.1f}%")
            else:
                insights.append(f"There are {stats['outliers_count']} {terms['outlier']}s in the data, accounting for {stats['outliers_percentage']:.1f}%")
        
        # 趋势洞察
        if trends and 'direction' in trends:
            direction_term = terms[trends['direction']]
            if self.language == 'zh':
                if trends['direction'] != 'stable':
                    change_pct = abs(trends['change_percentage'])
                    insights.append(f"数据{direction_term}，变化幅度为{change_pct:.1f}%")
                else:
                    insights.append(f"数据{direction_term}")
            else:
                if trends['direction'] != 'stable':
                    change_pct = abs(trends['change_percentage'])
                    insights.append(f"The data {direction_term} with a change of {change_pct:.1f}%")
                else:
                    insights.append(f"The data {direction_term}")
        
        # 分布洞察
        cv = stats['std'] / stats['mean'] if stats['mean'] != 0 else 0
        if cv > 0.5:
            if self.language == 'zh':
                insights.append(f"数据{terms['dispersion']}程度较高，变异系数为{cv:.2f}")
            else:
                insights.append(f"The data shows high {terms['dispersion']} with a coefficient of variation of {cv:.2f}")
        elif cv < 0.2:
            if self.language == 'zh':
                insights.append(f"数据{terms['concentration']}程度较高，变异系数为{cv:.2f}")
            else:
                insights.append(f"The data shows high {terms['concentration']} with a coefficient of variation of {cv:.2f}")
        
        return insights
    
    def generate_caption(self, df: pd.DataFrame, 
                        chart_type: str,
                        title: str = "",
                        value_col: str = None,
                        category_col: str = None,
                        time_col: str = None,
                        style: str = 'standard') -> str:
        """
        生成图表说明
        
        Args:
            df: 数据框
            chart_type: 图表类型
            title: 图表标题
            value_col: 数值列名
            category_col: 分类列名
            time_col: 时间列名
            style: 说明风格 ('standard', 'academic', 'brief')
            
        Returns:
            图表说明文字
        """
        # 数据分析
        if value_col:
            stats = self.analyze_data_statistics(df, value_col, category_col)
            trends = self.detect_trends(df, value_col, time_col) if time_col else {}
            insights = self.generate_insights(stats, trends, chart_type)
        else:
            insights = []
        
        # 选择模板
        template = self.templates[self.language].get(chart_type, 
                   self.templates[self.language]['bar_chart'])
        
        # 生成洞察文字
        if insights:
            if style == 'brief':
                insight_text = insights[0] if insights else ""
            elif style == 'academic':
                insight_text = "；".join(insights) if self.language == 'zh' else "; ".join(insights)
            else:  # standard
                insight_text = "，".join(insights[:3]) if self.language == 'zh' else ", ".join(insights[:3])
        else:
            insight_text = ""
        
        # 格式化标题
        if not title:
            if category_col and value_col:
                title = f"{category_col}与{value_col}" if self.language == 'zh' else f"{category_col} and {value_col}"
            elif value_col:
                title = value_col
            else:
                title = "数据" if self.language == 'zh' else "data"
        
        # 生成最终说明
        caption = template.format(title=title, insights=insight_text)
        
        # 添加统计摘要（学术风格）
        if style == 'academic' and value_col and 'stats' in locals():
            if self.language == 'zh':
                summary = f"数据总计{stats['count']}个观测值，平均值为{stats['mean']:.2f}，标准差为{stats['std']:.2f}。"
            else:
                summary = f"The dataset contains {stats['count']} observations with a mean of {stats['mean']:.2f} and standard deviation of {stats['std']:.2f}."
            caption = summary + caption
        
        return caption
    
    def generate_multiple_captions(self, df: pd.DataFrame,
                                 chart_configs: List[Dict]) -> Dict[str, str]:
        """
        为多个图表生成说明
        
        Args:
            df: 数据框
            chart_configs: 图表配置列表
            
        Returns:
            图表说明字典
        """
        captions = {}
        
        for config in chart_configs:
            chart_id = config.get('id', f"chart_{len(captions)}")
            caption = self.generate_caption(
                df=df,
                chart_type=config.get('type', 'bar_chart'),
                title=config.get('title', ''),
                value_col=config.get('value_col'),
                category_col=config.get('category_col'),
                time_col=config.get('time_col'),
                style=config.get('style', 'standard')
            )
            captions[chart_id] = caption
        
        return captions


def demo_auto_caption():
    """演示图说自动生成功能"""
    print("=== 图说自动生成演示 ===\n")
    
    # 创建测试数据
    np.random.seed(42)
    test_data = pd.DataFrame({
        'category': ['Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace', 'Economics'] * 10,
        'count': np.random.randint(5, 50, 60),
        'year': np.repeat(range(2014, 2024), 6)
    })
    
    # 初始化生成器
    caption_gen_zh = AutoCaptionGenerator(language='zh')
    caption_gen_en = AutoCaptionGenerator(language='en')
    
    print("1. 中文图说生成:")
    
    # 柱状图说明
    caption_zh = caption_gen_zh.generate_caption(
        df=test_data,
        chart_type='bar_chart',
        title='诺贝尔奖各类别获奖数量',
        value_col='count',
        category_col='category',
        style='standard'
    )
    print(f"  柱状图: {caption_zh}")
    
    # 折线图说明
    caption_zh_line = caption_gen_zh.generate_caption(
        df=test_data,
        chart_type='line_chart',
        title='诺贝尔奖年度趋势',
        value_col='count',
        time_col='year',
        style='academic'
    )
    print(f"  折线图: {caption_zh_line}")
    
    print("\n2. 英文图说生成:")
    
    # 柱状图说明
    caption_en = caption_gen_en.generate_caption(
        df=test_data,
        chart_type='bar_chart',
        title='Nobel Prize Categories',
        value_col='count',
        category_col='category',
        style='standard'
    )
    print(f"  Bar Chart: {caption_en}")
    
    # 折线图说明
    caption_en_line = caption_gen_en.generate_caption(
        df=test_data,
        chart_type='line_chart',
        title='Nobel Prize Annual Trends',
        value_col='count',
        time_col='year',
        style='brief'
    )
    print(f"  Line Chart: {caption_en_line}")
    
    print("\n3. 数据统计分析:")
    stats = caption_gen_zh.analyze_data_statistics(test_data, 'count', 'category')
    print(f"  数据总数: {stats['count']}")
    print(f"  平均值: {stats['mean']:.2f}")
    print(f"  最高类别: {stats['top_category']}")
    print(f"  异常值数量: {stats['outliers_count']}")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    demo_auto_caption()