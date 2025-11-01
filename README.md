# Agentic-AI

智能代理AI项目，支持多模型集成和灵活的环境配置。

## 🚀 快速开始

### 环境配置

项目支持三种环境配置，满足不同使用场景：

| 环境 | 配置文件 | 用途 | 推荐模型 |
|-----|---------|------|---------|
| 本地开发 | `.env.local` | 开发调试 | qwen, deepseek |
| 仓库测试 | `.env.test` | CI/CD | openai |
| 生产部署 | `.env.prod` | 生产环境 | 可配置 |

### 本地开发设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd Agentic-AI

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置本地环境
cp .env.local .env

# 4. 配置API Keys
# 编辑 .env 文件，添加你的API Keys：
# DASHSCOPE_API_KEY=your_dashscope_api_key
# DEEPSEEK_API_KEY=your_deepseek_api_key

# 5. 验证配置
python -m src.mcp.api_key_manager --check
```

### 模型支持

- **qwen模型**：通过dashscope provider（本地开发推荐）
- **deepseek模型**：高性能开源模型
- **openai模型**：稳定的生产级模型

## 📚 文档

- [环境配置指南](./docs/ENVIRONMENT_SETUP.md) - 详细的环境配置说明
- [测试文档](./TESTING.md) - 测试系统使用指南
- [API文档](./docs/) - API接口文档

## 🧪 测试

本项目配置了完整的测试系统，帮助你在推送代码前验证更改。

### 快速开始

```bash
# 安装依赖
pip install -r requirements.txt
pip install -r requirements-test.txt

# 运行所有测试
pytest tests/

# 预提交检查
python pre_commit_test.py
```

### 测试选项

```bash
# 使用测试运行器
python run_tests.py --help
python run_tests.py --fast        # 快速测试
python run_tests.py --coverage    # 带覆盖率的测试
python run_tests.py --lint        # 代码质量检查
```

### CI/CD

项目配置了GitHub Actions自动化测试，支持：
- 多Python版本 (3.9-3.12)
- 多操作系统 (Ubuntu, macOS)
- 自动化测试和覆盖率报告

详细测试文档请参考 [TESTING.md](./TESTING.md)
