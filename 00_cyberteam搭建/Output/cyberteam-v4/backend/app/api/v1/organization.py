"""组织配置 API v1 - 自定义组织架构管理。

核心功能：
- 组织结构 CRUD 操作（多租户支持）
- 讨论层/执行层团队/部门管理
- Agent ↔ 节点绑定管理
- 组织配置快照保存/加载

API 路由：
- GET  /api/v1/organization/structure/{company_id} - 获取组织结构
- PUT  /api/v1/organization/structure/{company_id} - 更新组织结构
- POST /api/v1/organization/nodes - 新增节点
- DELETE /api/v1/organization/nodes/{node_id} - 删除节点
- PUT  /api/v1/organization/nodes/{node_id}/agents - 绑定/解绑Agent
- POST /api/v1/organization/nodes/reorder - 调整节点顺序
- GET  /api/v1/organization/configs/{company_id} - 列出配置快照
- POST /api/v1/organization/configs/{company_id} - 保存配置快照
- DELETE /api/v1/organization/configs/{config_id} - 删除配置快照
"""

import threading
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.organization import (
    OrgNodeType,
    OrgNode,
    OrgStructure,
    OrgConfig,
    DEFAULT_STRUCTURE,
)

router = APIRouter(prefix="/organization", tags=["organization v1"])


# === In-Memory Store ===

