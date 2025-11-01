"""
任务管理 API 路由

提供研究任务的创建、管理和进度监控功能。
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import logging
import uuid

from config import get_settings, Settings

router = APIRouter()
logger = logging.getLogger(__name__)


# 枚举和模型定义
class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型枚举"""
    LITERATURE_REVIEW = "literature_review"
    DATA_ANALYSIS = "data_analysis"
    CHART_GENERATION = "chart_generation"
    DOCUMENT_PROCESSING = "document_processing"


class TaskCreate(BaseModel):
    """创建任务请求模型"""
    title: str
    description: Optional[str] = None
    task_type: TaskType
    parameters: Optional[dict] = {}


class Task(BaseModel):
    """任务模型"""
    id: str
    title: str
    description: Optional[str]
    task_type: TaskType
    status: TaskStatus
    parameters: dict
    progress: float  # 0.0 - 1.0
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    error_message: Optional[str] = None


class TaskUpdate(BaseModel):
    """更新任务请求模型"""
    status: Optional[TaskStatus] = None
    progress: Optional[float] = None
    result: Optional[dict] = None
    error_message: Optional[str] = None


# 模拟任务存储（实际应用中应使用数据库）
tasks_storage = {}


@router.post("/tasks", response_model=Task)
async def create_task(
    task_data: TaskCreate,
    settings: Settings = Depends(get_settings)
):
    """
    创建新的研究任务
    """
    try:
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            id=task_id,
            title=task_data.title,
            description=task_data.description,
            task_type=task_data.task_type,
            status=TaskStatus.PENDING,
            parameters=task_data.parameters,
            progress=0.0,
            created_at=now,
            updated_at=now
        )
        
        tasks_storage[task_id] = task
        
        logger.info(f"创建新任务: {task.title} (ID: {task_id})")
        
        return task
        
    except Exception as e:
        logger.error(f"创建任务时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/tasks", response_model=List[Task])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    获取任务列表
    """
    try:
        tasks = list(tasks_storage.values())
        
        # 过滤条件
        if status:
            tasks = [t for t in tasks if t.status == status]
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        
        # 排序（按创建时间倒序）
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        # 分页
        tasks = tasks[offset:offset + limit]
        
        return tasks
        
    except Exception as e:
        logger.error(f"获取任务列表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    获取特定任务的详细信息
    """
    try:
        if task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return tasks_storage[task_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详情时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, update_data: TaskUpdate):
    """
    更新任务状态和进度
    """
    try:
        if task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = tasks_storage[task_id]
        
        # 更新字段
        if update_data.status is not None:
            task.status = update_data.status
            if update_data.status == TaskStatus.IN_PROGRESS and task.started_at is None:
                task.started_at = datetime.now()
            elif update_data.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.now()
        
        if update_data.progress is not None:
            task.progress = max(0.0, min(1.0, update_data.progress))
        
        if update_data.result is not None:
            task.result = update_data.result
        
        if update_data.error_message is not None:
            task.error_message = update_data.error_message
        
        task.updated_at = datetime.now()
        
        logger.info(f"更新任务: {task.title} (ID: {task_id})")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新任务时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新任务失败: {str(e)}")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务
    """
    try:
        if task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = tasks_storage.pop(task_id)
        
        logger.info(f"删除任务: {task.title} (ID: {task_id})")
        
        return {"message": "任务已删除", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.get("/tasks/stats/summary")
async def get_tasks_summary():
    """
    获取任务统计摘要
    """
    try:
        tasks = list(tasks_storage.values())
        
        stats = {
            "total": len(tasks),
            "by_status": {},
            "by_type": {},
            "recent_activity": []
        }
        
        # 按状态统计
        for status in TaskStatus:
            stats["by_status"][status.value] = len([t for t in tasks if t.status == status])
        
        # 按类型统计
        for task_type in TaskType:
            stats["by_type"][task_type.value] = len([t for t in tasks if t.task_type == task_type])
        
        # 最近活动（最近5个更新的任务）
        recent_tasks = sorted(tasks, key=lambda x: x.updated_at, reverse=True)[:5]
        stats["recent_activity"] = [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "updated_at": t.updated_at
            }
            for t in recent_tasks
        ]
        
        return stats
        
    except Exception as e:
        logger.error(f"获取任务统计时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务统计失败: {str(e)}")