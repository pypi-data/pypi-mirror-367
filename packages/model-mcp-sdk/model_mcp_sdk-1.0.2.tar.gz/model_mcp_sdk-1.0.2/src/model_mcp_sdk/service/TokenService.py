import time
import threading
import logging
import json
from cachetools import TTLCache
from model_mcp_sdk.exceptions.SdkException import SdkException
from model_mcp_sdk.core.ModelUrlConstant import ModelUrlConstant


class TokenService:
    CACHE_KEY = "model_app_token"
    DEFAULT_CACHE_MINUTES = 55

    def __init__(self, sdk_config, http_client):
        self.logger = logging.getLogger(__name__)
        self.sdk_config = sdk_config
        self.http_client = http_client
        self.lock = threading.Lock()

        # 初始缓存设置
        cache_time = sdk_config.token_cache_time or self.DEFAULT_CACHE_MINUTES
        self.token_cache = TTLCache(maxsize=1, ttl=cache_time * 60)

        # 当使用自定义过期时间时的单独缓存管理
        self.custom_ttl_cache = None
        self.custom_ttl_lock = threading.Lock()

    def get_app_token(self):
        try:
            # 优先使用自定义过期时间的缓存
            if self.custom_ttl_cache and time.time() < self.custom_ttl_cache["expiry"]:
                return self.custom_ttl_cache["token"]

            # 检查主缓存
            token = self.token_cache.get(self.CACHE_KEY)
            if token:
                return token

            # 缓存未命中则获取新Token
            return self.fetch_new_token_from_server()

        except Exception as e:
            self.logger.error(f"获取Token失败: {str(e)}")
            raise SdkException("Token服务异常", 500)

    def refresh_app_token(self):
        with self.lock:
            # 清除所有缓存
            self.token_cache.clear()
            if self.custom_ttl_cache:
                with self.custom_ttl_lock:
                    self.custom_ttl_cache = None

            # 获取新Token
            new_token = self.fetch_new_token_from_server()
            return new_token

    def clear_token_cache(self):
        self.token_cache.clear()
        with self.custom_ttl_lock:
            self.custom_ttl_cache = None

    def get_headers(self):

        return {
            ModelUrlConstant.T0KEN_HEADER_NAME: self.get_app_token(),
            ModelUrlConstant.TOKEN_LOGIN_TYPE_HEADER_NAME: self.sdk_config.login_type,
        }

    def fetch_new_token_from_server(self):

        payload = {
            "appKey": self.sdk_config.app_key,
            "appSecret": self.sdk_config.app_secret,
        }

        try:
            # 发送请求获取Token
            response = self.http_client.send_post(
                ModelUrlConstant.TOKEN_URL, body=json.dumps(payload)
            )
            data = json.loads(response)
            # 验证响应
            if not data.get("success"):
                error_msg = data.get("message", "获取Token失败")
                raise SdkException(error_msg, 500)

            token_data = data.get("result", {})
            token = token_data.get("token")
            if not token:
                raise SdkException("Token响应缺少token字段", 500)

            self.logger.info("成功从服务器获取Token")

            # 检查是否返回自定义过期时间
            expires_in = token_data.get("expiresIn")
            if expires_in:
                self.update_cache_expiry(token, max(expires_in - 300, 60))
            else:
                with self.lock:
                    self.token_cache[self.CACHE_KEY] = token

            return token

        except json.JSONDecodeError:
            error_msg = "Token响应JSON解析失败"
            self.logger.error(error_msg)
            raise SdkException(error_msg, 500)
        except SdkException as e:
            self.logger.error(f"获取Token API失败: {e.message}")
            raise
        except Exception as e:
            self.logger.exception("获取Token时发生未知异常")
            raise SdkException("Token服务内部错误", 500)

    def update_cache_expiry(self, token, ttl_seconds):
        with self.custom_ttl_lock:
            self.custom_ttl_cache = {
                "token": token,
                "expiry": time.time() + ttl_seconds,
            }
