from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class GetIndexRequestVO:
    """
    获取指标请求模型
    对应 Java 的 com.yrihr.sdk.model.postprocess.GetIndexRequestVO

    属性:
    instance_id: str - 实例ID
    letter_name: str - 字母名称
    model_core_id: str - 模型核心ID
    scheme_id: str - 方案ID
    """

    instance_id: str = ""
    letter_name: str = ""
    model_core_id: str = ""
    scheme_id: str = ""

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_instance_id(self, instance_id: str) -> "GetIndexRequestVO":
        """设置实例ID"""
        self.instance_id = instance_id
        return self

    def with_letter_name(self, letter_name: str) -> "GetIndexRequestVO":
        """设置字母名称"""
        self.letter_name = letter_name
        return self

    def with_model_core_id(self, model_core_id: str) -> "GetIndexRequestVO":
        """设置模型核心ID"""
        self.model_core_id = model_core_id
        return self

    def with_scheme_id(self, scheme_id: str) -> "GetIndexRequestVO":
        """设置方案ID"""
        self.scheme_id = scheme_id
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将请求对象转换为字典

        返回:
        包含请求参数的字典
        """
        return {
            "instanceId": self.instance_id,
            "letterName": self.letter_name,
            "modelCoreId": self.model_core_id,
            "schemeId": self.scheme_id,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将请求对象转换为JSON字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetIndexRequestVO":
        """
        从字典创建请求对象

        参数:
        data: 包含请求参数的字典

        返回:
        GetIndexRequestVO 实例
        """
        request = cls()

        if "instanceId" in data:
            request.instance_id = data["instanceId"]
        if "letterName" in data:
            request.letter_name = data["letterName"]
        if "modelCoreId" in data:
            request.model_core_id = data["modelCoreId"]
        if "schemeId" in data:
            request.scheme_id = data["schemeId"]

        return request

    @classmethod
    def from_json(cls, json_str: str) -> "GetIndexRequestVO":
        """
        从JSON字符串创建请求对象

        参数:
        json_str: JSON格式的字符串

        返回:
        GetIndexRequestVO 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"GetIndexRequestVO(instance_id={self.instance_id!r}, "
            f"letter_name={self.letter_name!r}, "
            f"model_core_id={self.model_core_id!r}, "
            f"scheme_id={self.scheme_id!r})"
        )
