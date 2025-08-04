from dataclasses import dataclass
from typing import Optional, Dict, Any
import json


@dataclass
class BaseGeoStr:
    """
    地理信息基础模型
    对应 Java 的 com.yrihr.sdk.model.postprocess.BaseGeoStr

    属性:
    smid: int - SMID
    smgeometry: str - 几何信息
    code: str - 地理信息编码
    name: str - 地理信息名称
    base_file_url: str - 基础文件路径（二维且解析模式为文件时使用）
    topr_file_url: str - 拓扑关系文件路径（二维且解析模式为文件时使用）
    """

    smid: int = 0
    smgeometry: str = ""
    code: str = ""
    name: str = ""
    base_file_url: str = ""
    topr_file_url: str = ""

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_smid(self, smid: int) -> "BaseGeoStr":
        self.smid = smid
        return self

    def with_smgeometry(self, smgeometry: str) -> "BaseGeoStr":
        self.smgeometry = smgeometry
        return self

    def with_code(self, code: str) -> "BaseGeoStr":
        self.code = code
        return self

    def with_name(self, name: str) -> "BaseGeoStr":
        self.name = name
        return self

    def with_base_file_url(self, base_file_url: str) -> "BaseGeoStr":
        self.base_file_url = base_file_url
        return self

    def with_topr_file_url(self, topr_file_url: str) -> "BaseGeoStr":
        self.topr_file_url = topr_file_url
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将 BaseGeoStr 对象转换为字典

        返回:
        包含地理信息的字典
        """
        return {
            "smid": self.smid,
            "smgeometry": self.smgeometry,
            "code": self.code,
            "name": self.name,
            "baseFileUrl": self.base_file_url,
            "toprFileUrl": self.topr_file_url,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将 BaseGeoStr 对象转换为 JSON 字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseGeoStr":
        """
        从字典创建 BaseGeoStr 对象

        参数:
        data: 包含地理信息的字典

        返回:
        BaseGeoStr 实例
        """
        geo = cls()

        if "smid" in data:
            geo.smid = data["smid"]
        if "smgeometry" in data:
            geo.smgeometry = data["smgeometry"]
        if "code" in data:
            geo.code = data["code"]
        if "name" in data:
            geo.name = data["name"]
        if "baseFileUrl" in data:
            geo.base_file_url = data["baseFileUrl"]
        if "toprFileUrl" in data:
            geo.topr_file_url = data["toprFileUrl"]

        return geo

    @classmethod
    def from_json(cls, json_str: str) -> "BaseGeoStr":
        """
        从 JSON 字符串创建 BaseGeoStr 对象

        参数:
        json_str: JSON 格式的字符串

        返回:
        BaseGeoStr 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"BaseGeoStr(smid={self.smid}, code={self.code!r}, "
            f"name={self.name!r}, file_based={self.is_file_based()})"
        )
