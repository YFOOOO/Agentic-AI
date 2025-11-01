"""
RAG系统服务层
提供文档处理、向量搜索和知识检索的服务接口
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store import VectorStore
from src.rag.knowledge_retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)

class RAGService:
    """RAG系统服务类"""
    
    def __init__(self):
        """初始化RAG服务"""
        self.document_processor = None
        self.vector_store = None
        self.knowledge_retriever = None
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化RAG组件"""
        try:
            # 初始化文档处理器
            self.document_processor = DocumentProcessor()
            logger.info("✅ 文档处理器初始化成功")
            
            # 初始化向量存储
            self.vector_store = VectorStore()
            logger.info("✅ 向量存储初始化成功")
            
            # 初始化知识检索器（它会创建自己的vector_store和document_processor）
            self.knowledge_retriever = KnowledgeRetriever()
            logger.info("✅ 知识检索器初始化成功")
            
        except Exception as e:
            logger.error(f"❌ RAG组件初始化失败: {e}")
            raise
    
    async def process_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理文档并添加到向量存储
        
        Args:
            file_path: 文档文件路径
            metadata: 文档元数据
            
        Returns:
            处理结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 处理文档
            chunks = self.document_processor.process_document(file_path)
            logger.info(f"📄 文档处理完成，生成 {len(chunks)} 个文本块")
            
            # 添加到向量存储
            doc_ids = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "source": file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **(metadata or {})
                }
                
                doc_id = self.vector_store.add_document(
                    content=chunk,
                    metadata=chunk_metadata
                )
                doc_ids.append(doc_id)
            
            logger.info(f"💾 文档已添加到向量存储，生成 {len(doc_ids)} 个文档ID")
            
            return {
                "success": True,
                "message": "文档处理成功",
                "chunks_count": len(chunks),
                "document_ids": doc_ids,
                "file_path": file_path
            }
            
        except Exception as e:
            logger.error(f"❌ 文档处理失败: {e}")
            return {
                "success": False,
                "message": f"文档处理失败: {str(e)}",
                "error": str(e)
            }
    
    async def search_documents(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        搜索相关文档
        
        Args:
            query: 搜索查询
            n_results: 返回结果数量
            
        Returns:
            搜索结果
        """
        try:
            # 执行搜索
            results = self.knowledge_retriever.search(
                query=query,
                n_results=n_results
            )
            
            logger.info(f"🔍 搜索完成，找到 {len(results)} 个相关文档")
            
            return {
                "success": True,
                "message": "搜索完成",
                "query": query,
                "results_count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ 文档搜索失败: {e}")
            return {
                "success": False,
                "message": f"搜索失败: {str(e)}",
                "error": str(e)
            }
    
    async def get_query_suggestions(self, query: str, n_suggestions: int = 3) -> Dict[str, Any]:
        """
        获取查询建议
        
        Args:
            query: 原始查询
            n_suggestions: 建议数量
            
        Returns:
            查询建议
        """
        try:
            # 获取相关查询建议
            suggestions = self.knowledge_retriever.suggest_related_queries(
                query=query,
                n_suggestions=n_suggestions
            )
            
            logger.info(f"💡 生成 {len(suggestions)} 个查询建议")
            
            return {
                "success": True,
                "message": "查询建议生成成功",
                "original_query": query,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"❌ 查询建议生成失败: {e}")
            return {
                "success": False,
                "message": f"查询建议生成失败: {str(e)}",
                "error": str(e)
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        获取RAG系统统计信息
        
        Returns:
            统计信息
        """
        try:
            # 获取向量存储统计
            collection_info = self.vector_store.get_collection_info()
            
            return {
                "success": True,
                "message": "统计信息获取成功",
                "statistics": {
                    "total_documents": collection_info.get("count", 0),
                    "collection_name": collection_info.get("name", "unknown"),
                    "vector_store_status": "active",
                    "document_processor_status": "active",
                    "knowledge_retriever_status": "active",
                    "embedding_model": collection_info.get("embedding_model", "unknown")
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 统计信息获取失败: {e}")
            return {
                "success": False,
                "message": f"统计信息获取失败: {str(e)}",
                "error": str(e)
            }

# 全局RAG服务实例
rag_service = RAGService()