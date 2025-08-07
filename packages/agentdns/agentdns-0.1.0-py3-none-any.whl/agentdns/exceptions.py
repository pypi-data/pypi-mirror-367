"""AgentDNS SDK 异常定义"""

from typing import Optional, Dict, Any


class AgentDNSError(Exception):
    """AgentDNS 基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(AgentDNSError):
    """认证错误"""
    pass


class ServiceNotFoundError(AgentDNSError):
    """服务未找到错误"""
    pass


class RequestError(AgentDNSError):
    """请求错误"""
    pass


class RateLimitError(AgentDNSError):
    """频率限制错误"""
    pass


class InsufficientBalanceError(AgentDNSError):
    """余额不足错误"""
    pass


class ValidationError(AgentDNSError):
    """数据验证错误"""
    pass


class NetworkError(AgentDNSError):
    """网络错误"""
    pass


class ServerError(AgentDNSError):
    """服务器内部错误"""
    pass


# 保持向后兼容
ProxyError = RequestError 