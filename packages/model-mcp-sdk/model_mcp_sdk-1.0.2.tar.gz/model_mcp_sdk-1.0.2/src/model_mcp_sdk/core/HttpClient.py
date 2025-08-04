import json
import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from requests_toolbelt.multipart.encoder import MultipartEncoder
from model_mcp_sdk.exceptions.SdkException import SdkException


class HttpClient:
    def __init__(self, base_url, timeout, max_retries):
        self.base_url = base_url
        self.timeout = timeout / 1000.0  # Convert ms to seconds
        self.session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=max_retries,
            connect=max_retries,
            backoff_factor=0.3,
            status_forcelist=[],
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "PATCH"]),
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def send_get(self, endpoint, headers=None):
        return self._execute_request("GET", endpoint, headers=headers)

    def send_post(self, endpoint, headers=None, body=None):
        return self._execute_request("POST", endpoint, headers=headers, body=body)

    def build_endpoint(self, endpoint, path_vars=None, params=None):
        url = endpoint

        # Handle path variables
        if path_vars:
            for var in path_vars:
                url += f"/{urllib.parse.quote(str(var))}"

        # Handle query parameters
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    safe_key = urllib.parse.quote(str(key))
                    safe_value = urllib.parse.quote(str(value))
                    query_params.append(f"{safe_key}={safe_value}")

            if query_params:
                url += "?" + "&".join(query_params)

        return url

    def _execute_request(self, method, endpoint, headers=None, body=None):
        url = self.base_url + endpoint
        print(url)
        headers = headers or {}

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                headers["Content-Type"] = "application/json"
                response = self.session.post(
                    url, headers=headers, data=body, timeout=self.timeout
                )
            else:
                raise SdkException(1, f"Unsupported method: {method}")

            # Check for unsuccessful responses
            if not response.ok:
                raise SdkException(
                    response.status_code, f"Request failed: {response.reason}"
                )

            return response.text

        except requests.exceptions.RequestException as e:
            code = e.response.status_code if e.response else 1
            message = str(e)
            raise SdkException(code, message)

    def send_multipart_post(
        self, endpoint: str, headers: dict = None, files: dict = None
    ) -> dict:
        """
        发送 multipart/form-data POST 请求（仅文件部分）

        参数:
        :param endpoint: 请求端点路径
        :param headers: 请求头信息
        :param files: 文件字典，格式为 {'field_name': (filename, file_content, content_type)}

        返回:
        :return: 解析后的JSON响应
        """
        # 构建完整URL
        url = self.base_url + endpoint

        # 准备multipart数据
        fields = {}

        # 添加文件数据
        if files:
            for field_name, file_info in files.items():
                # 文件信息格式应为 (filename, content, content_type)
                if len(file_info) != 3:
                    raise SdkException(400, f"无效的文件格式: {field_name}")

                filename, content, content_type = file_info
                fields[field_name] = (filename, content, content_type)

        # 创建multipart编码器
        multipart_data = MultipartEncoder(fields=fields)

        # 设置请求头
        final_headers = headers.copy() if headers else {}
        final_headers["Content-Type"] = multipart_data.content_type

        try:
            # 发送请求
            response = self.session.post(
                url, headers=final_headers, data=multipart_data, timeout=self.timeout
            )

            # 检查响应状态
            if not response.ok:
                raise SdkException(
                    response.status_code,
                    f"请求失败: {response.reason} [状态码: {response.status_code}]",
                )

            # 尝试解析JSON响应
            try:
                return response.json()
            except ValueError:
                raise SdkException(
                    500,
                    f"响应解析失败: 无效的JSON格式\n响应内容: {response.text[:200]}",
                )

        except requests.exceptions.RequestException as e:
            # 处理请求异常
            code = e.response.status_code if e.response else 500
            message = f"网络请求失败: {str(e)}"
            raise SdkException(code, message) from e
        except Exception as e:
            # 处理其他异常
            raise SdkException(500, f"未知错误: {str(e)}") from e
