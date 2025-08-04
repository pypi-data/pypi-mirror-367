from model_mcp_sdk.service.TokenService import TokenService
from model_mcp_sdk.core.HttpClient import HttpClient
from model_mcp_sdk.core.SDKConfig import SDKConfig
from model_mcp_sdk.core.ModelUrlConstant import ModelUrlConstant
from model_mcp_sdk.exceptions.SdkException import SdkException
import os


class SystemService:
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

    def upload_file(self, file_path: str, is_rename: bool, biz_path: str) -> str:
        """文件上传接口

        :param file_path: 本地文件路径
        :param is_rename: 是否重命名文件 (True表示服务端重命名)
        :param biz_path: 业务目录路径
        :return: 上传成功后的文件访问路径
        """
        # 获取认证头部
        headers = self.token_service.get_headers()

        # 构建请求参数
        params = {
            "is_rename": "0" if is_rename else "1",  # 原Java逻辑：true->"0", false->"1"
            "biz": biz_path,
        }

        # 构建完整URL
        url = self.http_client.build_endpoint(ModelUrlConstant.UPLOAD, None, params)

        # 验证文件存在
        if not os.path.exists(file_path):
            raise SdkException(404, "文件不存在")

        # 读取文件内容
        file_name = os.path.basename(file_path)
        mime_type = self._get_media_type_from_file_name(file_name)

        with open(file_path, "rb") as f:
            file_content = f.read()

        # 准备multipart文件
        files = {"file": (file_name, file_content, mime_type)}

        # 发送请求并处理响应
        try:
            response_data = self.http_client.send_multipart_post(url, headers, files)
        except Exception as e:
            # 将底层异常转换为SDK异常
            if not isinstance(e, SdkException):
                raise SdkException(500, f"上传失败: {str(e)}")
            raise

        # 处理业务响应（根据实际API响应结构调整）
        if response_data.get("success", False):
            return response_data.get("message", "")
        else:
            code = response_data.get("code", 500)
            error_msg = response_data.get(
                "error", response_data.get("message", "上传文件失败")
            )
            raise SdkException(code, error_msg)

    def _get_media_type_from_file_name(self, file_name: str) -> str:
        """根据文件名后缀获取MIME类型 - 完整映射版"""
        # 统一转为小写处理
        lower_name = file_name.lower()

        # 图像类型
        if lower_name.endswith((".jpg", ".jpeg")):
            return "image/jpeg"
        elif lower_name.endswith(".png"):
            return "image/png"
        elif lower_name.endswith(".gif"):
            return "image/gif"
        elif lower_name.endswith(".webp"):
            return "image/webp"

        # 视频类型
        elif lower_name.endswith(".mp4"):
            return "video/mp4"
        elif lower_name.endswith(".mov"):
            return "video/quicktime"
        elif lower_name.endswith(".avi"):
            return "video/x-msvideo"

        # 文档类型
        elif lower_name.endswith(".pdf"):
            return "application/pdf"
        elif lower_name.endswith(".doc"):
            return "application/msword"
        elif lower_name.endswith(".docx"):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif lower_name.endswith(".xls"):
            return "application/vnd.ms-excel"
        elif lower_name.endswith(".xlsx"):
            return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif lower_name.endswith(".ppt"):
            return "application/vnd.ms-powerpoint"
        elif lower_name.endswith(".pptx"):
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        # 文本类型
        elif lower_name.endswith(".txt"):
            return "text/plain"
        elif lower_name.endswith(".csv"):
            return "text/csv"
        elif lower_name.endswith(".xml"):
            return "application/xml"
        elif lower_name.endswith(".json"):
            return "application/json"
        elif lower_name.endswith(".html"):
            return "text/html"

        # 压缩文件
        elif lower_name.endswith(".zip"):
            return "application/zip"
        elif lower_name.endswith(".rar"):
            return "application/x-rar-compressed"
        elif lower_name.endswith(".7z"):
            return "application/x-7z-compressed"

        # 其他常见类型
        elif lower_name.endswith(".exe"):
            return "application/octet-stream"
        elif lower_name.endswith(".apk"):
            return "application/vnd.android.package-archive"

        # 默认返回二进制流类型
        return "application/octet-stream"
