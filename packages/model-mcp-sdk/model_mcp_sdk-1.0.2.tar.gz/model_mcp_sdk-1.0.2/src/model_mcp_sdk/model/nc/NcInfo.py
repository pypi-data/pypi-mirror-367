from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json

# 假设这些类已经定义在同一个模块中
from model_mcp_sdk.model.nc.NcDimensions import NcDimensions
from model_mcp_sdk.model.nc.NcGlobalAttributes import NcGlobalAttributes
from model_mcp_sdk.model.nc.NcVariables import NcVariables


@dataclass
class NcInfo:
    """
    NC 文件完整信息模型
    对应 Java 的 com.yrihr.sdk.model.nc.NcInfo
    """

    # NC 文件名称
    nc_name: str = ""
    # NC 文件的中文名称
    nc_full_name: str = ""
    # 输出参数文件路径
    file_path: str = ""
    # 类型：string_array (NC 文件列表)、single (单值)、file (文件)、hydraulic_elements (液压元件 NC 文件)
    type: str = ""
    # 当类型为 hydraulic_elements 时，存储对应的液压元件 ID
    hydraulic_elements_id: str = ""
    # 当类型为 file 时，存储文件后缀名；当类型为 single 时，存储单值默认值
    extend: str = ""
    # 是否必填项
    required: bool = False
    # 参数类型：1 表示输入，2 表示输出
    arg_type: Optional[int] = None
    # 参数值
    value: str = ""
    # NC 文件维度列表
    dimensions_list: List[NcDimensions] = field(default_factory=list)
    # NC 文件变量列表
    variables_list: List[NcVariables] = field(default_factory=list)
    # NC 文件全局属性列表
    global_list: List[NcGlobalAttributes] = field(default_factory=list)

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_nc_name(self, name: str) -> "NcInfo":
        self.nc_name = name
        return self

    def with_nc_full_name(self, full_name: str) -> "NcInfo":
        self.nc_full_name = full_name
        return self

    def with_file_path(self, file_path: str) -> "NcInfo":
        self.file_path = file_path
        return self

    def with_type(self, info_type: str) -> "NcInfo":
        self.type = info_type
        return self

    def with_hydraulic_elements_id(self, element_id: str) -> "NcInfo":
        self.hydraulic_elements_id = element_id
        return self

    def with_extend(self, extend_value: str) -> "NcInfo":
        self.extend = extend_value
        return self

    def with_required(self, is_required: bool) -> "NcInfo":
        self.required = is_required
        return self

    def with_arg_type(self, arg_type: int) -> "NcInfo":
        self.arg_type = arg_type
        return self

    def with_value(self, param_value: str) -> "NcInfo":
        self.value = param_value
        return self

    def add_dimension(self, dimension: NcDimensions) -> "NcInfo":
        self.dimensions_list.append(dimension)
        return self

    def add_variable(self, variable: NcVariables) -> "NcInfo":
        self.variables_list.append(variable)
        return self

    def add_global_attribute(self, attribute: NcGlobalAttributes) -> "NcInfo":
        self.global_list.append(attribute)
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self, deep: bool = True) -> Dict[str, Any]:
        """
        将 NcInfo 对象转换为字典格式

        :param deep: 是否深度转换嵌套对象
        :return: 字典格式的数据
        """
        data = {
            "ncName": self.nc_name,
            "ncFullName": self.nc_full_name,
            "filePath": self.file_path,
            "type": self.type,
            "hydraulicElementsId": self.hydraulic_elements_id,
            "extend": self.extend,
            "required": self.required,
            "argType": self.arg_type,
            "value": self.value,
        }

        # 深度转换嵌套对象
        if deep:
            data["dimensionsList"] = [
                dim.to_dict() if hasattr(dim, "to_dict") else dim
                for dim in self.dimensions_list
            ]

            data["variablesList"] = [
                var.to_dict() if hasattr(var, "to_dict") else var
                for var in self.variables_list
            ]

            data["globalList"] = [
                attr.to_dict() if hasattr(attr, "to_dict") else attr
                for attr in self.global_list
            ]
        else:
            data["dimensionsList"] = self.dimensions_list
            data["variablesList"] = self.variables_list
            data["globalList"] = self.global_list

        return data

    def to_json(self, deep: bool = True, indent: Optional[int] = None) -> str:
        """
        将 NcInfo 对象转换为 JSON 字符串

        :param deep: 是否深度转换嵌套对象
        :param indent: JSON 格式化缩进（None 表示不格式化）
        :return: JSON 格式的字符串
        """
        return json.dumps(self.to_dict(deep), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NcInfo":
        """
        从字典创建 NcInfo 对象

        :param data: 包含 NcInfo 数据的字典
        :return: NcInfo 实例
        """
        nc_info = cls()

        # 设置基本字段
        if "ncName" in data:
            nc_info.nc_name = data["ncName"]
        if "ncFullName" in data:
            nc_info.nc_full_name = data["ncFullName"]
        if "filePath" in data:
            nc_info.file_path = data["filePath"]
        if "type" in data:
            nc_info.type = data["type"]
        if "hydraulicElementsId" in data:
            nc_info.hydraulic_elements_id = data["hydraulicElementsId"]
        if "extend" in data:
            nc_info.extend = data["extend"]
        if "required" in data:
            nc_info.required = data["required"]
        if "argType" in data:
            nc_info.arg_type = data["argType"]
        if "value" in data:
            nc_info.value = data["value"]

        # 创建嵌套对象 (根据需要实现这些类的 from_dict 方法)
        if "dimensionsList" in data:
            for dim_data in data["dimensionsList"]:
                if isinstance(dim_data, dict):
                    dimension = NcDimensions.from_dict(dim_data)  # 假设实现
                    nc_info.dimensions_list.append(dimension)
                else:
                    nc_info.dimensions_list.append(dim_data)  # 直接添加

        if "variablesList" in data:
            for var_data in data["variablesList"]:
                if isinstance(var_data, dict):
                    variable = NcVariables.from_dict(var_data)  # 假设实现
                    nc_info.variables_list.append(variable)
                else:
                    nc_info.variables_list.append(var_data)  # 直接添加

        if "globalList" in data:
            for attr_data in data["globalList"]:
                if isinstance(attr_data, dict):
                    attribute = NcGlobalAttributes.from_dict(attr_data)  # 假设实现
                    nc_info.global_list.append(attribute)
                else:
                    nc_info.global_list.append(attr_data)  # 直接添加

        return nc_info

    @classmethod
    def from_json(cls, json_str: str) -> "NcInfo":
        """
        从 JSON 字符串创建 NcInfo 对象

        :param json_str: JSON 格式的字符串
        :return: NcInfo 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    # ----------------------------
    # 增强功能
    # ----------------------------
    def validate(self) -> bool:
        """
        验证 NC 信息是否有效

        :return: True 如果有效，否则 False
        """
        if not self.nc_name:
            return False
        if not self.file_path:
            return False
        if self.type not in ["string_array", "single", "file", "hydraulic_elements"]:
            return False
        return True

    def get_dimension_by_name(self, name: str) -> Optional[NcDimensions]:
        """
        根据名称获取维度信息

        :param name: 维度名称
        :return: 匹配的维度对象，如果找不到则返回 None
        """
        for dim in self.dimensions_list:
            if dim.name == name:
                return dim
        return None

    def get_variable_by_name(self, name: str) -> Optional[NcVariables]:
        """
        根据名称获取变量信息

        :param name: 变量名称
        :return: 匹配的变量对象，如果找不到则返回 None
        """
        for var in self.variables_list:
            if var.name == name:
                return var
        return None

    def get_global_attribute_by_name(self, name: str) -> Optional[NcGlobalAttributes]:
        """
        根据名称获取全局属性

        :param name: 属性名称
        :return: 匹配的全局属性对象，如果找不到则返回 None
        """
        for attr in self.global_list:
            if attr.name == name:
                return attr
        return None

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"NcInfo(nc_name={self.nc_name!r}, type={self.type!r}, "
            f"file_path={self.file_path!r}, "
            f"dimensions={len(self.dimensions_list)}, "
            f"variables={len(self.variables_list)}, "
            f"global_attrs={len(self.global_list)})"
        )
