from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from model_mcp_sdk.model.service.KeyValueItem import KeyValueItem


@dataclass
class ExeArgoServiceCallBackVO:
    """
    Argo 服务执行回调视图模型
    对应 Java 的 com.yrihr.sdk.model.service.ExeArgoServiceCallBackVO

    属性:
    key: str - 主键
    inc_key: str - 增量键
    status: int - 状态
    data: List[KeyValueItem] - 键值对数据列表
    """

    key: str = ""
    inc_key: str = ""
    status: int = 0
    data: List[KeyValueItem] = field(default_factory=list)

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_key(self, key: str) -> "ExeArgoServiceCallBackVO":
        """设置主键"""
        self.key = key
        return self

    def with_inc_key(self, inc_key: str) -> "ExeArgoServiceCallBackVO":
        """设置增量键"""
        self.inc_key = inc_key
        return self

    def with_status(self, status: int) -> "ExeArgoServiceCallBackVO":
        """设置状态"""
        self.status = status
        return self

    def with_data(self, data: List[KeyValueItem]) -> "ExeArgoServiceCallBackVO":
        """设置键值对数据列表"""
        self.data = data
        return self

    def add_data_item(self, key: str, value: Any) -> "ExeArgoServiceCallBackVO":
        """添加一个键值对项"""
        self.data.append(KeyValueItem(key=key, value=value))
        return self

    def add_kv_item(self, item: KeyValueItem) -> "ExeArgoServiceCallBackVO":
        """添加一个键值对项"""
        self.data.append(item)
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将回调对象转换为字典

        返回:
        包含回调信息的字典
        """
        return {
            "key": self.key,
            "incKey": self.inc_key,
            "status": self.status,
            "data": [item.to_dict() for item in self.data],
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将回调对象转换为JSON字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExeArgoServiceCallBackVO":
        """
        从字典创建回调对象

        参数:
        data: 包含回调信息的字典

        返回:
        ExeArgoServiceCallBackVO 实例
        """
        callback = cls()

        if "key" in data:
            callback.key = data["key"]
        if "incKey" in data:
            callback.inc_key = data["incKey"]
        if "status" in data:
            callback.status = data["status"]
        if "data" in data:
            for item_data in data["data"]:
                if isinstance(item_data, dict):
                    callback.data.append(KeyValueItem.from_dict(item_data))
                else:
                    # 直接添加，假设已经是 KeyValueItem 对象
                    callback.data.append(item_data)

        return callback

    @classmethod
    def from_json(cls, json_str: str) -> "ExeArgoServiceCallBackVO":
        """
        从JSON字符串创建回调对象

        参数:
        json_str: JSON格式的字符串

        返回:
        ExeArgoServiceCallBackVO 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"ExeArgoServiceCallBackVO(key={self.key!r}, "
            f"status={self.get_status_text()}, "
            f"data_count={len(self.data)})"
        )
