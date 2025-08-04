from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from model_mcp_sdk.model.nc.NcFileVO import NcFileVO


# ----------------------------
# WriteNcFileRspVO 模型
# ----------------------------
@dataclass
class WriteNcFileRspVO:
    """
    写入 NC 文件响应模型
    对应 Java 的 com.yrihr.sdk.model.service.WriteNcFileRspVO

    属性:
    file_path: str - 文件路径
    file_list: List[NcFileVO] - NC 文件列表
    """

    file_path: str = ""
    file_list: List["NcFileVO"] = field(default_factory=list)

    # 链式调用方法
    def with_file_path(self, file_path: str) -> "WriteNcFileRspVO":
        self.file_path = file_path
        return self

    def with_file_list(self, file_list: List["NcFileVO"]) -> "WriteNcFileRspVO":
        self.file_list = file_list
        return self

    def add_file(self, file: "NcFileVO") -> "WriteNcFileRspVO":
        self.file_list.append(file)
        return self

    # 序列化/反序列化方法
    def to_dict(self) -> Dict[str, Any]:
        return {
            "filePath": self.file_path,
            "fileList": [file.to_dict() for file in self.file_list],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WriteNcFileRspVO":
        rsp = cls()
        if "filePath" in data:
            rsp.file_path = data["filePath"]
        if "fileList" in data:
            for file_data in data["fileList"]:
                if isinstance(file_data, dict):
                    rsp.file_list.append(NcFileVO.from_dict(file_data))
                else:
                    rsp.file_list.append(file_data)
        return rsp

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "WriteNcFileRspVO":
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return (
            f"WriteNcFileRspVO(file_path={self.file_path!r}, "
            f"file_count={len(self.file_list)})"
        )
