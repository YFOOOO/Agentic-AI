# 目录结构优化方案

## 当前问题分析

### 1. 根目录文件散乱
- 演示文件直接放在根目录：`examples/demos/demo_accessible_charts.py`, `examples/demos/demo_caption_charts.py`, `examples/demos/demo_professional_templates.py`
- 临时测试文件混杂：`pre_commit_test.py`, `run_tests.py`
- 多个输出目录分散：`outputs/figures/demo_figures/`, `outputs/figures/enhanced_figures/`, `outputs/figures/test_accessibility_figures/`, `outputs/figures/test_colorblind_figures/`, `outputs/figures/test_output/`

### 2. artifacts目录结构混乱
- 历史运行文件冗余：88个 `run_*.zip` 和 `run_log_*.json` 文件
- 输出目录重复：多个功能相似的子目录
- 临时文件与正式输出混合

### 3. 功能模块分散
- 核心功能在 `src/` 下组织良好
- 演示代码、测试输出、临时文件缺乏统一管理

## 优化后的目录结构

```
Agentic-AI/
├── .github/                    # CI/CD配置
├── .githooks/                  # Git钩子
├── src/                        # 核心源代码（保持不变）
│   ├── agents/
│   ├── analysis/
│   ├── data/
│   ├── eval/
│   └── mcp/
├── tests/                      # 单元测试（保持不变）
├── examples/                   # 演示和示例代码
│   ├── demos/
│   │   ├── accessible_charts.py
│   │   ├── caption_charts.py
│   │   └── professional_templates.py
│   └── notebooks/
│       └── 逻辑框架与项目需求.ipynb
├── outputs/                    # 统一输出目录
│   ├── figures/                # 图表输出
│   ├── reports/                # 报告输出
│   └── templates/              # 模板演示
├── data/                       # 数据文件
│   └── nobel/
│       └── laureates_prizes.csv
├── scripts/                    # 工具脚本
│   ├── run_tests.py
│   └── setup_hooks.py
├── docs/                       # 文档
│   ├── README.md
│   ├── TESTING.md
│   └── reports/
├── .temp/                      # 临时文件（添加到.gitignore）
└── 配置文件（根目录保持）
    ├── requirements.txt
    ├── requirements-test.txt
    ├── setup.cfg
    ├── pytest.ini
    └── .gitignore
```

## 文件迁移计划

### 第一阶段：清理冗余文件
1. 删除 `artifacts/nobel/run_*.zip` 和 `run_log_*.json`（88个文件）
2. 删除重复的测试目录

### 第二阶段：重组目录结构
1. 创建新目录：`examples/`, `outputs/`, `data/`, `scripts/`, `docs/`
2. 迁移演示文件到 `examples/demos/`
3. 整合输出目录到 `outputs/`
4. 迁移数据文件到 `data/`
5. 迁移工具脚本到 `scripts/`

### 第三阶段：更新引用路径
1. 更新演示文件中的导入路径
2. 更新测试文件中的路径引用
3. 更新CI/CD配置中的路径

## 预期效果

1. **清晰的功能分离**：源码、测试、演示、输出各司其职
2. **减少根目录混乱**：只保留必要的配置文件
3. **统一的输出管理**：所有生成文件集中管理
4. **更好的可维护性**：新功能有明确的归属位置
5. **空间节省**：清理冗余文件节省约6MB空间