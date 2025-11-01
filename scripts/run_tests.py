#!/usr/bin/env python3
"""
测试运行脚本

提供便捷的测试执行选项，包括不同类型的测试和覆盖率报告。

使用方法:
    python run_tests.py --help
    python run_tests.py --all
    python run_tests.py --unit
    python run_tests.py --integration
    python run_tests.py --coverage
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并处理结果"""
    if description:
        print(f"\n🔄 {description}")
        print("=" * 50)
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def check_dependencies():
    """检查测试依赖是否安装"""
    print("🔍 检查测试依赖...")
    
    required_packages = ['pytest', 'coverage', 'flake8']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements-test.txt")
        return False
    
    print("✅ 所有依赖已安装")
    return True


def run_linting():
    """运行代码质量检查"""
    return run_command(['flake8', 'src', 'tests'], "运行代码质量检查")


def run_unit_tests():
    """运行单元测试"""
    return run_command(['pytest', '-m', 'unit', '-v'], "运行单元测试")


def run_integration_tests():
    """运行集成测试"""
    return run_command(['pytest', '-m', 'integration', '-v'], "运行集成测试")


def run_all_tests():
    """运行所有测试"""
    return run_command(['pytest', '-v'], "运行所有测试")


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    cmd = [
        'pytest', 
        '--cov=src', 
        '--cov-report=html', 
        '--cov-report=term-missing',
        '--cov-fail-under=80',
        '-v'
    ]
    success = run_command(cmd, "运行测试并生成覆盖率报告")
    
    if success:
        print("\n📊 覆盖率报告已生成:")
        print("  - HTML报告: htmlcov/index.html")
        print("  - 在浏览器中查看: open htmlcov/index.html")
    
    return success


def run_fast_tests():
    """运行快速测试（排除慢速测试）"""
    return run_command(['pytest', '-m', 'not slow', '-v'], "运行快速测试")


def run_specific_test(test_path):
    """运行特定测试"""
    return run_command(['pytest', test_path, '-v'], f"运行测试: {test_path}")


def main():
    parser = argparse.ArgumentParser(description="测试运行脚本")
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--coverage', action='store_true', help='运行测试并生成覆盖率报告')
    parser.add_argument('--fast', action='store_true', help='运行快速测试（排除慢速测试）')
    parser.add_argument('--lint', action='store_true', help='运行代码质量检查')
    parser.add_argument('--test', type=str, help='运行特定测试文件或测试方法')
    parser.add_argument('--check-deps', action='store_true', help='检查测试依赖')
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🧪 Agentic-AI 测试运行器")
    print("=" * 50)
    
    # 检查依赖
    if args.check_deps:
        check_dependencies()
        return
    
    if not check_dependencies():
        sys.exit(1)
    
    success = True
    
    # 运行相应的测试
    if args.lint:
        success &= run_linting()
    
    if args.unit:
        success &= run_unit_tests()
    
    if args.integration:
        success &= run_integration_tests()
    
    if args.all:
        success &= run_all_tests()
    
    if args.coverage:
        success &= run_tests_with_coverage()
    
    if args.fast:
        success &= run_fast_tests()
    
    if args.test:
        success &= run_specific_test(args.test)
    
    # 输出结果
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有测试执行成功!")
    else:
        print("❌ 部分测试执行失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()