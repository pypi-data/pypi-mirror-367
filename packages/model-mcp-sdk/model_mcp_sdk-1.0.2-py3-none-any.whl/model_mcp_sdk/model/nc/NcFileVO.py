from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass
class NcFileVO:
    """
    NC 文件信息
    对应 Java 的 com.yrihr.sdk.model.nc.NcFileVO

    属性:
    file_path: str - 文件路径
    nc_name: str - NC文件名称
    """

    file_path: str = ""
    nc_name: str = ""

    # ------------------------
    # 链式调用方法
    # ------------------------
    def with_file_path(self, file_path: str) -> "NcFileVO":
        """设置文件路径并返回对象自身，支持链式调用"""
        self.file_path = file_path
        return self

    def with_nc_name(self, nc_name: str) -> "NcFileVO":
        """设置NC文件名称并返回对象自身，支持链式调用"""
        self.nc_name = nc_name
        return self

    # ------------------------
    # 序列化/反序列化方法
    # ------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NcFileVO":
        """
        从字典创建NcFileVO对象

        参数:
        data: 包含文件信息的字典，键应为"filePath"和"ncName"

        返回:
        新的NcFileVO实例

        示例:
        >>> file_info = NcFileVO.from_dict({"filePath": "/data.nc", "ncName": "dataset"})
        >>> file_info.file_path
        '/data.nc'
        """
        return cls(file_path=data.get("filePath", ""), nc_name=data.get("ncName", ""))

    @classmethod
    def from_json(cls, json_str: str) -> "NcFileVO":
        """
        从JSON字符串创建NcFileVO对象

        参数:
        json_str: JSON格式的字符串

        返回:
        新的NcFileVO实例

        示例:
        >>> json_str = '{"filePath": "/data/models/output.nc", "ncName": "model_output"}'
        >>> nc_file = NcFileVO.from_json(json_str)
        >>> nc_file.file_path
        '/data/models/output.nc'
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """
        将NcFileVO对象转换为字典

        返回:
        包含文件信息的字典，键使用与Java属性一致的命名风格("filePath"和"ncName")

        示例:
        >>> file_info = NcFileVO("/data.nc", "dataset")
        >>> file_info.to_dict()
        {'filePath': '/data.nc', 'ncName': 'dataset'}
        """
        return {"filePath": self.file_path, "ncName": self.nc_name}

    def to_json(self) -> str:
        """
        将NcFileVO对象转换为JSON字符串

        返回:
        JSON格式的字符串

        示例:
        >>> file_info = NcFileVO("/data/output.nc", "output_dataset")
        >>> file_info.to_json()
        '{"filePath": "/data/output.nc", "ncName": "output_dataset"}'
        """
        return json.dumps(self.to_dict())

    def validate(self) -> bool:
        """
        验证文件信息是否有效

        返回:
        True 如果文件路径和名称都非空，否则 False

        示例:
        >>> valid_file = NcFileVO("/valid/path.nc", "valid_name")
        >>> valid_file.validate()
        True
        >>> invalid_file = NcFileVO("", "name_without_path")
        >>> invalid_file.validate()
        False
        """
        return bool(self.file_path.strip()) and bool(self.nc_name.strip())

    def __repr__(self) -> str:
        """可读的对象表示"""
        return f"NcFileVO(file_path={self.file_path!r}, nc_name={self.nc_name!r})"
