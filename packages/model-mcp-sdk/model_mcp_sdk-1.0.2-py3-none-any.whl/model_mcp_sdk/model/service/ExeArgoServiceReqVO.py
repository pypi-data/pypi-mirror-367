from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from model_mcp_sdk.model.service.KeyValueItem import KeyValueItem


# ----------------------------
# ExeArgoServiceReqVO 模型
# ----------------------------
@dataclass
class ExeArgoServiceReqVO:
    """
    Argo 服务执行请求模型
    对应 Java 的 com.yrihr.sdk.model.service.ExeArgoServiceReqVO

    属性:
    call_back_url: str - 回调URL
    key: str - 主键
    data: List[KeyValueItem] - 键值对数据列表
    """

    call_back_url: str = ""
    key: str = ""
    data: List[KeyValueItem] = field(default_factory=list)

    # 链式调用方法
    def with_call_back_url(self, call_back_url: str) -> "ExeArgoServiceReqVO":
        self.call_back_url = call_back_url
        return self

    def with_key(self, key: str) -> "ExeArgoServiceReqVO":
        self.key = key
        return self

    def with_data(self, data: List[KeyValueItem]) -> "ExeArgoServiceReqVO":
        self.data = data
        return self

    def add_data_item(
        self, key: str, value: Any, key_describe: str = ""
    ) -> "ExeArgoServiceReqVO":
        self.data.append(KeyValueItem(key=key, value=value, key_describe=key_describe))
        return self

    def add_kv_item(self, item: KeyValueItem) -> "ExeArgoServiceReqVO":
        self.data.append(item)
        return self

    # 序列化/反序列化方法
    def to_dict(self) -> Dict[str, Any]:
        return {
            "callBackUrl": self.call_back_url,
            "key": self.key,
            "data": [item.to_dict() for item in self.data],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExeArgoServiceReqVO":
        req = cls()
        if "callBackUrl" in data:
            req.call_back_url = data["callBackUrl"]
        if "key" in data:
            req.key = data["key"]
        if "data" in data:
            for item_data in data["data"]:
                if isinstance(item_data, dict):
                    req.data.append(KeyValueItem.from_dict(item_data))
                else:
                    req.data.append(item_data)
        return req

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "ExeArgoServiceReqVO":
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return (
            f"ExeArgoServiceReqVO(key={self.key!r}, "
            f"callback_url={self.call_back_url!r}, "
            f"data_count={len(self.data)})"
        )
