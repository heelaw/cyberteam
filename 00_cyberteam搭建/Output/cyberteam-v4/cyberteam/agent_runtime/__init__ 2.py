"""CyberTeam Agents 模块。

整合所有 Agent，包括思维专家和专业 Agent。
包含增长BG的7个专家Agent。
"""

from cyberteam.agent_runtime.base import (
    BaseAgent,
    ThinkingExpert,
    SpecializedAgent,
    AgentMetadata
)
from cyberteam.agent_runtime.registry import AgentRegistry, get_registry
from cyberteam.agent_runtime.loader import (
    AgentLoader,
    get_loader,
    list_agents,
    get_agent,
    spawn_agent
)
from cyberteam.agent_runtime.thinking import (
    StrategyExpert,
    ProductExpert,
    TechnologyExpert,
    DesignExpert,
    OperationsExpert,
    FinanceExpert,
    MarketingExpert,
    HumanResourcesExpert,
    DataExpert,
    SecurityExpert,
    LegalExpert,
    CustomerExpert,
    QualityExpert,
)
from cyberteam.agent_runtime.specialized import (
    SwarmOrchestrator,
    DebateModerator,
    ScoreEvaluator,
    ReportWriter,
    # 增长BG Agents
    GrowthBGAgent,
    UserOpsAgent,
    ContentOpsAgent,
    ActivityOpsAgent,
    GrowthMarketingAgent,
    BrandMarketingAgent,
    PerformanceMarketingAgent,
)

__all__ = [
    # 基类
    "BaseAgent",
    "ThinkingExpert",
    "SpecializedAgent",
    "AgentMetadata",
    # 注册表和加载器
    "AgentRegistry",
    "get_registry",
    "AgentLoader",
    "get_loader",
    "list_agents",
    "get_agent",
    "spawn_agent",
    # 思维专家 (14个)
    "StrategyExpert",
    "ProductExpert",
    "TechnologyExpert",
    "DesignExpert",
    "OperationsExpert",
    "FinanceExpert",
    "MarketingExpert",
    "HumanResourcesExpert",
    "DataExpert",
    "SecurityExpert",
    "LegalExpert",
    "CustomerExpert",
    "QualityExpert",
    # 专业 Agent (4个)
    "SwarmOrchestrator",
    "DebateModerator",
    "ScoreEvaluator",
    "ReportWriter",
    # 增长BG Agents (7个)
    "GrowthBGAgent",
    "UserOpsAgent",
    "ContentOpsAgent",
    "ActivityOpsAgent",
    "GrowthMarketingAgent",
    "BrandMarketingAgent",
    "PerformanceMarketingAgent",
]

# 版本信息
__version__ = "4.0.0"
