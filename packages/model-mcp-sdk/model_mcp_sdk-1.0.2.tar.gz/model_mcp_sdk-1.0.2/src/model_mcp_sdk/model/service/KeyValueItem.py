from dataclasses import dataclass
from typing import Dict, Any
import json


# ----------------------------
# KeyValueItem 模型
# ----------------------------
@dataclass
class KeyValueItem:
    """
    键值对项模型
    对应 Java 的 com.yrihr.sdk.model.service.KeyValueItem

    属性:
    key: str - 键
    key_describe: str - 键描述
    value: Any - 值
    """

    key: str = ""
    key_describe: str = ""
    value: Any = None

    # 链式调用方法
    def with_key(self, key: str) -> "KeyValueItem":
        self.key = key
        return self

    def with_key_describe(self, key_describe: str) -> "KeyValueItem":
        self.key_describe = key_describe
        return self

    def with_value(self, value: Any) -> "KeyValueItem":
        self.value = value
        return self

    # 序列化/反序列化方法
    def to_dict(self) -> Dict[str, Any]:
        return {"key": self.key, "keyDescribe": self.key_describe, "value": self.value}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyValueItem":
        item = cls()
        if "key" in data:
            item.key = data["key"]
        if "keyDescribe" in data:
            item.key_describe = data["keyDescribe"]
        if "value" in data:
            item.value = data["value"]
        return item

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "KeyValueItem":
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return f"KeyValueItem(key={self.key!r}, value={self.value!r})"
