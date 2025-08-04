from dataclasses import dataclass
from typing import Dict, Any
import json


# ----------------------------
# ExeArgoServiceWorkflowResVO 模型
# ----------------------------
@dataclass
class ExeArgoServiceWorkflowResVO:
    """
    Argo 服务工作流响应模型
    对应 Java 的 com.yrihr.sdk.model.service.ExeArgoServiceWorkflowResVO

    属性:
    key: str - 主键
    inc_key: str - 增量键
    instance_id: str - 实例ID
    """

    key: str = ""
    inc_key: str = ""
    instance_id: str = ""

    def __init__(self, key: str = "", inc_key: str = "", instance_id: str = ""):
        self.key = key
        self.inc_key = inc_key
        self.instance_id = instance_id

    # 链式调用方法
    def with_key(self, key: str) -> "ExeArgoServiceWorkflowResVO":
        self.key = key
        return self

    def with_inc_key(self, inc_key: str) -> "ExeArgoServiceWorkflowResVO":
        self.inc_key = inc_key
        return self

    def with_instance_id(self, instance_id: str) -> "ExeArgoServiceWorkflowResVO":
        self.instance_id = instance_id
        return self

    # 序列化/反序列化方法
    def to_dict(self) -> Dict[str, Any]:
        return {"key": self.key, "incKey": self.inc_key, "instanceId": self.instance_id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExeArgoServiceWorkflowResVO":
        res = cls()
        if "key" in data:
            res.key = data["key"]
        if "incKey" in data:
            res.inc_key = data["incKey"]
        if "instanceId" in data:
            res.instance_id = data["instanceId"]
        return res

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "ExeArgoServiceWorkflowResVO":
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return (
            f"ExeArgoServiceWorkflowResVO(key={self.key!r}, "
            f"inc_key={self.inc_key!r}, "
            f"instance_id={self.instance_id!r})"
        )
