from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class GetTimeLineWithPointRequestVO:
    """
    获取时间线数据请求模型（带坐标点）
    对应 Java 的 com.yrihr.sdk.model.postprocess.GetTimeLineWithPointRequestVO

    属性:
    point_x: float - X坐标
    point_y: float - Y坐标
    instance_id: str - 实例ID
    index_code: str - 指标编码
    """

    point_x: float = 0.0
    point_y: float = 0.0
    instance_id: str = ""
    index_code: str = ""

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_point_x(self, point_x: float) -> "GetTimeLineWithPointRequestVO":
        """设置X坐标"""
        self.point_x = point_x
        return self

    def with_point_y(self, point_y: float) -> "GetTimeLineWithPointRequestVO":
        """设置Y坐标"""
        self.point_y = point_y
        return self

    def with_instance_id(self, instance_id: str) -> "GetTimeLineWithPointRequestVO":
        """设置实例ID"""
        self.instance_id = instance_id
        return self

    def with_index_code(self, index_code: str) -> "GetTimeLineWithPointRequestVO":
        """设置指标编码"""
        self.index_code = index_code
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
            "pointX": self.point_x,
            "pointY": self.point_y,
            "instanceId": self.instance_id,
            "indexCode": self.index_code,
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
    def from_dict(cls, data: Dict[str, Any]) -> "GetTimeLineWithPointRequestVO":
        """
        从字典创建请求对象

        参数:
        data: 包含请求参数的字典

        返回:
        GetTimeLineWithPointRequestVO 实例
        """
        request = cls()

        if "pointX" in data:
            request.point_x = data["pointX"]
        if "pointY" in data:
            request.point_y = data["pointY"]
        if "instanceId" in data:
            request.instance_id = data["instanceId"]
        if "indexCode" in data:
            request.index_code = data["indexCode"]

        return request

    @classmethod
    def from_json(cls, json_str: str) -> "GetTimeLineWithPointRequestVO":
        """
        从JSON字符串创建请求对象

        参数:
        json_str: JSON格式的字符串

        返回:
        GetTimeLineWithPointRequestVO 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"GetTimeLineWithPointRequestVO(point=({self.point_x}, {self.point_y}), "
            f"instance_id={self.instance_id!r}, index_code={self.index_code!r})"
        )
