from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import json


@dataclass
class NcVariables:
    """
    NC 文件变量信息模型
    对应 Java 的 com.yrihr.sdk.model.nc.NcVariables

    属性:
    value_type: str - 值类型 (string, int, double 等)
    array_type: str - 数组类型
    name: str - 变量名称
    full_name: str - 变量的中文名
    array_value: List[str] - 一维数组值
    array3_d_value: List[List[List[str]]] - 三维数组值
    dimensions_sort: List[str] - 维度排序
    object: Any - 特殊类型对象
    remark: str - 备注信息
    file: int - 是否是文件 (0-否, 1-是)
    file_type: str - 文件类型
    file_path: str - 文件路径
    """

    value_type: str = ""
    array_type: str = ""
    name: str = ""
    full_name: str = ""
    array_value: List[str] = field(default_factory=list)
    array3_d_value: List[List[List[str]]] = field(default_factory=list)
    dimensions_sort: List[str] = field(default_factory=list)
    object: Optional[Any] = None
    remark: str = ""
    file: int = 0
    file_type: str = ""
    file_path: str = ""

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_value_type(self, value_type: str) -> "NcVariables":
        """设置值类型 (string, int, double 等)"""
        self.value_type = value_type
        return self

    def with_array_type(self, array_type: str) -> "NcVariables":
        """设置数组类型"""
        self.array_type = array_type
        return self

    def with_name(self, name: str) -> "NcVariables":
        """设置变量名称"""
        self.name = name
        return self

    def with_full_name(self, full_name: str) -> "NcVariables":
        """设置变量的中文名"""
        self.full_name = full_name
        return self

    def with_array_value(self, array_value: List[str]) -> "NcVariables":
        """设置一维数组值"""
        self.array_value = array_value
        return self

    def add_array_value(self, value: str) -> "NcVariables":
        """添加一个值到一维数组"""
        self.array_value.append(value)
        return self

    def with_array3_d_value(
        self, array3_d_value: List[List[List[str]]]
    ) -> "NcVariables":
        """设置三维数组值"""
        self.array3_d_value = array3_d_value
        return self

    def add_to_3d_array(self, value: List[List[str]]) -> "NcVariables":
        """添加一个二维数组到三维数组"""
        self.array3_d_value.append(value)
        return self

    def with_dimensions_sort(self, dimensions_sort: List[str]) -> "NcVariables":
        """设置维度排序"""
        self.dimensions_sort = dimensions_sort
        return self

    def add_dimension_sort(self, dimension: str) -> "NcVariables":
        """添加一个维度到维度排序"""
        self.dimensions_sort.append(dimension)
        return self

    def with_object(self, obj: Any) -> "NcVariables":
        """设置特殊类型对象"""
        self.object = obj
        return self

    def with_remark(self, remark: str) -> "NcVariables":
        """设置备注信息"""
        self.remark = remark
        return self

    def with_file(self, is_file: int) -> "NcVariables":
        """设置是否是文件 (0-否, 1-是)"""
        self.file = is_file
        return self

    def with_file_type(self, file_type: str) -> "NcVariables":
        """设置文件类型"""
        self.file_type = file_type
        return self

    def with_file_path(self, file_path: str) -> "NcVariables":
        """设置文件路径"""
        self.file_path = file_path
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将 NcVariables 对象转换为字典格式

        返回:
        包含变量信息的字典，键使用与Java属性一致的命名风格

        示例:
        >>> var = NcVariables(name="temperature", value_type="float")
        >>> var_dict = var.to_dict()
        >>> var_dict["name"]
        'temperature'
        """
        return {
            "valueType": self.value_type,
            "arrayType": self.array_type,
            "name": self.name,
            "fullName": self.full_name,
            "arrayValue": self.array_value,
            "array3DValue": self.array3_d_value,
            "dimensionsSort": self.dimensions_sort,
            "object": self.object,
            "remark": self.remark,
            "file": self.file,
            "fileType": self.file_type,
            "filePath": self.file_path,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将 NcVariables 对象转换为JSON字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON格式的字符串

        示例:
        >>> var = NcVariables(name="pressure", value_type="double")
        >>> var_json = var.to_json()
        >>> var_json
        '{"valueType": "double", "arrayType": "", "name": "pressure", ...}'
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NcVariables":
        """
        从字典创建 NcVariables 对象

        参数:
        data: 包含变量信息的字典

        返回:
        新的 NcVariables 实例

        示例:
        >>> var_data = {
        ...     "valueType": "float",
        ...     "name": "temperature",
        ...     "arrayValue": ["25.5", "26.0", "27.2"]
        ... }
        >>> var = NcVariables.from_dict(var_data)
        >>> var.name
        'temperature'
        """
        variable = cls()

        # 设置基本字段
        if "valueType" in data:
            variable.value_type = data["valueType"]
        if "arrayType" in data:
            variable.array_type = data["arrayType"]
        if "name" in data:
            variable.name = data["name"]
        if "fullName" in data:
            variable.full_name = data["fullName"]
        if "arrayValue" in data and data["arrayValue"] != None:
            variable.array_value = list(data["arrayValue"])
        if "array3DValue" in data and data["array3DValue"] != None:
            # 转换为三维列表
            variable.array3_d_value = [
                [[str(item) for item in innermost] for innermost in middle]
                for middle in data["array3DValue"]
            ]
        if "dimensionsSort" in data and data["dimensionsSort"] != None:
            variable.dimensions_sort = list(data["dimensionsSort"])
        if "object" in data:
            variable.object = data["object"]
        if "remark" in data:
            variable.remark = data["remark"]
        if "file" in data:
            variable.file = int(data.get("file", 0))
        if "fileType" in data:
            variable.file_type = data["fileType"]
        if "filePath" in data:
            variable.file_path = data["filePath"]

        return variable

    @classmethod
    def from_json(cls, json_str: str) -> "NcVariables":
        """
        从JSON字符串创建 NcVariables 对象

        参数:
        json_str: JSON格式的字符串

        返回:
        新的 NcVariables 实例

        示例:
        >>> json_data = '{"name":"humidity","valueType":"double","arrayValue":["50.5","52.0"]}'
        >>> var = NcVariables.from_json(json_data)
        >>> var.array_value
        ['50.5', '52.0']
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    # ----------------------------
    # 增强功能
    # ----------------------------
    def validate(self) -> bool:
        """
        验证变量信息是否有效

        返回:
        True 如果变量有效，否则 False

        规则:
        - 变量名称不能为空
        - 如果 file=1，则文件路径不能为空
        """
        if not self.name.strip():
            return False
        if self.file == 1 and not self.file_path.strip():
            return False
        return True

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"NcVariables(name={self.name!r}, type={self.value_type!r}, "
            f"array_size={len(self.array_value)}, "
            f"3d_array_size={len(self.array3_d_value) if self.array3_d_value else 0})"
        )
