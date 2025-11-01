# 文件命名规范分析报告

## 当前命名模式分析

### 1. Python文件命名模式

#### 一致的模式（推荐保持）
- **下划线分隔**：`enhanced_viz.py`, `auto_caption.py`, `chart_templates.py`
- **功能描述清晰**：`accessibility_checker.py`, `nobel_analysis.py`

#### 不一致的模式（需要统一）
- **演示文件前缀不统一**：
  - `examples/demos/demo_accessible_charts.py` ✅ 
  - `examples/demos/demo_caption_charts.py` ✅
  - `examples/demos/demo_professional_templates.py` ✅
  - 但位置散乱（应移至 `examples/demos/`）

- **测试文件命名混乱**：
  - `pre_commit_test.py` ❌ （应为 `test_pre_commit.py` 或移至 `scripts/`）
  - `run_tests.py` ❌ （应移至 `scripts/`）

### 2. 目录命名模式

#### 严重不一致的问题
- **输出目录命名混乱**：
  - `outputs/figures/demo_figures/` - 下划线分隔
  - `outputs/figures/enhanced_figures/` - 下划线分隔
  - `outputs/figures/test_accessibility_figures/` - 下划线分隔，但过长
  - `outputs/figures/test_colorblind_figures/` - 下划线分隔，但过长
  - `test_output/` - 下划线分隔

- **模板相关目录不统一**：
  - `artifacts/template_demo/` - 下划线分隔
  - `artifacts/template_test/` - 下划线分隔
  - `artifacts/template_features/` - 下划线分隔
  - `artifacts/professional_templates/` - 下划线分隔

### 3. 配置文件命名

#### 一致性良好
- `requirements.txt` ✅
- `requirements-test.txt` ✅ （连字符分隔）
- `setup.cfg` ✅
- `pytest.ini` ✅

#### 文档文件命名问题
- `README.md` ✅ （标准）
- `TESTING.md` ✅ （全大写，标准）
- `TEST_SETUP_SUMMARY.md` ✅ （全大写+下划线）
- `11.1项目评估报告.md` ❌ （中文+数字，不规范）
- `directory_optimization_plan.md` ✅ （下划线分隔）

## 命名规范建议

### 1. Python文件命名规范
```
- 使用小写字母和下划线分隔：snake_case
- 功能描述清晰：accessibility_checker.py
- 演示文件前缀：demo_*.py
- 测试文件前缀：test_*.py
- 工具脚本后缀：*_script.py 或 *_tool.py
```

### 2. 目录命名规范
```
- 使用小写字母和下划线分隔
- 功能分组清晰：
  - examples/ (演示代码)
  - outputs/ (输出文件)
  - scripts/ (工具脚本)
  - docs/ (文档)
```

### 3. 文档文件命名规范
```
- 重要文档全大写：README.md, TESTING.md
- 普通文档下划线分隔：project_plan.md
- 避免中文文件名
- 使用英文描述性名称
```

## 需要重命名的文件

### 立即重命名
1. `11.1项目评估报告.md` → `project_evaluation_report.md`
2. `pre_commit_test.py` → 移至 `scripts/pre_commit_check.py`
3. `run_tests.py` → 移至 `scripts/run_tests.py`

### 目录重组（按优化方案执行）
1. 所有 `demo_*.py` → `examples/demos/`
2. 所有输出目录 → `outputs/`
3. 所有模板相关 → `outputs/templates/`

## 命名一致性评分

- **Python源码文件**: 85% ✅ （src/目录下规范良好）
- **演示文件**: 70% ⚠️ （命名一致但位置散乱）
- **配置文件**: 90% ✅ （基本规范）
- **文档文件**: 60% ❌ （存在中文命名）
- **目录结构**: 40% ❌ （严重不一致）

**总体评分**: 69% - 需要改进