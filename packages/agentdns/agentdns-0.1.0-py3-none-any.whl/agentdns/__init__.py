"""
AgentDNS Python SDK

专为 LLM Agent 设计的根域名命名和服务发现系统 Python 客户端。

Examples:
    基本使用：
    >>> from agentdns import AgentDNS
    >>> 
    >>> # 初始化客户端
    >>> client = AgentDNS(
    ...     api_key="your_agentdns_api_key",
    ...     base_url="https://agentdnsroot.com"
    ... )
    >>> 
    >>> # 服务发现
    >>> tools = client.search("我需要一个搜索服务")
    >>> 
    >>> # 服务调用
    >>> data = {
    ...     "q": "稳定币的定义和类型",
    ...     "scope": "webpage",
    ...     "includeSummary": True,
    ...     "size": 10
    ... }
    >>> response = client.request(tools[0]["agentdns_url"], json=data)
    
    异步使用：
    >>> import asyncio
    >>> from agentdns import AsyncAgentDNS
    >>> 
    >>> async def main():
    ...     async with AsyncAgentDNS(api_key="your_api_key") as client:
    ...         tools = await client.search("我需要一个搜索服务")
    ...         response = await client.request(tools[0]["agentdns_url"], json=data)
    >>> 
    >>> asyncio.run(main())
"""

__version__ = "2.0.0"
__author__ = "AgentDNS Team"
__email__ = "team@agentdns.com"

# 导入主要类
from .client import AgentDNS
from .async_client import AsyncAgentDNS

# 导入异常类
from .exceptions import (
    AgentDNSError,
    AuthenticationError,
    ServiceNotFoundError,
    RequestError,
    RateLimitError,
    InsufficientBalanceError,
    NetworkError,
    ServerError,
    ValidationError,
    # 向后兼容
    ProxyError,
)

# 导入模型类
from .models import (
    Tool,
    CostInfo,
    Service,
    Usage,
    Balance,
)

__all__ = [
    # 主要客户端类
    "AgentDNS",
    "AsyncAgentDNS",
    
    # 异常类
    "AgentDNSError",
    "AuthenticationError", 
    "ServiceNotFoundError",
    "RequestError",
    "RateLimitError",
    "InsufficientBalanceError",
    "NetworkError",
    "ServerError",
    "ValidationError",
    "ProxyError",  # 向后兼容
    
    # 模型类
    "Tool",
    "CostInfo",
    "Service",
    "ServiceDiscovery",
    "Usage",
    "Organization",
    "User",
    "Balance",
] 