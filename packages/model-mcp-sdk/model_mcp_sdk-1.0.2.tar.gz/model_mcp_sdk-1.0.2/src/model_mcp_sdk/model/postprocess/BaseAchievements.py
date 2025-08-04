from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from model_mcp_sdk.model.postprocess.BaseGeoStr import (
    BaseGeoStr,
)  # 确保正确导入 BaseGeoStr
import json


@dataclass
class BaseAchievements:
    """
    基础表模型
    对应 Java 的 com.yrihr.sdk.model.postprocess.BaseAchievements

    属性:
    id: str - 主键ID
    scheme_id: str - 计划ID
    model_core_id: str - 模型ID
    base_table: str - 基础表名
    letter_name: str - 字母名称
    node_scheme_model_id: str - 节点方案模型ID
    index_table: str - 指标表名
    status: int - 处理状态 (0:待处理, 1:处理中, 2:成功, 3:失败)
    create_time: datetime - 创建时间
    complete_time: datetime - 处理完成时间
    url_path: str - 地址信息
    index_code: str - 指标编码
    index_name: str - 指标名称
    instance_id: str - 实例ID
    begin_time: datetime - 开始时间
    end_time: datetime - 结束时间
    dt_unit: str - 时间单位
    dt: int - 时间值
    grid_table: str - 网格表名
    node_name: str - 节点名称
    args_name: str - 参数名称
    mode2d: str - 2D模式
    postprocess_type: str - 后处理类型
    args_type: int - 参数类型
    nc_file_path: str - NC文件路径
    geo_info: List[BaseGeoStr] - 地理信息列表
    """

    id: str = ""
    scheme_id: str = ""
    model_core_id: str = ""
    base_table: str = ""
    letter_name: str = ""
    node_scheme_model_id: str = ""
    index_table: str = ""
    status: int = 0
    create_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None
    url_path: str = ""
    index_code: str = ""
    index_name: str = ""
    instance_id: str = ""
    begin_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dt_unit: str = ""
    dt: int = 0
    grid_table: str = ""
    node_name: str = ""
    args_name: str = ""
    mode2d: str = ""
    postprocess_type: str = ""
    args_type: int = 0
    nc_file_path: str = ""
    geo_info: List[BaseGeoStr] = field(default_factory=list)

    # ----------------------------
    # 链式调用方法
    # ----------------------------
    def with_id(self, id: str) -> "BaseAchievements":
        self.id = id
        return self

    def with_scheme_id(self, scheme_id: str) -> "BaseAchievements":
        self.scheme_id = scheme_id
        return self

    def with_model_core_id(self, model_core_id: str) -> "BaseAchievements":
        self.model_core_id = model_core_id
        return self

    def with_base_table(self, base_table: str) -> "BaseAchievements":
        self.base_table = base_table
        return self

    def with_letter_name(self, letter_name: str) -> "BaseAchievements":
        self.letter_name = letter_name
        return self

    def with_node_scheme_model_id(
        self, node_scheme_model_id: str
    ) -> "BaseAchievements":
        self.node_scheme_model_id = node_scheme_model_id
        return self

    def with_index_table(self, index_table: str) -> "BaseAchievements":
        self.index_table = index_table
        return self

    def with_status(self, status: int) -> "BaseAchievements":
        self.status = status
        return self

    def with_create_time(self, create_time: datetime) -> "BaseAchievements":
        self.create_time = create_time
        return self

    def with_complete_time(self, complete_time: datetime) -> "BaseAchievements":
        self.complete_time = complete_time
        return self

    def with_url_path(self, url_path: str) -> "BaseAchievements":
        self.url_path = url_path
        return self

    def with_index_code(self, index_code: str) -> "BaseAchievements":
        self.index_code = index_code
        return self

    def with_index_name(self, index_name: str) -> "BaseAchievements":
        self.index_name = index_name
        return self

    def with_instance_id(self, instance_id: str) -> "BaseAchievements":
        self.instance_id = instance_id
        return self

    def with_begin_time(self, begin_time: datetime) -> "BaseAchievements":
        self.begin_time = begin_time
        return self

    def with_end_time(self, end_time: datetime) -> "BaseAchievements":
        self.end_time = end_time
        return self

    def with_dt_unit(self, dt_unit: str) -> "BaseAchievements":
        self.dt_unit = dt_unit
        return self

    def with_dt(self, dt: int) -> "BaseAchievements":
        self.dt = dt
        return self

    def with_grid_table(self, grid_table: str) -> "BaseAchievements":
        self.grid_table = grid_table
        return self

    def with_node_name(self, node_name: str) -> "BaseAchievements":
        self.node_name = node_name
        return self

    def with_args_name(self, args_name: str) -> "BaseAchievements":
        self.args_name = args_name
        return self

    def with_mode2d(self, mode2d: str) -> "BaseAchievements":
        self.mode2d = mode2d
        return self

    def with_postprocess_type(self, postprocess_type: str) -> "BaseAchievements":
        self.postprocess_type = postprocess_type
        return self

    def with_args_type(self, args_type: int) -> "BaseAchievements":
        self.args_type = args_type
        return self

    def with_nc_file_path(self, nc_file_path: str) -> "BaseAchievements":
        self.nc_file_path = nc_file_path
        return self

    def with_geo_info(self, geo_info: List[BaseGeoStr]) -> "BaseAchievements":
        self.geo_info = geo_info
        return self

    def add_geo_info(self, geo_item: BaseGeoStr) -> "BaseAchievements":
        self.geo_info.append(geo_item)
        return self

    # ----------------------------
    # 序列化/反序列化方法
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        将 BaseAchievements 对象转换为字典

        返回:
        包含基础表信息的字典

        日期时间字段会转换为 ISO 格式字符串
        """
        return {
            "id": self.id,
            "schemeId": self.scheme_id,
            "modelCoreId": self.model_core_id,
            "baseTable": self.base_table,
            "letterName": self.letter_name,
            "nodeSchemeModelId": self.node_scheme_model_id,
            "indexTable": self.index_table,
            "status": self.status,
            "createTime": self.create_time.isoformat() if self.create_time else None,
            "completeTime": (
                self.complete_time.isoformat() if self.complete_time else None
            ),
            "urlPath": self.url_path,
            "indexCode": self.index_code,
            "indexName": self.index_name,
            "instanceId": self.instance_id,
            "beginTime": self.begin_time.isoformat() if self.begin_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "dtUnit": self.dt_unit,
            "dt": self.dt,
            "gridTable": self.grid_table,
            "nodeName": self.node_name,
            "argsName": self.args_name,
            "mode2d": self.mode2d,
            "postprocessType": self.postprocess_type,
            "argsType": self.args_type,
            "ncFilePath": self.nc_file_path,
            "geoInfo": [
                geo.to_dict() for geo in self.geo_info
            ],  # 序列化每个地理信息对象
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        将 BaseAchievements 对象转换为 JSON 字符串

        参数:
        indent: JSON 格式化缩进（None 表示不格式化）

        返回:
        JSON 格式的字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseAchievements":
        """
        从字典创建 BaseAchievements 对象

        参数:
        data: 包含基础表信息的字典

        返回:
        BaseAchievements 实例

        日期时间字段会从 ISO 格式字符串转换
        """
        achievements = cls()

        # 设置基本字段
        if "id" in data:
            achievements.id = data["id"]
        if "schemeId" in data:
            achievements.scheme_id = data["schemeId"]
        if "modelCoreId" in data:
            achievements.model_core_id = data["modelCoreId"]
        if "baseTable" in data:
            achievements.base_table = data["baseTable"]
        if "letterName" in data:
            achievements.letter_name = data["letterName"]
        if "nodeSchemeModelId" in data:
            achievements.node_scheme_model_id = data["nodeSchemeModelId"]
        if "indexTable" in data:
            achievements.index_table = data["indexTable"]
        if "status" in data:
            achievements.status = data["status"]
        if "urlPath" in data:
            achievements.url_path = data["urlPath"]
        if "indexCode" in data:
            achievements.index_code = data["indexCode"]
        if "indexName" in data:
            achievements.index_name = data["indexName"]
        if "instanceId" in data:
            achievements.instance_id = data["instanceId"]
        if "dtUnit" in data:
            achievements.dt_unit = data["dtUnit"]
        if "dt" in data:
            achievements.dt = data["dt"]
        if "gridTable" in data:
            achievements.grid_table = data["gridTable"]
        if "nodeName" in data:
            achievements.node_name = data["nodeName"]
        if "argsName" in data:
            achievements.args_name = data["argsName"]
        if "mode2d" in data:
            achievements.mode2d = data["mode2d"]
        if "postprocessType" in data:
            achievements.postprocess_type = data["postprocessType"]
        if "argsType" in data:
            achievements.args_type = data["argsType"]
        if "ncFilePath" in data:
            achievements.nc_file_path = data["ncFilePath"]
        if "geoInfo" in data:
            # 反序列化每个地理信息对象
            achievements.geo_info = [
                BaseGeoStr.from_dict(geo_data) for geo_data in data["geoInfo"]
            ]

        # 处理日期时间字段
        if "createTime" in data and data["createTime"]:
            achievements.create_time = datetime.fromisoformat(data["createTime"])
        if "completeTime" in data and data["completeTime"]:
            achievements.complete_time = datetime.fromisoformat(data["completeTime"])
        if "beginTime" in data and data["beginTime"]:
            achievements.begin_time = datetime.fromisoformat(data["beginTime"])
        if "endTime" in data and data["endTime"]:
            achievements.end_time = datetime.fromisoformat(data["endTime"])

        return achievements

    @classmethod
    def from_json(cls, json_str: str) -> "BaseAchievements":
        """
        从 JSON 字符串创建 BaseAchievements 对象

        参数:
        json_str: JSON 格式的字符串

        返回:
        BaseAchievements 实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """简明的对象表示，用于调试"""
        return f"BaseAchievements(id={self.id!r}, scheme_id={self.scheme_id!r}, "
