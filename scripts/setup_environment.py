#!/usr/bin/env python3
"""
环境设置脚本

自动化配置不同环境的设置流程，简化团队成员的环境配置。
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.mcp.api_key_manager import APIKeyManager
except ImportError:
    APIKeyManager = None


class EnvironmentSetup:
    """环境设置管理器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.env_configs = {
            'local': '.env.local',
            'test': '.env.test',
            'prod': '.env.prod'
        }
    
    def setup_environment(self, env_type: str, interactive: bool = True) -> bool:
        """
        设置指定环境
        
        Args:
            env_type: 环境类型 (local, test, prod)
            interactive: 是否交互式配置
            
        Returns:
            bool: 设置是否成功
        """
        print(f"🚀 开始设置 {env_type} 环境...")
        
        try:
            # 1. 复制环境配置文件
            if not self._copy_env_config(env_type):
                return False
            
            # 2. 安装依赖
            if not self._install_dependencies(env_type):
                return False
            
            # 3. 配置API Keys（交互式）
            if interactive and env_type == 'local':
                self._configure_api_keys_interactive()
            
            # 4. 验证配置
            if not self._validate_configuration():
                return False
            
            # 5. 运行环境特定的设置
            if not self._run_environment_specific_setup(env_type):
                return False
            
            print(f"✅ {env_type} 环境设置完成！")
            return True
            
        except Exception as e:
            print(f"❌ 环境设置失败: {e}")
            return False
    
    def _copy_env_config(self, env_type: str) -> bool:
        """复制环境配置文件"""
        source_file = self.project_root / self.env_configs[env_type]
        target_file = self.project_root / '.env'
        
        if not source_file.exists():
            print(f"❌ 配置文件不存在: {source_file}")
            return False
        
        try:
            shutil.copy2(source_file, target_file)
            print(f"📋 已复制配置文件: {source_file} -> {target_file}")
            return True
        except Exception as e:
            print(f"❌ 复制配置文件失败: {e}")
            return False
    
    def _install_dependencies(self, env_type: str) -> bool:
        """安装依赖包"""
        print("📦 安装依赖包...")
        
        try:
            # 基础依赖
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ 安装基础依赖失败: {result.stderr}")
                return False
            
            # 测试依赖（仅测试环境）
            if env_type == 'test':
                test_req_file = self.project_root / 'requirements-test.txt'
                if test_req_file.exists():
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '-r', 'requirements-test.txt'
                    ], cwd=self.project_root, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"❌ 安装测试依赖失败: {result.stderr}")
                        return False
            
            print("✅ 依赖包安装完成")
            return True
            
        except Exception as e:
            print(f"❌ 安装依赖包异常: {e}")
            return False
    
    def _configure_api_keys_interactive(self):
        """交互式配置API Keys"""
        print("\n🔐 配置API Keys...")
        print("请输入你的API Keys（留空跳过）:")
        
        api_keys = {
            'DASHSCOPE_API_KEY': 'Dashscope API Key (用于qwen模型)',
            'DEEPSEEK_API_KEY': 'DeepSeek API Key',
            'OPENAI_API_KEY': 'OpenAI API Key'
        }
        
        env_file = self.project_root / '.env'
        
        for key_name, description in api_keys.items():
            current_value = os.getenv(key_name, '')
            if current_value:
                print(f"  {description}: 已配置 ({current_value[:8]}...)")
                continue
            
            value = input(f"  {description}: ").strip()
            if value:
                self._update_env_file(env_file, key_name, value)
                print(f"    ✅ 已设置 {key_name}")
    
    def _update_env_file(self, env_file: Path, key: str, value: str):
        """更新环境变量文件"""
        try:
            # 读取现有内容
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # 查找并更新或添加键值对
            key_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f'{key}='):
                    lines[i] = f'{key}={value}\n'
                    key_found = True
                    break
            
            if not key_found:
                lines.append(f'{key}={value}\n')
            
            # 写回文件
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
        except Exception as e:
            print(f"❌ 更新环境文件失败: {e}")
    
    def _validate_configuration(self) -> bool:
        """验证配置"""
        print("🔍 验证配置...")
        
        try:
            # 检查环境变量文件
            env_file = self.project_root / '.env'
            if not env_file.exists():
                print("❌ .env 文件不存在")
                return False
            
            # 验证API Keys（如果有API Key管理器）
            if APIKeyManager:
                try:
                    manager = APIKeyManager(str(env_file))
                    status = manager.get_status()
                    
                    has_valid_keys = False
                    for key_name, key_info in status['keys'].items():
                        if key_info.get('has_key'):
                            has_valid_keys = True
                            print(f"  ✅ {key_name}: 已配置")
                    
                    if not has_valid_keys:
                        print("⚠️  未配置任何API Key，某些功能可能无法使用")
                    
                except Exception as e:
                    print(f"⚠️  API Key验证异常: {e}")
            
            print("✅ 配置验证完成")
            return True
            
        except Exception as e:
            print(f"❌ 配置验证失败: {e}")
            return False
    
    def _run_environment_specific_setup(self, env_type: str) -> bool:
        """运行环境特定的设置"""
        print(f"⚙️  执行 {env_type} 环境特定设置...")
        
        try:
            if env_type == 'local':
                # 本地环境：检查本地aisuite路径
                self._setup_local_aisuite()
                
            elif env_type == 'test':
                # 测试环境：运行测试验证
                self._validate_test_environment()
                
            elif env_type == 'prod':
                # 生产环境：检查生产配置
                self._validate_production_environment()
            
            return True
            
        except Exception as e:
            print(f"❌ 环境特定设置失败: {e}")
            return False
    
    def _setup_local_aisuite(self):
        """设置本地aisuite"""
        from dotenv import load_dotenv
        load_dotenv(self.project_root / '.env')
        
        aisuite_path = os.getenv('AISUITE_PATH')
        if aisuite_path and Path(aisuite_path).exists():
            print(f"  ✅ 本地aisuite路径: {aisuite_path}")
        else:
            print("  ⚠️  本地aisuite路径未配置或不存在")
            print("     将使用标准aisuite包")
    
    def _validate_test_environment(self):
        """验证测试环境"""
        print("  🧪 验证测试环境...")
        
        # 运行简单的导入测试
        try:
            result = subprocess.run([
                sys.executable, '-c', 
                'import src.mcp.orchestrator; print("✅ 模块导入成功")'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ 模块导入测试通过")
            else:
                print(f"  ❌ 模块导入测试失败: {result.stderr}")
                
        except Exception as e:
            print(f"  ❌ 测试环境验证异常: {e}")
    
    def _validate_production_environment(self):
        """验证生产环境"""
        print("  🚀 验证生产环境配置...")
        
        from dotenv import load_dotenv
        load_dotenv(self.project_root / '.env')
        
        # 检查关键配置
        critical_configs = [
            'NOBEL_LLM_MODEL',
            'ENVIRONMENT'
        ]
        
        for config in critical_configs:
            value = os.getenv(config)
            if value:
                print(f"  ✅ {config}: {value}")
            else:
                print(f"  ⚠️  {config}: 未配置")
    
    def list_environments(self):
        """列出可用环境"""
        print("📋 可用环境配置:")
        
        for env_type, config_file in self.env_configs.items():
            config_path = self.project_root / config_file
            status = "✅ 存在" if config_path.exists() else "❌ 缺失"
            
            print(f"  {env_type:8} | {config_file:12} | {status}")
    
    def show_current_environment(self):
        """显示当前环境信息"""
        print("🔍 当前环境信息:")
        
        env_file = self.project_root / '.env'
        if not env_file.exists():
            print("  ❌ 未找到 .env 文件")
            return
        
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        key_info = [
            ('环境类型', 'ENVIRONMENT'),
            ('LLM模型', 'NOBEL_LLM_MODEL'),
            ('调试模式', 'DEBUG'),
            ('日志级别', 'LOG_LEVEL')
        ]
        
        for label, key in key_info:
            value = os.getenv(key, '未配置')
            print(f"  {label}: {value}")
        
        # API Keys状态
        if APIKeyManager:
            try:
                manager = APIKeyManager(str(env_file))
                status = manager.get_status()
                
                print("\n  API Keys状态:")
                for key_name, key_info in status['keys'].items():
                    if key_info.get('has_key'):
                        masked = key_info.get('masked_key', '***')
                        print(f"    {key_name}: ✅ {masked}")
                    else:
                        print(f"    {key_name}: ❌ 未配置")
                        
            except Exception as e:
                print(f"  ⚠️  API Key状态检查异常: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='环境设置脚本')
    parser.add_argument('command', nargs='?', choices=['setup', 'list', 'status'], 
                       default='setup', help='执行的命令')
    parser.add_argument('--env', choices=['local', 'test', 'prod'], 
                       default='local', help='环境类型')
    parser.add_argument('--non-interactive', action='store_true', 
                       help='非交互式模式')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    setup = EnvironmentSetup(project_root)
    
    if args.command == 'setup':
        interactive = not args.non_interactive
        success = setup.setup_environment(args.env, interactive)
        sys.exit(0 if success else 1)
        
    elif args.command == 'list':
        setup.list_environments()
        
    elif args.command == 'status':
        setup.show_current_environment()


if __name__ == '__main__':
    main()