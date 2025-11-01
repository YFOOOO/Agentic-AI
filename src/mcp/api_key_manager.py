"""
API Key 管理模块

提供API Key的自动更新、验证和轮换功能，确保测试和生产环境的稳定性。
"""

import os
import time
import json
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key

logger = logging.getLogger(__name__)


class APIKeyManager:
    """API Key 管理器"""
    
    def __init__(self, env_file: str = ".env"):
        """
        初始化API Key管理器
        
        Args:
            env_file: 环境变量文件路径
        """
        self.env_file = env_file
        self.load_config()
        self.last_update_time = {}
        self.validation_cache = {}
        
        # 初始化加密器（如果启用）
        if self.config.get('enable_encryption', False):
            self._init_encryption()
    
    def load_config(self):
        """加载配置"""
        load_dotenv(self.env_file)
        
        self.config = {
            'enable_auto_update': os.getenv('ENABLE_API_KEY_AUTO_UPDATE', 'false').lower() == 'true',
            'update_interval': int(os.getenv('API_KEY_UPDATE_INTERVAL', '3600')),
            'validation_enabled': os.getenv('API_KEY_VALIDATION_ENABLED', 'false').lower() == 'true',
            'rotation_enabled': os.getenv('API_KEY_ROTATION_ENABLED', 'false').lower() == 'true',
            'enable_encryption': os.getenv('ENABLE_API_KEY_ENCRYPTION', 'false').lower() == 'true',
        }
        
        # 支持的API Key配置
        self.api_keys = {
            'OPENAI_API_KEY': {
                'current': os.getenv('OPENAI_API_KEY'),
                'backup': os.getenv('OPENAI_API_KEY_BACKUP'),
                'validation_url': 'https://api.openai.com/v1/models',
            },
            'DASHSCOPE_API_KEY': {
                'current': os.getenv('DASHSCOPE_API_KEY'),
                'backup': os.getenv('DASHSCOPE_API_KEY_BACKUP'),
                'validation_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
            },
            'DEEPSEEK_API_KEY': {
                'current': os.getenv('DEEPSEEK_API_KEY'),
                'backup': os.getenv('DEEPSEEK_API_KEY_BACKUP'),
                'validation_url': 'https://api.deepseek.com/v1/models',
            }
        }
    
    def _init_encryption(self):
        """初始化加密功能"""
        key_file = Path('.api_key_encryption.key')
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # 设置文件权限为只读
            key_file.chmod(0o600)
        
        self.cipher = Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """加密API Key"""
        if not hasattr(self, 'cipher'):
            return api_key
        
        encrypted = self.cipher.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API Key"""
        if not hasattr(self, 'cipher'):
            return encrypted_key
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_key.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.warning(f"解密API Key失败: {e}")
            return encrypted_key
    
    def validate_api_key(self, key_name: str, api_key: str) -> bool:
        """
        验证API Key是否有效
        
        Args:
            key_name: API Key名称
            api_key: API Key值
            
        Returns:
            bool: 是否有效
        """
        if not self.config['validation_enabled']:
            return True
        
        # 检查缓存
        cache_key = hashlib.md5(f"{key_name}:{api_key}".encode()).hexdigest()
        if cache_key in self.validation_cache:
            cached_time, is_valid = self.validation_cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=30):
                return is_valid
        
        try:
            import requests
            
            key_config = self.api_keys.get(key_name, {})
            validation_url = key_config.get('validation_url')
            
            if not validation_url:
                logger.warning(f"未配置验证URL: {key_name}")
                return True
            
            # 根据不同的API提供商进行验证
            if 'openai' in validation_url or 'deepseek' in validation_url:
                headers = {'Authorization': f'Bearer {api_key}'}
                response = requests.get(validation_url, headers=headers, timeout=10)
                is_valid = response.status_code == 200
            
            elif 'dashscope' in validation_url:
                headers = {'Authorization': f'Bearer {api_key}'}
                # Dashscope需要POST请求进行验证
                data = {
                    "model": "qwen-turbo",
                    "input": {"messages": [{"role": "user", "content": "test"}]},
                    "parameters": {"max_tokens": 1}
                }
                response = requests.post(validation_url, headers=headers, json=data, timeout=10)
                is_valid = response.status_code in [200, 400]  # 400也表示API Key有效但请求格式问题
            
            else:
                is_valid = True
            
            # 缓存结果
            self.validation_cache[cache_key] = (datetime.now(), is_valid)
            
            if is_valid:
                logger.info(f"API Key验证成功: {key_name}")
            else:
                logger.error(f"API Key验证失败: {key_name}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"API Key验证异常: {key_name}, {e}")
            return False
    
    def update_api_key(self, key_name: str, new_key: str) -> bool:
        """
        更新API Key
        
        Args:
            key_name: API Key名称
            new_key: 新的API Key值
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证新的API Key
            if not self.validate_api_key(key_name, new_key):
                logger.error(f"新API Key验证失败: {key_name}")
                return False
            
            # 备份当前API Key
            current_key = self.api_keys[key_name]['current']
            if current_key:
                backup_key_name = f"{key_name}_BACKUP"
                set_key(self.env_file, backup_key_name, current_key)
                logger.info(f"已备份当前API Key: {backup_key_name}")
            
            # 加密新API Key（如果启用）
            if self.config['enable_encryption']:
                new_key = self.encrypt_api_key(new_key)
            
            # 更新API Key
            set_key(self.env_file, key_name, new_key)
            self.api_keys[key_name]['current'] = new_key
            self.last_update_time[key_name] = datetime.now()
            
            logger.info(f"API Key更新成功: {key_name}")
            return True
            
        except Exception as e:
            logger.error(f"API Key更新失败: {key_name}, {e}")
            return False
    
    def auto_update_check(self) -> Dict[str, bool]:
        """
        自动检查并更新API Key
        
        Returns:
            Dict[str, bool]: 各API Key的更新结果
        """
        if not self.config['enable_auto_update']:
            return {}
        
        results = {}
        current_time = datetime.now()
        
        for key_name, key_config in self.api_keys.items():
            current_key = key_config['current']
            if not current_key:
                continue
            
            # 检查是否需要更新
            last_update = self.last_update_time.get(key_name)
            if last_update:
                time_diff = current_time - last_update
                if time_diff.total_seconds() < self.config['update_interval']:
                    continue
            
            # 验证当前API Key
            if self.config['enable_encryption']:
                validation_key = self.decrypt_api_key(current_key)
            else:
                validation_key = current_key
            
            is_valid = self.validate_api_key(key_name, validation_key)
            
            if not is_valid:
                # 尝试使用备份API Key
                backup_key = key_config.get('backup')
                if backup_key:
                    logger.info(f"当前API Key无效，尝试使用备份: {key_name}")
                    success = self.update_api_key(key_name, backup_key)
                    results[key_name] = success
                else:
                    logger.error(f"API Key无效且无备份: {key_name}")
                    results[key_name] = False
            else:
                results[key_name] = True
        
        return results
    
    def rotate_api_keys(self) -> Dict[str, bool]:
        """
        轮换API Keys（如果启用）
        
        Returns:
            Dict[str, bool]: 轮换结果
        """
        if not self.config['rotation_enabled']:
            return {}
        
        results = {}
        
        for key_name, key_config in self.api_keys.items():
            current_key = key_config['current']
            backup_key = key_config.get('backup')
            
            if current_key and backup_key:
                # 交换当前和备份API Key
                success = self.update_api_key(key_name, backup_key)
                if success:
                    # 将原来的当前key设为备份
                    backup_key_name = f"{key_name}_BACKUP"
                    set_key(self.env_file, backup_key_name, current_key)
                
                results[key_name] = success
        
        return results
    
    def get_status(self) -> Dict:
        """
        获取API Key管理状态
        
        Returns:
            Dict: 状态信息
        """
        status = {
            'config': self.config,
            'keys': {},
            'last_check': datetime.now().isoformat()
        }
        
        for key_name, key_config in self.api_keys.items():
            current_key = key_config['current']
            has_backup = bool(key_config.get('backup'))
            
            if current_key:
                # 不显示完整的API Key，只显示前后几位
                masked_key = f"{current_key[:8]}...{current_key[-4:]}" if len(current_key) > 12 else "***"
                
                status['keys'][key_name] = {
                    'has_key': True,
                    'masked_key': masked_key,
                    'has_backup': has_backup,
                    'last_update': self.last_update_time.get(key_name, {}).isoformat() if self.last_update_time.get(key_name) else None,
                    'is_encrypted': self.config['enable_encryption']
                }
            else:
                status['keys'][key_name] = {
                    'has_key': False,
                    'has_backup': has_backup
                }
        
        return status


