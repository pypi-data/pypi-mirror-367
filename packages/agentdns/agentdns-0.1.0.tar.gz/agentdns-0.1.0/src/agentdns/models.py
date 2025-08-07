"""
AgentDNS SDK 数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class CostInfo(BaseModel):
    """费用信息"""
    type: str  # per_request, per_token, per_mb, etc.
    price: str  # 字符串格式的价格
    currency: str = "CNY"
    description: str = "按调用次数计费"


class Tool(BaseModel):
    """符合AgentDNS SDK规范的Tool对象"""
    name: str
    description: str
    organization: str  # 组织名称
    agentdns_url: str  # agentdns://org/category/service
    cost: CostInfo
    method: str = "POST"
    input_description: str
    output_description: str


class ToolsListResponse(BaseModel):
    """tools_list API响应格式"""
    tools: List[Tool]
    total: int
    query: str


class Service(BaseModel):
    """服务信息（向后兼容）"""
    id: int
    name: str
    description: str
    category: Optional[str] = None
    agentdns_uri: str
    agentdns_path: Optional[str] = None
    http_method: Optional[str] = None
    cost: Optional[float] = None
    currency: str = "CNY"
    organization: Optional[str] = None
    input_description: Optional[str] = None
    output_description: Optional[str] = None


class Usage(BaseModel):
    """使用记录"""
    id: int
    service_name: str
    cost: float
    currency: str = "CNY"
    timestamp: datetime
    tokens_used: Optional[int] = None
    requests_count: int = 1


class Balance(BaseModel):
    """账户余额信息"""
    balance: float
    currency: str = "CNY"
    last_updated: datetime


# 向后兼容的别名
ProxyResponse = Dict[str, Any] 