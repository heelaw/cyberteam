#!/usr/bin/env python3
"""
CyberTeam V4 - CEO 路由引擎 (L1)

职责：
1. 需求分拣 (简单咨询 vs 正式任务)
2. 意图识别 (数据分析/内容运营/技术研发/安全合规)
3. 复杂度评估 (高/中/低)
4. 路由决策 (L2/L3A/L3B/L3C)
5. Swarm 智能编排 (复杂任务自动组建团队)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
import re
import uuid
from datetime import datetime

# Swarm Intelligence 集成
from pathlib import Path
import sys

# 添加项目根目录到 path
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from integration.cyberteam_adapter import CyberTeamAdapter
    from swarm_orchestrator import SwarmOrchestrator, SwarmStatus
    SWARM_AVAILABLE = True
except ImportError:
    SWARM_AVAILABLE = False
    CyberTeamAdapter = None
    SwarmOrchestrator = None

# 思维注入系统
try:
    from engine.thinking import ThinkingInjector, InjectionContext
    THINKING_AVAILABLE = True
except ImportError:
    THINKING_AVAILABLE = False
    ThinkingInjector = None
    InjectionContext = None


class Complexity(Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class Intent(Enum):
    DATA_ANALYSIS = "数据分析"
    CONTENT_OPS = "内容运营"
    TECH_ENGINEERING = "技术研发"
    SECURITY = "安全合规"
    STRATEGY = "战略规划"
    HR = "人力资源"
    OPERATIONS = "运营支持"
    UNKNOWN = "未知"


class RoutingTarget(Enum):
    L2 = "L2"           # PM + Strategy 协调层
    L3A = "L3A"         # CyberTeam 部门
    L3B = "L3B"         # Gstack Skills
    L3C = "L3C"         # 独立 Agents
    SWARM = "SWARM"     # Swarm 群体智能 (新!)


@dataclass
class RoutingResult:
    """路由结果"""
    decision: str           # 路由决策
    target: str              # "L2"|"L3A"|"L3B"|"L3C"|"SWARM"
    target_name: str         # "PM"|"数据分析部"|"/review"|"gsd-executor"|"SwarmTeam"
    intent: str              # 识别的意图
    complexity: str          # "高"|"中"|"低"
    reason: str              # 路由理由
    swarm_id: Optional[str] = None  # Swarm ID (如果是 Swarm 路由)
    agents: Optional[List[str]] = None  # 子 Agent 列表
    # 思维注入字段
    thinking_models: Optional[List[str]] = None  # 注入的思维模型列表
    thinking_prompt: Optional[str] = None  # 注入的思维 prompt
    thinking_confidence: Optional[float] = None  # 思维注入置信度


class CEORouter:
    """CEO 任务路由引擎"""

    # 意图关键词映射
    INTENT_KEYWORDS = {
        Intent.DATA_ANALYSIS: [
            "增长", "数据", "分析", "财务", "投资", "ROI", "转化率",
            "GMV", "DAU", "MAU", "留存", "北极星指标", "LTV"
        ],
        Intent.CONTENT_OPS: [
            "内容", "文案", "创作", "文章", "发布", "公众号", "小红书",
            "抖音", "短视频", "脚本", "营销", "推广"
        ],
        Intent.TECH_ENGINEERING: [
            "开发", "代码", "功能", "实现", "修复", "Bug", "架构",
            "测试", "部署", "API", "系统"
        ],
        Intent.SECURITY: [
            "安全", "审计", "合规", "隐私", "漏洞", "渗透"
        ],
        Intent.STRATEGY: [
            "战略", "规划", "方案", "决策", "竞争", "市场", "进入"
        ],
        Intent.HR: [
            "招聘", "绩效", "团队", "人力", "OKR"
        ],
        Intent.OPERATIONS: [
            "运营", "活动", "用户", "社群", "增长黑客"
        ]
    }

    # 简单咨询关键词
    GREETING_KEYWORDS = [
        "你好", "您好", "嗨", "hi", "hello", "在吗", "在不在",
        "谢谢", "感谢", "辛苦了", "好的", "收到", "明白"
    ]

    def __init__(self):
        self.router_config = self._load_router_config()
        # Swarm 集成
        self._swarm_adapter = None
        self._active_swarms: Dict[str, Any] = {}
        # 思维注入系统
        self._thinking_injector = None

    @property
    def swarm_adapter(self) -> Optional[CyberTeamAdapter]:
        """懒加载 Swarm 适配器"""
        if CyberTeamAdapter is None:
            return None
        if self._swarm_adapter is None:
            self._swarm_adapter = CyberTeamAdapter(repo_root=Path(__file__).parent.parent)
        return self._swarm_adapter

    @property
    def thinking_injector(self) -> Optional[ThinkingInjector]:
        """懒加载思维注入器"""
        if not THINKING_AVAILABLE or ThinkingInjector is None:
            return None
        if self._thinking_injector is None:
            self._thinking_injector = ThinkingInjector()
            self._thinking_injector.load_models()
        return self._thinking_injector

    def _load_router_config(self) -> dict:
        """加载路由配置"""
        # TODO: 从 config/routing.yaml 加载
        return {
            "complexity_threshold": {
                "high": 100,  # 字符数 > 100 = 高复杂度
                "multi_domain": True  # 涉及多领域
            },
            "timeout": 300  # 默认超时秒数
        }

    def is_simple_consultation(self, user_input: str) -> bool:
        """需求分拣：判断是否为简单咨询"""
        cleaned = user_input.strip().lower()

        # 直接匹配
        for keyword in self.GREETING_KEYWORDS:
            if keyword in cleaned:
                return True

        # 纯符号/纯表情
        if len(re.sub(r'[\w\u4e00-\u9fff]', '', cleaned)) == len(cleaned):
            return True

        return False

    def recognize_intent(self, user_input: str) -> Intent:
        """意图识别"""
        user_input_lower = user_input.lower()

        # 统计关键词匹配
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in user_input_lower)
            if score > 0:
                intent_scores[intent] = score

        if not intent_scores:
            return Intent.UNKNOWN

        # 返回得分最高的意图
        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def evaluate_complexity(self, user_input: str, intent: Intent) -> Complexity:
        """复杂度评估"""
        # 因素1: 任务描述长度
        length_score = Complexity.LOW
        if len(user_input) > self.router_config["complexity_threshold"]["high"]:
            length_score = Complexity.HIGH
        elif len(user_input) > 50:
            length_score = Complexity.MEDIUM

        # 因素2: 是否涉及多领域
        domain_score = Complexity.LOW
        if len(user_input.split()) > 5 and any(
            kw in user_input.lower()
            for kw in ["并且", "以及", "还有", "和", "and", ","]
        ):
            domain_score = Complexity.HIGH

        # 因素3: 特殊任务类型
        special_score = Complexity.LOW
        if intent in [Intent.DATA_ANALYSIS, Intent.STRATEGY]:
            special_score = Complexity.MEDIUM

        # 综合评估
        scores = [length_score, domain_score, special_score]
        if scores.count(Complexity.HIGH) >= 2:
            return Complexity.HIGH
        elif scores.count(Complexity.MEDIUM) >= 2:
            return Complexity.MEDIUM
        else:
            return Complexity.LOW

    def route(self, user_input: str) -> RoutingResult:
        """执行路由决策"""

        # Step 1: 需求分拣
        if self.is_simple_consultation(user_input):
            return RoutingResult(
                decision="直接回复",
                target="NONE",
                target_name="N/A",
                intent="简单咨询",
                complexity="低",
                reason="简单问候/感谢"
            )

        # Step 2: 意图识别
        intent = self.recognize_intent(user_input)

        # Step 3: 复杂度评估
        complexity = self.evaluate_complexity(user_input, intent)

        # Step 4: 路由决策
        result = self._make_routing_decision(user_input, intent, complexity)

        # Step 5: 思维注入（对于非简单咨询，注入思维模型）
        if result.target != "NONE":
            thinking_result = self._inject_thinking(user_input, intent.value, complexity.value, result.target)
            if thinking_result:
                result.thinking_models = thinking_result.models_used
                result.thinking_prompt = thinking_result.injected_prompt
                result.thinking_confidence = thinking_result.confidence

        return result

    def _inject_thinking(self, task: str, intent: str, complexity: str, target: str) -> Optional[Any]:
        """注入思维模型到任务"""
        if not self.thinking_injector:
            return None

        # 根据目标选择 Agent 角色
        role_map = {
            "L2": "项目经理",
            "L3A": "部门专家",
            "L3B": "技能专家",
            "L3C": "执行专家",
            "SWARM": "Swarm协调者",
        }
        agent_role = role_map.get(target, "通用专家")

        try:
            context = InjectionContext(
                agent_name=f"{agent_role}",
                agent_role=agent_role,
                task=task
            )
            return self.thinking_injector.inject_auto(context)
        except Exception as e:
            print(f"[CEO] 思维注入失败: {e}")
            return None

    def should_use_swarm(self, user_input: str, intent: Intent, complexity: Complexity) -> bool:
        """判断是否应该使用 Swarm 群体智能"""
        # 不需要 Swarm 的情况
        if not SWARM_AVAILABLE:
            return False

        # Swarm 关键词
        swarm_keywords = [
            "团队", "团队协作", "多个专家", "分工", "并行",
            "组建团队", "自主完成", "群体智能", "swarm"
        ]
        has_swarm_keyword = any(kw in user_input.lower() for kw in swarm_keywords)

        # 高复杂度任务
        is_high_complexity = complexity == Complexity.HIGH

        # 多领域任务 (需要多个专家)
        multi_domain = len(user_input.split()) > 5 and any(
            kw in user_input.lower()
            for kw in ["并且", "以及", "还有", "和", "and", ","]
        )

        # 战略/规划类任务 (需要多轮迭代)
        is_strategy_task = intent in [Intent.STRATEGY, Intent.DATA_ANALYSIS]

        return has_swarm_keyword or is_high_complexity or multi_domain or is_strategy_task

    def _make_routing_decision(
        self,
        user_input: str,
        intent: Intent,
        complexity: Complexity
    ) -> RoutingResult:
        """路由决策逻辑"""

        # 规则1: 技术类任务 + 纯技术实现 → L3B (Gstack)
        if intent == Intent.TECH_ENGINEERING:
            if any(kw in user_input.lower() for kw in ["审查", "review", "测试"]):
                return RoutingResult(
                    decision="技术审查",
                    target=RoutingTarget.L3B.value,
                    target_name="/review",
                    intent=intent.value,
                    complexity=complexity.value,
                    reason="代码审查任务"
                )
            return RoutingResult(
                decision="技术研发",
                target=RoutingTarget.L3B.value,
                target_name="/codex",
                intent=intent.value,
                complexity=complexity.value,
                reason="技术开发任务"
            )

        # 规则2: 通用功能开发 → L3C (独立 Agents)
        if any(kw in user_input.lower() for kw in ["实现", "开发", "构建", "create"]):
            if complexity == Complexity.LOW:
                return RoutingResult(
                    decision="通用开发",
                    target=RoutingTarget.L3C.value,
                    target_name="gsd-executor",
                    intent=intent.value,
                    complexity=complexity.value,
                    reason="通用功能开发"
                )

        # 规则2.5: Swarm 群体智能 (高复杂度/多领域/明确要求)
        if self.should_use_swarm(user_input, intent, complexity):
            swarm_id = f"swarm-{uuid.uuid4().hex[:8]}"
            agents = ["researcher-1", "researcher-2", "executor-1", "executor-2", "qa"]
            self._active_swarms[swarm_id] = {
                "goal": user_input,
                "intent": intent.value,
                "created_at": datetime.utcnow().isoformat()
            }
            return RoutingResult(
                decision="Swarm 群体智能",
                target=RoutingTarget.SWARM.value,
                target_name="SwarmTeam",
                intent=intent.value,
                complexity=complexity.value,
                reason="高复杂度任务，自动组建 Swarm 团队",
                swarm_id=swarm_id,
                agents=agents
            )

        # 规则3: 复杂任务 → L2 (PM + Strategy)
        if complexity == Complexity.HIGH:
            return RoutingResult(
                decision="复杂任务",
                target=RoutingTarget.L2.value,
                target_name="PM",
                intent=intent.value,
                complexity=complexity.value,
                reason="高复杂度任务需要协调"
            )

        # 规则4: 中等复杂度 + 非技术 → L2 (简单协调)
        if complexity == Complexity.MEDIUM:
            return RoutingResult(
                decision="中等任务",
                target=RoutingTarget.L2.value,
                target_name="PM",
                intent=intent.value,
                complexity=complexity.value,
                reason="中等复杂度任务"
            )

        # 规则5: 默认 → L3A (CyberTeam 部门)
        dept_map = {
            Intent.DATA_ANALYSIS: "数据分析部",
            Intent.CONTENT_OPS: "内容运营部",
            Intent.TECH_ENGINEERING: "技术研发部",
            Intent.SECURITY: "安全合规部",
            Intent.STRATEGY: "战略规划部",
            Intent.HR: "人力资源部",
            Intent.OPERATIONS: "运营支持部"
        }

        return RoutingResult(
            decision="部门执行",
            target=RoutingTarget.L3A.value,
            target_name=dept_map.get(intent, "战略规划部"),
            intent=intent.value,
            complexity=complexity.value,
            reason="直接路由到部门"
        )

    # ========== Swarm 执行方法 ==========

    def create_swarm_team(self, goal: str, intent: str) -> Dict[str, Any]:
        """
        创建 Swarm 团队

        Args:
            goal: 团队目标
            intent: 意图类型

        Returns:
            Swarm 创建结果
        """
        if not SWARM_AVAILABLE or self.swarm_adapter is None:
            return {
                "success": False,
                "error": "Swarm 模块不可用"
            }

        # 生成团队名称
        team_name = f"ceo-{intent[:8]}-{uuid.uuid4().hex[:6]}"

        try:
            # 创建 Swarm
            swarm = self.swarm_adapter.create_swarm(
                team_name=team_name,
                goal=goal,
                template="swarm"
            )

            return {
                "success": True,
                "swarm_id": team_name,
                "swarm": swarm,
                "agents": list(swarm.agents.keys()),
                "status": "created"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def execute_swarm(self, goal: str, intent: str, task: str, blocked_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        执行 Swarm 任务

        Args:
            goal: 目标
            intent: 意图
            task: 任务描述
            blocked_by: 依赖任务

        Returns:
            执行结果
        """
        if not SWARM_AVAILABLE or self.swarm_adapter is None:
            return {"success": False, "error": "Swarm 不可用"}

        team_name = f"ceo-{intent[:8]}-{uuid.uuid4().hex[:6]}"

        try:
            # 1. 创建团队
            swarm = self.swarm_adapter.create_swarm(team_name, goal)

            # 2. 分配任务
            agents = ["researcher-1", "researcher-2", "executor-1", "executor-2"]
            for agent in agents:
                self.swarm_adapter.assign_task(team_name, agent, f"{agent} 的任务", blocked_by=blocked_by)

            return {
                "success": True,
                "swarm_id": team_name,
                "task_id": task,
                "status": "executed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_swarm_status(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """获取 Swarm 状态"""
        if not SWARM_AVAILABLE or self.swarm_adapter is None:
            return None
        return self.swarm_adapter.get_swarm_status(swarm_id)

    def list_active_swarms(self) -> List[Dict[str, Any]]:
        """列出活跃的 Swarms"""
        if not SWARM_AVAILABLE or self.swarm_adapter is None:
            return []
        return self.swarm_adapter.list_swarms()


def main():
    """CLI 测试"""
    import sys

    router = CEORouter()

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("输入任务描述: ")

    result = router.route(user_input)

    print("\n" + "=" * 50)
    print("CEO 路由结果")
    print("=" * 50)
    print(f"决策: {result.decision}")
    print(f"目标: {result.target} → {result.target_name}")
    print(f"意图: {result.intent}")
    print(f"复杂度: {result.complexity}")
    print(f"理由: {result.reason}")

    # Swarm 相关输出
    if hasattr(result, 'swarm_id') and result.swarm_id:
        print(f"Swarm ID: {result.swarm_id}")
        print(f"子 Agents: {result.agents}")

        # 如果是 Swarm 路由，尝试创建团队
        if result.target == RoutingTarget.SWARM.value and "--no-swarm" not in user_input:
            print("\n" + "=" * 50)
            print("自动创建 Swarm 团队")
            print("=" * 50)
            swarm_result = router.create_swarm_team(result.reason, result.intent)
            if swarm_result["success"]:
                print(f"✅ Swarm 创建成功: {swarm_result['swarm_id']}")
                print(f"   Agents: {swarm_result['agents']}")
                print(f"   状态: {swarm_result['status']}")
            else:
                print(f"❌ Swarm 创建失败: {swarm_result.get('error')}")


if __name__ == "__main__":
    main()
