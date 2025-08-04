from dataclasses import dataclass
from typing import Optional, Dict, Any
import json


@dataclass
class GetAchivementDetailRequestVO:
    """
    获取成就详情请求模型
    对应 Java 的 com.yrihr.sdk.model.postprocess.GetAchivementDetailRequestVO

    属性:
    index: str - 指标标识
    instance_id: str - 实例ID
    letter_name: str - 字母名称
    model_core_id: str - 模型核心ID
    scheme_model_id: str - 方案模型ID
    smid: int - SMID (空间模型ID)
    t: int - 时间参数 (通常是时间步长或时间索引)
    """

    index: str = ""
    instance_id: str = ""
    letter_name: str = ""
    model_core_id: str = ""
    scheme_model_id: str = ""
    smid: int = 0
    t: int = 0

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_index(self, index: str) -> "GetAchivementDetailRequestVO":
        """设置指标标识"""
        self.index = index
        return self

    def with_instance_id(self, instance_id: str) -> "GetAchivementDetailRequestVO":
        """设置实例ID"""
        self.instance_id = instance_id
        return self

    def with_letter_name(self, letter_name: str) -> "GetAchivementDetailRequestVO":
        """设置字母名称"""
        self.letter_name = letter_name
        return self

    def with_model_core_id(self, model_core_id: str) -> "GetAchivementDetailRequestVO":
        """设置模型核心ID"""
        self.model_core_id = model_core_id
        return self

    def with_scheme_model_id(
        self, scheme_model_id: str
    ) -> "GetAchivementDetailRequestVO":
        """设置方案模型ID"""
        self.scheme_model_id = scheme_model_id
        return self

    def with_smid(self, smid: int) -> "GetAchivementDetailRequestVO":
        """设置SMID (空间模型ID)"""
        self.smid = smid
        return self

    def with_t(self, t: int) -> "GetAchivementDetailRequestVO":
        """设置时间参数"""
        self.t = t
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
            "index": self.index,
            "instanceId": self.instance_id,
            "letterName": self.letter_name,
            "modelCoreId": self.model_core_id,
            "schemeModelId": self.scheme_model_id,
            "smid": self.smid,
            "t": self.t,
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
    def from_dict(cls, data: Dict[str, Any]) -> "GetAchivementDetailRequestVO":
        """
        从字典创建请求对象

        参数:
        data: 包含请求参数的字典

        返回:
        GetAchivementDetailRequestVO 实例
        """
        request = cls()

        if "index" in data:
            request.index = data["index"]
        if "instanceId" in data:
            request.instance_id = data["instanceId"]
        if "letterName" in data:
            request.letter_name = data["letterName"]
        if "modelCoreId" in data:
            request.model_core_id = data["modelCoreId"]
        if "schemeModelId" in data:
            request.scheme_model_id = data["schemeModelId"]
        if "smid" in data:
            request.smid = data["smid"]
        if "t" in data:
            request.t = data["t"]

        return request

    @classmethod
    def from_json(cls, json_str: str) -> "GetAchivementDetailRequestVO":
        """
        从JSON字符串创建请求对象

        参数:
        json_str: JSON格式的字符串

        返回:
        GetAchivementDetailRequestVO 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"GetAchivementDetailRequestVO(index={self.index!r}, "
            f"instance_id={self.instance_id!r}, smid={self.smid})"
        )
