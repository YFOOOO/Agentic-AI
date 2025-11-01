# 测试指南

本文档介绍如何在本项目中运行测试，包括本地测试和CI/CD测试。

## 📋 目录

- [快速开始](#快速开始)
- [测试结构](#测试结构)
- [本地测试](#本地测试)
- [CI/CD测试](#cicd测试)
- [测试覆盖率](#测试覆盖率)
- [测试类型](#测试类型)
- [故障排除](#故障排除)

## 🚀 快速开始

### 安装测试依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装测试依赖
pip install -r requirements-test.txt
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 📁 测试结构

```
tests/
├── __init__.py
├── test_mcp_server.py              # MCP服务器测试
├── test_accessibility_features.py  # 无障碍功能测试
├── test_auto_caption.py            # 自动图说测试
├── test_chart_templates.py         # 图表模板测试
└── test_enhanced_viz_integration.py # 可视化集成测试
```

## 🔧 本地测试

### 运行特定测试文件

```bash
# 运行单个测试文件
pytest tests/test_auto_caption.py

# 运行特定测试类
pytest tests/test_auto_caption.py::TestAutoCaptionGenerator

# 运行特定测试方法
pytest tests/test_auto_caption.py::TestAutoCaptionGenerator::test_basic_caption_generation
```

### 使用标记运行测试

```bash
# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行可视化测试
pytest -m visualization

# 排除慢速测试
pytest -m "not slow"
```

### 并行测试

```bash
# 使用多个CPU核心并行运行测试
pytest -n auto

# 指定并行进程数
pytest -n 4
```

### 详细输出

```bash
# 显示详细输出
pytest -v

# 显示测试输出（print语句等）
pytest -s

# 组合使用
pytest -v -s
```

## 🔄 CI/CD测试

### GitHub Actions

项目配置了GitHub Actions自动化测试，包括：

- **多Python版本测试**: 3.9, 3.10, 3.11, 3.12
- **多操作系统测试**: Ubuntu, macOS
- **代码质量检查**: flake8 linting
- **测试覆盖率**: 自动生成覆盖率报告
- **集成测试**: 验证核心功能

### 触发条件

- 推送到 `main` 或 `develop` 分支
- 创建Pull Request到 `main` 或 `develop` 分支
- 手动触发 (workflow_dispatch)

### 查看测试结果

1. 访问GitHub仓库的Actions页面
2. 查看最新的工作流运行结果
3. 点击具体的job查看详细日志

## 📊 测试覆盖率

### 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest --cov=src --cov-report=html

# 生成XML覆盖率报告（用于CI）
pytest --cov=src --cov-report=xml

# 生成终端覆盖率报告
pytest --cov=src --cov-report=term-missing
```

### 查看覆盖率报告

```bash
# 在浏览器中打开HTML报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 覆盖率目标

- **最低覆盖率**: 80%
- **目标覆盖率**: 90%+
- **关键模块**: 95%+

## 🧪 测试类型

### 单元测试 (Unit Tests)

测试单个函数或类的功能：

```python
import pytest
from src.analysis.auto_caption import AutoCaptionGenerator

@pytest.mark.unit
def test_caption_generation():
    generator = AutoCaptionGenerator()
    caption = generator.generate_caption(data, "bar", "Test Chart")
    assert isinstance(caption, str)
    assert len(caption) > 0
```

### 集成测试 (Integration Tests)

测试多个组件的协作：

```python
@pytest.mark.integration
def test_full_visualization_pipeline():
    agent = EnhancedVizAgent()
    fig = agent.create_interactive_bar_chart(df, 'x', 'y', template='business')
    assert fig is not None
```

### 可视化测试 (Visualization Tests)

测试图表生成功能：

```python
@pytest.mark.visualization
def test_chart_template_application():
    agent = EnhancedVizAgent()
    templates = agent.list_available_templates()
    assert len(templates) >= 8
```

### 无障碍测试 (Accessibility Tests)

测试无障碍功能：

```python
@pytest.mark.accessibility
def test_color_contrast_validation():
    checker = AccessibilityChecker()
    result = checker.check_color_contrast('#000000', '#FFFFFF')
    assert result['passes']
```

## 🐛 故障排除

### 常见问题

#### 1. 图形显示问题 (Linux)

```bash
# 安装虚拟显示
sudo apt-get install xvfb

# 使用虚拟显示运行测试
xvfb-run -a pytest
```

#### 2. 依赖冲突

```bash
# 清理pip缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

#### 3. 测试文件未发现

确保：
- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 测试类以 `Test` 开头
- `__init__.py` 文件存在于tests目录

#### 4. 覆盖率报告不准确

```bash
# 清理之前的覆盖率数据
coverage erase

# 重新运行测试
pytest --cov=src --cov-report=html
```

### 调试测试

```bash
# 在第一个失败处停止
pytest -x

# 进入调试器
pytest --pdb

# 显示最慢的10个测试
pytest --durations=10
```

## 📝 编写新测试

### 测试文件命名

- 文件名: `test_<module_name>.py`
- 放置位置: `tests/` 目录下

### 测试函数结构

```python
import pytest
from src.your_module import YourClass

class TestYourClass:
    def setup_method(self):
        """每个测试方法前运行"""
        self.instance = YourClass()
    
    def test_basic_functionality(self):
        """测试基本功能"""
        result = self.instance.method()
        assert result is not None
    
    @pytest.mark.slow
    def test_performance(self):
        """性能测试"""
        # 耗时测试代码
        pass
```

### 使用fixtures

```python
@pytest.fixture
def sample_data():
    return pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})

def test_with_fixture(sample_data):
    assert len(sample_data) == 3
```

## 🔗 相关资源

- [pytest文档](https://docs.pytest.org/)
- [coverage.py文档](https://coverage.readthedocs.io/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [项目README](./README.md)

---

如有问题，请查看项目的Issue页面或联系维护者。