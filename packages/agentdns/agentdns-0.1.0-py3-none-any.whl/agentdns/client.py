"""AgentDNS Python SDK 客户端"""

import time
import random
import requests
import logging
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin

from .models import (
    Tool,
    CostInfo,
    Service, 
    Usage, 
    Balance
)
from .exceptions import (
    AgentDNSError,
    AuthenticationError,
    ServiceNotFoundError,
    RequestError,
    RateLimitError,
    InsufficientBalanceError,
    NetworkError,
    ServerError,
    ValidationError
)

logger = logging.getLogger(__name__)


class AgentDNS:
    """AgentDNS 客户端
    
    专为 LLM Agent 设计的根域名命名和服务发现系统客户端。
    
    Examples:
        >>> from agentdns import AgentDNS
        >>> 
        >>> # 基本使用
        >>> client = AgentDNS(api_key="your_api_key")
        >>> 
        >>> # 服务发现
        >>> tools = client.search("我需要一个搜索服务")
        >>> 
        >>> # 服务调用
        >>> data = {"q": "稳定币的定义", "scope": "webpage"}
        >>> response = client.request(tools[0]["agentdns_url"], json=data)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://agentdnsroot.com",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        初始化 AgentDNS 客户端
        
        Args:
            api_key: API 密钥（必需）
            base_url: API 基础 URL，默认为 https://agentdnsroot.com
            timeout: 请求超时时间（秒），默认30秒
            max_retries: 最大重试次数，默认3次
        """
        if not api_key:
            raise ValueError("API密钥不能为空")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 设置请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "AgentDNS-Python-SDK/2.0.0",
            "Content-Type": "application/json"
        })
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """关闭客户端"""
        self.session.close()
    
    def _exponential_backoff(self, attempt: int) -> float:
        """计算指数退避延迟时间"""
        base_delay = 1.0
        max_delay = 60.0
        delay = min(base_delay * (2 ** attempt), max_delay)
        # 添加随机抖动
        jitter = random.uniform(0.1, 0.9)
        return delay * jitter
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求，支持重试和指数退避
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 表单数据
            params: URL 参数
            json_data: JSON 数据
            
        Returns:
            Dict: 响应数据
        """
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"发送请求: {method} {url} (尝试 {attempt + 1}/{self.max_retries + 1})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    json=json_data,
                    timeout=self.timeout
                )
                
                # 处理HTTP状态码
                self._handle_response_status(response)
                
                # 返回JSON响应
                try:
                    return response.json()
                except ValueError:
                    if response.text:
                        return {"result": response.text}
                    return {}
                    
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout) as e:
                if attempt < self.max_retries:
                    delay = self._exponential_backoff(attempt)
                    logger.warning(f"网络错误，{delay:.2f}秒后重试: {str(e)}")
                    time.sleep(delay)
                    continue
                else:
                    raise NetworkError(f"网络请求失败: {str(e)}")
            
            except RateLimitError as e:
                if attempt < self.max_retries:
                    delay = self._exponential_backoff(attempt)
                    logger.warning(f"频率限制，{delay:.2f}秒后重试")
                    time.sleep(delay)
                    continue
                else:
                    raise e
    
    def _handle_response_status(self, response: requests.Response):
        """处理响应状态码"""
        if response.status_code == 200:
            return
        elif response.status_code == 401:
            raise AuthenticationError("API密钥无效或已过期", response.status_code)
        elif response.status_code == 402:
            raise InsufficientBalanceError("账户余额不足", response.status_code)
        elif response.status_code == 404:
            raise ServiceNotFoundError("请求的资源不存在", response.status_code)
        elif response.status_code == 429:
            raise RateLimitError("请求频率超限", response.status_code)
        elif response.status_code >= 500:
            raise ServerError(f"服务器内部错误: {response.status_code}", response.status_code)
        else:
            try:
                error_data = response.json()
                error_message = error_data.get("detail", f"请求失败: {response.status_code}")
            except:
                error_message = f"请求失败: {response.status_code}"
            raise RequestError(error_message, response.status_code)
    
    # === 核心API方法 ===
    
    def search(self, tool_need_prompt: str) -> List[Dict]:
        """
        根据自然语言描述搜索匹配的工具
        
        Args:
            tool_need_prompt: 工具需求的自然语言描述
            
        Returns:
            List[Dict]: 工具列表，每个工具为包含完整元数据的字典
        """
        search_data = {
            "query": tool_need_prompt,
            "limit": 10
        }
        
        response = self._make_request("POST", "/api/v1/discovery/search", json_data=search_data)
        
        if response.get("tools"):
            # 返回Tool格式的数据
            return response["tools"]
        else:
            # 向后兼容：如果返回的是旧格式，转换为新格式
            services = response.get("services", [])
        tools = []
        for service in services:
            tool = self._service_to_tool(service)
            tools.append(tool)
        return tools
    
    def request(
        self, 
        agentdns_url: str, 
        json: Optional[Dict] = None, 
        data: Optional[Dict] = None
    ) -> Dict:
        """
        调用指定工具并返回结果
        
        Args:
            agentdns_url: 工具的 AgentDNS URL 标识符（如 "agentdns://metaso-cn/search/websearch"）
            json: JSON 格式的请求数据（优先使用）
            data: 表单格式的请求数据
            
        Returns:
            Dict: 工具执行结果的字典
            
        Examples:
            >>> data = {"q": "稳定币", "scope": "webpage"}
            >>> result = client.request("agentdns://metaso-cn/search/websearch", json=data)
        """
        logger.info(f"调用工具: {agentdns_url}")
        
        # 清理URI前缀
        uri_path = agentdns_url.replace("agentdns://", "")
        
        # 优先使用json数据
        request_data = json if json is not None else data
        
        response = self._make_request(
            "POST",
            f"/api/v1/proxy/{uri_path}",
            data=data if json is None else None,
            json_data=json
        )
        
        logger.info(f"工具调用成功: {agentdns_url}")
        return response
    
    def get_tool_info(self, agentdns_identifier: str) -> Dict:
        """
        根据AgentDNS标识符获取工具详细信息
        
        Args:
            agentdns_identifier: 工具的完整标识符
            
        Returns:
            Dict: 工具详细信息字典
        """
        logger.info(f"获取工具信息: {agentdns_identifier}")
        
        # 规范化agentdns_identifier，去掉agentdns://前缀用于URL路径
        clean_identifier = agentdns_identifier
        if clean_identifier.startswith("agentdns://"):
            clean_identifier = clean_identifier[11:]  # 去掉 "agentdns://" 前缀
        
        response = self._make_request("GET", f"/api/v1/discovery/resolve/{clean_identifier}")
        
        # 如果返回的是Tool格式，直接返回
        if "cost" in response and isinstance(response["cost"], dict):
            return response
        else:
            # 如果是旧格式，转换为Tool格式
            return self._service_to_tool(response)
    
    def get_balance(self) -> Dict:
        """
        获取当前账户余额信息
        
        Returns:
            Dict: 包含余额、货币等信息的字典
            
        Examples:
            >>> balance = client.get_balance()
            >>> print(f"余额: {balance['balance']} {balance['currency']}")
        """
        logger.info("获取账户余额")
        
        response = self._make_request("GET", "/api/v1/billing/balance")
        return response
    
    # === 辅助方法 ===
    
    def _service_to_tool(self, service: Dict) -> Dict:
        """将Service对象转换为Tool格式"""
        # 构建cost对象
        cost_description_map = {
            "per_request": "按调用次数计费",
            "per_token": "按token数量计费",
            "per_mb": "按数据传输量计费",
            "monthly": "按月订阅计费",
            "yearly": "按年订阅计费"
        }
        
        pricing_model = service.get("pricing_model", "per_request")
        
        return {
            "name": service.get("name", ""),
            "description": service.get("description", ""),
            "organization": service.get("organization", "Unknown"),
            "agentdns_url": service.get("agentdns_uri", ""),
            "cost": {
                "type": pricing_model,
                "price": str(service.get("price_per_unit", 0.0)),
                "currency": service.get("currency", "CNY"),
                "description": cost_description_map.get(pricing_model, "按调用次数计费")
            },
            "method": service.get("http_method", "POST"),
            "input_description": service.get("input_description", "{}"),
            "output_description": service.get("output_description", "{}")
        }
    
    # === 扩展方法（保持向后兼容） ===
    
    def discover(self, query: str, **kwargs) -> List[Dict]:
        """向后兼容的方法，调用search"""
        return self.search(query)
    
    def call(self, agentdns_uri: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """向后兼容的方法，调用request"""
        return self.request(agentdns_uri, json=data)
    
    def resolve(self, agentdns_uri: str) -> Dict:
        """向后兼容的方法，调用get_tool_info"""
        return self.get_tool_info(agentdns_uri)
    
    # === 其他功能方法 ===
    
    def get_categories(self) -> List[str]:
        """获取可用的服务类别列表"""
        response = self._make_request("GET", "/api/v1/discovery/categories")
        return response
    
    def get_protocols(self) -> List[str]:
        """获取支持的协议列表"""
        response = self._make_request("GET", "/api/v1/discovery/protocols")
        return response
    
    def get_trending_services(self, limit: int = 10) -> List[Dict]:
        """获取热门服务"""
        params = {"limit": limit}
        response = self._make_request("GET", "/api/v1/discovery/trending", params=params)
        
        # 转换为Tool格式
        tools = []
        for service in response:
            tool = self._service_to_tool(service)
            tools.append(tool)
        
        return tools
    
    def get_usage_history(
        self, 
        service_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict]:
        """获取使用记录"""
        params = {"limit": limit}
        if service_id:
            params["service_id"] = service_id
        
        response = self._make_request("GET", "/api/v1/billing/usage", params=params)
        return response
    
    def get_billing_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取计费统计"""
        params = {"days": days}
        return self._make_request("GET", "/api/v1/billing/stats", params=params) 