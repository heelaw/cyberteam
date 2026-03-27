#!/usr/bin/env python3
"""
CyberTeam V4 - COO 工作流引擎

定义四层对话体系的工作流：
1. Layer1: CEO → COO 战略对齐
2. Layer2: COO → 专家团队 策略制定
3. Layer3: 专家团队内部分歧讨论
4. Layer4: COO → CEO 汇报
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class WorkflowPhase(Enum):
    """工作流阶段"""
    LAYER1_ALIGNMENT = "layer1_alignment"      # 第一层：战略对齐
    LAYER2_STRATEGY = "layer2_strategy"        # 第二层：策略制定
    LAYER3_DEBATE = "layer3_debate"            # 第三层：深度讨论
    LAYER4_REPORTING = "layer4_reporting"       # 第四层：汇报
    COMPLETED = "completed"                    # 完成


class TopicType(Enum):
    """讨论议题类型"""
    SELLING_POINT = "卖点方向"           # 卖点方向
    USER_SCENARIO = "用户场景"           # 用户场景
    CHANNEL_STRATEGY = "渠道策略"        # 渠道策略
    CONVERSION_STRATEGY = "转化策略"     # 转化策略
    RISK_ASSESSMENT = "风险预案"         # 风险预案
    BACKUP_PLAN = "保底措施"            # 保底措施
    EFFECT_PREDICTION = "效果预测"       # 效果预测
    WARNING_MECHANISM = "预警机制"       # 预警机制


@dataclass
class AlignmentItem:
    """对齐项"""
    name: str                    # 对齐项名称
    ceo_decision: str            # CEO 的决定
    coo_confirmation: str        # COO 的确认
    status: str = "pending"      # pending/confirmed


@dataclass
class Layer1Alignment:
    """第一层对话：CEO-COO战略对齐"""
    layer: int = 1
    phase: WorkflowPhase = WorkflowPhase.LAYER1_ALIGNMENT

    # 战略对齐项
    north_star: Optional[str] = None        # 北极星指标
    constraints: List[str] = field(default_factory=list)   # 约束条件
    risk_appetite: Optional[str] = None     # 风险偏好
    resource_allocation: Dict[str, Any] = field(default_factory=dict)  # 资源配置

    # 状态
    status: str = "pending"                # pending/in_progress/completed
    alignment_items: List[AlignmentItem] = field(default_factory=list)
    completed_at: Optional[datetime] = None

    def is_complete(self) -> bool:
        """检查是否完成"""
        return self.status == "completed" and len(self.alignment_items) >= 4

    def to_dict(self) -> dict:
        return {
            "layer": self.layer,
            "phase": self.phase.value,
            "north_star": self.north_star,
            "constraints": self.constraints,
            "risk_appetite": self.risk_appetite,
            "resource_allocation": self.resource_allocation,
            "status": self.status,
            "alignment_items": [
                {
                    "name": item.name,
                    "ceo_decision": item.ceo_decision,
                    "coo_confirmation": item.coo_confirmation,
                    "status": item.status
                }
                for item in self.alignment_items
            ],
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class StrategyTopic:
    """策略议题"""
    topic_type: TopicType
    question: str                # 需要回答的问题
    expert_answers: Dict[str, str] = field(default_factory=dict)  # 专家回答
    consensus: Optional[str] = None  # 共识
    status: str = "pending"       # pending/discussing/converged


@dataclass
class Layer2Strategy:
    """第二层对话：COO-专家团队 策略制定"""
    layer: int = 2
    phase: WorkflowPhase = WorkflowPhase.LAYER2_STRATEGY

    # 四大议题
    selling_point_topic: Optional[StrategyTopic] = None    # 卖点方向
    user_scenario_topic: Optional[StrategyTopic] = None     # 用户场景
    channel_strategy_topic: Optional[StrategyTopic] = None # 渠道策略
    conversion_strategy_topic: Optional[StrategyTopic] = None  # 转化策略

    # 参与专家
    invited_experts: List[str] = field(default_factory=list)

    # 状态
    status: str = "pending"
    current_topic: Optional[TopicType] = None
    completed_at: Optional[datetime] = None

    def get_topic(self, topic_type: TopicType) -> Optional[StrategyTopic]:
        """获取指定议题"""
        topic_map = {
            TopicType.SELLING_POINT: self.selling_point_topic,
            TopicType.USER_SCENARIO: self.user_scenario_topic,
            TopicType.CHANNEL_STRATEGY: self.channel_strategy_topic,
            TopicType.CONVERSION_STRATEGY: self.conversion_strategy_topic,
        }
        return topic_map.get(topic_type)

    def set_topic(self, topic_type: TopicType, topic: StrategyTopic):
        """设置议题"""
        if topic_type == TopicType.SELLING_POINT:
            self.selling_point_topic = topic
        elif topic_type == TopicType.USER_SCENARIO:
            self.user_scenario_topic = topic
        elif topic_type == TopicType.CHANNEL_STRATEGY:
            self.channel_strategy_topic = topic
        elif topic_type == TopicType.CONVERSION_STRATEGY:
            self.conversion_strategy_topic = topic

    def is_complete(self) -> bool:
        """检查是否完成"""
        topics = [
            self.selling_point_topic,
            self.user_scenario_topic,
            self.channel_strategy_topic,
            self.conversion_strategy_topic
        ]
        return all(t and t.status == "converged" for t in topics)

    def to_dict(self) -> dict:
        return {
            "layer": self.layer,
            "phase": self.phase.value,
            "topics": {
                "selling_point": self._topic_to_dict(self.selling_point_topic),
                "user_scenario": self._topic_to_dict(self.user_scenario_topic),
                "channel_strategy": self._topic_to_dict(self.channel_strategy_topic),
                "conversion_strategy": self._topic_to_dict(self.conversion_strategy_topic),
            },
            "invited_experts": self.invited_experts,
            "status": self.status,
            "current_topic": self.current_topic.value if self.current_topic else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def _topic_to_dict(self, topic: Optional[StrategyTopic]) -> Optional[dict]:
        if not topic:
            return None
        return {
            "type": topic.topic_type.value,
            "question": topic.question,
            "expert_answers": topic.expert_answers,
            "consensus": topic.consensus,
            "status": topic.status
        }


@dataclass
class DebatePoint:
    """辩论点"""
    point_id: str
    description: str            # 辩论点描述
    expert_positions: Dict[str, str] = field(default_factory=dict)  # 各专家立场
    resolution: Optional[str] = None  # 解决方案
    resolved: bool = False


@dataclass
class RiskItem:
    """风险项"""
    risk_id: str
    description: str
    probability: str             # high/medium/low
    impact: str                 # high/medium/low
    prevention: str              # 预防措施
    contingency: str             # 应急预案


@dataclass
class Layer3Debate:
    """第三层对话：专家团队内部分歧讨论"""
    layer: int = 3
    phase: WorkflowPhase = WorkflowPhase.LAYER3_DEBATE

    # 风险预案讨论
    effect_prediction: Optional[str] = None     # 效果预测
    identified_risks: List[RiskItem] = field(default_factory=list)  # 识别的风险
    backup_plans: List[str] = field(default_factory=list)  # 保底措施（三层）
    warning_mechanism: Optional[str] = None      # 预警机制

    # 辩论点
    debate_points: List[DebatePoint] = field(default_factory=list)
    current_debate: Optional[DebatePoint] = None

    # 状态
    status: str = "pending"
    completed_at: Optional[datetime] = None

    def is_complete(self) -> bool:
        """检查是否完成"""
        return (
            self.effect_prediction is not None
            and len(self.identified_risks) > 0
            and len(self.backup_plans) >= 3
            and self.warning_mechanism is not None
            and all(dp.resolved for dp in self.debate_points)
        )

    def to_dict(self) -> dict:
        return {
            "layer": self.layer,
            "phase": self.phase.value,
            "effect_prediction": self.effect_prediction,
            "identified_risks": [
                {
                    "risk_id": r.risk_id,
                    "description": r.description,
                    "probability": r.probability,
                    "impact": r.impact,
                    "prevention": r.prevention,
                    "contingency": r.contingency
                }
                for r in self.identified_risks
            ],
            "backup_plans": self.backup_plans,
            "warning_mechanism": self.warning_mechanism,
            "debate_points": [
                {
                    "point_id": dp.point_id,
                    "description": dp.description,
                    "expert_positions": dp.expert_positions,
                    "resolution": dp.resolution,
                    "resolved": dp.resolved
                }
                for dp in self.debate_points
            ],
            "status": self.status,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class Layer4Reporting:
    """第四层对话：COO向CEO汇报"""
    layer: int = 4
    phase: WorkflowPhase = WorkflowPhase.LAYER4_REPORTING

    # 汇报内容
    strategy_summary: Optional[str] = None    # 策略摘要
    effect_prediction: Optional[str] = None   # 预期效果
    risk_plan: Optional[str] = None           # 风险预案
    authorization_request: List[str] = field(default_factory=list)  # 需要授权项
    support_request: List[str] = field(default_factory=list)       # 请求支持

    # CEO 反馈
    ceo_decision: Optional[str] = None         # 批准/修改/打回
    ceo_authorization: Dict[str, Any] = field(default_factory=dict)  # 授权范围
    ceo_supplement: Optional[str] = None       # CEO 补充的风险提醒

    # 状态
    status: str = "pending"
    completed_at: Optional[datetime] = None

    def is_complete(self) -> bool:
        """检查是否完成"""
        return (
            self.ceo_decision is not None
            and self.ceo_decision in ["approved", "modified", "rejected"]
        )

    def to_dict(self) -> dict:
        return {
            "layer": self.layer,
            "phase": self.phase.value,
            "strategy_summary": self.strategy_summary,
            "effect_prediction": self.effect_prediction,
            "risk_plan": self.risk_plan,
            "authorization_request": self.authorization_request,
            "support_request": self.support_request,
            "ceo_decision": self.ceo_decision,
            "ceo_authorization": self.ceo_authorization,
            "ceo_supplement": self.ceo_supplement,
            "status": self.status,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class COOWorkflow:
    """COO 工作流管理器

    管理四层对话的完整生命周期。
    """

    def __init__(self, session_id: str, task_id: str):
        self.session_id = session_id
        self.task_id = task_id

        # 四层对话状态
        self.layer1 = Layer1Alignment()
        self.layer2 = Layer2Strategy()
        self.layer3 = Layer3Debate()
        self.layer4 = Layer4Reporting()

        # 当前阶段
        self.current_phase = WorkflowPhase.LAYER1_ALIGNMENT

        # 创建时间
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def get_current_layer(self) -> int:
        """获取当前层"""
        return self.current_phase.value.count("layer") + 1

    def advance_phase(self) -> bool:
        """推进到下一阶段"""
        phase_order = [
            WorkflowPhase.LAYER1_ALIGNMENT,
            WorkflowPhase.LAYER2_STRATEGY,
            WorkflowPhase.LAYER3_DEBATE,
            WorkflowPhase.LAYER4_REPORTING,
            WorkflowPhase.COMPLETED
        ]

        try:
            current_idx = phase_order.index(self.current_phase)
            if current_idx < len(phase_order) - 1:
                self.current_phase = phase_order[current_idx + 1]
                self.updated_at = datetime.now()
                return True
            return False
        except ValueError:
            return False

    def complete_current_phase(self) -> bool:
        """完成当前阶段"""
        if self.current_phase == WorkflowPhase.LAYER1_ALIGNMENT:
            self.layer1.status = "completed"
            self.layer1.completed_at = datetime.now()
        elif self.current_phase == WorkflowPhase.LAYER2_STRATEGY:
            self.layer2.status = "completed"
            self.layer2.completed_at = datetime.now()
        elif self.current_phase == WorkflowPhase.LAYER3_DEBATE:
            self.layer3.status = "completed"
            self.layer3.completed_at = datetime.now()
        elif self.current_phase == WorkflowPhase.LAYER4_REPORTING:
            self.layer4.status = "completed"
            self.layer4.completed_at = datetime.now()

        return self.advance_phase()

    def get_progress(self) -> dict:
        """获取进度"""
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "current_phase": self.current_phase.value,
            "current_layer": self.get_current_layer(),
            "layer1_status": self.layer1.status,
            "layer2_status": self.layer2.status,
            "layer3_status": self.layer3.status,
            "layer4_status": self.layer4.status,
            "is_complete": self.current_phase == WorkflowPhase.COMPLETED,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def to_dict(self) -> dict:
        """导出完整状态"""
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "current_phase": self.current_phase.value,
            "layers": {
                "layer1": self.layer1.to_dict(),
                "layer2": self.layer2.to_dict(),
                "layer3": self.layer3.to_dict(),
                "layer4": self.layer4.to_dict()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


def main():
    """CLI 测试"""
    workflow = COOWorkflow(
        session_id="test-session-001",
        task_id="test-task-001"
    )

    print("=" * 50)
    print("COO 工作流测试")
    print("=" * 50)

    print("\n初始状态:")
    print(f"  当前阶段: {workflow.current_phase.value}")
    print(f"  当前层: {workflow.get_current_layer()}")

    # 模拟 Layer1 完成
    workflow.layer1.north_star = "提升DAU 20%"
    workflow.layer1.constraints = ["预算<100万", "时间<3个月"]
    workflow.layer1.risk_appetite = "平衡型"
    workflow.layer1.status = "completed"
    workflow.complete_current_phase()

    print("\nLayer1 完成后:")
    print(f"  当前阶段: {workflow.current_phase.value}")
    print(f"  Layer1 状态: {workflow.layer1.status}")

    # 模拟 Layer2 完成
    workflow.layer2.status = "completed"
    workflow.complete_current_phase()

    print("\nLayer2 完成后:")
    print(f"  当前阶段: {workflow.current_phase.value}")

    # 获取进度
    print("\n进度:")
    print(workflow.get_progress())


if __name__ == "__main__":
    main()