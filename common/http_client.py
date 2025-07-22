import time
import json
from typing import Dict, Any, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from common.logger import logger


class HttpClient:
    """HTTP客户端封装类"""
    
    def __init__(self, base_url: str = "", timeout: int = 30, retry_times: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_times = retry_times
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建会话对象"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.retry_times,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置默认请求头
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "API-Test-Framework/1.0"
        })
        
        return session
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整URL"""
        if endpoint.startswith('http'):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def _log_request(self, method: str, url: str, **kwargs) -> None:
        """记录请求日志"""
        logger.info(f"发送 {method} 请求到: {url}")
        if 'json' in kwargs:
            logger.debug(f"请求体: {json.dumps(kwargs['json'], ensure_ascii=False, indent=2)}")
        if 'data' in kwargs:
            logger.debug(f"请求数据: {kwargs['data']}")
    
    def _log_response(self, response: requests.Response) -> None:
        """记录响应日志"""
        logger.info(f"响应状态码: {response.status_code}")
        try:
            response_json = response.json()
            logger.debug(f"响应体: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        except:
            logger.debug(f"响应体: {response.text[:500]}...")
    
    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """发送HTTP请求"""
        url = self._build_url(endpoint)
        
        # 设置超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        self._log_request(method, url, **kwargs)
        
        start_time = time.time()
        response = self.session.request(method, url, **kwargs)
        end_time = time.time()
        
        logger.info(f"请求耗时: {end_time - start_time:.2f}秒")
        self._log_response(response)
        
        return response
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """发送PUT请求"""
        return self.request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self.request("DELETE", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """发送PATCH请求"""
        return self.request("PATCH", endpoint, **kwargs)
    
    def close(self) -> None:
        """关闭会话"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 