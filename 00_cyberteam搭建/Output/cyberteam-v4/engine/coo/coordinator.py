#!/usr/bin/env python3
"""
CyberTeam V4 - COO 协调器核心

职责：
1. 接收 CEO 的任务消息（MailboxManager.receive）
2. 分析任务类型，制定讨论议题
3. 向各专家发送讨论邀请
4. 等待专家响应（多轮迭代）
5. 识别分歧点，组织深度讨论
6. 汇总策略方案和风险预案
7. 向 CEO 发送汇报消息
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import uuid
import json
from pathlib import Path

# 添加 engine 目录到路径
import sys
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Mailbox 集成
try:
    from cyberteam.team.mailbox import MailboxManager
    from cyberteam.team.models import MessageType
    MAILBOX_AVAILABLE = True
except ImportError:
    MAILBOX_AVAILABLE = False
    MailboxManager = None
    MessageType = None

# 引入工作流
from .workflow import (
    COOWorkflow,
    WorkflowPhase,
    TopicType,
    StrategyTopic,
    RiskItem,
    DebatePoint,
)


class DialogueLayer(Enum):
    """对话层级"""
    LAYER1_CEO_ALIGNMENT = 1  # CEO-COO 战略对齐
    LAYER2_EXPERT_STRATEGY = 2  # COO-专家策略制定
    LAYER3_EXPERT_DEBATE = 3   # 专家内部分歧讨论
    LAYER4_COO_REPORTING = 4   # COO 向 CEO 汇报


class WorkflowState(Enum):
    """工作流状态"""
    IDLE = "idle"
    WAITING_CEO_TASK = "waiting_ceo_task"
    LAYER1_IN_PROGRESS = "layer1_in_progress"
    LAYER2_IN_PROGRESS = "layer2_in_progress"
    LAYER3_IN_PROGRESS = "layer3_in_progress"
    LAYER4_IN_PROGRESS = "layer4_in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class DiscussionTopic(Enum):
    """讨论议题"""
    SELLING_POINT = "卖点方向"
    USER_SCENARIO = "用户场景"
    CHANNEL_STRATEGY = "渠道策略"
    CONVERSION_STRATEGY = "转化策略"
    RISK_PLAN = "风险预案"
    BACKUP_PLAN = "保底措施"
    EFFECT_PREDICTION = "效果预测"


@dataclass
class ExpertInvitation:
    """专家邀请"""
    invitation_id: str
    expert_id: str
    expert_name: str
    topic: DiscussionTopic
    question: str
    context: Dict[str, Any]
    status: str = "pending"  # pending/accepted/declined/responded
    response: Optional[str] = None
    concerns: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None


@dataclass
class DiscussionSession:
    """讨论会话"""
    session_id: str
    task_id: str
    workflow: COOWorkflow

    # 专家邀请
    invitations: List[ExpertInvitation] = field(default_factory=list)

    # 状态
    state: WorkflowState = WorkflowState.IDLE
    current_layer: DialogueLayer = DialogueLayer.LAYER1_CEO_ALIGNMENT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # 消息队列
    pending_messages: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class COOSummary:
    """COO 汇总报告"""
    session_id: str
    task_id: str

    # 策略摘要
    strategy_summary: str

    # 四大议题结论
    selling_point_conclusion: str
    user_scenario_conclusion: str
    channel_strategy_conclusion: str
    conversion_strategy_conclusion: str

    # 风险预案
    effect_prediction: Dict[str, Any]
    identified_risks: List[Dict[str, Any]]
    backup_plans: List[str]
    warning_mechanism: str

    # 预期效果
    conservative_estimate: str
    normal_estimate: str
    optimistic_estimate: str
    confidence: float

    # 需要授权
    authorization_required: List[str]

    # 完成时间
    completed_at: datetime


class COOCoordinator:
    """COO 协调器

    负责管理专家讨论流程，实现四层对话体系。
    """

    # 专家库
    EXPERT_REGISTRY = {
        "user_operations_expert": {
            "name": "用户运营专家",
            "expertise": ["用户增长", "留存分析", "社群运营"],
            "topics": [DiscussionTopic.USER_SCENARIO, DiscussionTopic.SELLING_POINT]
        },
        "content_expert": {
            "name": "内容运营专家",
            "expertise": ["内容策划", "文案写作", "平台运营"],
            "topics": [DiscussionTopic.SELLING_POINT, DiscussionTopic.CHANNEL_STRATEGY]
        },
        "growth_expert": {
            "name": "增长专家",
            "expertise": ["AARRR", "转化优化", "数据分析"],
            "topics": [DiscussionTopic.CONVERSION_STRATEGY, DiscussionTopic.EFFECT_PREDICTION]
        },
        "risk_expert": {
            "name": "风险控制专家",
            "expertise": ["风险评估", "应急预案", "合规审查"],
            "topics": [DiscussionTopic.RISK_PLAN, DiscussionTopic.BACKUP_PLAN]
        },
        "channel_expert": {
            "name": "渠道运营专家",
            "expertise": ["多渠道运营", "投放策略", "渠道整合"],
            "topics": [DiscussionTopic.CHANNEL_STRATEGY, DiscussionTopic.CONVERSION_STRATEGY]
        }
    }

    # 议题问题定义
    TOPIC_QUESTIONS = {
        DiscussionTopic.SELLING_POINT: "用户痛点是什么？应该主打什么卖点？",
        DiscussionTopic.USER_SCENARIO: "用户从看到内容到转化经历哪些场景？关键流失点在哪？",
        DiscussionTopic.CHANNEL_STRATEGY: "各渠道如何分工定位？小红书做什么？抖音做什么？",
        DiscussionTopic.CONVERSION_STRATEGY: "如何确保转化？转化路径是什么？优惠设计是什么？",
        DiscussionTopic.RISK_PLAN: "主要风险有哪些？概率和影响是什么？",
        DiscussionTopic.BACKUP_PLAN: "如果效果不好，应该怎么办？（分三层）",
        DiscussionTopic.EFFECT_PREDICTION: "如果按计划执行，预期效果是什么？置信度多少？"
    }

    def __init__(
        self,
        team_name: str = "cyberteam",
        coo_name: str = "coo",
        storage_dir: Optional[str] = None
    ):
        self.team_name = team_name
        self.coo_name = coo_name

        # Mailbox 集成
        self.mailbox: Optional[MailboxManager] = None
        if MAILBOX_AVAILABLE and MailboxManager:
            self.mailbox = MailboxManager(team_name)

        # 存储目录
        self.storage_dir = Path(storage_dir) if storage_dir else Path(f"./data/coo_sessions")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 活跃会话
        self.active_sessions: Dict[str, DiscussionSession] = {}

        # 回调函数
        self.on_layer1_complete: Optional[Callable] = None
        self.on_layer2_complete: Optional[Callable] = None
        self.on_layer3_complete: Optional[Callable] = None
        self.on_layer4_complete: Optional[Callable] = None

    def create_session(
        self,
        task_id: str,
        user_input: str,
        intent: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> DiscussionSession:
        """创建讨论会话"""

        session_id = f"coo-{uuid.uuid4().hex[:8]}"

        # 创建工作流
        workflow = COOWorkflow(session_id=session_id, task_id=task_id)

        # 创建会话
        session = DiscussionSession(
            session_id=session_id,
            task_id=task_id,
            workflow=workflow
        )

        # 保存会话
        self.active_sessions[session_id] = session

        # 持久化
        self._save_session(session)

        return session

    def receive_ceo_task(self) -> Optional[Dict[str, Any]]:
        """接收 CEO 的任务消息"""
        if not self.mailbox:
            return None

        messages = self.mailbox.receive(self.coo_name, limit=10)

        for msg in messages:
            if msg.type == MessageType.message if MessageType else msg.get("type") == "message":
                content = msg.content
                if content and "task" in content.lower():
                    return {
                        "message_id": msg.request_id,
                        "task_id": msg.get("task_id"),
                        "user_input": content,
                        "from_agent": msg.from_agent,
                        "timestamp": msg.get("timestamp")
                    }

        return None

    def analyze_task(
        self,
        session: DiscussionSession,
        user_input: str,
        intent: str
    ) -> Dict[str, Any]:
        """分析任务，确定讨论议题"""

        # Layer1: 战略对齐项
        session.workflow.layer1.north_star = self._extract_north_star(user_input)
        session.workflow.layer1.constraints = self._extract_constraints(user_input)
        session.workflow.layer1.risk_appetite = self._assess_risk_appetite(intent)

        # Layer2: 确定需要讨论的议题
        topics = []
        if intent in ["内容运营", "运营支持"]:
            topics.extend([
                DiscussionTopic.SELLING_POINT,
                DiscussionTopic.USER_SCENARIO,
                DiscussionTopic.CHANNEL_STRATEGY,
                DiscussionTopic.CONVERSION_STRATEGY
            ])
        elif intent in ["数据分析", "战略规划"]:
            topics.append(DiscussionTopic.EFFECT_PREDICTION)
            topics.append(DiscussionTopic.RISK_PLAN)

        # Layer3: 风险预案议题
        topics.extend([
            DiscussionTopic.RISK_PLAN,
            DiscussionTopic.BACKUP_PLAN
        ])

        session.workflow.layer2.invited_experts = self._select_experts(topics)

        # 更新状态
        session.state = WorkflowState.LAYER1_IN_PROGRESS
        session.current_layer = DialogueLayer.LAYER1_CEO_ALIGNMENT
        session.updated_at = datetime.now()

        self._save_session(session)

        return {
            "topics": [t.value for t in topics],
            "experts": session.workflow.layer2.invited_experts
        }

    def invite_experts(
        self,
        session: DiscussionSession,
        topic: DiscussionTopic
    ) -> List[ExpertInvitation]:
        """向专家发送讨论邀请"""

        # 选择相关专家
        expert_ids = [
            exp_id for exp_id, exp_info in self.EXPERT_REGISTRY.items()
            if topic in exp_info["topics"]
        ]

        invitations = []

        for expert_id in expert_ids:
            expert_info = self.EXPERT_REGISTRY[expert_id]
            question = self.TOPIC_QUESTIONS.get(topic, "请发表您的专业意见")

            invitation = ExpertInvitation(
                invitation_id=str(uuid.uuid4())[:8],
                expert_id=expert_id,
                expert_name=expert_info["name"],
                topic=topic,
                question=question,
                context={},
                status="pending",
                sent_at=datetime.now()
            )

            invitations.append(invitation)
            session.invitations.append(invitation)

        # 通过 Mailbox 发送邀请
        if self.mailbox:
            for invitation in invitations:
                self._send_expert_invitation(invitation)

        session.updated_at = datetime.now()
        self._save_session(session)

        return invitations

    def handle_expert_response(
        self,
        session: DiscussionSession,
        expert_id: str,
        response: str,
        concerns: Optional[List[str]] = None,
        suggestions: Optional[List[str]] = None
    ) -> bool:
        """处理专家响应"""

        # 找到对应的邀请
        invitation = None
        for inv in session.invitations:
            if inv.expert_id == expert_id and inv.status == "pending":
                invitation = inv
                break

        if not invitation:
            return False

        # 更新邀请状态
        invitation.status = "responded"
        invitation.response = response
        invitation.concerns = concerns or []
        invitation.suggestions = suggestions or []
        invitation.responded_at = datetime.now()

        # 根据议题更新对应的话题
        topic = invitation.topic
        topic_key = self._topic_to_key(topic)

        if topic_key == "selling_point":
            topic_obj = session.workflow.layer2.selling_point_topic
            if not topic_obj:
                topic_obj = StrategyTopic(
                    topic_type=TopicType.SELLING_POINT,
                    question=invitation.question,
                    status="discussing"
                )
                session.workflow.layer2.selling_point_topic = topic_obj
            topic_obj.expert_answers[expert_id] = response

        elif topic_key == "user_scenario":
            topic_obj = session.workflow.layer2.user_scenario_topic
            if not topic_obj:
                topic_obj = StrategyTopic(
                    topic_type=TopicType.USER_SCENARIO,
                    question=invitation.question,
                    status="discussing"
                )
                session.workflow.layer2.user_scenario_topic = topic_obj
            topic_obj.expert_answers[expert_id] = response

        # 检查是否所有专家都已响应
        all_responded = all(
            inv.status == "responded"
            for inv in session.invitations
            if inv.topic == topic
        )

        if all_responded:
            # 收敛讨论
            self._converge_topic(session, topic)

        session.updated_at = datetime.now()
        self._save_session(session)

        return True

    def identify_divergence(
        self,
        session: DiscussionSession,
        topic: DiscussionTopic
    ) -> List[DebatePoint]:
        """识别分歧点，组织深度讨论"""

        # 找到相关邀请
        invitations = [inv for inv in session.invitations if inv.topic == topic]

        if len(invitations) < 2:
            return []

        # 识别分歧
        debate_points = []
        all_suggestions = []

        for inv in invitations:
            all_suggestions.extend(inv.suggestions)

        # 简化的分歧识别：基于建议的重叠
        from collections import Counter
        suggestion_counts = Counter(all_suggestions)

        # 找出支持较少的建议作为潜在分歧点
        for inv in invitations:
            for suggestion in inv.suggestions:
                if suggestion_counts[suggestion] == 1:  # 只有一个专家支持
                    debate_point = DebatePoint(
                        point_id=str(uuid.uuid4())[:8],
                        description=f"专家 {inv.expert_name} 建议的 '{suggestion}' 存在分歧",
                        expert_positions={inv.expert_id: inv.response},
                        resolved=False
                    )
                    debate_points.append(debate_point)
                    session.workflow.layer3.debate_points.append(debate_point)

        session.updated_at = datetime.now()
        self._save_session(session)

        return debate_points

    def converge_topic(
        self,
        session: DiscussionSession,
        topic: DiscussionTopic,
        consensus: str
    ):
        """收敛指定议题"""

        topic_key = self._topic_to_key(topic)
        topic_type = self._topic_to_type(topic)

        topic_obj = None
        if topic_key == "selling_point":
            topic_obj = session.workflow.layer2.selling_point_topic
        elif topic_key == "user_scenario":
            topic_obj = session.workflow.layer2.user_scenario_topic
        elif topic_key == "channel_strategy":
            topic_obj = session.workflow.layer2.channel_strategy_topic
        elif topic_key == "conversion_strategy":
            topic_obj = session.workflow.layer2.conversion_strategy_topic

        if topic_obj:
            topic_obj.consensus = consensus
            topic_obj.status = "converged"

        session.updated_at = datetime.now()
        self._save_session(session)

    def summarize(
        self,
        session: DiscussionSession
    ) -> COOSummary:
        """生成 COO 汇总报告"""

        workflow = session.workflow

        # 收集四大议题结论
        selling_point = workflow.layer2.selling_point_topic.consensus if workflow.layer2.selling_point_topic else ""
        user_scenario = workflow.layer2.user_scenario_topic.consensus if workflow.layer2.user_scenario_topic else ""
        channel_strategy = workflow.layer2.channel_strategy_topic.consensus if workflow.layer2.channel_strategy_topic else ""
        conversion_strategy = workflow.layer2.conversion_strategy_topic.consensus if workflow.layer2.conversion_strategy_topic else ""

        # 收集风险预案
        effect_prediction = {
            "conservative": workflow.layer3.effect_prediction or "待评估",
            "normal": workflow.layer3.effect_prediction or "待评估",
            "optimistic": workflow.layer3.effect_prediction or "待评估"
        }

        identified_risks = [
            {
                "risk_id": r.risk_id,
                "description": r.description,
                "probability": r.probability,
                "impact": r.impact
            }
            for r in workflow.layer3.identified_risks
        ]

        summary = COOSummary(
            session_id=session.session_id,
            task_id=session.task_id,
            strategy_summary=f"基于{len(workflow.layer2.invited_experts)}位专家的讨论形成的策略方案",
            selling_point_conclusion=selling_point,
            user_scenario_conclusion=user_scenario,
            channel_strategy_conclusion=channel_strategy,
            conversion_strategy_conclusion=conversion_strategy,
            effect_prediction=effect_prediction,
            identified_risks=identified_risks,
            backup_plans=workflow.layer3.backup_plans,
            warning_mechanism=workflow.layer3.warning_mechanism or "待确定",
            conservative_estimate=workflow.layer3.effect_prediction or "待评估",
            normal_estimate=workflow.layer3.effect_prediction or "待评估",
            optimistic_estimate=workflow.layer3.effect_prediction or "待评估",
            confidence=0.7,
            authorization_required=workflow.layer4.authorization_request,
            completed_at=datetime.now()
        )

        # 更新会话状态
        session.state = WorkflowState.COMPLETED
        session.workflow.layer4.status = "completed"
        session.workflow.layer4.completed_at = datetime.now()
        session.updated_at = datetime.now()

        self._save_session(session)

        return summary

    def report_to_ceo(
        self,
        session: DiscussionSession,
        summary: COOSummary
    ) -> bool:
        """向 CEO 发送汇报消息"""

        if not self.mailbox:
            return False

        # 构造汇报内容
        content = self._format_report(summary)

        # 发送到 CEO
        try:
            self.mailbox.send(
                from_agent=self.coo_name,
                to="ceo",
                content=content,
                msg_type=MessageType.message if MessageType else "message",
                plan=json.dumps(summary.__dict__, ensure_ascii=False, default=str)
            )
            return True
        except Exception:
            return False

    # ========== 私有方法 ==========

    def _extract_north_star(self, user_input: str) -> str:
        """提取北极星指标"""
        # 简化实现
        if "增长" in user_input:
            return "用户增长"
        elif "转化" in user_input:
            return "转化率提升"
        elif "留存" in user_input:
            return "留存率提升"
        return "待确定"

    def _extract_constraints(self, user_input: str) -> List[str]:
        """提取约束条件"""
        constraints = []
        if "预算" in user_input or "成本" in user_input:
            constraints.append("预算约束")
        if "时间" in user_input or "期限" in user_input:
            constraints.append("时间约束")
        return constraints

    def _assess_risk_appetite(self, intent: str) -> str:
        """评估风险偏好"""
        if intent in ["战略规划", "数据分析"]:
            return "保守"
        elif intent in ["内容运营", "运营支持"]:
            return "平衡"
        return "平衡"

    def _select_experts(self, topics: List[DiscussionTopic]) -> List[str]:
        """选择相关专家"""
        selected = set()
        for topic in topics:
            for exp_id, exp_info in self.EXPERT_REGISTRY.items():
                if topic in exp_info["topics"]:
                    selected.add(exp_id)
        return list(selected)

    def _topic_to_key(self, topic: DiscussionTopic) -> str:
        """将议题转换为键名"""
        mapping = {
            DiscussionTopic.SELLING_POINT: "selling_point",
            DiscussionTopic.USER_SCENARIO: "user_scenario",
            DiscussionTopic.CHANNEL_STRATEGY: "channel_strategy",
            DiscussionTopic.CONVERSION_STRATEGY: "conversion_strategy"
        }
        return mapping.get(topic, "")

    def _topic_to_type(self, topic: DiscussionTopic) -> TopicType:
        """将议题转换为 TopicType"""
        mapping = {
            DiscussionTopic.SELLING_POINT: TopicType.SELLING_POINT,
            DiscussionTopic.USER_SCENARIO: TopicType.USER_SCENARIO,
            DiscussionTopic.CHANNEL_STRATEGY: TopicType.CHANNEL_STRATEGY,
            DiscussionTopic.CONVERSION_STRATEGY: TopicType.CONVERSION_STRATEGY
        }
        return mapping.get(topic, TopicType.SELLING_POINT)

    def _converge_topic(self, session: DiscussionSession, topic: DiscussionTopic):
        """收敛话题"""
        invitations = [inv for inv in session.invitations if inv.topic == topic]

        # 收集所有建议
        all_suggestions = []
        for inv in invitations:
            all_suggestions.extend(inv.suggestions)

        # 简单收敛：多数决
        from collections import Counter
        suggestion_counts = Counter(all_suggestions)

        if suggestion_counts:
            top_suggestion = suggestion_counts.most_common(1)[0][0]
            self.converge_topic(session, topic, top_suggestion)

    def _send_expert_invitation(self, invitation: ExpertInvitation):
        """发送专家邀请"""
        if not self.mailbox:
            return

        content = f"""【讨论邀请】
