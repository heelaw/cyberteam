#!/usr/bin/env python3
"""
CyberTeam V4 - 部门间 Handoff 协议 (L3)

职责：
1. HandoffStateMachine - 状态机管理
2. HandoffMessage - 交接消息格式
3. HandoffValidator - 交接验证器
4. HandoffManager - 交接管理器

Handoff流程：
IDLE → PENDING → ACTIVE → COMPLETED
                ↓          ↓
            CANCELLED    FAILED
"""

import uuid
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable
from datetime import datetime


class HandoffState(Enum):
    """Handoff状态枚举"""
    IDLE = "idle"           # 空闲/初始状态
    PENDING = "pending"     # 待接收
    ACTIVE = "active"       # 进行中
    COMPLETED = "completed" # 已完成
    FAILED = "failed"       # 失败
    CANCELLED = "cancelled" # 已取消


@dataclass
class HandoffMessage:
    """交接消息格式"""
    handoff_id: str                      # 唯一标识
    from_agent: str                       # 源Agent
    to_agent: str                         # 目标Agent
    task_id: str                          # 关联任务ID
    context: Dict = field(default_factory=dict)  # 上下文数据
    handover_notes: str = ""              # 交接备注

    # 元数据
    created_at: str = ""                  # 创建时间
    updated_at: str = ""                  # 更新时间
    state: HandoffState = HandoffState.IDLE

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "handoff_id": self.handoff_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "task_id": self.task_id,
            "context": self.context,
            "handover_notes": self.handover_notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state": self.state.value
        }


class HandoffValidator:
    """交接验证器"""

    # 必填上下文字段
    REQUIRED_CONTEXT_FIELDS = ["task_title", "task_description"]

    # 最小上下文字段（可选但推荐）
    RECOMMENDED_CONTEXT_FIELDS = ["priority", "deadline", "dependencies"]

    def validate_context(self, msg: HandoffMessage) -> bool:
        """
        验证上下文完整性

        Returns:
            bool: 验证是否通过
        """
        if not msg.context:
            return False

        # 检查必填字段
        for field in self.REQUIRED_CONTEXT_FIELDS:
            if field not in msg.context:
                return False

        return True

    def validate_prerequisites(self, task_id: str) -> List[str]:
        """
        验证任务前置条件

        Args:
            task_id: 任务ID

        Returns:
            List[str]: 未满足的前置条件列表，空列表表示全部满足
        """
        # TODO: 实际实现时应从任务管理系统获取前置条件
        # 这里返回空列表表示默认全部满足
        return []

    def validate_agents(self, from_agent: str, to_agent: str) -> bool:
        """
        验证Agent有效性

        Args:
            from_agent: 源Agent
            to_agent: 目标Agent

        Returns:
            bool: Agent是否有效
        """
        if not from_agent or not to_agent:
            return False
        if from_agent == to_agent:
            return False
        return True


class HandoffStateMachine:
    """Handoff状态机"""

    # 合法状态转换
    VALID_TRANSITIONS = {
        HandoffState.IDLE: [HandoffState.PENDING],
        HandoffState.PENDING: [HandoffState.ACTIVE, HandoffState.CANCELLED],
        HandoffState.ACTIVE: [HandoffState.COMPLETED, HandoffState.FAILED],
        HandoffState.COMPLETED: [],
        HandoffState.FAILED: [],
        HandoffState.CANCELLED: []
    }

    def __init__(self):
        self._state: HandoffState = HandoffState.IDLE
        self._history: List[HandoffState] = []

    @property
    def state(self) -> HandoffState:
        """获取当前状态"""
        return self._state

    @property
    def history(self) -> List[HandoffState]:
        """获取状态历史"""
        return self._history.copy()

    def can_transition(self, target_state: HandoffState) -> bool:
        """检查是否可以从当前状态转换到目标状态"""
        valid_targets = self.VALID_TRANSITIONS.get(self._state, [])
        return target_state in valid_targets

    def transition(self, target_state: HandoffState) -> bool:
        """
        执行状态转换

        Args:
            target_state: 目标状态

        Returns:
            bool: 转换是否成功
        """
        if not self.can_transition(target_state):
            return False

        self._history.append(self._state)
        self._state = target_state
        return True

    def reset(self):
        """重置状态机到初始状态"""
        self._history.append(self._state)
        self._state = HandoffState.IDLE

    def is_terminal(self) -> bool:
        """检查是否处于终态"""
        return self._state in [
            HandoffState.COMPLETED,
            HandoffState.FAILED,
            HandoffState.CANCELLED
        ]


