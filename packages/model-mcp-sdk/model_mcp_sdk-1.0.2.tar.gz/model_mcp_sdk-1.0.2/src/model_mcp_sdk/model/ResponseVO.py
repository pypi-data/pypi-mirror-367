from dataclasses import dataclass, field
from typing import TypeVar, Generic, Any, Optional, Dict
import time

# 定义泛型类型变量
T = TypeVar("T")


@dataclass
class ResponseVO(Generic[T]):
    """
    通用响应对象（支持泛型）
    对应 Java 的 com.yrihr.sdk.model.ResponseVO<T>

    属性:
    success: bool - 成功标志 (默认 True)
    message: str - 返回处理消息 (默认空字符串)
    code: int - 返回代码 (默认 0)
    result: T - 返回数据对象 (默认 None)
    timestamp: int - 时间戳 (默认当前时间毫秒数)
    """

    success: bool = True
    message: str = ""
    code: int = 0
    result: Optional[T] = None
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    # =====================
    # 成功响应工厂方法
    # =====================
    @classmethod
    def success(cls) -> "ResponseVO[None]":
        """
        创建成功响应 (无结果数据)

        返回:
        成功的响应对象
        """
        return cls(success=True)

    @classmethod
    def success_with_data(cls, data: T) -> "ResponseVO[T]":
        """
        创建带结果的成功响应

        参数:
        data: 返回的数据对象

        返回:
        包含数据的成功响应对象
        """
        return cls(success=True, result=data)

    @classmethod
    def success_with_message(cls, message: str, data: T = None) -> "ResponseVO[T]":
        """
        创建带消息的成功响应

        参数:
        message: 成功消息
        data: 返回的数据对象 (可选)

        返回:
        包含消息和数据的成功响应对象
        """
        return cls(success=True, message=message, result=data)

    # =====================
    # 失败响应工厂方法
    # =====================
    @classmethod
    def failure(cls, code: int, message: str) -> "ResponseVO[None]":
        """
        创建失败响应

        参数:
        code: 错误代码
        message: 错误消息

        返回:
        包含错误信息的失败响应对象
        """
        return cls(success=False, code=code, message=message)

    @classmethod
    def failure_with_detail(
        cls, code: int, message: str, error_detail: T
    ) -> "ResponseVO[T]":
        """
        创建带失败详情的响应

        参数:
        code: 错误代码
        message: 错误消息
        error_detail: 错误详情对象

        返回:
        包含错误信息和详情的失败响应对象
        """
        return cls(success=False, code=code, message=message, result=error_detail)

    # =====================
    # 常用状态码常量
    # =====================
    SUCCESS_CODE: int = 200
    BAD_REQUEST: int = 400
    UNAUTHORIZED: int = 401
    FORBIDDEN: int = 403
    NOT_FOUND: int = 404
    INTERNAL_ERROR: int = 500

    # =====================
    # 序列化/反序列化方法
    # =====================
    def to_dict(self) -> Dict[str, Any]:
        """
        将响应对象转换为字典

        返回:
        包含响应信息的字典
        """
        return {
            "success": self.success,
            "message": self.message,
            "code": self.code,
            "result": self.result,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResponseVO":
        """
        从字典创建响应对象

        参数:
        data: 包含响应信息的字典

        返回:
        ResponseVO 实例
        """
        return cls(
            success=data.get("success", True),
            message=data.get("message", ""),
            code=data.get("code", 0),
            result=data.get("result"),
            timestamp=data.get("timestamp", int(time.time() * 1000)),
        )

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将响应对象转换为JSON字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        import json

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "ResponseVO":
        """
        从JSON字符串创建响应对象

        参数:
        json_str: JSON格式的字符串

        返回:
        ResponseVO 实例
        """
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"ResponseVO(success={self.success}, code={self.code}, "
            f"message={self.message!r}, result_type={type(self.result).__name__})"
        )
