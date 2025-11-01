"""
知识检索器

整合向量存储和文档处理，提供高级的知识检索和增强功能
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .vector_store import VectorStore
from .document_processor import DocumentProcessor

class KnowledgeRetriever:
    """知识检索和增强类"""
    
    def __init__(
        self,
        collection_name: str = "literature_knowledge",
        persist_directory: str = "artifacts/rag/chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        初始化知识检索器
        
        Args:
            collection_name: 向量数据库集合名称
            persist_directory: 持久化目录
            embedding_model: 嵌入模型名称
            chunk_size: 文档块大小
            chunk_overlap: 块重叠大小
        """
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_model=embedding_model
        )
        
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        logging.info("知识检索器初始化完成")
    
    def add_documents_from_text(
        self,
        texts: Union[str, List[str]],
        sources: Optional[Union[str, List[str]]] = None,
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        从文本添加文档到知识库
        
        Args:
            texts: 文档文本或文本列表
            sources: 文档来源或来源列表
            metadata_list: 额外元数据列表
            
        Returns:
            添加结果统计
        """
        # 标准化输入
        if isinstance(texts, str):
            texts = [texts]
        
        if sources is None:
            sources = ["unknown"] * len(texts)
        elif isinstance(sources, str):
            sources = [sources] * len(texts)
        
        if metadata_list is None:
            metadata_list = [{}] * len(texts)
        
        # 处理每个文档
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for i, (text, source, extra_metadata) in enumerate(zip(texts, sources, metadata_list)):
            # 处理文档
            processed_chunks = self.document_processor.process_document(
                text=text,
                source=source,
                additional_metadata=extra_metadata
            )
            
            # 收集块数据
            for j, chunk_data in enumerate(processed_chunks):
                all_chunks.append(chunk_data["text"])
                all_metadatas.append(chunk_data["metadata"])
                all_ids.append(f"{source}_{i}_{j}")
        
        # 添加到向量数据库
        if all_chunks:
            self.vector_store.add_documents(
                documents=all_chunks,
                metadatas=all_metadatas,
                ids=all_ids
            )
        
        return {
            "documents_processed": len(texts),
            "chunks_created": len(all_chunks),
            "total_tokens": sum(chunk["metadata"]["chunk_token_count"] for chunk in 
                              [{"metadata": meta} for meta in all_metadatas])
        }
    
    def add_documents_from_files(
        self,
        file_paths: Union[str, Path, List[Union[str, Path]]],
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        从文件添加文档到知识库
        
        Args:
            file_paths: 文件路径或路径列表
            encoding: 文件编码
            
        Returns:
            添加结果统计
        """
        # 标准化输入
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]
        
        texts = []
        sources = []
        metadata_list = []
        
        for file_path in file_paths:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logging.warning(f"文件不存在: {file_path}")
                continue
            
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                texts.append(content)
                sources.append(str(file_path))
                metadata_list.append({
                    "file_name": file_path.name,
                    "file_extension": file_path.suffix,
                    "file_size": file_path.stat().st_size
                })
                
            except Exception as e:
                logging.error(f"读取文件失败 {file_path}: {e}")
                continue
        
        if not texts:
            return {"documents_processed": 0, "chunks_created": 0, "total_tokens": 0}
        
        return self.add_documents_from_text(texts, sources, metadata_list)
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            filter_metadata: 元数据过滤条件
            min_similarity: 最小相似度阈值
            
        Returns:
            搜索结果列表
        """
        results = self.vector_store.search(
            query=query,
            n_results=n_results,
            where=filter_metadata
        )
        
        # 过滤低相似度结果
        filtered_results = [
            result for result in results 
            if result["similarity_score"] >= min_similarity
        ]
        
        return filtered_results
    
    def get_context_for_query(
        self,
        query: str,
        max_context_length: int = 4000,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        为查询获取上下文信息
        
        Args:
            query: 查询文本
            max_context_length: 最大上下文长度
            n_results: 搜索结果数量
            filter_metadata: 元数据过滤条件
            
        Returns:
            包含上下文和来源信息的字典
        """
        # 搜索相关文档
        results = self.search(
            query=query,
            n_results=n_results,
            filter_metadata=filter_metadata
        )
        
        if not results:
            return {
                "context": "",
                "sources": [],
                "total_chunks": 0,
                "avg_similarity": 0.0
            }
        
        # 构建上下文
        context_parts = []
        sources = set()
        current_length = 0
        
        for result in results:
            chunk_text = result["document"]
            chunk_length = len(chunk_text)
            
            # 检查是否超过长度限制
            if current_length + chunk_length > max_context_length:
                # 尝试截断当前块
                remaining_length = max_context_length - current_length
                if remaining_length > 100:  # 至少保留100字符
                    chunk_text = chunk_text[:remaining_length] + "..."
                    context_parts.append(chunk_text)
                break
            
            context_parts.append(chunk_text)
            current_length += chunk_length
            
            # 收集来源信息
            source = result["metadata"].get("source", "unknown")
            sources.add(source)
        
        # 计算平均相似度
        avg_similarity = sum(r["similarity_score"] for r in results) / len(results)
        
        return {
            "context": "\n\n".join(context_parts),
            "sources": list(sources),
            "total_chunks": len(results),
            "avg_similarity": round(avg_similarity, 3),
            "context_length": current_length
        }
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        collection_info = self.vector_store.get_collection_info()
        
        return {
            "collection_name": collection_info["collection_name"],
            "total_documents": collection_info["document_count"],
            "embedding_model": collection_info["embedding_model"],
            "storage_path": collection_info["persist_directory"]
        }
    
    def clear_knowledge_base(self) -> None:
        """清空知识库"""
        self.vector_store.clear_collection()
        logging.info("知识库已清空")
    
    def suggest_related_queries(
        self,
        query: str,
        n_suggestions: int = 3
    ) -> List[str]:
        """
        基于查询建议相关查询
        
        Args:
            query: 原始查询
            n_suggestions: 建议数量
            
        Returns:
            相关查询建议列表
        """
        # 搜索相关文档
        results = self.search(query, n_results=10)
        
        if not results:
            return []
        
        # 从相关文档中提取关键词
        all_keywords = []
        for result in results:
            keywords = result["metadata"].get("keywords", [])
            all_keywords.extend(keywords)
        
        # 统计关键词频率
        keyword_freq = {}
        for keyword in all_keywords:
            if keyword.lower() not in query.lower():  # 排除查询中已有的词
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # 生成建议查询
        suggestions = []
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        
        for keyword, freq in top_keywords[:n_suggestions]:
            suggestions.append(f"{query} {keyword}")
        
        return suggestions