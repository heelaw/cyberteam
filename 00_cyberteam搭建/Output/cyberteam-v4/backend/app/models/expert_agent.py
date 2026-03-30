"""数字员工（专家 Agent）数据模型"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExpertAgentProfile(BaseModel):
    """专家 Agent Profile"""
    agent_id: str = Field(..., description="唯一标识")
    name: str = Field(..., description="名称，如'法务专家'")
    department: str = Field(..., description="所属部门，如'运营部'")
    description: str = Field(default="", description="详细描述")
    capabilities: list[str] = Field(default_factory=list, description="能力列表")
    keywords: list[str] = Field(default_factory=list, description="搜索关键词")
    avatar: str = Field(default="🤖", description="头像 emoji")
    rating: float = Field(default=5.0, ge=0, le=5, description="用户评分")
    call_count: int = Field(default=0, ge=0, description="被调用次数")
    avg_response_time_ms: float = Field(default=0, ge=0, description="平均响应时间")
    status: str = Field(default="online", description="online/offline/busy")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ExpertAgentRegistry:
    """专家 Agent 注册表"""
    _instance: Optional['ExpertAgentRegistry'] = None

    def __init__(self):
        self._agents: dict[str, ExpertAgentProfile] = {}

    @classmethod
    def get_instance(cls) -> 'ExpertAgentRegistry':
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._seed_defaults()  # 预置默认专家
        return cls._instance

    def _seed_defaults(self):
        """预置 CyberTeam 默认专家"""
        defaults = [
            ExpertAgentProfile(
                agent_id="ops-expert-01",
                name="运营总监",
                department="运营部",
                description="擅长活动策划、用户增长、数据分析",
                capabilities=["活动策划", "用户增长", "数据分析", "A/B测试"],
                keywords=["运营", "增长", "活动", "策划", "用户"],
            ),
            ExpertAgentProfile(
                agent_id="design-expert-01",
                name="设计总监",
                department="设计部",
                description="擅长品牌设计、UI/UX、视觉系统",
                capabilities=["品牌设计", "UI设计", "UX研究", "视觉系统"],
                keywords=["设计", "品牌", "UI", "UX", "视觉"],
            ),
            ExpertAgentProfile(
                agent_id="eng-expert-01",
                name="技术总监",
                department="开发部",
                description="擅长架构设计、技术选型、代码审查",
                capabilities=["架构设计", "技术选型", "代码审查", "性能优化"],
                keywords=["技术", "架构", "开发", "代码", "性能"],
            ),
            ExpertAgentProfile(
                agent_id="marketing-expert-01",
                name="营销总监",
                department="市场部",
                description="擅长全渠道营销、内容策略、KOL合作",
                capabilities=["小红书运营", "抖音运营", "内容营销", "KOL合作"],
                keywords=["营销", "小红书", "抖音", "内容", "KOL"],
            ),
        ]
        for agent in defaults:
            self._agents[agent.agent_id] = agent

    def register(self, profile: ExpertAgentProfile) -> str:
        """注册新专家"""
        profile.created_at = datetime.utcnow()
        profile.updated_at = datetime.utcnow()
        self._agents[profile.agent_id] = profile
        return profile.agent_id

    def get(self, agent_id: str) -> Optional[ExpertAgentProfile]:
        return self._agents.get(agent_id)

    def discover(self, query: str, department: Optional[str] = None) -> list[ExpertAgentProfile]:
        """语义搜索专家（关键词匹配）"""
        query_lower = query.lower()
        results = []

        for agent in self._agents.values():
            if department and agent.department != department:
                continue
            # 匹配关键词
            score = 0
            for kw in agent.keywords:
                if kw.lower() in query_lower:
                    score += 2
            for cap in agent.capabilities:
                if cap.lower() in query_lower:
                    score += 1
            if query_lower in agent.name.lower() or query_lower in agent.description.lower():
                score += 3
            if score > 0:
                results.append((score, agent))

        results.sort(key=lambda x: (-x[0], -x[1].rating))
        return [r for _, r in results]

    def get_market(self, department: Optional[str] = None) -> list[ExpertAgentProfile]:
        """获取数字员工市场"""
        agents = list(self._agents.values())
        if department:
            agents = [a for a in agents if a.department == department]
        return sorted(agents, key=lambda a: -a.call_count)

    def record_call(self, agent_id: str, response_time_ms: float) -> None:
        """记录调用（更新统计数据）"""
        agent = self._agents.get(agent_id)
        if not agent:
            return
        agent.call_count += 1
        # 滑动平均更新响应时间
        agent.avg_response_time_ms = (
            (agent.avg_response_time_ms * (agent.call_count - 1) + response_time_ms)
            / agent.call_count
        )
        agent.updated_at = datetime.utcnow()

    def unregister(self, agent_id: str) -> bool:
        """注销专家"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False