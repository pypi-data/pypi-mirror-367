from dataclasses import dataclass
from typing import Dict, Any, Union
import json


@dataclass
class NcGlobalAttributes:
    """
    NC 文件全局属性信息
    对应 Java 的 com.yrihr.sdk.model.nc.NcGlobalAttributes

    属性:
    type: str - 属性类型 (string, int, double)
    name: str - 属性名称
    full_name: str - 属性的中文名
    value: str - 属性值
    remark: str - 备注信息
    default_value: str - 默认值
    """

    type: str = ""
    name: str = ""
    full_name: str = ""
    value: str = ""
    remark: str = ""
    default_value: str = ""

    # ------------------------
    # 链式调用方法
    # ------------------------
    def set_type(self, attribute_type: str) -> "NcGlobalAttributes":
        """设置属性类型 (string, int, double)"""
        self.type = attribute_type
        return self

    def set_name(self, name: str) -> "NcGlobalAttributes":
        """设置属性名称"""
        self.name = name
        return self

    def set_full_name(self, full_name: str) -> "NcGlobalAttributes":
        """设置属性的中文名"""
        self.full_name = full_name
        return self

    def set_value(self, value: str) -> "NcGlobalAttributes":
        """设置属性值"""
        self.value = value
        return self

    def set_remark(self, remark: str) -> "NcGlobalAttributes":
        """设置备注信息"""
        self.remark = remark
        return self

    def set_default_value(self, default_value: str) -> "NcGlobalAttributes":
        """设置默认值"""
        self.default_value = default_value
        return self

    # ------------------------
    # 序列化/反序列化方法
    # ------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NcGlobalAttributes":
        """
        从字典创建 NcGlobalAttributes 对象

        参数:
        data: 包含全局属性信息的字典

        返回:
        新的 NcGlobalAttributes 实例

        示例:
        >>> attr_data = {
        ...     "type": "string",
        ...     "name": "title",
        ...     "fullName": "标题",
        ...     "value": "全球气候数据",
        ...     "remark": "数据集标题",
        ...     "defaultValue": "无标题"
        ... }
        >>> attr = NcGlobalAttributes.from_dict(attr_data)
        >>> attr.type
        'string'
        """
        return cls(
            type=data.get("type", ""),
            name=data.get("name", ""),
            full_name=data.get("fullName", ""),  # Java字段名称不同
            value=data.get("value", ""),
            remark=data.get("remark", ""),
            default_value=data.get("defaultValue", ""),  # Java字段名称不同
        )

    @classmethod
    def from_json(cls, json_str: str) -> "NcGlobalAttributes":
        """
        从JSON字符串创建 NcGlobalAttributes 对象

        参数:
        json_str: JSON格式的字符串

        返回:
        新的 NcGlobalAttributes 实例

        示例:
        >>> json_data = '{"type":"int","name":"version","fullName":"版本号","value":"2","remark":"数据格式版本"}'
        >>> attr = NcGlobalAttributes.from_json(json_data)
        >>> attr.name
        'version'
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """
        将 NcGlobalAttributes 对象转换为字典

        返回:
        包含全局属性信息的字典，键使用与Java属性一致的命名风格

        示例:
        >>> attr = NcGlobalAttributes(
        ...     type="string",
        ...     name="title",
        ...     full_name="标题",
        ...     value="全球气候数据",
        ...     remark="数据集标题",
        ...     default_value="无标题"
        ... )
        >>> attr_dict = attr.to_dict()
        >>> attr_dict["fullName"]
        '标题'
        >>> attr_dict["defaultValue"]
        '无标题'
        """
        return {
            "type": self.type,
            "name": self.name,
            "fullName": self.full_name,  # 使用Java风格命名
            "value": self.value,
            "remark": self.remark,
            "defaultValue": self.default_value,  # 使用Java风格命名
        }

    def to_json(self) -> str:
        """
        将 NcGlobalAttributes 对象转换为JSON字符串

        返回:
        JSON格式的字符串

        示例:
        >>> attr = NcGlobalAttributes(
        ...     type="double",
        ...     name="scale_factor",
        ...     value="0.01"
        ... )
        >>> attr.to_json()
        '{"type": "double", "name": "scale_factor", "fullName": "", "value": "0.01", "remark": "", "defaultValue": ""}'
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    # ------------------------
    # 增强功能
    # ------------------------
    def validate(self) -> bool:
        """
        验证属性是否有效

        返回:
        True 如果属性有效，否则 False

        规则:
        - 属性类型必须是 "string", "int" 或 "double"
        - 属性名称不能为空
        """
        if self.type not in ["string", "int", "double"]:
            return False
        if not self.name.strip():
            return False
        return True

    def value_as_type(self) -> Union[str, int, float]:
        """
        将属性值转换为指定的类型

        返回:
        转换后的值 (str, int 或 float)

        示例:
        >>> attr = NcGlobalAttributes(type="int", value="123")
        >>> attr.value_as_type()
        123
        """
        try:
            if self.type == "int":
                return int(self.value)
            elif self.type == "double":
                return float(self.value)
            else:
                return self.value  # string
        except (ValueError, TypeError):
            return self.value  # 类型转换失败时返回原始字符串

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"NcGlobalAttributes(type={self.type!r}, name={self.name!r}, "
            f"value={self.value!r})"
        )
