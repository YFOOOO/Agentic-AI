"""
引用管理API路由
提供引用的增删改查、格式化和验证功能
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.citation_service import (
    citation_service, 
    Citation, 
    Author, 
    CitationStyle
)

router = APIRouter(prefix="/citations", tags=["citations"])


class AuthorRequest(BaseModel):
    """作者请求模型"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None


class CitationRequest(BaseModel):
    """引用请求模型"""
    title: str
    authors: List[AuthorRequest]
    year: int
    publication_type: str
    
    # 期刊文章字段
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    
    # 书籍字段
    publisher: Optional[str] = None
    city: Optional[str] = None
    edition: Optional[str] = None
    
    # 网站字段
    url: Optional[str] = None
    access_date: Optional[str] = None
    
    # 其他字段
    isbn: Optional[str] = None
    pmid: Optional[str] = None


class CitationResponse(BaseModel):
    """引用响应模型"""
    id: str
    title: str
    authors: List[Dict[str, str]]
    year: int
    publication_type: str
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    publisher: Optional[str] = None
    city: Optional[str] = None
    edition: Optional[str] = None
    url: Optional[str] = None
    access_date: Optional[str] = None
    isbn: Optional[str] = None
    pmid: Optional[str] = None


class FormatRequest(BaseModel):
    """格式化请求模型"""
    citation_ids: List[str]
    style: str


class ParseRequest(BaseModel):
    """解析请求模型"""
    text: str


