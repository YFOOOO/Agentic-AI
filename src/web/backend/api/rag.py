"""RAG系统API路由
提供文档搜索、上传和管理的REST接口
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
import tempfile
import json

from config import get_settings, Settings
from services.rag_service import rag_service

router = APIRouter()
logger = logging.getLogger(__name__)

# 请求/响应模型
class SearchRequest(BaseModel):
    """文档搜索请求"""
    query: str = Field(..., description="搜索查询")
    n_results: int = Field(5, ge=1, le=20, description="返回结果数量")

class SearchResult(BaseModel):
    """搜索结果"""
    content: str = Field(..., description="文档内容")
    metadata: Dict[str, Any] = Field(..., description="文档元数据")
    score: float = Field(..., description="相似度分数")

class SearchResponse(BaseModel):
    """搜索响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    query: str = Field(..., description="搜索查询")
    results: List[SearchResult] = Field(..., description="搜索结果")
    total_results: int = Field(..., description="结果总数")

class QuerySuggestionsRequest(BaseModel):
    """查询建议请求"""
    query: str = Field(..., description="原始查询")
    n_suggestions: int = Field(3, ge=1, le=10, description="建议数量")

class QuerySuggestionsResponse(BaseModel):
    """查询建议响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    original_query: str = Field(..., description="原始查询")
    suggestions: List[str] = Field(..., description="查询建议")

class UploadResponse(BaseModel):
    """文档上传响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    file_path: str = Field(..., description="文件路径")
    chunks_count: int = Field(..., description="文本块数量")
    document_ids: List[str] = Field(..., description="文档ID列表")

class StatisticsResponse(BaseModel):
    """统计信息响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    statistics: Dict[str, Any] = Field(..., description="统计信息")


@router.post("/search", response_model=SearchResponse, summary="搜索文档")
async def search_documents(
    request: SearchRequest,
    settings: Settings = Depends(get_settings)
):
    """
    在知识库中搜索相关文档
    """
    try:
        logger.info(f"🔍 搜索请求: {request.query}")
        
        # 调用RAG服务进行搜索
        result = await rag_service.search_documents(
            query=request.query,
            n_results=request.n_results
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        # 转换结果格式
        search_results = []
        for doc in result["results"]:
            search_results.append(SearchResult(
                content=doc["content"],
                metadata=doc["metadata"],
                score=doc.get("score", 0.0)
            ))
        
        response = SearchResponse(
            success=True,
            message=result["message"],
            query=request.query,
            results=search_results,
            total_results=result["results_count"]
        )
        
        logger.info(f"✅ 搜索完成，返回 {len(search_results)} 个结果")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/suggestions", response_model=QuerySuggestionsResponse, summary="获取查询建议")
async def get_query_suggestions(
    request: QuerySuggestionsRequest,
    settings: Settings = Depends(get_settings)
):
    """
    获取相关查询建议
    """
    try:
        logger.info(f"💡 查询建议请求: {request.query}")
        
        # 调用RAG服务获取建议
        result = await rag_service.get_query_suggestions(
            query=request.query,
            n_suggestions=request.n_suggestions
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        response = QuerySuggestionsResponse(
            success=True,
            message=result["message"],
            original_query=request.query,
            suggestions=result["suggestions"]
        )
        
        logger.info(f"✅ 查询建议生成完成，返回 {len(result['suggestions'])} 个建议")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 查询建议生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询建议生成失败: {str(e)}")

@router.post("/upload", response_model=UploadResponse, summary="上传文档")
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings)
):
    """
    上传文档到知识库
    """
    try:
        logger.info(f"📤 上传文档: {file.filename}")
        
        # 解析元数据
        doc_metadata = {}
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"元数据解析失败，使用默认值: {metadata}")
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 调用RAG服务处理文档
            result = await rag_service.process_document(
                file_path=temp_file_path,
                metadata={
                    "filename": file.filename,
                    "content_type": file.content_type,
                    **doc_metadata
                }
            )
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            response = UploadResponse(
                success=True,
                message=result["message"],
                file_path=result["file_path"],
                chunks_count=result["chunks_count"],
                document_ids=result["document_ids"]
            )
            
            logger.info(f"✅ 文档上传成功: {file.filename}")
            return response
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 文档上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")


@router.get("/statistics", response_model=StatisticsResponse, summary="获取统计信息")
async def get_statistics(settings: Settings = Depends(get_settings)):
    """
    获取RAG系统统计信息
    """
    try:
        logger.info("📊 获取统计信息")
        
        # 调用RAG服务获取统计信息
        result = await rag_service.get_statistics()
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        response = StatisticsResponse(
            success=True,
            message=result["message"],
            statistics=result["statistics"]
        )
        
        logger.info("✅ 统计信息获取成功")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 统计信息获取失败: {e}")
        raise HTTPException(status_code=500, detail=f"统计信息获取失败: {str(e)}")