import json
from typing import List, Dict, Callable, Type, TypeVar, Any, Optional
from model_mcp_sdk.service.TokenService import TokenService
from model_mcp_sdk.core.HttpClient import HttpClient
from model_mcp_sdk.core.SDKConfig import SDKConfig
from model_mcp_sdk.core.ModelUrlConstant import ModelUrlConstant
from model_mcp_sdk.model.nc.NcInfo import NcInfo
from model_mcp_sdk.model.service.WriteNcFileRspVO import WriteNcFileRspVO
from model_mcp_sdk.model.service.ExeArgoServiceReqVO import ExeArgoServiceReqVO
from model_mcp_sdk.model.service.ExeArgoServiceWorkflowResVO import (
    ExeArgoServiceWorkflowResVO,
)
from model_mcp_sdk.model.ResponseVO import ResponseVO
from model_mcp_sdk.exceptions.SdkException import SdkException

T = TypeVar("T")


class SchemeServiceService:
    """
    方案服务核心类 - 提供模型方案相关的各种服务功能

    此类负责处理与方案模型（scheme）相关的各项业务操作，主要包括：
    - 获取模型核心信息（NC Schema）
    - 将核心信息写入NC文件
    - 执行Argo服务工作流

    通过统一的响应处理器（ResponseHandler）处理所有API响应，
    确保一致的错误处理、令牌刷新和重试逻辑。
    """

    def __init__(
        self,
        http_client: HttpClient,
        token_service: TokenService,
        config: SDKConfig,
    ):
        """
        初始化方案服务

        参数:
        http_client: HTTP客户端实例，负责发送HTTP请求
        token_service: 令牌服务实例，用于获取认证头信息
        response_handler: 响应处理器实例，统一处理API响应和错误逻辑
        """
        self.http_client = http_client
        self.token_service = token_service
        self.config = config
        self.max_retries = config.max_retries

    def get_nc_info_schema_by_scheme_id(self, scheme_id: str, key: str) -> NcInfo:
        """
        获取指定方案的NC模型信息架构

        此方法获取模型的"骨架"结构（schema），而不是实际数据。

        工作原理:
        1. 准备认证头信息
        2. 构建URL路径变量和查询参数
        3. 发送GET请求到模型服务
        4. 处理响应

        参数:
        scheme_id: 方案的唯一标识符
        key: 模型的键（用于标识特定模型结构）

        返回:
        NcInfo对象，包含模型的结构信息
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                # 获取认证头
                headers = self.token_service.get_headers()
                # 准备路径变量
                path_vars = [scheme_id]
                # 准备查询参数
                params = {"key": key}
                # 构建完整URL
                url = self.http_client.build_endpoint(
                    ModelUrlConstant.SERVICE_GET_NC_SCHEMA_URL,
                    path_vars=path_vars,
                    params=params,
                )
                # 发送GET请求
                response_str = self.http_client.send_get(url, headers=headers)
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

    def write_nc_file_with_nc_info(
        self, nc_info_list: List[NcInfo]
    ) -> WriteNcFileRspVO:
        """
        将NcInfo列表写入NC文件

        此方法将内存中的模型数据实际写入NC文件

        处理流程:
        1. 准备认证头信息
        2. 序列化NC信息列表为JSON请求体
        3. 构建API端点URL
        4. 发送POST请求
        5. 处理响应

        参数:
        nc_info_list: 要写入的NC信息列表

        返回:
        WriteNcFileRspVO 包含写入操作的结果（如文件路径、状态等）
        """

        retries = 0
        while retries <= self.max_retries:
            try:
                # 获取认证头
                headers = self.token_service.get_headers()
                # 序列化NC信息列表为JSON字符串
                body = json.dumps([nc_info.to_dict() for nc_info in nc_info_list])
                # 构建完整URL
                url = ModelUrlConstant.SERVICE_WRITE_SERVICE_NC_URL
                # 发送POST请求
                response_str = self.http_client.send_post(
                    url, headers=headers, body=body
                )
                response_json = json.loads(response_str)
                success = response_json["success"]
                if success:
                    return WriteNcFileRspVO.from_dict(response_json["result"])
                else:
                    code = response_json["code"]
                    message = response_json["message"]
                    raise SdkException(code, message)
            except SdkException as e:
                if e.code == 401:
                    self.token_service.refresh_app_token()
                retries += 1

    def exec_scheme_service(
        self, scheme_id: str, vo: ExeArgoServiceReqVO
    ) -> ExeArgoServiceWorkflowResVO:
        """
        执行Argo服务工作流

        此方法启动指定的Argo服务工作流执行

        工作流程:
        1. 准备认证头信息
        2. 构建URL路径变量
        3. 序列化请求参数为JSON请求体
        4. 构建API端点URL
        5. 发送POST请求
        6. 处理响应

        参数:
        scheme_id: 方案的唯一标识符
        vo: 执行Argo服务的请求参数对象

        返回:
        ExeArgoServiceWorkflowResVO 包含工作流执行结果（如工作流ID、状态等）
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                # 获取认证头
                headers = self.token_service.get_headers()
                # 准备路径变量
                path_vars = [scheme_id]
                # 序列化请求参数为JSON字符串
                body = json.dumps(vo.to_dict())
                # 构建完整URL
                url = self.http_client.build_endpoint(
                    ModelUrlConstant.SERVICE_EXEC_SCHEME_SERVICE_URL,
                    path_vars=path_vars,
                    params=None,
                )
                # 发送POST请求
                response_str = self.http_client.send_post(
                    url, headers=headers, body=body
                )
                response_json = json.loads(response_str)
                success = response_json["success"]
                if success:
                    return ExeArgoServiceWorkflowResVO.from_dict(
                        response_json["result"]
                    )
                else:
                    code = response_json["code"]
                    message = response_json["message"]
                    raise SdkException(code, message)
            except SdkException as e:
                if e.code == 401:
                    self.token_service.refresh_app_token()
                retries += 1
