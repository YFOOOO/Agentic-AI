"""
智能研究助手 Web Dashboard - FastAPI 后端主应用

这是Web Dashboard的后端服务，提供RESTful API接口，
集成RAG系统、任务管理和进度监控功能。
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from config.settings import get_settings
from api import health, rag, tasks
from routers import citations

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 启动智能研究助手 Web Dashboard 后端服务")
    logger.info(f"📊 运行环境: {settings.environment}")
    logger.info(f"🔧 调试模式: {settings.debug}")
    
    yield
    
    logger.info("🛑 关闭智能研究助手 Web Dashboard 后端服务")


# 创建FastAPI应用实例
app = FastAPI(
    title="智能研究助手 Web Dashboard API",
    description="提供RAG系统、任务管理和进度监控的RESTful API接口",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "message": "服务暂时不可用，请稍后重试" if not settings.debug else str(exc)
        }
    )


# 注册API路由
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(rag.router, prefix="/api/v1", tags=["RAG系统"])
app.include_router(tasks.router, prefix="/api/v1", tags=["任务管理"])
app.include_router(citations.router, prefix="/api/v1", tags=["引用管理"])


@app.get("/")
async def root():
    """根路径欢迎信息"""
    return {
        "message": "欢迎使用智能研究助手 Web Dashboard API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "文档在生产环境中不可用",
        "status": "运行中"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )