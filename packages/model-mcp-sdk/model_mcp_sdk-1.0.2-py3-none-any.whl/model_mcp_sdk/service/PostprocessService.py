import json
from typing import List, Dict, Callable, Type, TypeVar, Any
from dataclasses import dataclass, field
from model_mcp_sdk.service.TokenService import TokenService
from model_mcp_sdk.core.HttpClient import HttpClient
from model_mcp_sdk.core.SDKConfig import SDKConfig
from model_mcp_sdk.core.ModelUrlConstant import ModelUrlConstant
from model_mcp_sdk.model.postprocess.ShowSchemeModelElementVO import (
    ShowSchemeModelElementVO,
)
from model_mcp_sdk.model.postprocess.BaseAchievements import BaseAchievements
from model_mcp_sdk.model.postprocess.GetIndexRequestVO import GetIndexRequestVO
from model_mcp_sdk.model.postprocess.GetAchivementDetailRequestVO import (
    GetAchivementDetailRequestVO,
)
from model_mcp_sdk.model.postprocess.GetTimeLineWithPointRequestVO import (
    GetTimeLineWithPointRequestVO,
)
from model_mcp_sdk.exceptions.SdkException import SdkException
from model_mcp_sdk.model.postprocess.GetTimeLineWithPointResponseVO import (
    GetTimeLineWithPointResponseVO,
)
from model_mcp_sdk.model.ResponseVO import ResponseVO


