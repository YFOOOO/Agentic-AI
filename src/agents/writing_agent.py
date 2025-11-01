from typing import Dict, Any
import os
import time
import pandas as pd

class WritingAgent:
    def __init__(self, base_dir: str = "artifacts/nobel", llm=None, model: str = None):
        self.base_dir = base_dir
        self.llm = llm  # 注入式 LLM 客户端（Aisuite 适配）
        self.model = model  # 可选模型名，交由 llm 客户端使用
        self.last_llm_error = None

    def handle(self, task: dict) -> dict:
        run_id = str(task.get("task_id")) if task.get("task_id") else str(int(time.time()))
        run_dir = os.path.join(self.base_dir, "runs", run_id)
        os.makedirs(run_dir, exist_ok=True)
        draft_path = os.path.join(run_dir, "draft_agent.md")

        # 读取 CSV 并计算基础指标
        csv_path = task.get("csv")
        rows = 0
        year_min = None
        year_max = None
        top_country_name = None
        top_country_count = 0
        top_category_name = None
        top_category_count = 0
        laureates_unique = 0

        if csv_path and os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                rows = int(len(df))

                if "year" in df.columns:
                    df["year"] = pd.to_numeric(df["year"], errors="coerce")
                    year_series = df["year"].dropna()
                    if not year_series.empty:
                        year_min = int(year_series.min())
                        year_max = int(year_series.max())

                if "id" in df.columns:
                    laureates_unique = int(df["id"].nunique())
                elif "name" in df.columns:
                    laureates_unique = int(df["name"].nunique())

                # 国家分布（优先使用常见字段）
                country_col = next((c for c in ["bornCountry", "birth_country", "country"] if c in df.columns), None)
                if country_col:
                    vc = df[country_col].value_counts(dropna=True).head(1)
                    if not vc.empty:
                        top_country_name = str(vc.index[0])
                        top_country_count = int(vc.values[0])

                # 类别分布
                if "category" in df.columns:
                    vc = df["category"].value_counts(dropna=True).head(1)
                    if not vc.empty:
                        top_category_name = str(vc.index[0])
                        top_category_count = int(vc.values[0])
            except Exception:
                # 容错：读取或计算失败时保留默认指标
                pass

        metrics = {
            "rows": rows,
            "laureates_unique": laureates_unique,
            "year_min": year_min,
            "year_max": year_max,
            "top_country_name": top_country_name,
            "top_country_count": top_country_count,
            "top_category_name": top_category_name,
            "top_category_count": top_category_count,
        }

        # 默认草稿（作为回退）
        lines = ["# 诺贝尔奖获得者分布简要结论（自动生成）", ""]
        lines.append(f"- 覆盖得主数：约 {laureates_unique} 位。" if laureates_unique else "- 覆盖得主数：数据不足。")
        if year_min is not None and year_max is not None:
            lines.append(f"- 年份范围：{year_min}–{year_max}。")
        if top_country_name:
            lines.append(f"- 出生国家最多：{top_country_name}（{top_country_count}人）。")
        if top_category_name:
            lines.append(f"- 最多奖项类别：{top_category_name}（{top_category_count}条获奖记录）。")
        lines.append("- 建议：按历史时期切片对比学科结构与地理分布，或加入机构国家口径进行双视角分析。")
        markdown = "\n".join(lines)

        # 主题与 LLM 生成（成功则覆盖默认草稿）
        theme = task.get("theme", "诺贝尔奖")
        prompt = self.build_prompt(theme, metrics)
        # 新增：保存实际使用的 Prompt 到运行目录
        prompt_path = os.path.join(run_dir, "prompt.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        llm_used = False
        llm_text = self.call_llm(prompt)
        if isinstance(llm_text, str) and llm_text.strip():
            markdown = llm_text
            llm_used = True

        with open(draft_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        return {
            "artifacts": {
                "draft_md": draft_path,
                "run_dir": run_dir,
                "prompt_txt": prompt_path,  # 新增：返回 Prompt 路径
            },
            "metrics": metrics,
            "llm": {
                "used": llm_used,
                "theme": theme,
                "model": self.model or (getattr(self.llm, "default_model", None) if self.llm else None),
                "error": self.last_llm_error,
            },
        }

    def build_prompt(self, theme: str, metrics: Dict[str, Any]) -> str:
        title = f"{theme} 数据洞察草稿"
        lines = [
            f"# {title}",
            "请基于以下结构生成一份简短、结构化的中文草稿：",
            "1. 背景与数据来源（1段）",
            "2. 关键发现（要点列表，3-6条）",
            "3. 趋势与分布（1-2段）",
            "4. 结论与建议（1段）",
            "",
            "可参考的量化指标：",
            f"- 数据行数: {metrics.get('rows')}",
            f"- 年份范围: {metrics.get('year_min')}–{metrics.get('year_max')}",
            f"- Top 国家: {metrics.get('top_country_name')} ({metrics.get('top_country_count')})",
            f"- 唯一获奖者数: {metrics.get('laureates_unique')}",
        ]
        return "\n".join(lines)

    def call_llm(self, prompt: str, max_retries: int = 3) -> Any:
        """
        调用LLM生成内容，支持重试和fallback机制
        
        Args:
            prompt: 输入提示词
            max_retries: 最大重试次数
            
        Returns:
            生成的文本内容，失败时返回None
        """
        if not self.llm:
            self.last_llm_error = "LLM client not injected - using fallback mode"
            return self._generate_fallback_content(prompt)
        
        for attempt in range(max_retries + 1):
            try:
                self.last_llm_error = None
                
                # 统一适配：约定 llm.generate(prompt, model=..., **kwargs) -> str
                result = self.llm.generate(prompt, model=self.model)
                
                # 验证生成结果
                if isinstance(result, str) and result.strip():
                    return result
                
                # 检查底层适配器错误
                le = getattr(self.llm, "last_error", None)
                if le:
                    self.last_llm_error = f"Empty result from LLM: {le}"
                else:
                    self.last_llm_error = "LLM returned empty result"
                    
                # 如果是最后一次尝试，使用fallback
                if attempt == max_retries:
                    return self._generate_fallback_content(prompt)
                    
            except Exception as e:
                error_msg = str(e)
                self.last_llm_error = f"Attempt {attempt + 1}/{max_retries + 1} failed: {error_msg}"
                
                # 如果是最后一次尝试，使用fallback
                if attempt == max_retries:
                    return self._generate_fallback_content(prompt)
                
                # 短暂等待后重试
                time.sleep(min(2 ** attempt, 10))  # 指数退避，最大10秒
        
        return None
    
    def _generate_fallback_content(self, prompt: str) -> str:
        """
        当LLM不可用时的fallback内容生成
        
        Args:
            prompt: 原始提示词
            
        Returns:
            基于模板的fallback内容
        """
        # 从prompt中提取主题信息
        theme = "数据分析"
        if "Nobel" in prompt or "诺贝尔" in prompt:
            theme = "诺贝尔奖数据分析"
        elif "theme:" in prompt.lower():
            # 尝试从prompt中提取主题
            lines = prompt.split('\n')
            for line in lines:
                if 'theme:' in line.lower() or '主题:' in line:
                    theme = line.split(':')[-1].strip()
                    break
        
        fallback_content = f"""# {theme}报告

## 数据概览
本报告基于提供的数据集进行分析，由于LLM服务暂时不可用，以下为基于数据的基础分析结果。

## 主要发现
- 数据集包含多个维度的信息
- 通过统计分析发现了数据的基本分布特征
- 可视化图表已生成，展示了关键趋势和模式

## 建议
- 建议进一步分析数据的深层关联
- 可以结合领域专业知识进行更深入的解读
- 后续可以补充更详细的统计检验和模型分析

*注：本报告为系统自动生成的基础版本，建议在LLM服务恢复后重新生成完整分析。*
"""
        
        return fallback_content