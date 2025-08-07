import time
from typing import TypeVar, Type, Dict, Any, Optional

import requests
from requests.exceptions import RequestException
import os
from dotenv import load_dotenv

load_dotenv()

T = TypeVar('T')


class TaientClient:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 配置初始化
        self.HRP_SERVER = os.getenv("TAIENT_HRP_SERVER", config.get("TAIENT_HRP_SERVER"))
        self.HRP_PORT = os.getenv("TAIENT_HRP_PORT", config.get("TAIENT_HRP_PORT"))
        self.HRP_USERNAME = config.get('TAIENT_HRP_USERNAME')
        self.HRP_PASSWORD = config.get('TAIENT_HRP_PASSWORD')

        # 检查 TAIENT_HRP_SERVER 和 TAIENT_HRP_PORT 必须存在
        if not self.HRP_SERVER or not self.HRP_PORT:
            raise ValueError("环境变量 'TAIENT_HRP_SERVER' 和 'TAIENT_HRP_PORT' 必须设置")

        # 检查 TAIENT_HRP_USERNAME 和 TAIENT_HRP_PASSWORD 必须存在
        if not self.HRP_USERNAME or not self.HRP_PASSWORD:
            raise ValueError("配置必须包含 'TAIENT_HRP_USERNAME' 和 'TAIENT_HRP_PASSWORD'")

        # 凭证缓存
        self._cached_cookie = None
        self._cookie_timestamp = 0
        self._cached_token = None
        self._token_timestamp = 0

        # 超时时间设置（7天）
        self.EXPIRATION_TIME = 7 * 24 * 60 * 60
        self.session = requests.Session()  # 复用HTTP连接

    # URL构建器 =================================================================
    def hrp_url(self, api: str) -> str:
        return f"http://{self.HRP_SERVER}:{self.HRP_PORT}/api/v1{api}"

    # 认证管理 =================================================================
    def get_cookie(self) -> str:
        """获取HRP系统的Cookie（带缓存和自动刷新）"""
        if not self._cached_cookie or time.time() - self._cookie_timestamp > self.EXPIRATION_TIME:
            self._cached_cookie = self._login_and_get_cookie()
            self._cookie_timestamp = time.time()
        return self._cached_cookie

    def _login_and_get_cookie(self) -> str:
        """登录HRP系统并获取Cookie"""
        url = self.hrp_url("/pass/login")
        payload = {"username": self.HRP_USERNAME, "password": self.HRP_PASSWORD}

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return '; '.join([f"{name}={value}" for name, value in response.cookies.items()])
        except RequestException as e:
            raise Exception(f"HRP登录失败: {str(e)}")

    # HTTP请求封装 =============================================================
    def hrp_get(self, api: str) -> Optional[Dict[str, Any]]:
        """HRP系统GET请求"""
        return self._request_with_cookie("GET", self.hrp_url(api))

    def hrp_post(self, api: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """HRP系统POST请求"""
        return self._request_with_cookie("POST", self.hrp_url(api), payload)

    def _request_with_cookie(self, method: str, url: str, payload: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """携带Cookie的请求"""
        headers = {"Cookie": self.get_cookie()}
        return self._make_request(method, url, headers, payload)

    def _make_request(self, method: str, url: str, headers: Dict[str, str], payload: Optional[Dict]) -> Optional[
        Dict[str, Any]]:
        """统一的请求处理"""
        headers["Content-Type"] = "application/json"

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            else:
                response = self.session.post(url, json=payload, headers=headers, timeout=10)

            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"请求失败: {method} {url} - {str(e)}")
            return None

    # 响应数据处理 =============================================================
    def get_code(self, response: Dict[str, Any]) -> int:
        """提取响应状态码"""
        return response.get('result', {}).get('code', -1)

    def get_message(self, response: Dict[str, Any]) -> str:
        """提取响应消息"""
        return response.get('result', {}).get('message', '')

    def get_data(self, response: Dict[str, Any], data_type: Type[T]) -> Optional[T]:
        """提取data对象"""
        data = response.get('data')
        return data_type(**data) if data else None


