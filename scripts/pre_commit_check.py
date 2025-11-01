#!/usr/bin/env python3
"""
预提交测试脚本

在提交代码到Git仓库之前运行的快速验证脚本。
包括基本的测试、代码质量检查和覆盖率验证。

使用方法:
    python pre_commit_test.py
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description="", ignore_errors=False):
    """运行命令并处理结果"""
    if description:
        print(f"\n🔄 {description}")
        print("=" * 50)
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 成功")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"⚠️  警告: {e}")
            if e.stderr:
                print(f"错误输出: {e.stderr}")
            return False
        else:
            print(f"❌ 失败: {e}")
            if e.stderr:
                print(f"错误输出: {e.stderr}")
            return False


def main():
    print("🚀 预提交测试检查")
    print("=" * 50)
    
    success = True
    
    # 1. 运行快速测试（排除慢速测试）
    print("\n📋 第1步: 运行快速测试")
    if not run_command(['pytest', 'tests/', '-m', 'not slow', '-q'], ignore_errors=True):
        print("⚠️  部分测试失败，但继续进行其他检查")
        success = False
    
    # 2. 检查测试覆盖率
    print("\n📊 第2步: 检查测试覆盖率")
    coverage_success = True
    if not run_command(['coverage', 'run', '-m', 'pytest', 'tests/', '-q'], ignore_errors=True):
        coverage_success = False
    
    if coverage_success:
        if not run_command(['coverage', 'report', '--fail-under=60'], ignore_errors=True):
            print("⚠️  测试覆盖率低于60%")
            success = False
    
    # 3. 代码质量检查（忽略错误，仅作警告）
    print("\n🔍 第3步: 代码质量检查")
    run_command(['flake8', 'src/', '--count', '--select=E9,F63,F7,F82', '--show-source', '--statistics'], 
                "检查严重的代码错误", ignore_errors=True)
    
    # 4. 检查Git状态
    print("\n📝 第4步: Git状态检查")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("📋 待提交的文件:")
            print(result.stdout)
        else:
            print("✅ 工作目录干净")
    except subprocess.CalledProcessError:
        print("⚠️  无法检查Git状态（可能不在Git仓库中）")
    
    # 5. 生成测试报告摘要
    print("\n📈 第5步: 测试摘要")
    print("=" * 50)
    
    if success:
        print("✅ 预提交检查通过!")
        print("\n💡 建议的提交流程:")
        print("   1. git add .")
        print("   2. git commit -m '你的提交信息'")
        print("   3. git push")
        
        print("\n📊 查看详细覆盖率报告:")
        print("   coverage html && open htmlcov/index.html")
        
    else:
        print("⚠️  预提交检查发现问题!")
        print("\n🔧 建议的修复步骤:")
        print("   1. 修复失败的测试")
        print("   2. 提高测试覆盖率")
        print("   3. 修复代码质量问题")
        print("   4. 重新运行: python pre_commit_test.py")
    
    print("\n📚 更多测试选项:")
    print("   python run_tests.py --help")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)