专家：{invitation.expert_name}
议题：{invitation.topic.value}
问题：{invitation.question}

请回复您的专业意见、顾虑和建议。
"""

        try:
            self.mailbox.send(
                from_agent=self.coo_name,
                to=invitation.expert_id,
                content=content,
                msg_type=MessageType.message if MessageType else "message",
                key=f"invitation:{invitation.invitation_id}"
            )
        except Exception:
            pass

    def _format_report(self, summary: COOSummary) -> str:
        """格式化汇报内容"""
        return f"""【COO 汇报】

任务ID: {summary.task_id}
完成时间: {summary.completed_at.strftime('%Y-%m-%d %H:%M:%S')}

## 策略摘要
{summary.strategy_summary}

## 四大议题结论
- 卖点方向：{summary.selling_point_conclusion}
- 用户场景：{summary.user_scenario_conclusion}
- 渠道策略：{summary.channel_strategy_conclusion}
- 转化策略：{summary.conversion_strategy_conclusion}

## 预期效果
- 保守估计：{summary.conservative_estimate}
- 正常估计：{summary.normal_estimate}
- 乐观估计：{summary.optimistic_estimate}
- 置信度：{summary.confidence}

## 风险预案
{len(summary.identified_risks)} 个风险项
{len(summary.backup_plans)} 层保底措施

