"""
数据源基类

定义所有数据源必须实现的统一接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """搜索结果数据结构"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    source: str  # 数据源标识
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    citation_count: Optional[int] = None
    keywords: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.metadata is None:
            self.metadata = {}

class DataSource(ABC):
    """数据源抽象基类"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[SearchResult]:
        """
        搜索文献
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            **kwargs: 其他搜索参数
            
        Returns:
            List[SearchResult]: 搜索结果列表
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[SearchResult]:
        """
        根据ID获取特定文献
        
        Args:
            item_id: 文献ID
            
        Returns:
            Optional[SearchResult]: 文献详情
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        pass
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 数据源是否可用
        """
        try:
            # 执行简单的搜索测试
            results = await self.search("test", limit=1)
            return True
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return False
    
    def get_source_info(self) -> Dict[str, Any]:
        """
        获取数据源信息
        
        Returns:
            Dict[str, Any]: 数据源信息
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "config_keys": list(self.config.keys()),
            "is_configured": self.validate_config()
        }