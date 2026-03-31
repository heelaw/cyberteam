"""组织架构数据模型。

支持用户自定义组织架构（CEO固定顶层，下方分「讨论层」「执行层」两组，
每组可自由添加团队/Agent）。
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class OrgNodeType(str, Enum):
    """节点类型"""
    CEO = "ceo"  # 固定顶层，只有一个
    DISCUSSION_LAYER = "discussion_layer"  # 讨论层分组
    EXECUTION_LAYER = "execution_layer"  # 执行层分组
    TEAM = "team"  # 团队（讨论层）
    DEPARTMENT = "department"  # 部门（执行层）
    AGENT = "agent"  # Agent 节点


class OrgNode(BaseModel):
    """组织树节点"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="唯一标识")
    node_type: OrgNodeType = Field(..., description="节点类型")
    name: str = Field(..., description="名称")
    parent_id: Optional[str] = Field(None, description="父节点ID")
    icon: Optional[str] = Field(None, description="图标emoji")
    color: Optional[str] = Field(None, description="颜色")
    description: Optional[str] = Field(None, description="描述")
    agent_ids: List[str] = Field(default_factory=list, description="绑定到此节点的Agent")
    order: int = Field(0, description="排序顺序")
    is_expanded: bool = Field(True, description="是否展开")
    children: List['OrgNode'] = Field(default_factory=list, description="子节点")


class OrgStructure(BaseModel):
    """完整组织架构"""
    model_config = ConfigDict(from_attributes=True)

    company_id: str = Field(..., description="公司ID")
    ceo_node: OrgNode = Field(..., description="顶层CEO节点")
    discussion_teams: List[OrgNode] = Field(
        default_factory=list, description="讨论层团队列表"
    )
    execution_departments: List[OrgNode] = Field(
        default_factory=list, description="执行层部门列表"
    )
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


class OrgConfig(BaseModel):
    """组织配置（用于保存/加载）"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="配置ID")
    company_id: str = Field(..., description="公司ID")
    name: str = Field(..., description="配置名称")
    structure: OrgStructure = Field(..., description="组织结构")
    is_default: bool = Field(False, description="是否为默认配置")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


# === 默认组织结构 ===

DEFAULT_STRUCTURE = OrgStructure(
    company_id="default",
    ceo_node=OrgNode(
        id="ceo-root",
        node_type=OrgNodeType.CEO,
        name="CEO（总指挥）",
        description="CyberTeam 最高决策层",
        icon="👑",
        color="#f59e0b",
        is_expanded=True,
    ),
    discussion_teams=[
        OrgNode(
            id="discussion-default",
            node_type=OrgNodeType.DISCUSSION_LAYER,
            name="讨论层",
            description="战略分析、风险评估、方案讨论",
            icon="💭",
            color="#8b5cf6",
            is_expanded=True,
        )
    ],
    execution_departments=[
        OrgNode(
            id="execution-default",
            node_type=OrgNodeType.EXECUTION_LAYER,
            name="执行层",
            description="技术开发、设计实现、运营执行",
            icon="⚙️",
            color="#10b981",
            is_expanded=True,
        )
    ],
)
