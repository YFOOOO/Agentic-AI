"""
Web搜索数据源

支持多种学术搜索引擎：
- Semantic Scholar API
- arXiv API  
- CrossRef API
- 可扩展支持Google Scholar等
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from .base_source import DataSource, SearchResult

class WebSearchSource(DataSource):
    """Web搜索数据源"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("web_search", config)
        
        # 默认配置
        self.default_config = {
            "semantic_scholar_enabled": True,
            "arxiv_enabled": True, 
            "crossref_enabled": True,
            "timeout": 30,
            "max_retries": 3
        }
        
        # 合并配置
        self.config = {**self.default_config, **(config or {})}
        
        # API端点
        self.endpoints = {
            "semantic_scholar": "https://api.semanticscholar.org/graph/v1/paper/search",
            "arxiv": "http://export.arxiv.org/api/query",
            "crossref": "https://api.crossref.org/works"
        }
    
    def validate_config(self) -> bool:
        """验证配置"""
        required_keys = ["timeout", "max_retries"]
        return all(key in self.config for key in required_keys)
    
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[SearchResult]:
        """搜索文献"""
        results = []
        
        # 并发搜索多个数据源
        tasks = []
        
        if self.config.get("semantic_scholar_enabled"):
            tasks.append(self._search_semantic_scholar(query, limit // 3))
        
        if self.config.get("arxiv_enabled"):
            tasks.append(self._search_arxiv(query, limit // 3))
            
        if self.config.get("crossref_enabled"):
            tasks.append(self._search_crossref(query, limit // 3))
        
        # 执行并发搜索
        try:
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in search_results:
                if isinstance(result, list):
                    results.extend(result)
                elif isinstance(result, Exception):
                    self.logger.warning(f"搜索失败: {result}")
            
        except Exception as e:
            self.logger.error(f"并发搜索失败: {e}")
        
        # 去重和排序
        results = self._deduplicate_results(results)
        return results[:limit]
    
    async def get_by_id(self, item_id: str) -> Optional[SearchResult]:
        """根据ID获取文献详情"""
        # 根据ID格式判断数据源
        if item_id.startswith("arxiv:"):
            return await self._get_arxiv_by_id(item_id.replace("arxiv:", ""))
        elif item_id.startswith("doi:"):
            return await self._get_crossref_by_doi(item_id.replace("doi:", ""))
        elif item_id.startswith("s2:"):
            return await self._get_semantic_scholar_by_id(item_id.replace("s2:", ""))
        
        return None
    
    async def _search_semantic_scholar(self, query: str, limit: int) -> List[SearchResult]:
        """搜索Semantic Scholar"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config["timeout"])) as session:
                params = {
                    "query": query,
                    "limit": limit,
                    "fields": "title,authors,abstract,url,publicationDate,journal,citationCount,externalIds"
                }
                
                async with session.get(self.endpoints["semantic_scholar"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_semantic_scholar_results(data.get("data", []))
                    else:
                        self.logger.warning(f"Semantic Scholar API错误: {response.status}")
                        return []
        
        except Exception as e:
            self.logger.error(f"Semantic Scholar搜索失败: {e}")
            return []
    
    async def _search_arxiv(self, query: str, limit: int) -> List[SearchResult]:
        """搜索arXiv"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config["timeout"])) as session:
                params = {
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": limit
                }
                
                async with session.get(self.endpoints["arxiv"], params=params) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        return self._parse_arxiv_results(xml_data)
                    else:
                        self.logger.warning(f"arXiv API错误: {response.status}")
                        return []
        
        except Exception as e:
            self.logger.error(f"arXiv搜索失败: {e}")
            return []
    
    async def _search_crossref(self, query: str, limit: int) -> List[SearchResult]:
        """搜索CrossRef"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config["timeout"])) as session:
                params = {
                    "query": query,
                    "rows": limit
                }
                
                async with session.get(self.endpoints["crossref"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_crossref_results(data.get("message", {}).get("items", []))
                    else:
                        self.logger.warning(f"CrossRef API错误: {response.status}")
                        return []
        
        except Exception as e:
            self.logger.error(f"CrossRef搜索失败: {e}")
            return []
    
    def _parse_semantic_scholar_results(self, data: List[Dict]) -> List[SearchResult]:
        """解析Semantic Scholar结果"""
        results = []
        
        for item in data:
            try:
                authors = [author.get("name", "") for author in item.get("authors", [])]
                
                result = SearchResult(
                    title=item.get("title", ""),
                    authors=authors,
                    abstract=item.get("abstract", ""),
                    url=item.get("url", ""),
                    source="semantic_scholar",
                    publication_date=self._parse_date(item.get("publicationDate")),
                    journal=item.get("journal", {}).get("name") if item.get("journal") else None,
                    citation_count=item.get("citationCount"),
                    metadata={
                        "s2_id": item.get("paperId"),
                        "external_ids": item.get("externalIds", {})
                    }
                )
                results.append(result)
                
            except Exception as e:
                self.logger.warning(f"解析Semantic Scholar结果失败: {e}")
        
        return results
    
    def _parse_arxiv_results(self, xml_data: str) -> List[SearchResult]:
        """解析arXiv XML结果"""
        results = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_data)
            
            # arXiv使用Atom命名空间
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            for entry in root.findall("atom:entry", ns):
                try:
                    title = entry.find("atom:title", ns).text.strip()
                    abstract = entry.find("atom:summary", ns).text.strip()
                    
                    # 解析作者
                    authors = []
                    for author in entry.findall("atom:author", ns):
                        name = author.find("atom:name", ns)
                        if name is not None:
                            authors.append(name.text)
                    
                    # 获取arXiv ID和URL
                    arxiv_id = entry.find("atom:id", ns).text.split("/")[-1]
                    url = f"https://arxiv.org/abs/{arxiv_id}"
                    
                    # 解析发布日期
                    published = entry.find("atom:published", ns)
                    pub_date = self._parse_date(published.text) if published is not None else None
                    
                    result = SearchResult(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        url=url,
                        source="arxiv",
                        publication_date=pub_date,
                        metadata={"arxiv_id": arxiv_id}
                    )
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"解析arXiv条目失败: {e}")
        
        except Exception as e:
            self.logger.error(f"解析arXiv XML失败: {e}")
        
        return results
    
    def _parse_crossref_results(self, data: List[Dict]) -> List[SearchResult]:
        """解析CrossRef结果"""
        results = []
        
        for item in data:
            try:
                # 解析作者
                authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    name = f"{given} {family}".strip()
                    if name:
                        authors.append(name)
                
                # 获取标题
                title_list = item.get("title", [])
                title = title_list[0] if title_list else ""
                
                # 获取摘要
                abstract_list = item.get("abstract", [])
                abstract = abstract_list[0] if abstract_list else ""
                
                # 构建URL
                doi = item.get("DOI", "")
                url = f"https://doi.org/{doi}" if doi else ""
                
                # 解析发布日期
                date_parts = item.get("published-print", {}).get("date-parts")
                if not date_parts:
                    date_parts = item.get("published-online", {}).get("date-parts")
                
                pub_date = None
                if date_parts and date_parts[0]:
                    try:
                        year, month, day = (date_parts[0] + [1, 1])[:3]
                        pub_date = datetime(year, month, day)
                    except:
                        pass
                
                result = SearchResult(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=url,
                    source="crossref",
                    publication_date=pub_date,
                    journal=item.get("container-title", [None])[0],
                    doi=doi,
                    metadata={
                        "type": item.get("type"),
                        "publisher": item.get("publisher")
                    }
                )
                results.append(result)
                
            except Exception as e:
                self.logger.warning(f"解析CrossRef结果失败: {e}")
        
        return results
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试多种日期格式
            formats = [
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # 如果都失败，尝试只解析年份
            year_match = re.search(r'\d{4}', date_str)
            if year_match:
                return datetime(int(year_match.group()), 1, 1)
                
        except Exception as e:
            self.logger.warning(f"日期解析失败: {date_str}, {e}")
        
        return None
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重搜索结果"""
        seen_titles = set()
        unique_results = []
        
        for result in results:
            # 使用标题的小写版本作为去重键
            title_key = result.title.lower().strip()
            
            if title_key not in seen_titles and title_key:
                seen_titles.add(title_key)
                unique_results.append(result)
        
        # 按相关性排序（这里简单按citation_count排序）
        unique_results.sort(key=lambda x: x.citation_count or 0, reverse=True)
        
        return unique_results
    
    async def _get_arxiv_by_id(self, arxiv_id: str) -> Optional[SearchResult]:
        """根据arXiv ID获取详情"""
        results = await self._search_arxiv(f"id:{arxiv_id}", 1)
        return results[0] if results else None
    
    async def _get_crossref_by_doi(self, doi: str) -> Optional[SearchResult]:
        """根据DOI获取详情"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config["timeout"])) as session:
                url = f"{self.endpoints['crossref']}/{doi}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self._parse_crossref_results([data.get("message", {})])
                        return results[0] if results else None
        
        except Exception as e:
            self.logger.error(f"根据DOI获取详情失败: {e}")
        
        return None
    
    async def _get_semantic_scholar_by_id(self, paper_id: str) -> Optional[SearchResult]:
        """根据Semantic Scholar ID获取详情"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config["timeout"])) as session:
                url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
                params = {
                    "fields": "title,authors,abstract,url,publicationDate,journal,citationCount,externalIds"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self._parse_semantic_scholar_results([data])
                        return results[0] if results else None
        
        except Exception as e:
            self.logger.error(f"根据S2 ID获取详情失败: {e}")
        
        return None