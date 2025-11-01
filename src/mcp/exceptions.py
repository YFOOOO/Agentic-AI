"""
MCP 统一异常处理模块

提供标准化的异常类型和错误处理机制，确保系统错误信息的一致性和用户友好性。
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = "low"          # 轻微错误，不影响主要功能
    MEDIUM = "medium"    # 中等错误，影响部分功能
    HIGH = "high"        # 严重错误，影响核心功能
    CRITICAL = "critical" # 致命错误，系统无法继续运行


class ErrorCategory(Enum):
    """错误类别枚举"""
    VALIDATION = "validation"     # 输入验证错误
    CONFIGURATION = "configuration" # 配置错误
    NETWORK = "network"          # 网络相关错误
    LLM = "llm"                 # LLM服务错误
    FILE_IO = "file_io"         # 文件操作错误
    DATA_PROCESSING = "data_processing" # 数据处理错误
    AGENT = "agent"             # 代理执行错误
    SYSTEM = "system"           # 系统级错误


class MCPError(Exception):
    """MCP 基础异常类"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.suggestions = suggestions or []
        self.error_code = error_code or f"{category.value.upper()}_ERROR"
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """将异常转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat()
        }
    
    def get_user_message(self) -> str:
        """获取用户友好的错误消息"""
        base_message = f"[{self.category.value.upper()}] {self.message}"
        
        if self.suggestions:
            suggestions_text = "\n建议解决方案:\n" + "\n".join(f"  • {s}" for s in self.suggestions)
            return base_message + suggestions_text
        
        return base_message


class ValidationError(MCPError):
    """输入验证错误"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        if field:
            self.details["field"] = field


class ConfigurationError(MCPError):
    """配置错误"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "检查配置文件是否存在且格式正确",
                "验证环境变量是否正确设置",
                "参考文档中的配置示例"
            ]
        
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )
        if config_key:
            self.details["config_key"] = config_key


class NetworkError(MCPError):
    """网络相关错误"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, **kwargs):
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "检查网络连接是否正常",
                "验证API密钥是否有效",
                "稍后重试或联系服务提供商"
            ]
        
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        if url:
            self.details["url"] = url
        if status_code:
            self.details["status_code"] = status_code


class LLMError(MCPError):
    """LLM服务错误"""
    
    def __init__(self, message: str, provider: str = None, model: str = None, **kwargs):
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "检查API密钥配置是否正确",
                "验证模型名称是否支持",
                "尝试使用其他模型或降级到fallback模式"
            ]
        
        super().__init__(
            message,
            category=ErrorCategory.LLM,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        if provider:
            self.details["provider"] = provider
        if model:
            self.details["model"] = model


class FileIOError(MCPError):
    """文件操作错误"""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, **kwargs):
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "检查文件路径是否正确",
                "验证文件权限设置",
                "确保磁盘空间充足"
            ]
        
        super().__init__(
            message,
            category=ErrorCategory.FILE_IO,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        if file_path:
            self.details["file_path"] = file_path
        if operation:
            self.details["operation"] = operation


class DataProcessingError(MCPError):
    """数据处理错误"""
    
    def __init__(self, message: str, data_type: str = None, **kwargs):
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "检查输入数据格式是否正确",
                "验证数据完整性",
                "尝试使用数据清洗功能"
            ]
        
        super().__init__(
            message,
            category=ErrorCategory.DATA_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        if data_type:
            self.details["data_type"] = data_type


class AgentError(MCPError):
    """代理执行错误"""
    
    def __init__(self, message: str, agent_name: str = None, task_id: str = None, **kwargs):
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "检查代理配置是否正确",
                "验证输入参数格式",
                "查看详细日志获取更多信息"
            ]
        
        super().__init__(
            message,
            category=ErrorCategory.AGENT,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        if agent_name:
            self.details["agent_name"] = agent_name
        if task_id:
            self.details["task_id"] = task_id


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self, logger_name: str = "mcp"):
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = True
    ) -> Dict[str, Any]:
        """
        统一处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文信息
            reraise: 是否重新抛出异常
            
        Returns:
            错误信息字典
        """
        context = context or {}
        
        # 如果是MCP自定义异常，直接处理
        if isinstance(error, MCPError):
            error_info = error.to_dict()
            error_info["context"] = context
            
            # 记录日志
            log_level = self._get_log_level(error.severity)
            self.logger.log(log_level, f"{error.get_user_message()}")
            
            if reraise:
                raise error
            return error_info
        
        # 处理标准异常
        error_info = self._convert_standard_exception(error, context)
        
        # 记录日志
        self.logger.error(f"Unhandled exception: {str(error)}")
        self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        if reraise:
            # 将标准异常包装为MCP异常
            mcp_error = MCPError(
                message=str(error),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                details={"original_type": type(error).__name__},
                suggestions=["查看详细日志获取更多信息", "联系技术支持"]
            )
            raise mcp_error
        
        return error_info
    
    def _convert_standard_exception(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """将标准异常转换为统一格式"""
        error_type = type(error).__name__
        
        # 根据异常类型推断类别和严重程度
        category = ErrorCategory.SYSTEM
        severity = ErrorSeverity.MEDIUM
        suggestions = ["查看详细日志获取更多信息"]
        
        # 注意：检查顺序很重要，更具体的异常类型应该先检查
        if isinstance(error, (ConnectionError, TimeoutError)):
            category = ErrorCategory.NETWORK
            suggestions = [
                "检查网络连接",
                "稍后重试"
            ]
        elif isinstance(error, (FileNotFoundError, PermissionError, IOError)):
            category = ErrorCategory.FILE_IO
            suggestions = [
                "检查文件路径是否正确",
                "验证文件权限设置"
            ]
        elif isinstance(error, (ValueError, TypeError)):
            category = ErrorCategory.VALIDATION
            severity = ErrorSeverity.LOW
            suggestions = [
                "检查输入参数格式",
                "验证数据类型是否正确"
            ]
        
        return {
            "error_code": f"{category.value.upper()}_{error_type.upper()}",
            "message": str(error),
            "category": category.value,
            "severity": severity.value,
            "details": {
                "original_type": error_type,
                **context
            },
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """根据错误严重程度获取日志级别"""
        level_map = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return level_map.get(severity, logging.ERROR)
    
    def create_error_response(
        self,
        error: Exception,
        include_traceback: bool = False
    ) -> Dict[str, Any]:
        """
        创建标准化的错误响应
        
        Args:
            error: 异常对象
            include_traceback: 是否包含堆栈跟踪
            
        Returns:
            标准化错误响应
        """
        error_info = self.handle_error(error, reraise=False)
        
        response = {
            "success": False,
            "error": error_info
        }
        
        if include_traceback and not isinstance(error, MCPError):
            response["error"]["traceback"] = traceback.format_exc()
        
        return response


# 全局错误处理器实例
error_handler = ErrorHandler()


def handle_mcp_error(func):
    """MCP错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return error_handler.create_error_response(e)
    return wrapper