class OrganizationStore:
    """内存存储 - 组织架构数据存储（线程安全）"""

    def __init__(self):
        self._lock = threading.RLock()
        # company_id -> OrgStructure
        self._structures: Dict[str, OrgStructure] = {"default": DEFAULT_STRUCTURE}
        # config_id -> OrgConfig
        self._configs: Dict[str, OrgConfig] = {}
        # node_id -> company_id (用于快速查找节点所属公司)
        self._node_index: Dict[str, str] = {}
        self._build_node_index()

    def _build_node_index(self):
        """构建节点索引"""
        for company_id, structure in self._structures.items():
            self._index_node(structure.ceo_node, company_id)
            for team in structure.discussion_teams:
                self._index_node(team, company_id)
                self._index_children(team.children, company_id)
            for dept in structure.execution_departments:
                self._index_node(dept, company_id)
                self._index_children(dept.children, company_id)

    def _index_node(self, node: OrgNode, company_id: str):
        """索引单个节点"""
        self._node_index[node.id] = company_id
        for child in node.children:
            self._index_node(child, company_id)

    def _index_children(self, children: List[OrgNode], company_id: str):
        """递归索引子节点"""
        for child in children:
            self._node_index[child.id] = company_id
            self._index_children(child.children, company_id)

    def get_structure(self, company_id: str) -> Optional[OrgStructure]:
        """获取组织结构"""
        with self._lock:
            return self._structures.get(company_id)

    def get_or_create_structure(self, company_id: str) -> OrgStructure:
        """获取或创建组织结构"""
        with self._lock:
            if company_id not in self._structures:
                # 创建默认结构（使用新的company_id）
                structure = OrgStructure(
                    company_id=company_id,
                    ceo_node=OrgNode(
                        id=f"ceo-{company_id}",
                        node_type=OrgNodeType.CEO,
                        name="CEO（总指挥）",
                        description="CyberTeam 最高决策层",
                        icon="👑",
                        color="#f59e0b",
                        is_expanded=True,
                    ),
                    discussion_teams=[
                        OrgNode(
                            id=f"discussion-{company_id}",
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
                            id=f"execution-{company_id}",
                            node_type=OrgNodeType.EXECUTION_LAYER,
                            name="执行层",
                            description="技术开发、设计实现、运营执行",
                            icon="⚙️",
                            color="#10b981",
                            is_expanded=True,
                        )
                    ],
                    updated_at=datetime.utcnow(),
                )
                self._structures[company_id] = structure
                self._index_node(structure.ceo_node, company_id)
                for team in structure.discussion_teams:
                    self._index_node(team, company_id)
                for dept in structure.execution_departments:
                    self._index_node(dept, company_id)
            return self._structures[company_id]

    def update_structure(self, company_id: str, structure: OrgStructure) -> OrgStructure:
        """更新组织结构"""
        with self._lock:
            structure.updated_at = datetime.utcnow()
            self._structures[company_id] = structure
            # 重建索引
            self._node_index.clear()
            self._build_node_index()
            return structure

    def get_node(self, node_id: str) -> Optional[tuple[OrgNode, OrgStructure, str]]:
        """获取节点及其所属结构"""
        with self._lock:
            company_id = self._node_index.get(node_id)
            if not company_id:
                return None
            structure = self._structures.get(company_id)
            if not structure:
                return None

            # 在各个位置查找节点
            node = self._find_node(structure.ceo_node, node_id)
            if node:
                return node, structure, "ceo_node"

            for i, team in enumerate(structure.discussion_teams):
                node = self._find_node(team, node_id)
                if node:
                    return node, structure, f"discussion_teams[{i}]"

            for i, dept in enumerate(structure.execution_departments):
                node = self._find_node(dept, node_id)
                if node:
                    return node, structure, f"execution_departments[{i}]"

            return None

    def _find_node(self, parent: OrgNode, node_id: str) -> Optional[OrgNode]:
        """递归查找节点"""
        if parent.id == node_id:
            return parent
        for child in parent.children:
            found = self._find_node(child, node_id)
            if found:
                return found
        return None

    def _find_parent(self, structure: OrgStructure, node_id: str) -> Optional[tuple[OrgNode, int]]:
        """查找节点的父节点和位置"""
        # 检查CEO
        if structure.ceo_node.id == node_id:
            return None, -1

        # 检查讨论层
        for i, team in enumerate(structure.discussion_teams):
            if team.id == node_id:
                return None, i
            for j, child in enumerate(team.children):
                if child.id == node_id:
                    return team, j

        # 检查执行层
        for i, dept in enumerate(structure.execution_departments):
            if dept.id == node_id:
                return None, i
            for j, child in enumerate(dept.children):
                if child.id == node_id:
                    return dept, j

        return None, -1

    def add_node(
        self,
        parent_id: str,
        node_type: OrgNodeType,
        name: str,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
        order: int = 0,
    ) -> Optional[OrgNode]:
        """新增节点"""
        with self._lock:
            company_id = self._node_index.get(parent_id)
            if not company_id:
                return None

            structure = self._structures.get(company_id)
            if not structure:
                return None

            new_node = OrgNode(
                id=str(uuid.uuid4()),
                node_type=node_type,
                name=name,
                parent_id=parent_id,
                icon=icon,
                color=color,
                description=description,
                order=order,
                is_expanded=True,
            )

            # 添加到父节点
            if structure.ceo_node.id == parent_id:
                # CEO下的直接子节点，应该添加到讨论层或执行层
                if node_type == OrgNodeType.TEAM or node_type == OrgNodeType.DISCUSSION_LAYER:
                    structure.discussion_teams.append(new_node)
                elif node_type == OrgNodeType.DEPARTMENT or node_type == OrgNodeType.EXECUTION_LAYER:
                    structure.execution_departments.append(new_node)
                else:
                    # 其他类型添加到讨论层
                    structure.discussion_teams.append(new_node)
            else:
                # 找到父节点并添加为子节点
                parent = None
                # 先在讨论层查找
                for team in structure.discussion_teams:
                    if team.id == parent_id:
                        parent = team
                        break
                    parent = self._find_node(team, parent_id)
                    if parent:
                        break
                # 如果没找到，在执行层查找
                if not parent:
                    for dept in structure.execution_departments:
                        if dept.id == parent_id:
                            parent = dept
                            break
                        parent = self._find_node(dept, parent_id)
                        if parent:
                            break

                if parent:
                    parent.children.append(new_node)
                else:
                    return None

            self._node_index[new_node.id] = company_id
            structure.updated_at = datetime.utcnow()
            return new_node

    def update_node(
        self,
        node_id: str,
        name: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
        is_expanded: Optional[bool] = None,
    ) -> Optional[OrgNode]:
        """更新节点"""
        with self._lock:
            result = self.get_node(node_id)
            if not result:
                return None
            node, structure, _ = result

            if name is not None:
                node.name = name
            if icon is not None:
                node.icon = icon
            if color is not None:
                node.color = color
            if description is not None:
                node.description = description
            if is_expanded is not None:
                node.is_expanded = is_expanded

            structure.updated_at = datetime.utcnow()
            return node

    def delete_node(self, node_id: str) -> bool:
        """删除节点"""
        with self._lock:
            company_id = self._node_index.get(node_id)
            if not company_id:
                return False

            structure = self._structures.get(company_id)
            if not structure:
                return False

            # 不能删除CEO
            if structure.ceo_node.id == node_id:
                return False

            # 从讨论层删除
            for i, team in enumerate(structure.discussion_teams):
                if team.id == node_id:
                    structure.discussion_teams.pop(i)
                    self._remove_from_index(node_id)
                    structure.updated_at = datetime.utcnow()
                    return True
                # 从子节点删除
                for j, child in enumerate(team.children):
                    if child.id == node_id:
                        team.children.pop(j)
                        self._remove_from_index(node_id)
                        structure.updated_at = datetime.utcnow()
                        return True

            # 从执行层删除
            for i, dept in enumerate(structure.execution_departments):
                if dept.id == node_id:
                    structure.execution_departments.pop(i)
                    self._remove_from_index(node_id)
                    structure.updated_at = datetime.utcnow()
                    return True
                # 从子节点删除
                for j, child in enumerate(dept.children):
                    if child.id == node_id:
                        dept.children.pop(j)
                        self._remove_from_index(node_id)
                        structure.updated_at = datetime.utcnow()
                        return True

            return False

    def _remove_from_index(self, node_id: str):
        """从索引中移除节点及其子节点"""
        if node_id in self._node_index:
            del self._node_index[node_id]

    def bind_agents(self, node_id: str, agent_ids: List[str]) -> Optional[OrgNode]:
        """绑定/解绑Agent到节点"""
        with self._lock:
            result = self.get_node(node_id)
            if not result:
                return None
            node, structure, _ = result

            node.agent_ids = agent_ids
            structure.updated_at = datetime.utcnow()
            return node

    def reorder_node(self, node_id: str, new_parent_id: str, new_order: int) -> bool:
        """调整节点顺序"""
        with self._lock:
            company_id = self._node_index.get(node_id)
            if not company_id:
                return False

            structure = self._structures.get(company_id)
            if not structure:
                return False

            # 不能移动CEO
            if node_id == structure.ceo_node.id:
                return False

            # 查找要移动的节点
            node = None
            # 在讨论层查找
            for team in structure.discussion_teams:
                if team.id == node_id:
                    node = team
                    break
                node = self._find_node(team, node_id)
                if node:
                    break
            # 在执行层查找
            if not node:
                for dept in structure.execution_departments:
                    if dept.id == node_id:
                        node = dept
                        break
                    node = self._find_node(dept, node_id)
                    if node:
                        break

            if not node:
                return False

            # 从原位置移除
            # 从讨论层移除
            for i, team in enumerate(structure.discussion_teams):
                if team.id == node_id:
                    structure.discussion_teams.pop(i)
                    break
                # 检查 children
                for j, child in enumerate(team.children):
                    if child.id == node_id:
                        team.children.pop(j)
                        break

            # 从执行层移除
            for i, dept in enumerate(structure.execution_departments):
                if dept.id == node_id:
                    structure.execution_departments.pop(i)
                    break
                # 检查 children
                for j, child in enumerate(dept.children):
                    if child.id == node_id:
                        dept.children.pop(j)
                        break

            # 添加到新位置
            node.parent_id = new_parent_id
            node.order = new_order

            if new_parent_id == structure.ceo_node.id:
                # 添加到CEO的直接子层
                if node.node_type in [OrgNodeType.TEAM, OrgNodeType.DISCUSSION_LAYER]:
                    structure.discussion_teams.append(node)
                else:
                    structure.execution_departments.append(node)
            else:
                # 添加到指定父节点
                parent = None
                # 在讨论层查找父节点
                for team in structure.discussion_teams:
                    if team.id == new_parent_id:
                        parent = team
                        break
                    parent = self._find_node(team, new_parent_id)
                    if parent:
                        break
                # 在执行层查找父节点
                if not parent:
                    for dept in structure.execution_departments:
                        if dept.id == new_parent_id:
                            parent = dept
                            break
                        parent = self._find_node(dept, new_parent_id)
                        if parent:
                            break

                if parent:
                    parent.children.append(node)
                else:
                    return False

            structure.updated_at = datetime.utcnow()
            return True

    # === 配置快照管理 ===

    def list_configs(self, company_id: str) -> List[OrgConfig]:
        """列出公司的所有配置快照"""
        with self._lock:
            return [c for c in self._configs.values() if c.company_id == company_id]

    def save_config(
        self, company_id: str, name: str, structure: OrgStructure, is_default: bool = False
    ) -> OrgConfig:
        """保存配置快照"""
        with self._lock:
            # 如果设为默认，先取消其他默认
            if is_default:
                for config in self._configs.values():
                    if config.company_id == company_id:
                        config.is_default = False

            config_id = str(uuid.uuid4())
            config = OrgConfig(
                id=config_id,
                company_id=company_id,
                name=name,
                structure=structure,
                is_default=is_default,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self._configs[config_id] = config
            return config

    def load_config(self, config_id: str) -> Optional[OrgStructure]:
        """加载配置快照"""
        with self._lock:
            config = self._configs.get(config_id)
            if not config:
                return None
            return config.structure

    def delete_config(self, config_id: str) -> bool:
        """删除配置快照"""
        with self._lock:
            if config_id in self._configs:
                del self._configs[config_id]
                return True
            return False


# 全局单例
_org_store = OrganizationStore()


def get_org_store() -> OrganizationStore:
    """获取组织存储实例"""
    return _org_store


def reset_org_store():
    """重置组织存储（用于测试）"""
    global _org_store
    _org_store = OrganizationStore()


# === Request/Response Models ===

class NodeCreate(BaseModel):
    """创建节点请求"""
    parent_id: str = Field(..., description="父节点ID")
    node_type: OrgNodeType = Field(..., description="节点类型")
    name: str = Field(..., min_length=1, max_length=200, description="节点名称")
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    order: int = 0


class NodeUpdate(BaseModel):
    """更新节点请求"""
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    is_expanded: Optional[bool] = None


class AgentBindRequest(BaseModel):
    """绑定Agent请求"""
    agent_ids: List[str] = Field(default_factory=list, description="要绑定的Agent ID列表")


class NodeReorderRequest(BaseModel):
    """调整节点顺序请求"""
    node_id: str = Field(..., description="节点ID")
    new_parent_id: str = Field(..., description="新父节点ID")
    new_order: int = Field(0, description="新顺序")


class ConfigCreate(BaseModel):
    """保存配置请求"""
    name: str = Field(..., min_length=1, max_length=200, description="配置名称")
    structure: OrgStructure = Field(..., description="组织结构")
    is_default: bool = Field(False, description="是否设为默认")


class StructureOut(BaseModel):
    """组织结构响应"""
    company_id: str
    ceo_node: OrgNode
    discussion_teams: List[OrgNode]
    execution_departments: List[OrgNode]
    updated_at: datetime


class NodeOut(BaseModel):
    """节点响应"""
    id: str
    node_type: OrgNodeType
    name: str
    parent_id: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    description: Optional[str]
    agent_ids: List[str]
    order: int
    is_expanded: bool
    children: List[OrgNode]


class ConfigOut(BaseModel):
    """配置快照响应"""
    id: str
    company_id: str
    name: str
    structure: OrgStructure
    is_default: bool
    created_at: datetime
    updated_at: datetime


# === Routes ===

@router.get("/structure/{company_id}", response_model=OrgStructure)
async def get_structure(company_id: str):
    """获取组织结构（完整树形结构）"""
    store = get_org_store()
    structure = store.get_or_create_structure(company_id)
    return structure


@router.put("/structure/{company_id}", response_model=OrgStructure)
async def update_structure(company_id: str, structure: OrgStructure):
    """更新组织结构"""
    store = get_org_store()
    # 验证 company_id 匹配
    if structure.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_id 不匹配",
        )
    return store.update_structure(company_id, structure)


