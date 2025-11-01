# 环境配置指南

本文档详细说明了Agentic-AI项目在不同环境下的配置要求和使用方法。

## 📋 目录

- [环境概述](#环境概述)
- [本地开发环境](#本地开发环境)
- [仓库测试环境](#仓库测试环境)
- [生产部署环境](#生产部署环境)
- [API Key管理](#api-key管理)
- [环境切换](#环境切换)
- [故障排除](#故障排除)

## 🌍 环境概述

项目支持三种主要环境配置：

| 环境类型 | 配置文件 | 主要用途 | 推荐模型 |
|---------|---------|---------|---------|
| 本地开发 | `.env.local` | 开发调试 | qwen, deepseek |
| 仓库测试 | `.env.test` | CI/CD测试 | openai (稳定) |
| 生产部署 | `.env.prod` | 生产环境 | 可配置 |

## 🛠️ 本地开发环境

### 配置要求

1. **模型支持**：优先使用qwen和deepseek模型
2. **aisuite版本**：使用本地克隆的扩展版本
3. **调试功能**：启用详细日志和进度条

### 快速设置

```bash
# 1. 复制本地开发配置
cp .env.local .env

# 2. 配置本地aisuite路径
# 编辑 .env 文件，确保 AISUITE_PATH 指向正确路径
AISUITE_PATH=/path/to/your/local/aisuite

# 3. 配置API Keys
DASHSCOPE_API_KEY=your_dashscope_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# 4. 安装依赖
pip install -r requirements.txt

# 5. 验证配置
python -m src.mcp.api_key_manager --check --env-file .env
```

### 本地开发特性

- ✅ **模型切换**：支持qwen和deepseek之间快速切换
- ✅ **缓存加速**：启用本地缓存提升开发效率
- ✅ **详细日志**：DEBUG级别日志便于调试
- ✅ **自动重载**：代码变更自动重载
- ✅ **进度显示**：显示处理进度条

### 推荐配置

```env
# 主要模型配置
NOBEL_LLM_MODEL=dashscope:qwen3-max
FALLBACK_MODEL=deepseek:deepseek-chat

# 开发优化
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_CACHE=true
SHOW_PROGRESS_BARS=true
```

## 🧪 仓库测试环境

### 配置要求

1. **稳定性优先**：使用标准aisuite包
2. **模型选择**：使用稳定的OpenAI模型
3. **自动化支持**：支持CI/CD集成

### CI/CD配置

```yaml
# .github/workflows/ci.yml 示例
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  DASHSCOPE_API_KEY: ${{ secrets.DASHSCOPE_API_KEY }}
  DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}

steps:
  - name: Setup Environment
    run: |
      cp .env.test .env
      pip install -r requirements.txt
  
  - name: Validate API Keys
    run: |
      python -m src.mcp.api_key_manager --validate --env-file .env
  
  - name: Run Tests
    run: |
      pytest --cov=src tests/
```

### 测试环境特性

- ✅ **API Key验证**：自动验证API Key有效性
- ✅ **覆盖率报告**：生成测试覆盖率报告
- ✅ **并行测试**：支持并行执行测试
- ✅ **超时控制**：设置合理的超时时间
- ✅ **无缓存**：确保测试一致性

## 🚀 生产部署环境

### 配置要求

1. **高可用性**：支持多模型负载均衡
2. **安全性**：API Key加密和轮换
3. **监控**：性能监控和日志记录
4. **扩展性**：支持分布式缓存

### Docker部署示例

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY .env.prod .env

EXPOSE 8000
CMD ["python", "-m", "src.mcp.server"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  agentic-ai:
    build: .
    environment:
      - LLM_MODEL=deepseek:deepseek-chat
      - ENABLE_CACHE=true
      - CACHE_TYPE=redis
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### 生产环境特性

- ✅ **负载均衡**：多模型负载均衡
- ✅ **API Key管理**：自动轮换和加密
- ✅ **性能监控**：实时性能指标
- ✅ **分布式缓存**：Redis缓存支持
- ✅ **安全配置**：速率限制和安全头
- ✅ **健康检查**：服务健康状态监控

## 🔐 API Key管理

### 自动更新功能

项目提供了完整的API Key管理功能：

```bash
# 检查API Key状态
python -m src.mcp.api_key_manager --check

# 验证所有API Key
python -m src.mcp.api_key_manager --validate

# 执行自动更新检查
python -m src.mcp.api_key_manager --auto-update

# 轮换API Keys
python -m src.mcp.api_key_manager --rotate
```

### 配置选项

```env
# API Key管理配置
ENABLE_API_KEY_AUTO_UPDATE=true
API_KEY_UPDATE_INTERVAL=3600
API_KEY_VALIDATION_ENABLED=true
API_KEY_ROTATION_ENABLED=false
ENABLE_API_KEY_ENCRYPTION=true
```

### 安全最佳实践

1. **加密存储**：启用API Key加密
2. **定期轮换**：设置自动轮换周期
3. **备份机制**：配置备份API Key
4. **访问控制**：限制API Key文件权限
5. **监控告警**：监控API Key使用情况

## 🔄 环境切换

### 快速切换命令

```bash
# 切换到本地开发环境
cp .env.local .env

# 切换到测试环境
cp .env.test .env

# 切换到生产环境
cp .env.prod .env
```

### 环境验证

```bash
# 验证当前环境配置
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'环境: {os.getenv(\"ENVIRONMENT\", \"未知\")}')
print(f'模型: {os.getenv(\"NOBEL_LLM_MODEL\", \"未配置\")}')
print(f'调试: {os.getenv(\"DEBUG\", \"false\")}')
"
```

## 🔧 故障排除

### 常见问题

#### 1. qwen模型调用失败

**问题**：`No module named 'dashscope'`

**解决方案**：
```bash
# 安装dashscope依赖
pip install dashscope>=1.14.0

# 或者切换到deepseek模型
export NOBEL_LLM_MODEL=deepseek:deepseek-chat
```

#### 2. 本地aisuite不生效

**问题**：仍使用标准aisuite包

**解决方案**：
```bash
# 检查AISUITE_PATH配置
echo $AISUITE_PATH

# 确保路径正确且未被注释
grep AISUITE_PATH .env
```

#### 3. API Key验证失败

**问题**：API Key无效或过期

**解决方案**：
```bash
# 验证API Key
python -m src.mcp.api_key_manager --validate

# 更新API Key
# 编辑 .env 文件更新相应的API Key
```

#### 4. 模型切换不生效

**问题**：模型切换后仍使用旧模型

**解决方案**：
```bash
# 清除缓存
rm -rf .cache/

# 重启应用
# 确保重新加载环境变量
```

### 调试技巧

1. **启用详细日志**：
   ```env
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

2. **检查环境变量**：
   ```bash
   python -c "import os; print({k:v for k,v in os.environ.items() if 'API_KEY' in k or 'MODEL' in k})"
   ```

3. **测试模型连接**：
   ```bash
   python -c "
   from src.mcp.orchestrator import get_llm_client_from_env
   client = get_llm_client_from_env()
   print(f'客户端类型: {type(client).__name__}')
   print(f'默认模型: {getattr(client, \"default_model\", \"未知\")}')
   "
   ```

## 📞 技术支持

如果遇到配置问题，请：

1. 检查本文档的故障排除部分
2. 查看项目的GitHub Issues
3. 运行诊断命令获取详细信息
4. 提供完整的错误日志和环境信息

---

**注意**：请勿在版本控制中提交包含真实API Key的配置文件。使用环境变量或密钥管理系统来管理敏感信息。