class PostprocessService:
    """
    后处理服务类 - 提供成果模型数据相关操作

    该类封装了后处理模块的API调用，包括成果模型元素的获取、详细数据查询、
    地理位置数据获取以及时间线数据查询等功能。

    通过 ResponseHandler 统一处理HTTP请求、响应解析、重试逻辑和错误处理，
    确保API调用的健壮性和一致性。

    依赖项:
    token_service: TokenService - 提供身份验证所需的请求头信息
    http_client: HttpClient - 实际执行HTTP请求的客户端
    response_handler: ResponseHandler - 统一处理API响应和错误逻辑
    """

    def __init__(
        self,
        http_client: HttpClient,
        token_service: TokenService,
        config: SDKConfig,
    ):
        """
        初始化后处理服务

        参数:
        http_client: HTTP客户端实例，负责发送HTTP请求
        token_service: 令牌服务实例，用于获取认证头信息
        response_handler: 响应处理器实例，统一处理API响应和错误逻辑
        """
        self.http_client = http_client
        self.token_service = token_service
        self.config = config
        self.max_retries = config.max_retries

    def get_all_achievements_by_scheme_id(
        self, scheme_id: str
    ) -> List[ShowSchemeModelElementVO]:
        """
        根据方案ID获取所有成果模型元素

        执行流程:
        1. 准备认证头和查询参数
        2. 构建完整的API端点URL
        3. 发送GET请求
        4. 处理响应并解析为 ShowSchemeModelElementVO 列表

        响应处理器将:
        - 处理401等认证错误，自动刷新令牌后重试
        - 执行重试逻辑（递归调用自身）
        - 统一解析 ResponseVO 响应结构

        参数:
        scheme_id: 方案唯一标识符 - 不可为空

        返回:
        方案对应的所有成果模型元素列表 - 可能为空列表但不会返回None
        """

        retries = 0
        while retries <= self.max_retries:
            try:
                # 获取认证头
                headers = self.token_service.get_headers()
                # 构建查询参数
                params = {"schemeId": scheme_id}
                # 构建完整URL
                url = self.http_client.build_endpoint(
                    ModelUrlConstant.POSTPROCESS_GET_ALL_ACHIEVEMENTS_URL, params=params
                )
                # 发送GET请求
                response_str = self.http_client.send_get(url, headers=headers)
                response_json = json.loads(response_str)
                success = response_json["success"]
                if success:
                    result: List[ShowSchemeModelElementVO] = []
                    for vo in response_json["result"]:
                        result.append(ShowSchemeModelElementVO.from_dict(vo))
                    return result
                else:
                    code = response_json["code"]
                    message = response_json["message"]
                    raise SdkException(code, message)
            except SdkException as e:
                if e.code == 401:
                    self.token_service.refresh_app_token()
                retries += 1

    def get_latest_achievements_by_scheme_id(
        self, scheme_id: str
    ) -> List[ShowSchemeModelElementVO]:
        """
        获取方案的最新成果模型元素

        与 get_all_achievements_by_scheme_id 类似，但使用不同的API端点
        获取经过时间过滤后的最新成果数据。

        参数:
        scheme_id: 方案唯一标识符 - 不可为空

        返回:
        方案的最新成果模型元素列表
        """

        retries = 0
        while retries <= self.max_retries:
            try:
                headers = self.token_service.get_headers()
                params = {"schemeId": scheme_id}
                url = self.http_client.build_endpoint(
                    ModelUrlConstant.POSTPROCESS_GET_LATEST_ACHIEVEMENTS_URL,
                    params=params,
                )
                response_str = self.http_client.send_get(url, headers=headers)
                response_json = json.loads(response_str)
                success = response_json["success"]
                if success:
                    result: List[ShowSchemeModelElementVO] = []
                    for vo in response_json["result"]:
                        result.append(ShowSchemeModelElementVO.from_dict(vo))
                    return result
                else:
                    code = response_json["code"]
                    message = response_json["message"]
                    raise SdkException(code, message)
            except SdkException as e:
                if e.code == 401:
                    self.token_service.refresh_app_token()
                retries += 1

    def get_achievements_full_data(
        self, vo: GetIndexRequestVO
    ) -> List[BaseAchievements]:
        """
        获取成果模型完整数据

        执行流程:
        1. 准备认证头
        2. 将请求对象序列化为JSON请求体
        3. 发送POST请求
        4. 解析响应为 BaseAchievements 对象列表

        参数:
        vo: 成果数据请求对象 - 包含筛选条件和分页参数

        返回:
        符合条件的成果完整数据列表
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                headers = self.token_service.get_headers()
                # 将请求对象序列化为JSON字符串
                body = json.dumps(vo.to_dict())
                url = ModelUrlConstant.POSTPROCESS_GET_ACHIEVEMENTS_FULL_URL
                response_str = self.http_client.send_post(
                    url, headers=headers, body=body
                )
                response_json = json.loads(response_str)
                success = response_json["success"]
                if success:
                    result: List[BaseAchievements] = []
                    for vo in response_json["result"]:
                        result.append(BaseAchievements.from_dict(vo))
                    return result
                else:
                    code = response_json["code"]
                    message = response_json["message"]
                    raise SdkException(code, message)
            except SdkException as e:
                if e.code == 401:
                    self.token_service.refresh_app_token()
                retries += 1

    def get_achievements_details(self, vo: GetAchivementDetailRequestVO):
        """
        获取成果详细数据

        执行流程:
        1. 准备认证头和JSON请求体
        2. 发送POST请求到详情API端点
        3. 解析响应为字典列表

        说明: 使用字典列表作为返回值类型是因为成果详情数据结构灵活，
        不需要固定的对象映射。

        参数:
        vo: 成果详情请求参数对象

        返回:
        包含任意结构的成果详细信息列表
        """
        retries = 0
        while retries <= self.max_retries:
            try:

                headers = self.token_service.get_headers()
                body = json.dumps(vo.to_dict())
                url = ModelUrlConstant.POSTPROCESS_GET_ACHIEVEMENTS_DETAIL_URL
                response_str = self.http_client.send_post(
                    url, headers=headers, body=body
                )
                response_json = json.loads(response_str)
                success = response_json["success"]
                print(response_json)
                if success:
                    print(response_json)
                    return response_json["result"]
                else:
                    code = response_json["code"]
                    message = response_json["message"]
                    raise SdkException(code, message)
            except SdkException as e:
                if e.code == 401:
                    self.token_service.refresh_app_token()
                retries += 1

    def get_achievements_time_line(
        self, vo: GetTimeLineWithPointRequestVO
    ) -> GetTimeLineWithPointResponseVO:
        """
        获取成果时间线数据

        执行流程:
        1. 准备认证头和JSON请求体
        2. 发送POST请求到时间线API端点
        3. 解析响应为 GetTimeLineWithPointResponseVO 对象

        参数:
        vo: 时间线请求参数对象

        返回:
        包含时间点分段数据的结构化响应
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                headers = self.token_service.get_headers()
                body = json.dumps(vo.to_dict())
                url = ModelUrlConstant.POSTPROCESS_GET_ACHIEVEMENTS_TIMELINE_URL
                response_str = self.http_client.send_post(
                    url, headers=headers, body=body
                )
                response_json = json.loads(response_str)
                success = response_json["success"]
                if success:
                    return GetTimeLineWithPointResponseVO.from_dict(
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
