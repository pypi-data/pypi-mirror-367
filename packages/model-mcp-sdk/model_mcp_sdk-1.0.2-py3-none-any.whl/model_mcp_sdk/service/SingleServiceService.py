from model_mcp_sdk.service.TokenService import TokenService
from model_mcp_sdk.core.HttpClient import HttpClient
from model_mcp_sdk.core.SDKConfig import SDKConfig
from model_mcp_sdk.core.ModelUrlConstant import ModelUrlConstant
from model_mcp_sdk.exceptions.SdkException import SdkException
from model_mcp_sdk.model.service.ExeArgoServiceReqVO import ExeArgoServiceReqVO
from model_mcp_sdk.core.ModelUrlConstant import ModelUrlConstant
from model_mcp_sdk.model.service.ExeArgoServiceWorkflowResVO import (
    ExeArgoServiceWorkflowResVO,
)
import json


class SingleServiceService:

    def __init__(
        self,
        http_client: HttpClient,
        token_service: TokenService,
        config: SDKConfig,
    ):
        """
        初始化单模型服务

        参数:
        http_client: HTTP客户端实例，负责发送HTTP请求
        token_service: 令牌服务实例，用于获取认证头信息
        response_handler: 响应处理器实例，统一处理API响应和错误逻辑
        """
        self.http_client = http_client
        self.token_service = token_service
        self.config = config
        self.max_retries = config.max_retries

    def execSingleService(
        self, modelCoreName: str, isStandard: bool, vo: ExeArgoServiceReqVO
    ):
        retries = 0
        while retries <= self.max_retries:
            try:
                # 获取认证头
                headers = self.token_service.get_headers()
                # 准备路径变量
                path_vars = [modelCoreName]
                # 构建完整URL
                end_point = (
                    ModelUrlConstant.SERVICE_EXEC_SINGLE_SERVICE_STD_URL
                    if isStandard
                    else ModelUrlConstant.SERVICE_EXEC_SINGLE_SERVICE_NSTD_URL
                )
                url = self.http_client.build_endpoint(
                    end_point,
                    path_vars=path_vars,
                    params=None,
                )
                body = json.dumps(vo.to_dict())
                # 发送GET请求
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