## 需要授权
{', '.join(summary.authorization_required) if summary.authorization_required else '无'}
"""

    def _save_session(self, session: DiscussionSession):
        """保存会话到磁盘"""
        try:
            filepath = self.storage_dir / f"{session.session_id}.json"
            data = {
                "session_id": session.session_id,
                "task_id": session.task_id,
                "state": session.state.value,
                "current_layer": session.current_layer.value,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "workflow": session.workflow.to_dict(),
                "invitations": [
                    {
                        "invitation_id": inv.invitation_id,
                        "expert_id": inv.expert_id,
                        "expert_name": inv.expert_name,
                        "topic": inv.topic.value,
                        "question": inv.question,
                        "status": inv.status,
                        "response": inv.response,
                        "concerns": inv.concerns,
                        "suggestions": inv.suggestions,
                        "sent_at": inv.sent_at.isoformat() if inv.sent_at else None,
                        "responded_at": inv.responded_at.isoformat() if inv.responded_at else None
                    }
                    for inv in session.invitations
                ]
            }
            filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def load_session(self, session_id: str) -> Optional[DiscussionSession]:
        """从磁盘加载会话"""
        try:
            filepath = self.storage_dir / f"{session_id}.json"
            if not filepath.exists():
                return None

            data = json.loads(filepath.read_text("utf-8"))

            # 重建工作流
            workflow = COOWorkflow(
                session_id=data["session_id"],
                task_id=data["task_id"]
            )

            session = DiscussionSession(
                session_id=data["session_id"],
                task_id=data["task_id"],
                workflow=workflow,
                state=WorkflowState(data["state"]),
                current_layer=DialogueLayer(data["current_layer"])
            )

            return session

        except Exception:
            return None


def main():
    """CLI 测试"""
    coordinator = COOCoordinator()

    print("=" * 50)
    print("COO 协调器测试")
    print("=" * 50)

    # 创建会话
    session = coordinator.create_session(
        task_id="test-task-001",
        user_input="帮我分析下季度增长策略",
        intent="数据分析"
    )

    print(f"\n创建会话: {session.session_id}")
    print(f"任务ID: {session.task_id}")
    print(f"状态: {session.state.value}")

    # 分析任务
    result = coordinator.analyze_task(
        session,
        user_input="帮我分析下季度增长策略",
        intent="数据分析"
    )

    print(f"\n任务分析:")
    print(f"  议题: {result['topics']}")
    print(f"  专家: {result['experts']}")

    # 邀请专家
    invitations = coordinator.invite_experts(
        session,
        topic=DiscussionTopic.SELLING_POINT
    )

    print(f"\n发送邀请: {len(invitations)} 位专家")
    for inv in invitations:
        print(f"  - {inv.expert_name}: {inv.topic.value}")


if __name__ == "__main__":
    main()