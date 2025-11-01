"""
Zotero数据源集成模块

支持从Zotero API获取文献数据，包括个人库和群组库的访问。
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_source import DataSource, SearchResult


class ZoteroSource(DataSource):
    """Zotero数据源实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Zotero数据源
        
        Args:
            config: 配置字典，包含：
                - api_key: Zotero API密钥
                - user_id: 用户ID（可选）
                - group_id: 群组ID（可选）
                - timeout: 请求超时时间
                - max_retries: 最大重试次数
        """
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.user_id = config.get('user_id')
        self.group_id = config.get('group_id')
        self.base_url = 'https://api.zotero.org'
        
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.api_key:
            return False
        if not self.user_id and not self.group_id:
            return False
        return True
    
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        搜索Zotero库中的文献
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        if not self.validate_config():
            return []
            
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                # 构建搜索URL
                if self.user_id:
                    url = f"{self.base_url}/users/{self.user_id}/items"
                else:
                    url = f"{self.base_url}/groups/{self.group_id}/items"
                
                headers = {
                    'Zotero-API-Key': self.api_key,
                    'User-Agent': 'LiteratureAgent/1.0'
                }
                
                params = {
                    'q': query,
                    'limit': limit,
                    'format': 'json',
                    'include': 'data'
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        items = await response.json()
                        return self._parse_zotero_items(items)
                    else:
                        print(f"Zotero API错误: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"Zotero搜索错误: {e}")
            return []
    
    async def get_by_id(self, item_id: str) -> Optional[SearchResult]:
        """
        根据ID获取特定文献
        
        Args:
            item_id: Zotero项目ID
            
        Returns:
            文献详情或None
        """
        if not self.validate_config():
            return None
            
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                if self.user_id:
                    url = f"{self.base_url}/users/{self.user_id}/items/{item_id}"
                else:
                    url = f"{self.base_url}/groups/{self.group_id}/items/{item_id}"
                
                headers = {
                    'Zotero-API-Key': self.api_key,
                    'User-Agent': 'LiteratureAgent/1.0'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        item = await response.json()
                        results = self._parse_zotero_items([item])
                        return results[0] if results else None
                    else:
                        return None
                        
        except Exception as e:
            print(f"获取Zotero项目错误: {e}")
            return None
    
    def _parse_zotero_items(self, items: List[Dict]) -> List[SearchResult]:
        """解析Zotero API返回的项目数据"""
        results = []
        
        for item in items:
            try:
                data = item.get('data', {})
                
                # 提取基本信息
                title = data.get('title', '未知标题')
                abstract = data.get('abstractNote', '')
                url = data.get('url', '')
                
                # 提取作者信息
                authors = []
                creators = data.get('creators', [])
                for creator in creators:
                    if creator.get('creatorType') in ['author', 'editor']:
                        first_name = creator.get('firstName', '')
                        last_name = creator.get('lastName', '')
                        if first_name and last_name:
                            authors.append(f"{first_name} {last_name}")
                        elif last_name:
                            authors.append(last_name)
                
                # 提取发表信息
                publication_title = data.get('publicationTitle', '')
                date = data.get('date', '')
                
                # 构建元数据
                metadata = {
                    'publication_title': publication_title,
                    'date': date,
                    'item_type': data.get('itemType', ''),
                    'zotero_key': item.get('key', ''),
                    'tags': [tag.get('tag', '') for tag in data.get('tags', [])]
                }
                
                result = SearchResult(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=url,
                    source='zotero',
                    metadata=metadata
                )
                
                results.append(result)
                
            except Exception as e:
                print(f"解析Zotero项目错误: {e}")
                continue
        
        return results
    
    def get_source_info(self) -> Dict[str, Any]:
        """获取数据源信息"""
        return {
            'name': 'Zotero',
            'type': 'bibliography_manager',
            'description': 'Zotero文献管理系统API',
            'capabilities': ['search', 'get_by_id', 'personal_library', 'group_library'],
            'config_required': ['api_key', 'user_id或group_id']
        }