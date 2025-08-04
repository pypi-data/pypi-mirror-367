from model_mcp_sdk.core.HttpClient import HttpClient
from model_mcp_sdk.core.SDKConfig import SDKConfig
from model_mcp_sdk.service.TokenService import TokenService
from model_mcp_sdk.service.ModelCoresService import ModelCoresService
from model_mcp_sdk.service.PostprocessService import PostprocessService
from model_mcp_sdk.service.SchemeServiceService import SchemeServiceService
from model_mcp_sdk.service.SystemService import SystemService
from model_mcp_sdk.service.SingleServiceService import SingleServiceService


class ModelMcpSDK:
    """
    MCP 模型 SDK 入口类

    此类是整个模型SDK的入口点，负责初始化所有核心组件和服务：
    - HTTP客户端
    - SDK配置
    - 令牌服务
    - 响应处理器
    - 各个功能服务（模型核心、后处理、方案服务）

    使用示例:
    sdk = ModelMcpSDK(base_url="https://api.example.com", app_key="your_app_key", app_secret="your_secret")

    # 使用模型核心服务
    nc_info = sdk.model_cores().nc_to_json(nc_request)

    # 使用后处理服务
    achievements = sdk.postprocess().get_all_achievements_by_scheme_id("scheme-123")

    # 使用方案服务
    nc_schema = sdk.scheme_service().get_nc_info_schema_by_scheme_id("scheme-456", "model-key")
    """

    def __init__(self, base_url: str, app_key: str, app_secret: str, upload_path: str):
        """
        初始化 MCP 模型 SDK

        参数:
        base_url: API基础URL (例如 "https://api.example.com")
        app_key: 应用密钥
        app_secret: 应用密钥
        """
        # 创建SDK配置
        config = (
            SDKConfig.Builder()
            .base_url(base_url)
            .app_key(app_key)
            .app_secret(app_secret)
            .upload_path(upload_path)
            .build()
        )

        # 创建HTTP客户端
        http_client = HttpClient(
            base_url=base_url, timeout=6000, max_retries=3  # 6秒超时  # 最大重试次数
        )

        # 创建令牌服务
        self.token_service = TokenService(config, http_client)

        # 初始化各个服务
        self.model_cores_service = ModelCoresService(
            http_client, self.token_service, config
        )
        self.postprocess_service = PostprocessService(
            http_client, self.token_service, config
        )
        self.scheme_service_service = SchemeServiceService(
            http_client, self.token_service, config
        )
        self.system_service_service = SystemService(
            http_client, self.token_service, config
        )
        self.single_service_servcie = SingleServiceService(
            http_client, self.token_service, config
        )

    def model_cores(self) -> ModelCoresService:
        """
        获取模型核心服务

        返回:
        ModelCoresService 实例，提供NC数据处理相关功能
        """
        return self.model_cores_service

    def token(self) -> TokenService:
        """
        获取令牌服务

        返回:
        TokenService 实例，用于管理认证令牌
        """
        return self.token_service

    def postprocess(self) -> PostprocessService:
        """
        获取后处理服务

        返回:
        PostprocessService 实例，提供成果模型数据相关操作
        """
        return self.postprocess_service

    def scheme_service(self) -> SchemeServiceService:
        """
        获取方案服务

        返回:
        SchemeServiceService 实例，提供模型方案相关服务
        """
        return self.scheme_service_service

    def system_service(self) -> SystemService:
        """
        获取方案服务

        返回:
        SchemeServiceService 实例，提供模型方案相关服务
        """
        return self.system_service_service

    def single_service(self) -> SingleServiceService:
        """
        获取方案服务

        返回:
        SchemeServiceService 实例，提供模型方案相关服务
        """
        return self.single_service_servcie
