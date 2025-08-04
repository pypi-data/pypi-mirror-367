from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ReadNcRequest:
    """
    读取 NC 文件的请求参数
    对应 Java 的 com.yrihr.sdk.model.core.ReadNcRequest

    属性:
    file_path: str - NC文件的路径
    """

    file_path: str = ""

    # ------------------------
    # 链式调用方法 (可选但推荐)
    # ------------------------
    def with_file_path(self, file_path: str) -> "ReadNcRequest":
        """设置文件路径并返回对象自身，支持链式调用"""
        self.file_path = file_path
        return self

    # ------------------------
    # 序列化/反序列化方法
    # ------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReadNcRequest":
        """
        从字典创建 ReadNcRequest 对象

        参数:
        data: 包含文件路径信息的字典，键应为"filePath"

        返回:
        新的 ReadNcRequest 实例

        示例:
        >>> request_data = {"filePath": "/path/to/data.nc"}
        >>> request = ReadNcRequest.from_dict(request_data)
        >>> request.file_path
        '/path/to/data.nc'
        """
        return cls(file_path=data.get("filePath", ""))

    @classmethod
    def from_json(cls, json_str: str) -> "ReadNcRequest":
        """
        从JSON字符串创建 ReadNcRequest 对象

        参数:
        json_str: JSON格式的字符串

        返回:
        新的 ReadNcRequest 实例

        示例:
        >>> json_str = '{"filePath": "/path/to/file.nc"}'
        >>> request = ReadNcRequest.from_json(json_str)
        >>> request.file_path
        '/path/to/file.nc'
        """
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """
        将 ReadNcRequest 对象转换为字典

        返回:
        包含文件路径信息的字典，键使用与Java属性一致的命名风格("filePath")

        示例:
        >>> request = ReadNcRequest("/path/to/file.nc")
        >>> request.to_dict()
        {'filePath': '/path/to/file.nc'}
        """
        return {"filePath": self.file_path}

    def to_json(self) -> str:
        """
        将 ReadNcRequest 对象转换为JSON字符串

        返回:
        JSON格式的字符串

        示例:
        >>> request = ReadNcRequest("/data/output.nc")
        >>> request.to_json()
        '{"filePath": "/data/output.nc"}'
        """
        import json

        return json.dumps(self.to_dict())
