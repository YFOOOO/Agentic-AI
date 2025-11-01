"""
多源数据集成模块

提供统一的数据源接口，支持：
- Web搜索 (Google Scholar, Semantic Scholar, arXiv)
- Zotero文献库集成
- 本地知识库
- 外部API数据源

设计原则：
1. 统一接口：所有数据源实现相同的接口
2. 可扩展性：易于添加新的数据源
3. 异步处理：支持并发数据获取
4. 错误处理：优雅的错误处理和重试机制
"""

from .base_source import DataSource, SearchResult
from .web_search import WebSearchSource
from .zotero_source import ZoteroSource
from .local_knowledge import LocalKnowledgeSource
from .multi_source_manager import MultiSourceManager

__all__ = [
    'DataSource',
    'SearchResult', 
    'WebSearchSource',
    'ZoteroSource',
    'LocalKnowledgeSource',
    'MultiSourceManager'
]