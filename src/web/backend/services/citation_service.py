"""
引用管理服务
支持多种引用格式，包括APA、MLA、Chicago等
提供引用生成、格式化和验证功能
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class CitationStyle(Enum):
    """引用格式枚举"""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    HARVARD = "harvard"


@dataclass
class Author:
    """作者信息"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    
    def format_apa(self) -> str:
        """APA格式：Last, F. M."""
        if self.middle_name:
            return f"{self.last_name}, {self.first_name[0]}. {self.middle_name[0]}."
        return f"{self.last_name}, {self.first_name[0]}."
    
    def format_mla(self) -> str:
        """MLA格式：Last, First Middle"""
        if self.middle_name:
            return f"{self.last_name}, {self.first_name} {self.middle_name}"
        return f"{self.last_name}, {self.first_name}"


@dataclass
class Citation:
    """引用信息"""
    title: str
    authors: List[Author]
    year: int
    publication_type: str  # journal, book, website, etc.
    
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


class CitationService:
    """引用管理服务"""
    
    def __init__(self):
        self.citations: Dict[str, Citation] = {}
        self.citation_counter = 0
    
    def add_citation(self, citation: Citation) -> str:
        """添加引用，返回引用ID"""
        self.citation_counter += 1
        citation_id = f"cite_{self.citation_counter}"
        self.citations[citation_id] = citation
        return citation_id
    
    def get_citation(self, citation_id: str) -> Optional[Citation]:
        """获取引用"""
        return self.citations.get(citation_id)
    
    def list_citations(self) -> Dict[str, Citation]:
        """列出所有引用"""
        return self.citations.copy()
    
    def format_citation(self, citation_id: str, style: CitationStyle) -> str:
        """格式化引用"""
        citation = self.get_citation(citation_id)
        if not citation:
            return f"Citation {citation_id} not found"
        
        if style == CitationStyle.APA:
            return self._format_apa(citation)
        elif style == CitationStyle.MLA:
            return self._format_mla(citation)
        elif style == CitationStyle.CHICAGO:
            return self._format_chicago(citation)
        elif style == CitationStyle.IEEE:
            return self._format_ieee(citation)
        elif style == CitationStyle.HARVARD:
            return self._format_harvard(citation)
        else:
            return "Unsupported citation style"
    
    def _format_apa(self, citation: Citation) -> str:
        """APA格式化"""
        authors_str = self._format_authors_apa(citation.authors)
        
        if citation.publication_type == "journal":
            result = f"{authors_str} ({citation.year}). {citation.title}."
            if citation.journal:
                result += f" {citation.journal}"
            if citation.volume:
                result += f", {citation.volume}"
            if citation.issue:
                result += f"({citation.issue})"
            if citation.pages:
                result += f", {citation.pages}"
            if citation.doi:
                result += f". https://doi.org/{citation.doi}"
            return result
        
        elif citation.publication_type == "book":
            result = f"{authors_str} ({citation.year}). {citation.title}."
            if citation.publisher:
                result += f" {citation.publisher}"
            return result
        
        elif citation.publication_type == "website":
            result = f"{authors_str} ({citation.year}). {citation.title}."
            if citation.url:
                result += f" Retrieved from {citation.url}"
            return result
        
        return f"{authors_str} ({citation.year}). {citation.title}."
    
    def _format_mla(self, citation: Citation) -> str:
        """MLA格式化"""
        authors_str = self._format_authors_mla(citation.authors)
        
        if citation.publication_type == "journal":
            result = f"{authors_str} \"{citation.title}.\""
            if citation.journal:
                result += f" {citation.journal}"
            if citation.volume:
                result += f", vol. {citation.volume}"
            if citation.issue:
                result += f", no. {citation.issue}"
            result += f", {citation.year}"
            if citation.pages:
                result += f", pp. {citation.pages}"
            return result + "."
        
        elif citation.publication_type == "book":
            result = f"{authors_str} {citation.title}."
            if citation.publisher:
                result += f" {citation.publisher}"
            result += f", {citation.year}."
            return result
        
        return f"{authors_str} \"{citation.title}.\" {citation.year}."
    
    def _format_chicago(self, citation: Citation) -> str:
        """Chicago格式化"""
        authors_str = self._format_authors_chicago(citation.authors)
        
        if citation.publication_type == "journal":
            result = f"{authors_str} \"{citation.title}.\""
            if citation.journal:
                result += f" {citation.journal}"
            if citation.volume:
                result += f" {citation.volume}"
            if citation.issue:
                result += f", no. {citation.issue}"
            result += f" ({citation.year})"
            if citation.pages:
                result += f": {citation.pages}"
            return result + "."
        
        elif citation.publication_type == "book":
            result = f"{authors_str} {citation.title}."
            if citation.city and citation.publisher:
                result += f" {citation.city}: {citation.publisher}"
            elif citation.publisher:
                result += f" {citation.publisher}"
            result += f", {citation.year}."
            return result
        
        return f"{authors_str} \"{citation.title}.\" {citation.year}."
    
    def _format_ieee(self, citation: Citation) -> str:
        """IEEE格式化"""
        authors_str = self._format_authors_ieee(citation.authors)
        
        if citation.publication_type == "journal":
            result = f"{authors_str}, \"{citation.title},\""
            if citation.journal:
                result += f" {citation.journal}"
            if citation.volume:
                result += f", vol. {citation.volume}"
            if citation.issue:
                result += f", no. {citation.issue}"
            if citation.pages:
                result += f", pp. {citation.pages}"
            result += f", {citation.year}."
            return result
        
        elif citation.publication_type == "book":
            result = f"{authors_str}, {citation.title}."
            if citation.publisher:
                result += f" {citation.publisher}"
            result += f", {citation.year}."
            return result
        
        return f"{authors_str}, \"{citation.title},\" {citation.year}."
    
    def _format_harvard(self, citation: Citation) -> str:
        """Harvard格式化"""
        authors_str = self._format_authors_harvard(citation.authors)
        
        if citation.publication_type == "journal":
            result = f"{authors_str} {citation.year}, '{citation.title}'"
            if citation.journal:
                result += f", {citation.journal}"
            if citation.volume:
                result += f", vol. {citation.volume}"
            if citation.issue:
                result += f", no. {citation.issue}"
            if citation.pages:
                result += f", pp. {citation.pages}"
            return result + "."
        
        elif citation.publication_type == "book":
            result = f"{authors_str} {citation.year}, {citation.title}"
            if citation.publisher:
                result += f", {citation.publisher}"
            if citation.city:
                result += f", {citation.city}"
            return result + "."
        
        return f"{authors_str} {citation.year}, '{citation.title}'."
    
    def _format_authors_apa(self, authors: List[Author]) -> str:
        """APA作者格式化"""
        if not authors:
            return "Unknown Author"
        
        if len(authors) == 1:
            return authors[0].format_apa()
        elif len(authors) == 2:
            return f"{authors[0].format_apa()}, & {authors[1].format_apa()}"
        else:
            formatted = [author.format_apa() for author in authors[:-1]]
            return ", ".join(formatted) + f", & {authors[-1].format_apa()}"
    
    def _format_authors_mla(self, authors: List[Author]) -> str:
        """MLA作者格式化"""
        if not authors:
            return "Unknown Author."
        
        if len(authors) == 1:
            return authors[0].format_mla() + "."
        elif len(authors) == 2:
            return f"{authors[0].format_mla()}, and {authors[1].format_mla()}."
        else:
            return f"{authors[0].format_mla()}, et al."
    
    def _format_authors_chicago(self, authors: List[Author]) -> str:
        """Chicago作者格式化"""
        if not authors:
            return "Unknown Author."
        
        if len(authors) == 1:
            return authors[0].format_mla() + "."
        elif len(authors) == 2:
            return f"{authors[0].format_mla()}, and {authors[1].format_mla()}."
        else:
            formatted = [author.format_mla() for author in authors[:-1]]
            return ", ".join(formatted) + f", and {authors[-1].format_mla()}."
    
    def _format_authors_ieee(self, authors: List[Author]) -> str:
        """IEEE作者格式化"""
        if not authors:
            return "Unknown Author"
        
        if len(authors) == 1:
            return f"{authors[0].first_name[0]}. {authors[0].last_name}"
        else:
            formatted = []
            for author in authors:
                formatted.append(f"{author.first_name[0]}. {author.last_name}")
            return ", ".join(formatted)
    
    def _format_authors_harvard(self, authors: List[Author]) -> str:
        """Harvard作者格式化"""
        if not authors:
            return "Unknown Author"
        
        if len(authors) == 1:
            return f"{authors[0].last_name}, {authors[0].first_name[0]}."
        elif len(authors) == 2:
            return f"{authors[0].last_name}, {authors[0].first_name[0]}. & {authors[1].last_name}, {authors[1].first_name[0]}."
        else:
            return f"{authors[0].last_name}, {authors[0].first_name[0]}. et al."
    
    def parse_citation_text(self, text: str) -> Optional[Citation]:
        """解析引用文本，尝试提取引用信息"""
        # 简单的引用解析逻辑
        # 这里可以扩展为更复杂的解析算法
        
        # 尝试匹配年份
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        year = int(year_match.group()) if year_match else datetime.now().year
        
        # 尝试匹配DOI
        doi_match = re.search(r'10\.\d+/[^\s]+', text)
        doi = doi_match.group() if doi_match else None
        
        # 简单的标题提取（假设用引号包围）
        title_match = re.search(r'"([^"]+)"', text)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        # 创建默认作者
        authors = [Author("Unknown", "Author")]
        
        return Citation(
            title=title,
            authors=authors,
            year=year,
            publication_type="journal",
            doi=doi
        )
    
    def validate_citation(self, citation: Citation) -> List[str]:
        """验证引用信息，返回错误列表"""
        errors = []
        
        if not citation.title or citation.title.strip() == "":
            errors.append("标题不能为空")
        
        if not citation.authors:
            errors.append("至少需要一个作者")
        
        if citation.year < 1000 or citation.year > datetime.now().year + 1:
            errors.append("年份不合理")
        
        if citation.publication_type == "journal":
            if not citation.journal:
                errors.append("期刊文章需要期刊名称")
        
        elif citation.publication_type == "book":
            if not citation.publisher:
                errors.append("书籍需要出版社信息")
        
        elif citation.publication_type == "website":
            if not citation.url:
                errors.append("网站引用需要URL")
        
        return errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取引用统计信息"""
        total_citations = len(self.citations)
        
        # 按类型统计
        type_counts = {}
        for citation in self.citations.values():
            pub_type = citation.publication_type
            type_counts[pub_type] = type_counts.get(pub_type, 0) + 1
        
        # 按年份统计
        year_counts = {}
        for citation in self.citations.values():
            year = citation.year
            year_counts[year] = year_counts.get(year, 0) + 1
        
        return {
            "total_citations": total_citations,
            "by_type": type_counts,
            "by_year": year_counts,
            "supported_styles": [style.value for style in CitationStyle]
        }


# 全局引用服务实例
citation_service = CitationService()