class HandoffManager:
    """交接管理器"""

    def __init__(self):
        self._handoffs: Dict[str, HandoffMessage] = {}
        self._state_machines: Dict[str, HandoffStateMachine] = {}
        self._validators: Dict[str, HandoffValidator] = {}
        self._callbacks: Dict[str, List[Callable]] = {}  # 状态变更回调

        # 默认验证器
        self._default_validator = HandoffValidator()

    def _get_validator(self, handoff_id: str) -> HandoffValidator:
        """获取验证器"""
        return self._validators.get(handoff_id, self._default_validator)

    def _create_handoff_id(self) -> str:
        """生成唯一handoff_id"""
        return f"hd-{uuid.uuid4().hex[:12]}"

    def _update_timestamp(self, msg: HandoffMessage):
        """更新时间戳"""
        msg.updated_at = datetime.now().isoformat()

    def _trigger_callbacks(self, handoff_id: str, old_state: HandoffState, new_state: HandoffState):
        """触发状态变更回调"""
        callbacks = self._callbacks.get(handoff_id, [])
        for callback in callbacks:
            try:
                callback(handoff_id, old_state, new_state)
            except Exception as e:
                # 回调执行失败不影响主流程
                print(f"回调执行失败: {e}")

    def register_callback(self, handoff_id: str, callback: Callable):
        """注册状态变更回调"""
        if handoff_id not in self._callbacks:
            self._callbacks[handoff_id] = []
        self._callbacks[handoff_id].append(callback)

    def initiate(
        self,
        from_agent: str,
        to_agent: str,
        task: dict
    ) -> HandoffMessage:
        """
        发起交接

        Args:
            from_agent: 源Agent
            to_agent: 目标Agent
            task: 任务数据，包含task_id、context等

        Returns:
            HandoffMessage: 交接消息对象

        Raises:
            ValueError: 参数验证失败
        """
        # 创建消息
        handoff_id = self._create_handoff_id()
        msg = HandoffMessage(
            handoff_id=handoff_id,
            from_agent=from_agent,
            to_agent=to_agent,
            task_id=task.get("task_id", ""),
            context=task.get("context", {}),
            handover_notes=task.get("handover_notes", ""),
            state=HandoffState.IDLE
        )

        # 验证Agent
        validator = self._get_validator(handoff_id)
        if not validator.validate_agents(from_agent, to_agent):
            raise ValueError(f"无效的Agent: from={from_agent}, to={to_agent}")

        # 验证上下文
        if not validator.validate_context(msg):
            raise ValueError("上下文验证失败：缺少必填字段")

        # 创建状态机并转换到PENDING
        sm = HandoffStateMachine()
        sm.transition(HandoffState.PENDING)
        msg.state = sm.state

        # 存储
        self._handoffs[handoff_id] = msg
        self._state_machines[handoff_id] = sm

        self._update_timestamp(msg)
        return msg

    def accept(self, handoff_id: str) -> bool:
        """
        接收交接

        Args:
            handoff_id: 交接ID

        Returns:
            bool: 是否成功
        """
        if handoff_id not in self._handoffs:
            return False

        msg = self._handoffs[handoff_id]
        sm = self._state_machines[handoff_id]
        old_state = sm.state

        if sm.transition(HandoffState.ACTIVE):
            msg.state = sm.state
            self._update_timestamp(msg)
            self._trigger_callbacks(handoff_id, old_state, sm.state)
            return True
        return False

    def complete(self, handoff_id: str, result: dict = None) -> bool:
        """
        完成交接

        Args:
            handoff_id: 交接ID
            result: 可选的完成结果数据

        Returns:
            bool: 是否成功
        """
        if handoff_id not in self._handoffs:
            return False

        msg = self._handoffs[handoff_id]
        sm = self._state_machines[handoff_id]
        old_state = sm.state

        if sm.transition(HandoffState.COMPLETED):
            msg.state = sm.state
            # 更新上下文中的结果
            if result:
                msg.context["result"] = result
            self._update_timestamp(msg)
            self._trigger_callbacks(handoff_id, old_state, sm.state)
            return True
        return False

    def fail(self, handoff_id: str, error: str = "") -> bool:
        """
        标记交接失败

        Args:
            handoff_id: 交接ID
            error: 错误信息

        Returns:
            bool: 是否成功
        """
        if handoff_id not in self._handoffs:
            return False

        msg = self._handoffs[handoff_id]
        sm = self._state_machines[handoff_id]
        old_state = sm.state

        if sm.transition(HandoffState.FAILED):
            msg.state = sm.state
            if error:
                msg.context["error"] = error
            self._update_timestamp(msg)
            self._trigger_callbacks(handoff_id, old_state, sm.state)
            return True
        return False

    def cancel(self, handoff_id: str, reason: str = "") -> bool:
        """
        取消交接

        Args:
            handoff_id: 交接ID
            reason: 取消原因

        Returns:
            bool: 是否成功
        """
        if handoff_id not in self._handoffs:
            return False

        msg = self._handoffs[handoff_id]
        sm = self._state_machines[handoff_id]
        old_state = sm.state

        if sm.transition(HandoffState.CANCELLED):
            msg.state = sm.state
            if reason:
                msg.context["cancel_reason"] = reason
            self._update_timestamp(msg)
            self._trigger_callbacks(handoff_id, old_state, sm.state)
            return True
        return False

    def get_handoff(self, handoff_id: str) -> Optional[HandoffMessage]:
        """获取交接消息"""
        return self._handoffs.get(handoff_id)

    def get_state(self, handoff_id: str) -> Optional[HandoffState]:
        """获取交接状态"""
        sm = self._state_machines.get(handoff_id)
        return sm.state if sm else None

    def list_handoffs(
        self,
        from_agent: str = None,
        to_agent: str = None,
        state: HandoffState = None
    ) -> List[HandoffMessage]:
        """
        列出交接记录

        Args:
            from_agent: 按源Agent过滤
            to_agent: 按目标Agent过滤
            state: 按状态过滤

        Returns:
            List[HandoffMessage]: 匹配的交接列表
        """
        results = list(self._handoffs.values())

        if from_agent:
            results = [h for h in results if h.from_agent == from_agent]
        if to_agent:
            results = [h for h in results if h.to_agent == to_agent]
        if state:
            results = [h for h in results if h.state == state]

        return results

    def get_pending_for_agent(self, agent: str) -> List[HandoffMessage]:
        """获取待该Agent处理的交接"""
        return self.list_handoffs(to_agent=agent, state=HandoffState.PENDING)

    def get_active_for_agent(self, agent: str) -> List[HandoffMessage]:
        """获取该Agent正在处理的交接"""
        return self.list_handoffs(to_agent=agent, state=HandoffState.ACTIVE)

    def cleanup_completed(self, max_age_hours: int = 24) -> int:
        """
        清理已完成的交接记录

        Args:
            max_age_hours: 最长保留时间（小时）

        Returns:
            int: 清理的记录数
        """
        now = datetime.now()
        to_remove = []

        for handoff_id, msg in self._handoffs.items():
            if msg.state in [HandoffState.COMPLETED, HandoffState.FAILED, HandoffState.CANCELLED]:
                created = datetime.fromisoformat(msg.created_at)
                age_hours = (now - created).total_seconds() / 3600
                if age_hours >= max_age_hours:
                    to_remove.append(handoff_id)

        for handoff_id in to_remove:
            del self._handoffs[handoff_id]
            if handoff_id in self._state_machines:
                del self._state_machines[handoff_id]
            if handoff_id in self._callbacks:
                del self._callbacks[handoff_id]

        return len(to_remove)


