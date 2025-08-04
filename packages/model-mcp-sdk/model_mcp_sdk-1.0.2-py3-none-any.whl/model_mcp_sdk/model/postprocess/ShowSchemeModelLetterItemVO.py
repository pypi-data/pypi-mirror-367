from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class ShowSchemeModelLetterItemVO:
    """
    展示方案模型字母项视图模型
    对应 Java 的 com.yrihr.sdk.model.postprocess.ShowSchemeModelLetterItemVO

    属性:
    args_name: str - 参数名称
    args_type: int - 参数类型
    postprocess_type: str - 后处理类型
    grid_table: str - 网格表名
    letter_name: str - 字母名称
    """

    args_name: str = ""
    args_type: int = 0
    postprocess_type: str = ""
    grid_table: str = ""
    letter_name: str = ""

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_args_name(self, args_name: str) -> "ShowSchemeModelLetterItemVO":
        """设置参数名称"""
        self.args_name = args_name
        return self

    def with_args_type(self, args_type: int) -> "ShowSchemeModelLetterItemVO":
        """设置参数类型"""
        self.args_type = args_type
        return self

    def with_postprocess_type(
        self, postprocess_type: str
    ) -> "ShowSchemeModelLetterItemVO":
        """设置后处理类型"""
        self.postprocess_type = postprocess_type
        return self

    def with_grid_table(self, grid_table: str) -> "ShowSchemeModelLetterItemVO":
        """设置网格表名"""
        self.grid_table = grid_table
        return self

    def with_letter_name(self, letter_name: str) -> "ShowSchemeModelLetterItemVO":
        """设置字母名称"""
        self.letter_name = letter_name
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将字母项对象转换为字典

        返回:
        包含字母项信息的字典
        """
        return {
            "argsName": self.args_name,
            "argsType": self.args_type,
            "postprocessType": self.postprocess_type,
            "gridTable": self.grid_table,
            "letterName": self.letter_name,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将字母项对象转换为JSON字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShowSchemeModelLetterItemVO":
        """
        从字典创建字母项对象

        参数:
        data: 包含字母项信息的字典

        返回:
        ShowSchemeModelLetterItemVO 实例
        """
        item = cls()

        if "argsName" in data:
            item.args_name = data["argsName"]
        if "argsType" in data:
            item.args_type = data["argsType"]
        if "postprocessType" in data:
            item.postprocess_type = data["postprocessType"]
        if "gridTable" in data:
            item.grid_table = data["gridTable"]
        if "letterName" in data:
            item.letter_name = data["letterName"]

        return item

    @classmethod
    def from_json(cls, json_str: str) -> "ShowSchemeModelLetterItemVO":
        """
        从JSON字符串创建字母项对象

        参数:
        json_str: JSON格式的字符串

        返回:
        ShowSchemeModelLetterItemVO 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"ShowSchemeModelLetterItemVO(letter_name={self.letter_name!r}, "
            f"args_name={self.args_name!r}, type={self.get_args_type_text()})"
        )
