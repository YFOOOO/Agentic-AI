#!/usr/bin/env python3
"""
RAG系统集成测试
测试向量存储、文档处理和知识检索的基础功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag import VectorStore, DocumentProcessor, KnowledgeRetriever

def test_document_processor():
    """测试文档处理器功能"""
    print("🔍 测试文档处理器...")
    
    processor = DocumentProcessor()
    
    # 测试文本
    test_text = """
    人工智能（Artificial Intelligence, AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
    
    机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。深度学习是机器学习的一个分支，
    使用神经网络来模拟人脑的工作方式。
    
    自然语言处理（NLP）是人工智能的另一个重要分支，专注于使计算机能够理解、解释和生成人类语言。
    """
    
    # 测试文本清理
    cleaned_text = processor.clean_text(test_text)
    print(f"✅ 文本清理完成，长度: {len(cleaned_text)}")
    
    # 测试token计数
    token_count = processor.count_tokens(cleaned_text)
    print(f"✅ Token计数: {token_count}")
    
    # 测试文本分块
    chunks = processor.split_text(cleaned_text)
    print(f"✅ 文本分块完成，共 {len(chunks)} 个块")
    
    # 测试元数据提取
    metadata = processor.extract_metadata(cleaned_text, source="test_document")
    print(f"✅ 元数据提取完成: {metadata}")
    
    return True

def test_vector_store():
    """测试向量存储功能"""
    print("\n🔍 测试向量存储...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 初始化向量存储
        vector_store = VectorStore(
            collection_name="test_collection",
            persist_directory=temp_dir
        )
        
        # 测试文档
        documents = [
            "人工智能是计算机科学的重要分支",
            "机器学习使计算机能够自动学习",
            "深度学习使用神经网络模拟人脑",
            "自然语言处理专注于理解人类语言"
        ]
        
        metadatas = [
            {"source": "ai_intro", "topic": "AI"},
            {"source": "ml_intro", "topic": "ML"},
            {"source": "dl_intro", "topic": "DL"},
            {"source": "nlp_intro", "topic": "NLP"}
        ]
        
        # 添加文档
        vector_store.add_documents(documents, metadatas)
        print(f"✅ 成功添加 {len(documents)} 个文档")
        
        # 测试相似性搜索
        query = "什么是机器学习"
        results = vector_store.search(query, n_results=2)
        print(f"✅ 相似性搜索完成，找到 {len(results)} 个相关文档")
        
        for i, result in enumerate(results):
            doc = result.get('document', '')
            score = result.get('similarity_score', 0)
            metadata = result.get('metadata', {})
            print(f"   结果 {i+1}: {doc[:50]}... (相似度: {score:.3f})")
        
        return True
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_knowledge_retriever():
    """测试知识检索器功能"""
    print("\n🔍 测试知识检索器...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 初始化知识检索器
        retriever = KnowledgeRetriever(
            collection_name="test_knowledge",
            persist_directory=temp_dir
        )
        
        # 添加测试文档
        test_documents = [
            "人工智能（AI）是模拟人类智能的计算机系统。它包括机器学习、深度学习、自然语言处理等多个子领域。",
            "机器学习是AI的核心技术之一，通过算法让计算机从数据中学习模式，无需明确编程。常见算法包括线性回归、决策树、神经网络等。",
            "深度学习是机器学习的一个分支，使用多层神经网络来处理复杂数据。它在图像识别、语音识别、自然语言处理等领域取得了突破性进展。",
            "自然语言处理（NLP）专注于让计算机理解和生成人类语言。主要任务包括文本分类、情感分析、机器翻译、问答系统等。"
        ]
        
        # 添加文档
        topics = ["AI", "ML", "DL", "NLP"]
        for i, doc in enumerate(test_documents):
            retriever.add_documents_from_text(
                doc, 
                sources=f"doc_{i}",
                metadata_list=[{"doc_id": f"doc_{i}", "topic": topics[i]}]
            )
        
        print(f"✅ 成功添加 {len(test_documents)} 个文档到知识库")
        
        # 获取知识库统计
        stats = retriever.get_knowledge_base_stats()
        print(f"✅ 知识库统计: {stats}")
        
        # 测试搜索
        query = "深度学习在哪些领域有应用"
        results = retriever.search(query, n_results=2)
        print(f"✅ 搜索完成，找到 {len(results)} 个相关文档")
        
        # 测试上下文获取
        context_info = retriever.get_context_for_query(query, max_context_length=200)
        context = context_info.get('context', '')
        print(f"✅ 上下文获取完成，长度: {len(context)} 字符")
        print(f"   上下文预览: {context[:100]}...")
        
        # 测试相关查询建议
        suggestions = retriever.suggest_related_queries(query, n_suggestions=3)
        print(f"✅ 查询建议: {suggestions}")
        
        return True
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """运行所有测试"""
    print("🚀 开始RAG系统集成测试\n")
    
    try:
        # 运行各项测试
        success = True
        success &= test_document_processor()
        success &= test_vector_store()
        success &= test_knowledge_retriever()
        
        if success:
            print("\n✅ 所有测试通过！RAG系统基础功能正常")
            print("\n📊 测试总结:")
            print("   - 文档处理器: ✅ 文本清理、分块、元数据提取")
            print("   - 向量存储: ✅ 文档嵌入、存储、相似性搜索")
            print("   - 知识检索器: ✅ 文档管理、智能检索、上下文生成")
            return True
        else:
            print("\n❌ 部分测试失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)