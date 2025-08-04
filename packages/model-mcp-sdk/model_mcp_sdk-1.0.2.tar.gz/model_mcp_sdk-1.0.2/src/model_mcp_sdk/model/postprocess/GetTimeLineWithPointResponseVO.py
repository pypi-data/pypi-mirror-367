from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class GetTimeLineWithPointResponseVO:
    """
    获取时间线数据响应模型（带坐标点）
    对应 Java 的 com.yrihr.sdk.model.postprocess.GetTimeLineWithPointResponseVO

    属性:
    begin_time: datetime - 开始时间
    end_time: datetime - 结束时间
    dt: int - 时间步长
    dt_unit: str - 时间单位
    values: List[float] - 时间序列值数组
    """

    begin_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dt: int = 0
    dt_unit: str = ""
    values: List[float] = field(default_factory=list)

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_begin_time(self, begin_time: datetime) -> "GetTimeLineWithPointResponseVO":
        """设置开始时间"""
        self.begin_time = begin_time
        return self

    def with_end_time(self, end_time: datetime) -> "GetTimeLineWithPointResponseVO":
        """设置结束时间"""
        self.end_time = end_time
        return self

    def with_dt(self, dt: int) -> "GetTimeLineWithPointResponseVO":
        """设置时间步长"""
        self.dt = dt
        return self

    def with_dt_unit(self, dt_unit: str) -> "GetTimeLineWithPointResponseVO":
        """设置时间单位"""
        self.dt_unit = dt_unit
        return self

    def with_values(self, values: List[float]) -> "GetTimeLineWithPointResponseVO":
        """设置时间序列值数组"""
        self.values = values
        return self

    def add_value(self, value: float) -> "GetTimeLineWithPointResponseVO":
        """添加一个时间序列值"""
        self.values.append(value)
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将响应对象转换为字典

        返回:
        包含响应数据的字典

        日期时间字段会转换为 ISO 格式字符串
        """
        return {
            "beginTime": self.begin_time.isoformat() if self.begin_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "dt": self.dt,
            "dtUnit": self.dt_unit,
            "values": self.values,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将响应对象转换为JSON字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetTimeLineWithPointResponseVO":
        """
        从字典创建响应对象

        参数:
        data: 包含响应数据的字典

        返回:
        GetTimeLineWithPointResponseVO 实例

        日期时间字段会从 ISO 格式字符串转换
        """
        response = cls()

        if "beginTime" in data and data["beginTime"]:
            response.begin_time = datetime.fromisoformat(data["beginTime"])
        if "endTime" in data and data["endTime"]:
            response.end_time = datetime.fromisoformat(data["endTime"])
        if "dt" in data:
            response.dt = data["dt"]
        if "dtUnit" in data:
            response.dt_unit = data["dtUnit"]
        if "values" in data:
            response.values = [float(val) for val in data["values"]]

        return response

    @classmethod
    def from_json(cls, json_str: str) -> "GetTimeLineWithPointResponseVO":
        """
        从JSON字符串创建响应对象

        参数:
        json_str: JSON格式的字符串

        返回:
        GetTimeLineWithPointResponseVO 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return (
            f"GetTimeLineWithPointResponseVO(begin_time={self.begin_time}, "
            f"end_time={self.end_time}, values_count={len(self.values)})"
        )