def main():
    """CLI 测试"""
    manager = HandoffManager()

    print("\n" + "=" * 50)
    print("部门间 Handoff 协议测试")
    print("=" * 50)

    # 测试1: 正常交接流程
    print("\n【测试1】发起交接")
    task = {
        "task_id": "task-001",
        "context": {
            "task_title": "用户分析报告",
            "task_description": "生成季度用户分析报告",
            "priority": "high",
            "deadline": "2026-03-31"
        },
        "handover_notes": "数据已准备好，等待报告生成"
    }
    msg = manager.initiate(
        from_agent="数据分析部",
        to_agent="内容运营部",
        task=task
    )
    print(f"  handoff_id: {msg.handoff_id}")
    print(f"  state: {msg.state.value}")
    print(f"  from: {msg.from_agent}")
    print(f"  to: {msg.to_agent}")

    # 测试2: 状态转换
    print("\n【测试2】状态转换")
    print(f"  accept: {manager.accept(msg.handoff_id)}")
    print(f"  current state: {manager.get_state(msg.handoff_id).value}")

    # 测试3: 完成交接
    print("\n【测试3】完成交接")
    result = {"report_path": "/reports/q1-2026.pdf", "pages": 25}
    print(f"  complete: {manager.complete(msg.handoff_id, result)}")
    print(f"  current state: {manager.get_state(msg.handoff_id).value}")

    # 测试4: 列出交接
    print("\n【测试4】列出所有交接")
    for h in manager.list_handoffs():
        print(f"  - {h.handoff_id}: {h.from_agent} → {h.to_agent} ({h.state.value})")

    # 测试5: 取消交接
    print("\n【测试5】取消交接流程")
    task2 = {
        "task_id": "task-002",
        "context": {
            "task_title": "紧急修复",
            "task_description": "修复生产环境bug"
        }
    }
    msg2 = manager.initiate(
        from_agent="技术研发部",
        to_agent="运维部署部",
        task=task2
    )
    print(f"  initiated: {msg2.handoff_id}, state: {msg2.state.value}")
    print(f"  cancelled: {manager.cancel(msg2.handoff_id, '任务取消')}")
    print(f"  current state: {manager.get_state(msg2.handoff_id).value}")

    # 测试6: 验证器测试
    print("\n【测试6】验证器测试")
    validator = HandoffValidator()
    # 缺少必填字段
    incomplete_msg = HandoffMessage(
        handoff_id="test",
        from_agent="A",
        to_agent="B",
        task_id="t1",
        context={}
    )
    print(f"  空上下文验证: {validator.validate_context(incomplete_msg)}")

    complete_msg = HandoffMessage(
        handoff_id="test2",
        from_agent="A",
        to_agent="B",
        task_id="t2",
        context={"task_title": "测试", "task_description": "描述"}
    )
    print(f"  完整上下文验证: {validator.validate_context(complete_msg)}")

    # 测试7: 状态机测试
    print("\n【测试7】状态机测试")
    sm = HandoffStateMachine()
    print(f"  初始状态: {sm.state.value}")
    print(f"  IDLE → PENDING: {sm.transition(HandoffState.PENDING)}")
    print(f"  当前状态: {sm.state.value}")
    print(f"  PENDING → ACTIVE: {sm.transition(HandoffState.ACTIVE)}")
    print(f"  当前状态: {sm.state.value}")
    print(f"  ACTIVE → COMPLETED: {sm.transition(HandoffState.COMPLETED)}")
    print(f"  当前状态: {sm.state.value}")
    print(f"  状态历史: {[s.value for s in sm.history]}")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()