#!/usr/bin/env python3
"""
CyberTeam V4 - Swarm Orchestrator
群体智能编排器 - 实现完整的 Swarm Intelligence

核心功能:
1. Leader Agent 创建子 Agent (独立 Worktree + tmux)
2. 任务分配 + 依赖链管理
3. Agent 间消息传递
4. 监控进度 + 动态调整
5. 结果汇聚
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

from spawn import TmuxBackend, SpawnRegistryManager, check_all_alive, AgentInfo
from spawn.registry import is_agent_alive
from workspace import WorkspaceManager, WorkspaceInfo
from team import TaskStore, MailboxManager, TaskStatus, TaskItem, TeamMessage, MessageType


class SwarmStatus(Enum):
    """群体状态"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    IDLE = "idle"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SubAgent:
    """子 Agent"""
    name: str
    role: str
    task_id: Optional[str] = None
    workspace: Optional[WorkspaceInfo] = None
    tmux_target: Optional[str] = None
    status: str = "pending"  # pending, running, idle, completed, failed
    result: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_report: Optional[str] = None


@dataclass
class ExecutionResult:
    """执行结果"""
    status: str  # success, failure, partial
    outputs: Dict[str, Any]  # agent_name -> output
    summary: str
    metrics: Dict[str, Any] = field(default_factory=dict)


