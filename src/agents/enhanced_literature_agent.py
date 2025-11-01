"""
增强版文献收集代理

集成多源数据系统，支持从多个数据源收集文献信息：
- Nobel Prize API（保持向后兼容）
- Web搜索（学术搜索引擎）
- Zotero文献库
- 本地知识库（RAG系统）

保持与原LiteratureAgent相同的接口，确保无缝升级。
"""

from typing import Dict, Any, List, Optional
import os
import time
import pandas as pd
import asyncio
import logging
from datetime import datetime

# 导入原有的数据拉取函数
from src.data.nobel_fetch import fetch_laureates, normalize

# 导入多源数据集成系统
from src.integrations import MultiSourceManager, SearchResult


class EnhancedLiteratureAgent:
    """增强版文献收集代理"""
    
    def __init__(self, base_dir: str = "artifacts/nobel", multi_source_config: Optional[Dict[str, Any]] = None):
        """
        初始化增强版文献代理
        
        Args:
            base_dir: 输出目录
            multi_source_config: 多源数据配置，如果为None则只使用Nobel Prize API
        """
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)
        
        # 初始化多源数据管理器
        self.multi_source_manager = None
        if multi_source_config:
            try:
                self.multi_source_manager = MultiSourceManager(multi_source_config)
                self.logger.info("多源数据管理器初始化成功")
            except Exception as e:
                self.logger.error(f"多源数据管理器初始化失败: {e}")
                self.multi_source_manager = None
    
    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理文献收集任务
        
        Args:
            task: 任务配置，包含：
                - task_id: 任务ID（可选）
                - query: 搜索查询（可选，用于多源搜索）
                - sources: 指定使用的数据源（可选）
                - limit: 结果数量限制（可选）
                
        Returns:
            任务结果字典
        """
        # 运行 ID：优先使用 task_id，否则用当前时间戳
        run_id = str(task.get("task_id")) if task.get("task_id") else str(int(time.time()))
        out_dir = os.path.join(self.base_dir, "runs", run_id)
        os.makedirs(out_dir, exist_ok=True)
        
        # 收集数据
        all_data = []
        data_sources_used = []
        
        # 1. 始终包含Nobel Prize数据（保持向后兼容）
        try:
            nobel_data = fetch_laureates()
            nobel_df = normalize(nobel_data)
            nobel_df["data_source"] = "nobel_prize"
            all_data.append(nobel_df)
            data_sources_used.append("nobel_prize")
            self.logger.info(f"Nobel Prize数据收集成功: {len(nobel_df)} 条记录")
        except Exception as e:
            self.logger.error(f"Nobel Prize数据收集失败: {e}")
        
        # 2. 如果配置了多源数据且有查询，则进行多源搜索
        query = task.get("query")
        if self.multi_source_manager and query:
            try:
                multi_source_data = await self._collect_multi_source_data(
                    query=query,
                    sources=task.get("sources"),
                    limit=task.get("limit", 50)
                )
                if not multi_source_data.empty:
                    all_data.append(multi_source_data)
                    data_sources_used.extend(multi_source_data["data_source"].unique().tolist())
                    self.logger.info(f"多源数据收集成功: {len(multi_source_data)} 条记录")
            except Exception as e:
                self.logger.error(f"多源数据收集失败: {e}")
        
        # 3. 合并所有数据
        if all_data:
            df = pd.concat(all_data, ignore_index=True, sort=False)
        else:
            # 如果没有数据，创建空的DataFrame
            df = pd.DataFrame()
        
        # 4. 数据处理和标准化
        if not df.empty:
            df = self._standardize_dataframe(df)
        
        # 5. 保存数据
        csv_path = os.path.join(out_dir, "laureates_prizes.csv")
        df.to_csv(csv_path, index=False)
        
        # 6. 计算指标
        metrics = self._calculate_metrics(df, data_sources_used)
        
        # 7. 生成报告
        report_path = self._generate_report(df, metrics, out_dir, query)
        
        # 8. 返回结果
        result = {
            "type": "literature_collect",
            "task_id": run_id,
            "artifacts": {
                "csv": csv_path,
                "report": report_path,
                "run_dir": out_dir
            },
            "metrics": metrics,
            "query": query,
            "data_sources": data_sources_used,
            "notes": f"Enhanced collection from {len(data_sources_used)} sources"
        }
        
        return result
    
    async def _collect_multi_source_data(self, query: str, sources: Optional[List[str]] = None, limit: int = 50) -> pd.DataFrame:
        """收集多源数据"""
        try:
            # 使用异步方法收集数据
            search_results = await self.multi_source_manager.search_aggregated(query, limit)
            
            if not search_results:
                return pd.DataFrame()
            
            # 转换为DataFrame
            records = []
            for result in search_results:
                record = self._search_result_to_record(result)
                records.append(record)
            
            return pd.DataFrame(records)
            
        except Exception as e:
            self.logger.error(f"多源数据收集错误: {e}")
            return pd.DataFrame()
    
    def _search_result_to_record(self, result: SearchResult) -> Dict[str, Any]:
        """将SearchResult转换为记录字典"""
        return {
            "title": result.title,
            "authors": "; ".join(result.authors) if result.authors else "",
            "abstract": result.abstract or "",
            "url": result.url or "",
            "data_source": result.metadata.get("data_source", result.source) if result.metadata else result.source,
            "publication_date": result.metadata.get("date", "") if result.metadata else "",
            "publication_title": result.metadata.get("publication_title", "") if result.metadata else "",
            "tags": "; ".join(result.metadata.get("tags", [])) if result.metadata and result.metadata.get("tags") else "",
            "collected_at": datetime.now().isoformat()
        }
    
    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化DataFrame格式"""
        # 确保年份列存在并转换为数值
        if "year" in df.columns:
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
        elif "publication_date" in df.columns:
            # 尝试从publication_date提取年份
            df["year"] = pd.to_datetime(df["publication_date"], errors="coerce").dt.year
        
        # 确保ID列存在
        if "id" not in df.columns:
            df["id"] = range(len(df))
        
        # 去重（基于标题）
        if "title" in df.columns:
            df = df.drop_duplicates(subset=["title"], keep="first")
        
        return df
    
    def _calculate_metrics(self, df: pd.DataFrame, data_sources: List[str]) -> Dict[str, Any]:
        """计算数据指标"""
        if df.empty:
            return {
                "rows": 0,
                "data_sources_count": len(data_sources),
                "data_sources": data_sources
            }
        
        metrics = {
            "rows": int(len(df)),
            "data_sources_count": len(data_sources),
            "data_sources": data_sources,
            "unique_titles": int(df["title"].nunique()) if "title" in df.columns else 0,
        }
        
        # 添加年份相关指标
        if "year" in df.columns:
            metrics["year_missing_rate"] = round(float(df["year"].isna().mean()), 4)
            valid_years = df["year"].dropna()
            if not valid_years.empty:
                metrics["year_range"] = f"{int(valid_years.min())}-{int(valid_years.max())}"
        
        # 添加数据源分布
        if "data_source" in df.columns:
            source_counts = df["data_source"].value_counts().to_dict()
            metrics["source_distribution"] = {str(k): int(v) for k, v in source_counts.items()}
        
        return metrics
    
    def _generate_report(self, df: pd.DataFrame, metrics: Dict[str, Any], out_dir: str, query: Optional[str]) -> str:
        """生成数据收集报告"""
        report_path = os.path.join(out_dir, "collection_report.md")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 文献数据收集报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if query:
                f.write(f"**搜索查询**: {query}\n\n")
            
            f.write("## 数据概览\n\n")
            f.write(f"- **总记录数**: {metrics['rows']}\n")
            f.write(f"- **数据源数量**: {metrics['data_sources_count']}\n")
            f.write(f"- **使用的数据源**: {', '.join(metrics['data_sources'])}\n")
            
            if "unique_titles" in metrics:
                f.write(f"- **唯一标题数**: {metrics['unique_titles']}\n")
            
            if "year_range" in metrics:
                f.write(f"- **年份范围**: {metrics['year_range']}\n")
                f.write(f"- **年份缺失率**: {metrics['year_missing_rate']:.2%}\n")
            
            if "source_distribution" in metrics:
                f.write("\n## 数据源分布\n\n")
                for source, count in metrics["source_distribution"].items():
                    f.write(f"- **{source}**: {count} 条记录\n")
            
            if not df.empty and "title" in df.columns:
                f.write("\n## 样本数据\n\n")
                sample_size = min(5, len(df))
                for i, row in df.head(sample_size).iterrows():
                    f.write(f"### {i+1}. {row.get('title', '未知标题')}\n")
                    if row.get('authors'):
                        f.write(f"**作者**: {row['authors']}\n\n")
                    if row.get('abstract') and isinstance(row['abstract'], str):
                        abstract = row['abstract'][:200] + "..." if len(row['abstract']) > 200 else row['abstract']
                        f.write(f"**摘要**: {abstract}\n\n")
                    f.write(f"**数据源**: {row.get('data_source', '未知')}\n\n")
        
        return report_path


# 为了保持向后兼容性，创建一个别名
class LiteratureAgent(EnhancedLiteratureAgent):
    """向后兼容的LiteratureAgent别名"""
    
    def __init__(self, base_dir: str = "artifacts/nobel"):
        # 默认不启用多源数据，保持原有行为
        super().__init__(base_dir=base_dir, multi_source_config=None)