@router.post("/nodes", response_model=OrgNode, status_code=status.HTTP_201_CREATED)
async def create_node(request: NodeCreate):
    """新增节点（团队/部门/分组）"""
    store = get_org_store()
    node = store.add_node(
        parent_id=request.parent_id,
        node_type=request.node_type,
        name=request.name,
        icon=request.icon,
        color=request.color,
        description=request.description,
        order=request.order,
    )
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"父节点 {request.parent_id} 不存在",
        )
    return node


@router.get("/nodes/{node_id}", response_model=OrgNode)
async def get_node(node_id: str):
    """获取节点详情"""
    store = get_org_store()
    result = store.get_node(node_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"节点 {node_id} 不存在",
        )
    node, _, _ = result
    return node


@router.put("/nodes/{node_id}", response_model=OrgNode)
async def update_node(node_id: str, request: NodeUpdate):
    """更新节点"""
    store = get_org_store()
    node = store.update_node(
        node_id,
        name=request.name,
        icon=request.icon,
        color=request.color,
        description=request.description,
        is_expanded=request.is_expanded,
    )
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"节点 {node_id} 不存在",
        )
    return node


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """删除节点"""
    store = get_org_store()
    # 不能删除CEO
    if node_id == "ceo-root":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除 CEO 节点",
        )
    success = store.delete_node(node_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"节点 {node_id} 不存在",
        )
    return {"status": "ok", "node_id": node_id}


