"""
CyberTeam V4 - COO 协调引擎 (L2-协调层)

职责：
1. 接收 CEO 的任务消息（MailboxManager.receive）
2. 分析任务类型，制定讨论议题
3. 向各专家发送讨论邀请
4. 等待专家响应（多轮迭代）
5. 识别分歧点，组织深度讨论
6. 汇总策略方案和风险预案
7. 向 CEO 发送汇报消息

四层对话体系：
- 第一层：CEO → COO（战略对齐）
- 第二层：COO → 专家团队（策略制定）
- 第三层：专家团队内部分歧讨论（深度碰撞）
- 第四层：COO汇总上报（向上汇报）
"""

from .coordinator import (
    COOCoordinator,
    DialogueLayer,
    DiscussionTopic,
    ExpertInvitation,
    DiscussionSession,
    COOSummary,
    WorkflowState,
)
from .workflow import (
    COOWorkflow,
    Layer1Alignment,
    Layer2Strategy,
    Layer3Debate,
    Layer4Reporting,
)

__all__ = [
    # 协调器核心
    "COOCoordinator",
    "DialogueLayer",
    "DiscussionTopic",
    "ExpertInvitation",
    "DiscussionSession",
    "COOSummary",
    "WorkflowState",
    # 工作流
    "COOWorkflow",
    "Layer1Alignment",
    "Layer2Strategy",
    "Layer3Debate",
    "Layer4Reporting",
]