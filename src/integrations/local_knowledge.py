"""
本地知识库数据源集成模块

集成现有的RAG系统，支持从本地向量数据库检索文献信息。
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os

from .base_source import DataSource, SearchResult


class LocalKnowledgeSource(DataSource):
    """本地知识库数据源实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化本地知识库数据源
        
        Args:
            config: 配置字典，包含：
                - rag_system_path: RAG系统路径
                - collection_name: 向量数据库集合名称
                - top_k: 检索结果数量
        """
        super().__init__(config)
        self.rag_system_path = config.get('rag_system_path', 'src/rag')
        self.collection_name = config.get('collection_name', 'literature')
        self.top_k = config.get('top_k', 10)
        self._knowledge_retriever = None
        
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        # 检查RAG系统路径是否存在
        if not os.path.exists(self.rag_system_path):
            return False
        return True
    
    def _get_knowledge_retriever(self):
        """获取知识检索器实例"""
        if self._knowledge_retriever is None:
            try:
                # 动态导入RAG系统
                sys.path.append(self.rag_system_path)
                from knowledge_retriever import KnowledgeRetriever
                
                self._knowledge_retriever = KnowledgeRetriever()
            except Exception as e:
                print(f"初始化知识检索器失败: {e}")
                return None
        
        return self._knowledge_retriever
    
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        搜索本地知识库
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        retriever = self._get_knowledge_retriever()
        if not retriever:
            return []
        
        try:
            # 使用RAG系统进行搜索
            search_results = retriever.search(query, top_k=min(limit, self.top_k))
            
            results = []
            for result in search_results:
                # 解析RAG系统返回的结果
                content = result.get('content', '')
                metadata = result.get('metadata', {})
                
                # 尝试从内容中提取标题和摘要
                lines = content.split('\n')
                title = lines[0] if lines else '未知标题'
                abstract = content[:500] + '...' if len(content) > 500 else content
                
                # 从元数据中提取信息
                authors = metadata.get('authors', [])
                if isinstance(authors, str):
                    authors = [authors]
                
                url = metadata.get('url', '')
                source_file = metadata.get('source', '')
                
                search_result = SearchResult(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=url,
                    source='local_knowledge',
                    metadata={
                        'source_file': source_file,
                        'score': result.get('score', 0.0),
                        'chunk_id': result.get('id', ''),
                        **metadata
                    }
                )
                
                results.append(search_result)
            
            return results
            
        except Exception as e:
            print(f"本地知识库搜索错误: {e}")
            return []
    
    async def get_by_id(self, item_id: str) -> Optional[SearchResult]:
        """
        根据ID获取特定文档
        
        Args:
            item_id: 文档ID
            
        Returns:
            文档详情或None
        """
        retriever = self._get_knowledge_retriever()
        if not retriever:
            return None
        
        try:
            # 这里需要根据实际的RAG系统API来实现
            # 假设有get_by_id方法
            if hasattr(retriever, 'get_by_id'):
                result = retriever.get_by_id(item_id)
                if result:
                    content = result.get('content', '')
                    metadata = result.get('metadata', {})
                    
                    lines = content.split('\n')
                    title = lines[0] if lines else '未知标题'
                    abstract = content[:500] + '...' if len(content) > 500 else content
                    
                    authors = metadata.get('authors', [])
                    if isinstance(authors, str):
                        authors = [authors]
                    
                    return SearchResult(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        url=metadata.get('url', ''),
                        source='local_knowledge',
                        metadata=metadata
                    )
            
            return None
            
        except Exception as e:
            print(f"获取本地文档错误: {e}")
            return None
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """
        添加文档到本地知识库
        
        Args:
            content: 文档内容
            metadata: 文档元数据
            
        Returns:
            是否添加成功
        """
        retriever = self._get_knowledge_retriever()
        if not retriever:
            return False
        
        try:
            # 使用RAG系统添加文档
            retriever.add_document(content, metadata.get('source', ''), metadata)
            return True
            
        except Exception as e:
            print(f"添加文档到本地知识库错误: {e}")
            return False
    
    def get_source_info(self) -> Dict[str, Any]:
        """获取数据源信息"""
        return {
            'name': 'Local Knowledge Base',
            'type': 'vector_database',
            'description': '本地RAG向量知识库',
            'capabilities': ['search', 'get_by_id', 'add_document', 'semantic_search'],
            'config_required': ['rag_system_path']
        }