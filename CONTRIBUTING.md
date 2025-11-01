# 贡献指南（简要）

欢迎参与本项目！下面列出在本地开发、提交与在 CI 中验证代码的一组最小步骤，帮助你快速上手并保证提交质量。

## 开发环境（推荐）

建议使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
```

安装依赖（可选——如果只需要运行 linters/tests，可只安装对应工具）：

```bash
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
```

## 启用并使用 pre-commit（强烈推荐）

本仓库包含 `.pre-commit-config.yaml`，会在本地提交时自动运行格式化和静态检查（Black / Ruff / isort 等）。

在本地运行一次安装并启用：

```bash
pip install pre-commit
pre-commit install
# 可选：对所有文件运行一次检查并自动修复可修复项
pre-commit run --all-files
```

如果 CI 报告有 pre-commit 问题，通常在本地运行 `pre-commit run --all-files` 即可看到并修复差异。

## 本地快速命令（lint / test / coverage）

下面的命令可在本地用于检查和运行测试：

```bash
# Lint（ruff）
python -m pip install ruff
ruff check src tests

# 代码格式检查（Black）
python -m pip install black isort
black --check .
isort --check-only .

# 运行 pytest 并生成 coverage.xml
python -m pip install pytest coverage
pytest -q --maxfail=1 --disable-warnings --cov=src --cov-report=xml
```

## CI 行为简介

- 我们在 `.github/workflows/ci.yml` 中设置了两个主要 job：`lint` 和 `test`。
- `lint` job 会先运行 `pre-commit`，然后运行 `ruff`（若 `ruff` 报错，CI 会失败）。
- `test` job 在 Ubuntu 上针对 Python 3.10/3.11 运行 `pytest`，并在 3.11 上上传 `coverage.xml` 到 Codecov（如配置）。

## 建议的工作流（PR 提交前）

1. 在新分支完成开发并运行本地测试和 lint：
   - `pre-commit run --all-files`（会自动修复很多问题）
   - `ruff check src tests` 或 `pre-commit run --all-files`
   - `pytest -q`（确认测试通过）

2. 提交并推送到远端分支，创建 PR。CI 会自动运行 lint 与 tests。

3. 修复 CI 报告的问题并再次提交，直到 CI 通过。

## 其他说明

- 如果需要临时绕过 pre-commit（不推荐），可以在提交时用 `git commit --no-verify`，但请事后修复该分支问题。
- 若遇到大型或敏感文件误提交问题，请联系仓库管理员讨论历史清理策略（`git filter-repo` / BFG）。

感谢你的贡献！如果需要我把这份指南合并到 `README.md` 或在 PR 模板中加上检查项，我可以继续帮你处理。
