"""
Web Dashboard API 模块

提供所有API路由的统一入口。
"""

from . import health, rag, tasks

__all__ = ["health", "rag", "tasks"]