def main():
    """主函数 - 用于测试和手动执行"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API Key管理工具')
    parser.add_argument('--check', action='store_true', help='检查API Key状态')
    parser.add_argument('--validate', action='store_true', help='验证所有API Key')
    parser.add_argument('--auto-update', action='store_true', help='执行自动更新检查')
    parser.add_argument('--rotate', action='store_true', help='轮换API Keys')
    parser.add_argument('--env-file', default='.env', help='环境变量文件路径')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = APIKeyManager(args.env_file)
    
    if args.check:
        status = manager.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.validate:
        for key_name, key_config in manager.api_keys.items():
            current_key = key_config['current']
            if current_key:
                if manager.config['enable_encryption']:
                    validation_key = manager.decrypt_api_key(current_key)
                else:
                    validation_key = current_key
                
                is_valid = manager.validate_api_key(key_name, validation_key)
                print(f"{key_name}: {'✅ 有效' if is_valid else '❌ 无效'}")
    
    elif args.auto_update:
        results = manager.auto_update_check()
        for key_name, success in results.items():
            print(f"{key_name}: {'✅ 更新成功' if success else '❌ 更新失败'}")
    
    elif args.rotate:
        results = manager.rotate_api_keys()
        for key_name, success in results.items():
            print(f"{key_name}: {'✅ 轮换成功' if success else '❌ 轮换失败'}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()