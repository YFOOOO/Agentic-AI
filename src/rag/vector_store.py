"""
向量数据库封装类

使用ChromaDB作为底层向量存储，提供文档嵌入、存储和相似性检索功能
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logging.warning("ChromaDB或sentence-transformers未安装，RAG功能将不可用")

class VectorStore:
    """向量数据库管理类"""
    
    def __init__(
        self, 
        collection_name: str = "literature_knowledge",
        persist_directory: str = "artifacts/rag/chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        初始化向量数据库
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录
            embedding_model: 嵌入模型名称
        """
        if not CHROMA_AVAILABLE:
            raise ImportError("请安装chromadb和sentence-transformers: pip install chromadb sentence-transformers")
            
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.embedding_model_name = embedding_model
        
        # 创建持久化目录
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logging.info(f"向量数据库初始化完成: {collection_name}")
    
    def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: Optional[List[str]] = None
    ) -> None:
        """
        添加文档到向量数据库
        
        Args:
            documents: 文档文本列表
            metadatas: 文档元数据列表
            ids: 文档ID列表，如果为None则自动生成
        """
        if not documents:
            return
            
        # 生成嵌入向量
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # 生成ID（如果未提供）
        if ids is None:
            ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]
        
        # 添加到集合
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logging.info(f"成功添加 {len(documents)} 个文档到向量数据库")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        相似性搜索
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
            
        Returns:
            搜索结果列表，包含文档、元数据和相似度分数
        """
        # 生成查询嵌入
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # 执行搜索
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"][0] else {},
                    "similarity_score": 1 - results["distances"][0][i],  # 转换为相似度分数
                    "id": results["ids"][0][i] if results["ids"] else None
                })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "embedding_model": self.embedding_model_name,
            "persist_directory": str(self.persist_directory)
        }
    
    def clear_collection(self) -> None:
        """清空集合"""
        # 删除现有集合
        self.client.delete_collection(self.collection_name)
        # 重新创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logging.info(f"集合 {self.collection_name} 已清空")