@router.put("/nodes/{node_id}/agents", response_model=OrgNode)
async def bind_agents(node_id: str, request: AgentBindRequest):
    """绑定/解绑 Agent 到节点"""
    store = get_org_store()
    node = store.bind_agents(node_id, request.agent_ids)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"节点 {node_id} 不存在",
        )
    return node


@router.post("/nodes/reorder")
async def reorder_node(request: NodeReorderRequest):
    """调整节点顺序"""
    store = get_org_store()
    success = store.reorder_node(
        request.node_id,
        request.new_parent_id,
        request.new_order,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="节点调整失败",
        )
    return {"status": "ok"}


@router.get("/configs/{company_id}", response_model=List[ConfigOut])
async def list_configs(company_id: str):
    """列出所有已保存的组织配置"""
    store = get_org_store()
    configs = store.list_configs(company_id)
    return configs


@router.post("/configs/{company_id}", response_model=ConfigOut, status_code=status.HTTP_201_CREATED)
async def save_config(company_id: str, request: ConfigCreate):
    """保存当前配置为命名快照"""
    store = get_org_store()
    config = store.save_config(
        company_id=company_id,
        name=request.name,
        structure=request.structure,
        is_default=request.is_default,
    )
    return config


@router.get("/configs/{company_id}/{config_id}", response_model=OrgStructure)
async def load_config(company_id: str, config_id: str):
    """加载配置快照"""
    store = get_org_store()
    structure = store.load_config(config_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 {config_id} 不存在",
        )
    if structure.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置不属于指定公司",
        )
    return structure


@router.delete("/configs/{company_id}/{config_id}")
async def delete_config(company_id: str, config_id: str):
    """删除配置快照"""
    store = get_org_store()
    success = store.delete_config(config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 {config_id} 不存在",
        )
    return {"status": "ok", "config_id": config_id}
