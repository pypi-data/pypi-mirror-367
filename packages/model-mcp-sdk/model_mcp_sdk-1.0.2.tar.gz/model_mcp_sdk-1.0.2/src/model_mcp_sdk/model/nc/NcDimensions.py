from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass
class NcDimensions:
    """
    NC 文件维度信息
    对应 Java 的 com.yrihr.sdk.model.nc.NcDimensions

    属性:
    name: str - 维度名称
    full_name: str - 中文名
    value: int - 维度值
    remark: str - 备注
    default_value: str - 默认值
    """

    name: str = ""
    full_name: str = ""
    value: int = 0
    remark: str = ""
    default_value: str = ""

    # 支持链式调用
    def with_name(self, name: str) -> "NcDimensions":
        """设置维度名称并返回对象自身，支持链式调用"""
        self.name = name
        return self

    def with_full_name(self, full_name: str) -> "NcDimensions":
        """设置中文名并返回对象自身，支持链式调用"""
        self.full_name = full_name
        return self

    def with_value(self, value: int) -> "NcDimensions":
        """设置维度值并返回对象自身，支持链式调用"""
        self.value = value
        return self

    def with_remark(self, remark: str) -> "NcDimensions":
        """设置备注并返回对象自身，支持链式调用"""
        self.remark = remark
        return self

    def with_default_value(self, default_value: str) -> "NcDimensions":
        """设置默认值并返回对象自身，支持链式调用"""
        self.default_value = default_value
        return self

    def validate(self) -> bool:
        """验证维度信息是否有效"""
        if not self.name:
            return False
        if self.value < 0:
            return False
        return True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NcDimensions":
        """
        从字典创建NcDimensions对象

        参数:
        data: 包含维度信息的字典，键需要匹配字段名称

        返回:
        新的NcDimensions实例

        示例:
        >>> dim_data = {
        ...     "name": "time",
        ...     "fullName": "时间",
        ...     "value": 365,
        ...     "remark": "时间维度",
        ...     "defaultValue": "0"
        ... }
        >>> dim = NcDimensions.from_dict(dim_data)
        >>> dim.name
        'time'
        """
        return cls(
            name=data.get("name", ""),
            full_name=data.get("fullName", ""),
            value=data.get("value", 0),
            remark=data.get("remark", ""),
            default_value=data.get("defaultValue", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "NcDimensions":
        """
        从JSON字符串创建NcDimensions对象

        参数:
        json_str: JSON格式的字符串

        返回:
        新的NcDimensions实例

        示例:
        >>> json_data = '{"name":"lat","fullName":"纬度","value":180,"remark":"纬度维度"}'
        >>> dim = NcDimensions.from_json(json_data)
        >>> dim.full_name
        '纬度'
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """
        将NcDimensions对象转换为字典

        返回:
        包含维度信息的字典，键使用与Java属性一致的命名风格

        示例:
        >>> dim = NcDimensions("time", "时间", 365, "时间维度", "0")
        >>> dim_dict = dim.to_dict()
        >>> dim_dict["fullName"]
        '时间'
        >>> dim_dict["defaultValue"]
        '0'
        """
        return {
            "name": self.name,
            "fullName": self.full_name,
            "value": self.value,
            "remark": self.remark,
            "defaultValue": self.default_value,
        }

    def to_json(self) -> str:
        """
        将NcDimensions对象转换为JSON字符串

        返回:
        JSON格式的字符串

        示例:
        >>> dim = NcDimensions("level", "层级", 10, "", "0")
        >>> json_str = dim.to_json()
        >>> json_str
        '{"name": "level", "fullName": "层级", "value": 10, "remark": "", "defaultValue": "0"}'
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"NcDimensions(name='{self.name}', full_name='{self.full_name}', "
            f"value={self.value}, default_value='{self.default_value}')"
        )
