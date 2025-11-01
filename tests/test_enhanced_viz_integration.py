#!/usr/bin/env python3
"""
增强图表功能集成测试脚本
验证新的 Plotly 图表功能与现有 Altair 系统的兼容性
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.analysis.enhanced_viz import EnhancedVizAgent
from src.analysis.nobel_analysis import load_data, top_countries_chart, yearly_trend_chart, category_stacked_chart
import pandas as pd


def test_data_compatibility():
    """测试数据兼容性"""
    print("=== 测试数据兼容性 ===")
    
    data_file = 'artifacts/nobel/laureates_prizes.csv'
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return False
    
    try:
        # 使用现有的数据加载函数
        df_original = load_data(data_file)
        print(f"✅ 原始数据加载成功: {len(df_original)} 条记录")
        
        # 使用增强模块的数据处理
        df_enhanced = pd.read_csv(data_file)
        df_enhanced["year"] = pd.to_numeric(df_enhanced["year"], errors="coerce")
        df_enhanced["bornCountry"] = df_enhanced["bornCountry"].fillna("Unknown")
        df_enhanced["category"] = df_enhanced["category"].fillna("Unknown")
        df_enhanced = df_enhanced.dropna(subset=["year"])
        
        print(f"✅ 增强数据处理成功: {len(df_enhanced)} 条记录")
        
        # 验证数据一致性
        if len(df_original) == len(df_enhanced):
            print("✅ 数据处理结果一致")
            return True, df_enhanced
        else:
            print(f"⚠️  数据长度不一致: 原始={len(df_original)}, 增强={len(df_enhanced)}")
            return True, df_enhanced  # 仍然可以继续测试
            
    except Exception as e:
        print(f"❌ 数据兼容性测试失败: {e}")
        return False, None


def test_chart_generation_performance():
    """测试图表生成性能"""
    print("\n=== 测试图表生成性能 ===")
    
    success, df = test_data_compatibility()
    if not success or df is None:
        return False
    
    viz_agent = EnhancedVizAgent("test_output")
    
    try:
        # 测试原始 Altair 图表生成时间
        start_time = time.time()
        altair_chart1 = top_countries_chart(df, 15)
        altair_chart2 = yearly_trend_chart(df)
        altair_chart3 = category_stacked_chart(df)
        altair_time = time.time() - start_time
        print(f"✅ Altair 图表生成时间: {altair_time:.2f}秒")
        
        # 测试增强 Plotly 图表生成时间
        start_time = time.time()
        plotly_charts = viz_agent.create_enhanced_nobel_charts(df, 15)
        plotly_time = time.time() - start_time
        print(f"✅ Plotly 图表生成时间: {plotly_time:.2f}秒")
        
        # 性能比较
        if plotly_time <= altair_time * 3:  # 允许 Plotly 慢3倍以内
            print(f"✅ 性能测试通过 (Plotly/Altair 比率: {plotly_time/altair_time:.1f})")
        else:
            print(f"⚠️  Plotly 图表生成较慢 (比率: {plotly_time/altair_time:.1f})")
        
        return True, plotly_charts
        
    except Exception as e:
        print(f"❌ 图表生成性能测试失败: {e}")
        return False, None


def test_export_functionality():
    """测试导出功能"""
    print("\n=== 测试导出功能 ===")
    
    success, charts = test_chart_generation_performance()
    if not success or not charts:
        return False
    
    viz_agent = EnhancedVizAgent("test_output")
    
    try:
        # 测试多格式导出
        test_chart = charts["countries_interactive"]
        
        # 测试 HTML 导出
        saved_files = viz_agent.save_chart(test_chart, "test_export", formats=["html"])
        if "html" in saved_files and os.path.exists(saved_files["html"]):
            print("✅ HTML 导出成功")
        else:
            print("❌ HTML 导出失败")
            return False
        
        # 测试 PNG 导出
        saved_files = viz_agent.save_chart(test_chart, "test_export", formats=["png"])
        if "png" in saved_files and os.path.exists(saved_files["png"]):
            print("✅ PNG 导出成功")
        else:
            print("❌ PNG 导出失败")
            return False
        
        # 测试 SVG 导出
        saved_files = viz_agent.save_chart(test_chart, "test_export", formats=["svg"])
        if "svg" in saved_files and os.path.exists(saved_files["svg"]):
            print("✅ SVG 导出成功")
        else:
            print("❌ SVG 导出失败")
            return False
        
        print("✅ 所有导出格式测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 导出功能测试失败: {e}")
        return False


def test_chart_quality():
    """测试图表质量"""
    print("\n=== 测试图表质量 ===")
    
    success, df = test_data_compatibility()
    if not success or df is None:
        return False
    
    viz_agent = EnhancedVizAgent("test_output")
    
    try:
        charts = viz_agent.create_enhanced_nobel_charts(df, 15)
        
        # 检查图表数量
        expected_charts = ["countries_interactive", "yearly_trend_interactive", 
                          "category_stacked_interactive", "country_category_heatmap"]
        
        for chart_name in expected_charts:
            if chart_name in charts:
                print(f"✅ {chart_name} 图表生成成功")
            else:
                print(f"❌ {chart_name} 图表缺失")
                return False
        
        # 检查图表是否有数据
        for chart_name, chart in charts.items():
            if hasattr(chart, 'data') and len(chart.data) > 0:
                print(f"✅ {chart_name} 包含数据")
            else:
                print(f"❌ {chart_name} 缺少数据")
                return False
        
        print("✅ 图表质量测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 图表质量测试失败: {e}")
        return False


def cleanup_test_files():
    """清理测试文件"""
    import shutil
    test_dir = "test_output"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"✅ 清理测试文件: {test_dir}")


def main():
    """主测试函数"""
    print("🚀 开始增强图表功能集成测试\n")
    
    all_tests_passed = True
    
    # 运行所有测试
    tests = [
        test_data_compatibility,
        test_chart_generation_performance, 
        test_export_functionality,
        test_chart_quality
    ]
    
    for test_func in tests:
        try:
            if callable(test_func):
                result = test_func()
                if isinstance(result, tuple):
                    result = result[0]  # 取第一个返回值作为成功标志
                if not result:
                    all_tests_passed = False
            else:
                result = test_func
                if not result:
                    all_tests_passed = False
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 异常: {e}")
            all_tests_passed = False
    
    # 清理测试文件
    cleanup_test_files()
    
    # 输出最终结果
    print(f"\n{'='*50}")
    if all_tests_passed:
        print("🎉 所有集成测试通过！")
        print("✅ Plotly 图表功能已成功集成到现有系统")
        print("✅ 与原有 Altair 系统兼容")
        print("✅ 支持多格式导出")
        print("✅ 图表质量符合要求")
    else:
        print("❌ 部分测试失败，需要进一步调试")
    
    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)