class SwarmOrchestrator:
    """
    群体智能编排器

    实现人类只需提供初始目标，群体智能完成剩下的一切。
    """

    # 协作提示词模板
    COORDINATION_PROMPT = """
## CyberTeam Swarm Coordination Protocol

You are {agent_name}, a sub-agent in the CyberTeam swarm team "{team_name}".

### Your Role
{role}

### Current Task
{task}

### Coordination Commands
Available commands (use cyberteam or direct file ops):

1. Check tasks:
   - Read ~/.cyberteam/tasks/{team_name}/task-*.json

2. Update task status:
   - Write status to ~/.cyberteam/tasks/{team_name}/task-<task_id>.json

3. Send message to leader:
   - Write to ~/.cyberteam/teams/{team_name}/inboxes/leader/msg-*.json

4. Report idle:
   - Send "idle" message to leader

### Workflow
1. Check your assigned task
2. Execute the task
3. Report progress to leader
4. Wait for next instruction

Remember: You are part of a swarm. Coordinate with other agents via messages.
"""

    def __init__(
        self,
        team_name: str,
        goal: str,
        repo_root: Optional[Path] = None,
        spawn_backend: str = "tmux"
    ):
        self.team_name = team_name
        self.goal = goal
        self.repo_root = repo_root or Path.cwd()

        # 核心组件
        self.tmux = TmuxBackend(team_name)
        self.workspace_manager = WorkspaceManager(team_name, repo_root=self.repo_root)
        self.task_store = TaskStore(team_name)
        self.mailbox = MailboxManager(team_name)
        self.registry = SpawnRegistryManager(team_name)

        # 状态
        self.status = SwarmStatus.INITIALIZING
        self.leader_id = str(uuid.uuid4())[:8]
        self.agents: Dict[str, SubAgent] = {}
        self.started_at = datetime.utcnow().isoformat()

    def create_agent(
        self,
        name: str,
        role: str,
        task: Optional[str] = None,
        workspace: bool = True
    ) -> SubAgent:
        """
        创建子 Agent (Leader 调用)

        Args:
            name: Agent 名称
            role: Agent 角色
            task: 初始任务描述
            workspace: 是否创建独立 Worktree

        Returns:
            SubAgent
        """
        agent_id = str(uuid.uuid4())[:8]

        # 1. 创建 Worktree (可选)
        ws_info = None
        if workspace:
            try:
                ws_info = self.workspace_manager.create_workspace(
                    agent_name=name,
                    agent_id=agent_id,
                    base_branch="HEAD"
                )
            except Exception as e:
                print(f"Warning: Failed to create workspace for {name}: {e}")

        # 2. 创建 Task
        task_item = None
        if task:
            task_item = self.task_store.create(
                subject=f"[{name}] {task}",
                description=f"Assigned to {name}, role: {role}",
                owner=name
            )

        # 3. 构建 Agent
        agent = SubAgent(
            name=name,
            role=role,
            task_id=task_item.task_id if task_item else None,
            workspace=ws_info,
            status="running"
        )

        self.agents[name] = agent
        return agent

    def spawn_agent(
        self,
        name: str,
        role: str,
        command: str,
        task: Optional[str] = None,
        prompt: Optional[str] = None,
        workspace: bool = True
    ) -> SubAgent:
        """
        Spawn Agent 到 tmux (独立进程)

        Args:
            name: Agent 名称
            role: Agent 角色
            command: 启动命令
            task: 任务描述
            prompt: 协作提示词
            workspace: 是否创建独立 Worktree

        Returns:
            SubAgent
        """
        # 1. 创建 Agent
        agent = self.create_agent(name, role, task, workspace=workspace)

        # 2. 生成提示词
        coordination_prompt = self._build_prompt(name, role, task or "Awaiting instructions")

        # 3. Spawn 到 tmux
        try:
            agent_info = self.tmux.spawn(
                agent_name=name,
                command=command,
                prompt=coordination_prompt if prompt is None else prompt,
                cwd=Path(agent.workspace.worktree_path) if agent.workspace else None
            )
            agent.tmux_target = agent_info.tmux_target
        except Exception as e:
            agent.status = "failed"
            print(f"Warning: Failed to spawn {name}: {e}")

        return agent

    def _build_prompt(self, name: str, role: str, task: str) -> str:
        """构建协作提示词"""
        return self.COORDINATION_PROMPT.format(
            agent_name=name,
            team_name=self.team_name,
            role=role,
            task=task
        )

    def assign_task(
        self,
        agent_name: str,
        task: str,
        blocked_by: Optional[List[str]] = None
    ) -> TaskItem:
        """
        分配任务给 Agent

        Args:
            agent_name: Agent 名称
            task: 任务描述
            blocked_by: 依赖的任务 IDs

        Returns:
            TaskItem
        """
        task_item = self.task_store.create(
            subject=f"[{agent_name}] {task}",
            description=f"Assigned to {agent_name}",
            owner=agent_name,
            blocked_by=blocked_by
        )

        # 更新 Agent 状态
        if agent_name in self.agents:
            self.agents[agent_name].task_id = task_item.task_id

        # 发送消息通知 Agent
        self.mailbox.send(
            from_agent="leader",
            to=agent_name,
            content=f"New task assigned: {task}",
            msg_type=MessageType.MESSAGE
        )

        return task_item

    def send_message(
        self,
        from_agent: str,
        to: str,
        content: str,
        msg_type: MessageType = MessageType.MESSAGE
    ) -> TeamMessage:
        """发送消息"""
        return self.mailbox.send(from_agent, to, content, msg_type)

    def broadcast(self, from_agent: str, content: str) -> None:
        """广播消息"""
        self.mailbox.send(from_agent, "*", content, MessageType.BROADCAST)

    def check_agent_alive(self, agent_name: str) -> Optional[bool]:
        """检查 Agent 是否存活"""
        return is_agent_alive(self.team_name, agent_name)

    def check_all_alive(self) -> Dict[str, Optional[bool]]:
        """检查所有 Agent 存活状态"""
        return check_all_alive(self.team_name)

    def monitor_progress(self) -> Dict[str, Any]:
        """监控进度"""
        alive_status = self.check_all_alive()

        # 更新 Agent 状态
        for name, agent in self.agents.items():
            if agent.status not in ("completed", "failed"):
                alive = alive_status.get(name)
                if alive is False:
                    agent.status = "failed"
                elif alive is True:
                    if agent.status == "pending":
                        agent.status = "running"

        # 获取任务统计
        task_stats = self.task_store.get_stats()

        return {
            "team_name": self.team_name,
            "goal": self.goal,
            "status": self.status.value,
            "agents": {
                name: {
                    "role": agent.role,
                    "status": agent.status,
                    "task_id": agent.task_id,
                    "alive": alive_status.get(name)
                }
                for name, agent in self.agents.items()
            },
            "tasks": task_stats,
            "started_at": self.started_at
        }

    def resolve_dependencies(self, task_ids: List[str]) -> List[List[str]]:
        """解析任务依赖，返回执行顺序"""
        return self.task_store.resolve_dependencies(task_ids)

    def complete_task(self, task_id: str, result: str) -> None:
        """完成任务"""
        self.task_store.update(task_id, status=TaskStatus.COMPLETED, result=result)

    def fail_task(self, task_id: str, error: str) -> None:
        """标记任务失败"""
        self.task_store.update(task_id, status=TaskStatus.FAILED, error=error)

    def terminate_agent(self, agent_name: str, delete_workspace: bool = True) -> bool:
        """
        终止 Agent

        Args:
            agent_name: Agent 名称
            delete_workspace: 是否删除 Worktree

        Returns:
            是否成功
        """
        if agent_name not in self.agents:
            return False

        agent = self.agents[agent_name]

        # 1. 杀死 tmux window
        try:
            self.tmux.kill_window(agent_name)
        except Exception:
            pass

        # 2. 删除 workspace
        if delete_workspace and agent.workspace:
            try:
                self.workspace_manager.remove_workspace(agent_name)
            except Exception:
                pass

        # 3. 更新状态
        agent.status = "failed"

        return True

    def merge_all_workspaces(self, target_branch: str = "main") -> Dict[str, str]:
        """
        合并所有工作区到主分支

        Returns:
            agent_name -> commit_hash
        """
        results = {}

        for name, agent in self.agents.items():
            if agent.workspace:
                try:
                    # 提交
                    commit_hash = self.workspace_manager.commit_workspace(name)
                    # 合并
                    self.workspace_manager.merge_workspace(name, target_branch)
                    results[name] = commit_hash
                except Exception as e:
                    results[name] = f"Error: {e}"

        return results

    def get_result(self) -> ExecutionResult:
        """获取执行结果"""
        outputs = {}

        for name, agent in self.agents.items():
            if agent.task_id:
                task = self.task_store.get(agent.task_id)
                if task:
                    outputs[name] = {
                        "status": task.status.value,
                        "result": task.result,
                        "error": task.error
                    }

        # 判断整体状态
        all_completed = all(
            self.task_store.get(a.task_id).status == TaskStatus.COMPLETED
            for a in self.agents.values()
            if a.task_id
        )
        any_failed = any(
            self.task_store.get(a.task_id).status == TaskStatus.FAILED
            for a in self.agents.values()
            if a.task_id
        )

        if all_completed:
            status = "success"
        elif any_failed:
            status = "failure"
        else:
            status = "partial"

        return ExecutionResult(
            status=status,
            outputs=outputs,
            summary=f"Swarm completed with status: {status}",
            metrics={
                "total_agents": len(self.agents),
                "completed": sum(1 for a in self.agents.values() if a.status == "completed"),
                "failed": sum(1 for a in self.agents.values() if a.status == "failed")
            }
        )

    def shutdown(self) -> None:
        """关闭群体"""
        # 终止所有 Agent
        for name in list(self.agents.keys()):
            self.terminate_agent(name, delete_workspace=False)

        # 杀死 tmux session
        try:
            self.tmux.kill_session()
        except Exception:
            pass

        self.status = SwarmStatus.COMPLETED


