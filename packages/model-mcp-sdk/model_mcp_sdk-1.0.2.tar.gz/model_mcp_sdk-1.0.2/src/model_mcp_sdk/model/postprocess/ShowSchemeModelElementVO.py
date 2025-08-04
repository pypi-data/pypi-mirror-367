from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# 假设 ShowSchemeModelLetterItemVO 已定义在同一个模块中
from model_mcp_sdk.model.postprocess.ShowSchemeModelLetterItemVO import (
    ShowSchemeModelLetterItemVO,
)


@dataclass
class ShowSchemeModelElementVO:
    """
    展示方案模型元素视图模型
    对应 Java 的 com.yrihr.sdk.model.postprocess.ShowSchemeModelElementVO

    属性:
    bounds: str - 边界信息
    create_time: datetime - 创建时间
    grid_table: str - 网格表名
    instance_id: str - 实例ID
    letter_list: List[ShowSchemeModelLetterItemVO] - 字母项列表
    model_core_id: str - 模型核心ID
    node_name: str - 节点名称
    status: int - 状态
    """

    bounds: str = ""
    create_time: Optional[datetime] = None
    grid_table: str = ""
    instance_id: str = ""
    letter_list: List[ShowSchemeModelLetterItemVO] = field(default_factory=list)
    model_core_id: str = ""
    node_name: str = ""
    status: int = 0

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_bounds(self, bounds: str) -> "ShowSchemeModelElementVO":
        """设置边界信息"""
        self.bounds = bounds
        return self

    def with_create_time(self, create_time: datetime) -> "ShowSchemeModelElementVO":
        """设置创建时间"""
        self.create_time = create_time
        return self

    def with_grid_table(self, grid_table: str) -> "ShowSchemeModelElementVO":
        """设置网格表名"""
        self.grid_table = grid_table
        return self

    def with_instance_id(self, instance_id: str) -> "ShowSchemeModelElementVO":
        """设置实例ID"""
        self.instance_id = instance_id
        return self

    def with_letter_list(
        self, letter_list: List[ShowSchemeModelLetterItemVO]
    ) -> "ShowSchemeModelElementVO":
        """设置字母项列表"""
        self.letter_list = letter_list
        return self

    def add_letter_item(
        self, letter_item: ShowSchemeModelLetterItemVO
    ) -> "ShowSchemeModelElementVO":
        """添加一个字母项"""
        self.letter_list.append(letter_item)
        return self

    def with_model_core_id(self, model_core_id: str) -> "ShowSchemeModelElementVO":
        """设置模型核心ID"""
        self.model_core_id = model_core_id
        return self

    def with_node_name(self, node_name: str) -> "ShowSchemeModelElementVO":
        """设置节点名称"""
        self.node_name = node_name
        return self

    def with_status(self, status: int) -> "ShowSchemeModelElementVO":
        """设置状态"""
        self.status = status
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将元素对象转换为字典

        返回:
        包含元素信息的字典

        日期时间字段会转换为 ISO 格式字符串
        """
        return {
            "bounds": self.bounds,
            "createTime": self.create_time.isoformat() if self.create_time else None,
            "gridTable": self.grid_table,
            "instanceId": self.instance_id,
            "letterList": [item.to_dict() for item in self.letter_list],
            "modelCoreId": self.model_core_id,
            "nodeName": self.node_name,
            "status": self.status,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将元素对象转换为JSON字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShowSchemeModelElementVO":
        """
        从字典创建元素对象

        参数:
        data: 包含元素信息的字典

        返回:
        ShowSchemeModelElementVO 实例

        日期时间字段会从 ISO 格式字符串转换
        """
        element = cls()

        if "bounds" in data:
            element.bounds = data["bounds"]
        if "createTime" in data and data["createTime"]:
            element.create_time = datetime.fromisoformat(data["createTime"])
        if "gridTable" in data:
            element.grid_table = data["gridTable"]
        if "instanceId" in data:
            element.instance_id = data["instanceId"]
        if "modelCoreId" in data:
            element.model_core_id = data["modelCoreId"]
        if "nodeName" in data:
            element.node_name = data["nodeName"]
        if "status" in data:
            element.status = data["status"]

        # 处理字母项列表
        if "letterList" in data:
            for item_data in data["letterList"]:
                if isinstance(item_data, dict):
                    letter_item = ShowSchemeModelLetterItemVO.from_dict(item_data)
                    element.letter_list.append(letter_item)
                else:
                    element.letter_list.append(item_data)  # 直接添加

        return element

    @classmethod
    def from_json(cls, json_str: str) -> "ShowSchemeModelElementVO":
        """
        从JSON字符串创建元素对象

        参数:
        json_str: JSON格式的字符串

        返回:
        ShowSchemeModelElementVO 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"ShowSchemeModelElementVO(node_name={self.node_name!r}, "
            f"status={self.get_status_text()}, "
            f"letters={len(self.letter_list)})"
        )