@router.post("/", response_model=Dict[str, str])
async def create_citation(citation_request: CitationRequest):
    """创建新引用"""
    try:
        # 转换作者信息
        authors = [
            Author(
                first_name=author.first_name,
                last_name=author.last_name,
                middle_name=author.middle_name
            )
            for author in citation_request.authors
        ]
        
        # 创建引用对象
        citation = Citation(
            title=citation_request.title,
            authors=authors,
            year=citation_request.year,
            publication_type=citation_request.publication_type,
            journal=citation_request.journal,
            volume=citation_request.volume,
            issue=citation_request.issue,
            pages=citation_request.pages,
            doi=citation_request.doi,
            publisher=citation_request.publisher,
            city=citation_request.city,
            edition=citation_request.edition,
            url=citation_request.url,
            access_date=citation_request.access_date,
            isbn=citation_request.isbn,
            pmid=citation_request.pmid
        )
        
        # 验证引用
        errors = citation_service.validate_citation(citation)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # 添加引用
        citation_id = citation_service.add_citation(citation)
        
        return {
            "message": "引用创建成功",
            "citation_id": citation_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建引用失败: {str(e)}")


@router.get("/", response_model=List[CitationResponse])
async def list_citations():
    """获取所有引用列表"""
    try:
        citations = citation_service.list_citations()
        
        result = []
        for citation_id, citation in citations.items():
            authors_data = []
            for author in citation.authors:
                authors_data.append({
            "first_name": author.first_name,
            "last_name": author.last_name,
            "middle_name": author.middle_name or ""
        })
            
            result.append(CitationResponse(
                id=citation_id,
                title=citation.title,
                authors=authors_data,
                year=citation.year,
                publication_type=citation.publication_type,
                journal=citation.journal,
                volume=citation.volume,
                issue=citation.issue,
                pages=citation.pages,
                doi=citation.doi,
                publisher=citation.publisher,
                city=citation.city,
                edition=citation.edition,
                url=citation.url,
                access_date=citation.access_date,
                isbn=citation.isbn,
                pmid=citation.pmid
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取引用列表失败: {str(e)}")


@router.get("/{citation_id}", response_model=CitationResponse)
async def get_citation(citation_id: str):
    """获取特定引用"""
    try:
        citation = citation_service.get_citation(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="引用不存在")
        
        authors_data = []
        for author in citation.authors:
            authors_data.append({
                "first_name": author.first_name,
                "last_name": author.last_name,
                "middle_name": author.middle_name or ""
            })
        
        return CitationResponse(
            id=citation_id,
            title=citation.title,
            authors=authors_data,
            year=citation.year,
            publication_type=citation.publication_type,
            journal=citation.journal,
            volume=citation.volume,
            issue=citation.issue,
            pages=citation.pages,
            doi=citation.doi,
            publisher=citation.publisher,
            city=citation.city,
            edition=citation.edition,
            url=citation.url,
            access_date=citation.access_date,
            isbn=citation.isbn,
            pmid=citation.pmid
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取引用失败: {str(e)}")


@router.post("/format", response_model=Dict[str, Any])
async def format_citations(format_request: FormatRequest):
    """格式化引用"""
    try:
        # 验证引用格式
        try:
            style = CitationStyle(format_request.style.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的引用格式: {format_request.style}"
            )
        
        formatted_citations = {}
        not_found = []
        
        for citation_id in format_request.citation_ids:
            formatted = citation_service.format_citation(citation_id, style)
            if "not found" in formatted.lower():
                not_found.append(citation_id)
            else:
                formatted_citations[citation_id] = formatted
        
        result = {
            "style": format_request.style,
            "formatted_citations": formatted_citations
        }
        
        if not_found:
            result["not_found"] = not_found
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"格式化引用失败: {str(e)}")


@router.post("/parse", response_model=Dict[str, Any])
async def parse_citation(parse_request: ParseRequest):
    """解析引用文本"""
    try:
        citation = citation_service.parse_citation_text(parse_request.text)
        
        if not citation:
            raise HTTPException(status_code=400, detail="无法解析引用文本")
        
        # 验证解析结果
        errors = citation_service.validate_citation(citation)
        
        authors_data = []
        for author in citation.authors:
            authors_data.append({
            "first_name": author.first_name,
            "last_name": author.last_name,
            "middle_name": author.middle_name or ""
        })
        
        return {
            "parsed_citation": {
                "title": citation.title,
                "authors": authors_data,
                "year": citation.year,
                "publication_type": citation.publication_type,
                "journal": citation.journal,
                "volume": citation.volume,
                "issue": citation.issue,
                "pages": citation.pages,
                "doi": citation.doi,
                "publisher": citation.publisher,
                "city": citation.city,
                "url": citation.url
            },
            "validation_errors": errors,
            "confidence": "low"  # 简单解析的置信度较低
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析引用失败: {str(e)}")


@router.get("/styles/supported", response_model=List[str])
async def get_supported_styles():
    """获取支持的引用格式"""
    return [style.value for style in CitationStyle]


@router.get("/statistics/overview", response_model=Dict[str, Any])
async def get_citation_statistics():
    """获取引用统计信息"""
    try:
        stats = citation_service.get_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.delete("/{citation_id}", response_model=Dict[str, str])
async def delete_citation(citation_id: str):
    """删除引用"""
    try:
        citation = citation_service.get_citation(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="引用不存在")
        
        # 删除引用
        del citation_service.citations[citation_id]
        
        return {"message": "引用删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除引用失败: {str(e)}")


@router.put("/{citation_id}", response_model=Dict[str, str])
async def update_citation(citation_id: str, citation_request: CitationRequest):
    """更新引用"""
    try:
        # 检查引用是否存在
        existing_citation = citation_service.get_citation(citation_id)
        if not existing_citation:
            raise HTTPException(status_code=404, detail="引用不存在")
        
        # 转换作者信息
        authors = [
            Author(
                first_name=author.first_name,
                last_name=author.last_name,
                middle_name=author.middle_name
            )
            for author in citation_request.authors
        ]
        
        # 创建更新的引用对象
        updated_citation = Citation(
            title=citation_request.title,
            authors=authors,
            year=citation_request.year,
            publication_type=citation_request.publication_type,
            journal=citation_request.journal,
            volume=citation_request.volume,
            issue=citation_request.issue,
            pages=citation_request.pages,
            doi=citation_request.doi,
            publisher=citation_request.publisher,
            city=citation_request.city,
            edition=citation_request.edition,
            url=citation_request.url,
            access_date=citation_request.access_date,
            isbn=citation_request.isbn,
            pmid=citation_request.pmid
        )
        
        # 验证引用
        errors = citation_service.validate_citation(updated_citation)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # 更新引用
        citation_service.citations[citation_id] = updated_citation
        
        return {"message": "引用更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新引用失败: {str(e)}")