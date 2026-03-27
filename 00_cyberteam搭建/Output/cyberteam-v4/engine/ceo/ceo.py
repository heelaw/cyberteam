#!/usr/bin/env python3
"""
CyberTeam V4 - CEO 路由引擎 (L1)

职责：
1. 需求分拣 (简单咨询 vs 正式任务)
2. 意图识别 (数据分析/内容运营/技术研发/安全合规)
3. 复杂度评估 (高/中/低)
4. 路由决策 (L2/L3A/L3B/L3C)
5. Swarm 智能编排 (复杂任务自动组建团队)
6. 5W1H1Y 问题拆解 (新！)
7. 消息驱动架构 (通过 MailboxManager 发送任务)
"""

from dataclasses import dataclass
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

# MailboxManager 消息驱动
try:
    from CYBERTEAM.team.mailbox import MailboxManager
    MAILBOX_AVAILABLE = True
except ImportError:
    MAILBOX_AVAILABLE = False
    MailboxManager = None


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
    # 5W1H1Y 拆解字段
    analysis_5w1h1y: Optional[Dict[str, str]] = None  # 5W1H1Y 拆解结果
    # 消息驱动字段
    message_sent: bool = False  # 是否已发送消息
    message_id: Optional[str] = None  # 发送的消息 ID


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

    def __init__(self, team_name: str = "cyberteam", mailbox: MailboxManager = None):
        self.router_config = self._load_router_config()
        # Swarm 集成
        self._swarm_adapter = None
        self._active_swarms: Dict[str, Any] = {}
        # 思维注入系统
        self._thinking_injector = None
        # MailboxManager 消息驱动
        self._team_name = team_name
        self._mailbox = mailbox

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
        return {
            "complexity_threshold": {
                "high": 100,
                "multi_domain": True
            },
            "timeout": 300
        }

    def is_simple_consultation(self, user_input: str) -> bool:
        """需求分拣：判断是否为简单咨询"""
        cleaned = user_input.strip().lower()
        for keyword in self.GREETING_KEYWORDS:
            if keyword in cleaned:
                return True
        if len(re.sub(r'[\w\u4e00-\u9fff]', '', cleaned)) == len(cleaned):
            return True
        return False

    def recognize_intent(self, user_input: str) -> Intent:
        """意图识别"""
        user_input_lower = user_input.lower()
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in user_input_lower)
            if score > 0:
                intent_scores[intent] = score
        if not intent_scores:
            return Intent.UNKNOWN
        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def evaluate_complexity(self, user_input: str, intent: Intent) -> Complexity:
        """复杂度评估"""
        length_score = Complexity.LOW
        if len(user_input) > self.router_config["complexity_threshold"]["high"]:
            length_score = Complexity.HIGH
        elif len(user_input) > 50:
            length_score = Complexity.MEDIUM

        domain_score = Complexity.LOW
        if len(user_input.split()) > 5 and any(
            kw in user_input.lower()
            for kw in ["并且", "以及", "还有", "和", "and", ","]
        ):
            domain_score = Complexity.HIGH

        special_score = Complexity.LOW
        if intent in [Intent.DATA_ANALYSIS, Intent.STRATEGY]:
            special_score = Complexity.MEDIUM

        scores = [length_score, domain_score, special_score]
        if scores.count(Complexity.HIGH) >= 2:
            return Complexity.HIGH
        elif scores.count(Complexity.MEDIUM) >= 2:
            return Complexity.MEDIUM
        else:
            return Complexity.LOW

    def route(self, user_input: str, context: dict = None) -> RoutingResult:
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

        # Step 2: 5W1H1Y 问题拆解
        analysis_5w1h1y = self._analyze_5w1h1y(user_input)

        # Step 3: 意图识别
        intent = self.recognize_intent(user_input)

        # Step 4: 复杂度评估
        complexity = self.evaluate_complexity(user_input, intent)

        # Step 5: 路由决策
        result = self._make_routing_decision(user_input, intent, complexity)

        # Step 6: 思维注入
        if result.target != "NONE":
            thinking_result = self._inject_thinking(user_input, intent.value, complexity.value, result.target)
            if thinking_result:
                result.thinking_models = thinking_result.models_used
                result.thinking_prompt = thinking_result.injected_prompt
                result.thinking_confidence = thinking_result.confidence

        # Step 7: 填充 5W1H1Y 分析结果
        result.analysis_5w1h1y = analysis_5w1h1y

        # Step 8: 通过 MailboxManager 发送消息
        if result.target != "NONE" and result.target != "SWARM":
            msg_result = self._send_to_target(result, user_input, context)
            result.message_sent = msg_result["sent"]
            result.message_id = msg_result.get("message_id")

        return result

    def _inject_thinking(self, task: str, intent: str, complexity: str, target: str) -> Optional[Any]:
        """注入思维模型到任务"""
        if not self.thinking_injector:
            return None

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

    def _analyze_5w1h1y(self, user_input: str) -> Dict[str, str]:
        """5W1H1Y 问题拆解分析"""
        analysis = {
            "what": "",
            "why": "",
            "who": "",
            "when": "",
            "where": "",
            "how": "",
            "yield": ""
        }

        text = user_input.strip()

        # What
        what_patterns = [
            r'(?:帮我?|请?|给我?)(.*?)(?:做|搞|完成|实现|开发|分析|策划|制定)',
            r'(?:需要|要|想要)(.*?)(?:做|搞|完成|实现|开发|分析)',
            r'^(.*?)(?:方案|计划|策略|分析|报告)$',
        ]
        for pattern in what_patterns:
            match = re.search(pattern, text)
            if match:
                analysis["what"] = match.group(1).strip()
                break
        if not analysis["what"]:
            analysis["what"] = text[:min(20, len(text))]

        # Why
        why_keywords = ["因为", "为了", "原因", "目的", "所以", "需要"]
        for kw in why_keywords:
            if kw in text:
                idx = text.index(kw)
                start = max(0, idx - 10)
                end = min(len(text), idx + 20)
                analysis["why"] = text[start:end].strip()
                break

        # Who
        who_keywords = ["我来", "我们", "团队", "谁", "负责人", "张三", "李四", "王五"]
        for kw in who_keywords:
            if kw in text:
                idx = text.index(kw)
                start = max(0, idx - 5)
                end = min(len(text), idx + 10)
                analysis["who"] = text[start:end].strip()
                break
        if not analysis["who"]:
            analysis["who"] = "COO → 相关部门总监"

        # When
        when_patterns = [
            r'(?:在|到|截止|完成|之前|以后)(.{1,20}?(?:日|天|周|月|年|点|时))',
            r'(?:尽快|马上|立刻|立即)',
            r'(?:紧急|加急)',
            r'(?:本周|下周|本月|下月|今年|明年)',
        ]
        for pattern in when_patterns:
            match = re.search(pattern, text)
            if match:
                analysis["when"] = match.group(0).strip()
                break
        if not analysis["when"]:
            analysis["when"] = "尽快"

        # Where
        where_keywords = ["在", "到", "来自", "针对", "面向"]
        for kw in where_keywords:
            if kw in text:
                idx = text.index(kw)
                start = idx
                end = min(len(text), idx + 30)
                segment = text[start:end]
                place_match = re.search(r'[在到]\s*([^\s,，,。]+)', segment)
                if place_match:
                    analysis["where"] = place_match.group(1).strip()
                    break
        if not analysis["where"]:
            platforms = ["小红书", "抖音", "微信", "淘宝", "京东", "App", "Web", "网站"]
            for p in platforms:
                if p in text:
                    analysis["where"] = p
                    break

        # How
        how_keywords = ["怎么", "如何", "怎样", "通过", "用"]
        for kw in how_keywords:
            if kw in text:
                idx = text.index(kw)
                start = max(0, idx - 3)
                end = min(len(text), idx + 30)
                analysis["how"] = text[start:end].strip()
                break
        if not analysis["how"]:
            analysis["how"] = "组建专项团队执行"

        # Yield
        yield_keywords = ["产出", "结果", "交付", "完成", "目标", "得到", "达到"]
        for kw in yield_keywords:
            if kw in text:
                idx = text.index(kw)
                start = max(0, idx - 5)
                end = min(len(text), idx + 30)
                analysis["yield"] = text[start:end].strip()
                break
        if not analysis["yield"]:
            analysis["yield"] = "完整方案 + 执行报告"

        return analysis

    def _get_mailbox(self) -> Optional[MailboxManager]:
        """获取或创建 MailboxManager"""
        if not MAILBOX_AVAILABLE or MailboxManager is None:
            return None
        if self._mailbox is None:
            self._mailbox = MailboxManager(self._team_name)
        return self._mailbox

    def _send_to_target(self, result: RoutingResult, user_input: str, context: dict = None) -> Dict[str, Any]:
        """通过 MailboxManager 发送任务消息到目标 Agent"""
        mailbox = self._get_mailbox()
        if mailbox is None:
            return {"sent": False, "error": "MailboxManager 不可用"}

        task_message = self._build_task_message(result, user_input, context)

        target_map = {
            "L2": "coo",
            "L3A": self._map_intent_to_dept(result.intent),
            "L3B": "skills-executor",
            "L3C": "agent-executor",
        }
        target_inbox = target_map.get(result.target, "coo")

        try:
            msg = mailbox.send(
                from_agent="ceo",
                to=target_inbox,
                content=task_message["content"],
                msg_type="message",
                request_id=result.swarm_id or uuid.uuid4().hex[:12],
                summary=task_message["summary"],
                plan=task_message.get("plan"),
                reason=result.reason
            )

            print(f"[CEO] 消息已发送 → {target_inbox}, message_id={msg.request_id}")

            return {
                "sent": True,
                "message_id": msg.request_id,
                "target": target_inbox,
                "task_message": task_message
            }
        except Exception as e:
            print(f"[CEO] 消息发送失败: {e}")
            return {"sent": False, "error": str(e)}

    def _build_task_message(self, result: RoutingResult, user_input: str, context: dict = None) -> Dict[str, Any]:
        """构建标准化的任务描述消息格式"""
        analysis = result.analysis_5w1h1y or {}

        lines = [
            "## 任务下达 [CEO -> COO]",
            "",
            "### 5W1H1Y 拆解",
            f"- **What (什么)**: {analysis.get('what', '待确定')}",
            f"- **Why (为什么)**: {analysis.get('why', '待确定')}",
            f"- **Who (谁)**: {analysis.get('who', 'COO → 相关部门总监')}",
            f"- **When (何时)**: {analysis.get('when', '尽快')}",
            f"- **Where (在哪里)**: {analysis.get('where', '待确定')}",
            f"- **How (如何做)**: {analysis.get('how', '组建专项团队执行')}",
            f"- **Yield (产出)**: {analysis.get('yield', '完整方案 + 执行报告')}",
            "",
            "### 原始需求",
            user_input,
            "",
            "### 路由决策",
            f"- **意图**: {result.intent}",
            f"- **复杂度**: {result.complexity}",
            f"- **目标层**: {result.target} → {result.target_name}",
            f"- **理由**: {result.reason}",
        ]

        if result.thinking_models or result.thinking_prompt:
            lines.extend([
                "",
                "### 思维注入",
            ])
            if result.thinking_models:
                lines.append(f"- **模型**: {', '.join(result.thinking_models)}")
            if result.thinking_prompt:
                lines.append(f"- **Prompt**: {result.thinking_prompt[:100]}...")
            if result.thinking_confidence:
                lines.append(f"- **置信度**: {result.thinking_confidence:.2f}")

        content = "\n".join(lines)
        summary = f"[CEO路由] {result.intent} | {result.complexity}复杂度 | → {result.target_name}"

        return {
            "content": content,
            "summary": summary,
            "plan": content
        }

    def _map_intent_to_dept(self, intent: str) -> str:
        """将意图映射到部门收件箱"""
        dept_map = {
            "数据分析": "data-analytics",
            "内容运营": "content-ops",
            "技术研发": "engineering",
            "安全合规": "security",
            "战略规划": "strategy",
            "人力资源": "hr",
            "运营支持": "ops",
        }
        return dept_map.get(intent, "strategy")

    def should_use_swarm(self, user_input: str, intent: Intent, complexity: Complexity) -> bool:
        """判断是否应该使用 Swarm 群体智能"""
        if not SWARM_AVAILABLE:
            return False

        swarm_keywords = [
            "团队", "团队协作", "多个专家", "分工", "并行",
            "组建团队", "自主完成", "群体智能", "swarm"
        ]
        has_swarm_keyword = any(kw in user_input.lower() for kw in swarm_keywords)
        is_high_complexity = complexity == Complexity.HIGH
        multi_domain = len(user_input.split()) > 5 and any(
            kw in user_input.lower()
            for kw in ["并且", "以及", "还有", "和", "and", ","]
        )
        is_strategy_task = intent in [Intent.STRATEGY, Intent.DATA_ANALYSIS]

        return has_swarm_keyword or is_high_complexity or multi_domain or is_strategy_task

    def _make_routing_decision(
        self,
        user_input: str,
        intent: Intent,
        complexity: Complexity
    ) -> RoutingResult:
        """路由决策逻辑"""

        # 规则1: 技术类任务 → L3B
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

        # 规则2: 通用功能开发 → L3C
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

        # 规则2.5: Swarm 群体智能
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

        # 规则3: 复杂任务 → L2
        if complexity == Complexity.HIGH:
            return RoutingResult(
                decision="复杂任务",
                target=RoutingTarget.L2.value,
                target_name="PM",
                intent=intent.value,
                complexity=complexity.value,
                reason="高复杂度任务需要协调"
            )

        # 规则4: 中等复杂度 → L2
        if complexity == Complexity.MEDIUM:
            return RoutingResult(
                decision="中等任务",
                target=RoutingTarget.L2.value,
                target_name="PM",
                intent=intent.value,
                complexity=complexity.value,
                reason="中等复杂度任务"
            )

        # 规则5: 默认 → L3A
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

    def create_swarm_team(self, goal: str, intent: str) -> Dict[str, Any]:
        """创建 Swarm 团队"""
        if not SWARM_AVAILABLE or self.swarm_adapter is None:
            return {"success": False, "error": "Swarm 模块不可用"}

        team_name = f"ceo-{intent[:8]}-{uuid.uuid4().hex[:6]}"

        try:
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
            return {"success": False, "error": str(e)}

    def execute_swarm(self, goal: str, intent: str, task: str, blocked_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """执行 Swarm 任务"""
        if not SWARM_AVAILABLE or self.swarm_adapter is None:
            return {"success": False, "error": "Swarm 不可用"}

        team_name = f"ceo-{intent[:8]}-{uuid.uuid4().hex[:6]}"

        try:
            swarm = self.swarm_adapter.create_swarm(team_name, goal)
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

    if result.swarm_id:
        print(f"Swarm ID: {result.swarm_id}")
        print(f"子 Agents: {result.agents}")

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
