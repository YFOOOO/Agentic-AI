"""
健康检查 API 路由

提供系统健康状态检查和监控功能。
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import sys
import os

from config import get_settings, Settings

router = APIRouter()


@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    系统健康检查
    
    返回系统基本状态信息，包括服务状态、系统资源使用情况等。
    """
    try:
        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": {
                "name": settings.app_name,
                "version": "1.0.0",
                "environment": settings.environment,
                "debug": settings.debug
            },
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "memory_available": f"{memory.available / (1024**3):.2f} GB",
                "disk_usage": f"{disk.percent}%",
                "disk_free": f"{disk.free / (1024**3):.2f} GB"
            },
            "python": {
                "version": sys.version,
                "executable": sys.executable
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/health/ready")
async def readiness_check():
    """
    就绪状态检查
    
    检查服务是否准备好接收请求。
    """
    # 这里可以添加更复杂的就绪检查逻辑
    # 例如检查数据库连接、外部服务等
    
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "message": "服务已准备就绪"
    }


@router.get("/health/live")
async def liveness_check():
    """
    存活状态检查
    
    检查服务是否仍在运行。
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "message": "服务正在运行"
    }