"""
Web Dashboard 后端配置管理

使用Pydantic Settings进行配置管理，支持环境变量和.env文件。
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    app_name: str = Field(default="智能研究助手 Web Dashboard", description="应用名称")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=True, description="调试模式")
    
    # 服务器配置
    host: str = Field(default="127.0.0.1", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    
    # CORS配置
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="允许的跨域源"
    )
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///./dashboard.db", description="数据库连接URL")
    
    # RAG系统配置
    rag_collection_name: str = Field(default="research_documents", description="RAG向量集合名称")
    rag_embedding_model: str = Field(default="all-MiniLM-L6-v2", description="嵌入模型名称")
    rag_max_results: int = Field(default=10, description="RAG搜索最大结果数")
    
    # 文件上传配置
    max_file_size: int = Field(default=10 * 1024 * 1024, description="最大文件大小(字节)")  # 10MB
    allowed_file_types: List[str] = Field(
        default=[".txt", ".pdf", ".docx", ".md"],
        description="允许的文件类型"
    )
    upload_dir: str = Field(default="./uploads", description="文件上传目录")
    
    # 安全配置
    secret_key: str = Field(default="your-secret-key-change-in-production", description="密钥")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="./logs/dashboard.log", description="日志文件路径")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
_settings = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
        
        # 确保必要的目录存在
        os.makedirs(os.path.dirname(_settings.log_file), exist_ok=True)
        os.makedirs(_settings.upload_dir, exist_ok=True)
        
    return _settings