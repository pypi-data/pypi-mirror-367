"""
TopStack 客户端核心模块
"""

import json
import time
from typing import Any, Dict, Generic, Optional, TypeVar, Union
from datetime import datetime
import requests
from pydantic import BaseModel, Field

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    """API 响应模型"""
    status: Optional[int] = Field(None, description="HTTP 状态码")
    code: Optional[str] = Field(None, description="响应代码")
    msg: Optional[str] = Field(None, description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    def __str__(self) -> str:
        if self.msg:
            return f"{self.code}: {self.msg}"
        return self.code or "Unknown error"

class TopStackClient:
    """TopStack 客户端"""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        project_id: str,
        timeout: int = 20,
        verify_ssl: bool = False
    ):
        """
        初始化客户端
        
        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            project_id: 项目 ID
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证 SSL 证书
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.project_id = project_id
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # 创建会话
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key,
            'x-ProjectID': project_id,
        })
        
        if not verify_ssl:
            # 禁用 SSL 验证警告
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        response_model: Optional[type] = None
    ) -> Response:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求数据
            response_model: 响应数据模型
            
        Returns:
            Response 对象
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # 解析响应
            resp_data = response.json() if response.content else {}
            
            # 创建响应对象
            api_response = Response(
                status=response.status_code,
                code=resp_data.get('code'),
                msg=resp_data.get('msg'),
                data=resp_data.get('data')
            )
            
            # 如果提供了响应模型，尝试解析数据
            if response_model and api_response.data:
                try:
                    if isinstance(api_response.data, list):
                        api_response.data = [response_model(**item) for item in api_response.data]
                    else:
                        api_response.data = response_model(**api_response.data)
                except Exception as e:
                    # 如果解析失败，保持原始数据
                    pass
            
            # 检查错误
            if not response.ok:
                # 构建详细的错误信息
                error_msg = f"HTTP {response.status_code}"
                if api_response.msg:
                    error_msg += f": {api_response.msg}"
                elif api_response.code:
                    error_msg += f": {api_response.code}"
                else:
                    error_msg += f": {response.reason}"
                
                # 如果有响应内容，也包含进去
                if response.text:
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict):
                            if 'message' in error_data:
                                error_msg += f" - {error_data['message']}"
                            elif 'error' in error_data:
                                error_msg += f" - {error_data['error']}"
                    except:
                        # 如果不是 JSON，显示前 200 个字符
                        error_msg += f" - {response.text[:200]}"
                
                raise TopStackError(error_msg, response.status_code, api_response)
            
            return api_response
            
        except requests.exceptions.RequestException as e:
            raise TopStackError(f"请求失败: {str(e)}", 0, None)
        except json.JSONDecodeError as e:
            raise TopStackError(f"响应解析失败: {str(e)}", response.status_code, None)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, response_model: Optional[type] = None) -> Response:
        """发送 GET 请求"""
        return self._make_request('GET', endpoint, params, response_model)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, response_model: Optional[type] = None) -> Response:
        """发送 POST 请求"""
        return self._make_request('POST', endpoint, data, response_model)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, response_model: Optional[type] = None) -> Response:
        """发送 PUT 请求"""
        return self._make_request('PUT', endpoint, data, response_model)
    
    def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None, response_model: Optional[type] = None) -> Response:
        """发送 DELETE 请求"""
        return self._make_request('DELETE', endpoint, data, response_model)

class TopStackError(Exception):
    """TopStack SDK 异常"""
    
    def __init__(self, message: str, status_code: int, response: Optional[Response]):
        super().__init__(message)
        self.status_code = status_code
        self.response = response 