def main():
    """CLI 测试"""
    print("Swarm Orchestrator 测试")
    print("=" * 50)

    # 创建群体
    swarm = SwarmOrchestrator(
        team_name="test-swarm",
        goal="完成测试任务"
    )

    print(f"\n创建群体: {swarm.team_name}")
    print(f"目标: {swarm.goal}")

    # 创建 Agent
    print("\n创建 Agent:")
    agent1 = swarm.create_agent("researcher", "研究员", "搜索资料")
    print(f"  - researcher: {agent1.name} ({agent1.role})")

    agent2 = swarm.create_agent("writer", "写手", "撰写报告", workspace=False)
    print(f"  - writer: {agent2.name} ({agent2.role})")

    # 分配任务 (带依赖)
    print("\n分配任务:")
    task1 = swarm.assign_task("researcher", "搜索最新 AI 进展")
    print(f"  - researcher: {task1.subject} (ID: {task1.task_id})")

    task2 = swarm.assign_task("writer", "撰写报告", blocked_by=[task1.task_id])
    print(f"  - writer: {task2.subject} (blocked_by: {task1.task_id})")

    # 监控
    print("\n监控进度:")
    progress = swarm.monitor_progress()
    print(f"  状态: {progress['status']}")
    print(f"  Agent 数: {len(progress['agents'])}")
    print(f"  任务统计: {progress['tasks']}")

    # 完成任务
    print("\n完成任务1...")
    swarm.complete_task(task1.task_id, "找到 10 篇相关资料")

    # 检查任务2状态
    task2_updated = swarm.task_store.get(task2.task_id)
    print(f"任务2状态: {task2_updated.status.value} (应该自动解除阻塞)")


if __name__ == "__main__":
    main()
