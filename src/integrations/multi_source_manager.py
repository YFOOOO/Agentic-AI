"""
多源数据管理器

统一管理和协调不同的数据源，提供聚合搜索和数据融合功能。
"""

import asyncio
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
import logging

from .base_source import DataSource, SearchResult
from .web_search import WebSearchSource
from .zotero_source import ZoteroSource
from .local_knowledge import LocalKnowledgeSource


class MultiSourceManager:
    """多源数据管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化多源数据管理器
        
        Args:
            config: 配置字典，包含各个数据源的配置
        """
        self.config = config
        self.sources: Dict[str, DataSource] = {}
        self.logger = logging.getLogger(__name__)
        
        # 注册可用的数据源类型
        self.source_types: Dict[str, Type[DataSource]] = {
            'web_search': WebSearchSource,
            'zotero': ZoteroSource,
            'local_knowledge': LocalKnowledgeSource
        }
        
        # 初始化数据源
        self._initialize_sources()
    
    def _initialize_sources(self):
        """初始化配置的数据源"""
        for source_name, source_config in self.config.items():
            source_type = source_config.get('type')
            
            if source_type in self.source_types:
                try:
                    source_class = self.source_types[source_type]
                    source_instance = source_class(source_config)
                    
                    if source_instance.validate_config():
                        self.sources[source_name] = source_instance
                        self.logger.info(f"成功初始化数据源: {source_name}")
                    else:
                        self.logger.warning(f"数据源配置无效: {source_name}")
                        
                except Exception as e:
                    self.logger.error(f"初始化数据源失败 {source_name}: {e}")
    
    async def search_all(self, query: str, limit_per_source: int = 5) -> Dict[str, List[SearchResult]]:
        """
        在所有数据源中搜索
        
        Args:
            query: 搜索查询
            limit_per_source: 每个数据源的结果限制
            
        Returns:
            按数据源分组的搜索结果
        """
        tasks = []
        source_names = []
        
        for source_name, source in self.sources.items():
            tasks.append(source.search(query, limit_per_source))
            source_names.append(source_name)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            search_results = {}
            for i, result in enumerate(results):
                source_name = source_names[i]
                if isinstance(result, Exception):
                    self.logger.error(f"数据源 {source_name} 搜索失败: {result}")
                    search_results[source_name] = []
                else:
                    search_results[source_name] = result
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"多源搜索失败: {e}")
            return {}
    
    async def search_aggregated(self, query: str, total_limit: int = 20) -> List[SearchResult]:
        """
        聚合搜索，合并所有数据源的结果
        
        Args:
            query: 搜索查询
            total_limit: 总结果限制
            
        Returns:
            合并后的搜索结果列表
        """
        # 计算每个数据源的限制
        limit_per_source = max(1, total_limit // len(self.sources)) if self.sources else 0
        
        # 搜索所有数据源
        source_results = await self.search_all(query, limit_per_source)
        
        # 合并结果
        all_results = []
        for source_name, results in source_results.items():
            for result in results:
                # 确保结果包含数据源信息
                if result.metadata is None:
                    result.metadata = {}
                result.metadata['data_source'] = source_name
                all_results.append(result)
        
        # 去重和排序
        unique_results = self._deduplicate_results(all_results)
        sorted_results = self._sort_results(unique_results, query)
        
        return sorted_results[:total_limit]
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """去除重复结果"""
        seen_titles = set()
        unique_results = []
        
        for result in results:
            # 使用标题的小写版本作为去重键
            title_key = result.title.lower().strip()
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(result)
        
        return unique_results
    
    def _sort_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """对结果进行排序"""
        # 简单的相关性排序：标题包含查询词的排在前面
        query_lower = query.lower()
        
        def relevance_score(result: SearchResult) -> float:
            score = 0.0
            
            # 标题匹配
            if query_lower in result.title.lower():
                score += 2.0
            
            # 摘要匹配
            if result.abstract and query_lower in result.abstract.lower():
                score += 1.0
            
            # 作者匹配
            for author in result.authors:
                if query_lower in author.lower():
                    score += 0.5
            
            # 数据源权重
            source_weights = {
                'web_search': 1.0,
                'local_knowledge': 1.2,  # 本地知识库权重稍高
                'zotero': 1.1
            }
            
            data_source = result.metadata.get('data_source', '') if result.metadata else ''
            score *= source_weights.get(data_source, 1.0)
            
            return score
        
        return sorted(results, key=relevance_score, reverse=True)
    
    async def get_by_id(self, source_name: str, item_id: str) -> Optional[SearchResult]:
        """
        从指定数据源获取特定项目
        
        Args:
            source_name: 数据源名称
            item_id: 项目ID
            
        Returns:
            项目详情或None
        """
        if source_name not in self.sources:
            return None
        
        try:
            return await self.sources[source_name].get_by_id(item_id)
        except Exception as e:
            self.logger.error(f"获取项目失败 {source_name}/{item_id}: {e}")
            return None
    
    def get_available_sources(self) -> Dict[str, Dict[str, Any]]:
        """获取可用数据源信息"""
        sources_info = {}
        
        for source_name, source in self.sources.items():
            sources_info[source_name] = source.get_source_info()
        
        return sources_info
    
    def health_check(self) -> Dict[str, bool]:
        """检查所有数据源的健康状态"""
        health_status = {}
        
        for source_name, source in self.sources.items():
            try:
                health_status[source_name] = source.health_check()
            except Exception as e:
                self.logger.error(f"健康检查失败 {source_name}: {e}")
                health_status[source_name] = False
        
        return health_status
    
    def add_source(self, source_name: str, source_type: str, config: Dict[str, Any]) -> bool:
        """
        动态添加数据源
        
        Args:
            source_name: 数据源名称
            source_type: 数据源类型
            config: 数据源配置
            
        Returns:
            是否添加成功
        """
        if source_type not in self.source_types:
            self.logger.error(f"不支持的数据源类型: {source_type}")
            return False
        
        try:
            source_class = self.source_types[source_type]
            source_instance = source_class(config)
            
            if source_instance.validate_config():
                self.sources[source_name] = source_instance
                self.logger.info(f"成功添加数据源: {source_name}")
                return True
            else:
                self.logger.warning(f"数据源配置无效: {source_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"添加数据源失败 {source_name}: {e}")
            return False
    
    def remove_source(self, source_name: str) -> bool:
        """
        移除数据源
        
        Args:
            source_name: 数据源名称
            
        Returns:
            是否移除成功
        """
        if source_name in self.sources:
            del self.sources[source_name]
            self.logger.info(f"成功移除数据源: {source_name}")
            return True
        else:
            self.logger.warning(f"数据源不存在: {source_name}")
            return False