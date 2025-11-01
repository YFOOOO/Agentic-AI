# Agentic-AI
Learning use agentic ai and develop the agent

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
