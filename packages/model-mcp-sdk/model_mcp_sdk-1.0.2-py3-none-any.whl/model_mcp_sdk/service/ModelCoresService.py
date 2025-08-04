import json
from typing import Callable, Dict, Type, TypeVar, Generic, Any, Optional
from model_mcp_sdk.service.TokenService import TokenService
from model_mcp_sdk.core.HttpClient import HttpClient
from model_mcp_sdk.core.SDKConfig import SDKConfig
from model_mcp_sdk.core.ModelUrlConstant import ModelUrlConstant
from model_mcp_sdk.model.core.ReadNcRequest import ReadNcRequest
from model_mcp_sdk.model.nc.NcInfo import NcInfo
from model_mcp_sdk.model.ResponseVO import ResponseVO
from model_mcp_sdk.exceptions.SdkException import SdkException


class ModelCoresService:
    """
    模型核心服务类 - 提供NC（Numerical Control）数据处理的核心功能

    该类负责处理与NC数据转换相关的业务逻辑，特别是将NC格式数据转换为JSON格式

    主要功能：
    - 处理NC数据到JSON的转换请求
    - 与后端API服务交互
    - 处理认证和错误逻辑
    """

    def __init__(
        self, http_client: HttpClient, token_service: TokenService, config: SDKConfig
    ):
        """
        初始化模型核心服务

        参数:
        http_client: HTTP客户端实例，负责发送HTTP请求
        token_service: 令牌服务实例，用于获取认证头信息
        response_handler: 响应处理器实例，统一处理API响应和错误逻辑
        """
        self.token_service = token_service
        self.http_client = http_client
        self.config = config
        self.max_retries = config.max_retries

    def nc_to_json(self, nc_request: ReadNcRequest) -> NcInfo:
        """
        将NC格式数据转换为JSON格式

        此方法将NC数据转换请求发送到后端服务，并返回转换后的JSON数据结构

        处理流程：
        1. 准备请求头和认证信息
        2. 构造请求体（将输入对象序列化为JSON字符串）
        3. 构建完整的API端点URL
        4. 发送POST请求到NC到JSON的转换服务
        5. 处理响应并返回结果

        错误处理：
        - 如果遇到401未认证错误，会自动刷新令牌并重试
        - 其他错误会抛出SdkException异常

        参数:
        nc_request: NC转换请求对象，包含：
                    - NC文件信息
                    - 数据结构定义
                    - 其他转换参数

        返回:
        NcInfo对象，包含转换后的JSON结构信息

        抛出:
        SdkException: 如果API返回错误或处理过程中发生错误
        """

        """获取认证头信息并发送POST请求"""
        retries = 0
        while retries <= self.max_retries:
            try:
                # 获取认证头信息（包含Authorization等）
                headers = self.token_service.get_headers()

                # 将请求对象序列化为JSON字符串
                body = json.dumps(nc_request.to_dict())

                # 构建完整的API端点URL
                url = ModelUrlConstant.CORE_NC_TO_JSON_URL

                # 发送POST请求并返回响应体
                response_str = self.http_client.send_post(
                    url, headers=headers, body=body
                )
                response_json = json.loads(response_str)
                success = response_json["success"]
                if success:
                    return NcInfo.from_dict(response_json["result"])
                else:
                    code = response_json["code"]
                    message = response_json["message"]
                    raise SdkException(code, message)

            except SdkException as e:
                if e.code == 401:
                    self.token_service.refresh_app_token()
                retries += 1
