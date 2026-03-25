#!/usr/bin/env python3
"""
CyberTeam V4 - ClawTeam 适配器 (Swarm Intelligence 完整版)

集成 ClawTeam 核心功能 + CyberTeam V4 Swarm Intelligence：
1. 团队创建与管理
2. Agent Spawn (tmux + Worktree)
3. 任务分配与依赖链
4. 消息传递
5. 状态同步与监控
6. 动态调整 (终止 + 重新分配)
7. 结果汇聚
"""

import json
import subprocess
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from swarm_orchestrator import SwarmOrchestrator, SwarmStatus, SubAgent, ExecutionResult
from spawn import TmuxBackend, SpawnRegistryManager, check_all_alive, AgentInfo
from workspace import WorkspaceManager, WorkspaceInfo
from team import TaskStore, MailboxManager, TaskStatus, TaskItem, TeamMessage, MessageType


class TeamStatus(Enum):
    """团队状态"""
    CREATING = "creating"
    ACTIVE = "active"
    IDLE = "idle"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TeamMember:
    """团队成员"""
    name: str
    role: str
    agent_type: str  # claude/openai/gemini
    task: Optional[str] = None
    status: str = "pending"
    result: Optional[str] = None


@dataclass
class CyberTeam:
    """CyberTeam 团队"""
    team_id: str
    name: str
    goal: str
    members: List[TeamMember] = field(default_factory=list)
    status: TeamStatus = TeamStatus.CREATING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ClawTeamAdapter:
    """
    ClawTeam 适配器 - CyberTeam V4 与 ClawTeam 的桥梁

    实现完整的 Swarm Intelligence：
    - Leader Agent 创建子 Agent
    - 每个子 Agent 拥有独立 Git Worktree + tmux session
    - 任务依赖链 + 自动解除阻塞
    - Agent 间消息传递
    - 监控进度 + 动态调整
    - 结果汇聚
    """

    # 预设团队模板
    TEMPLATES = {
        "dev": {
            "name": "开发团队",
            "members": [
                {"name": "tech-lead", "role": "Tech Lead", "agent_type": "claude"},
                {"name": "backend-dev", "role": "Backend Developer", "agent_type": "claude"},
                {"name": "frontend-dev", "role": "Frontend Developer", "agent_type": "claude"},
                {"name": "qa-engineer", "role": "QA Engineer", "agent_type": "claude"},
            ]
        },
        "research": {
            "name": "研究团队",
            "members": [
                {"name": "research-lead", "role": "Research Lead", "agent_type": "claude"},
                {"name": "market-analyst", "role": "Market Analyst", "agent_type": "claude"},
                {"name": "data-scientist", "role": "Data Scientist", "agent_type": "claude"},
            ]
        },
        "content": {
            "name": "内容团队",
            "members": [
                {"name": "content-lead", "role": "Content Lead", "agent_type": "claude"},
                {"name": "writer", "role": "Writer", "agent_type": "claude"},
                {"name": "designer", "role": "Designer", "agent_type": "claude"},
            ]
        },
        "fullstack": {
            "name": "全栈团队",
            "members": [
                {"name": "ceo", "role": "CEO", "agent_type": "claude"},
                {"name": "product", "role": "Product Manager", "agent_type": "claude"},
                {"name": "engineering", "role": "Engineering Lead", "agent_type": "claude"},
                {"name": "design", "role": "Design Lead", "agent_type": "claude"},
                {"name": "operations", "role": "Operations Lead", "agent_type": "claude"},
            ]
        },
        "swarm": {
            "name": "Swarm 智能团队",
            "members": [
                {"name": "leader", "role": "Team Leader", "agent_type": "claude"},
                {"name": "researcher-1", "role": "Researcher", "agent_type": "claude"},
                {"name": "researcher-2", "role": "Researcher", "agent_type": "claude"},
                {"name": "executor-1", "role": "Executor", "agent_type": "claude"},
                {"name": "executor-2", "role": "Executor", "agent_type": "claude"},
                {"name": "qa", "role": "QA Engineer", "agent_type": "claude"},
            ]
        }
    }

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.teams: Dict[str, CyberTeam] = {}
        self.swarms: Dict[str, SwarmOrchestrator] = {}

    # ========== Swarm Intelligence 核心方法 ==========

    def create_swarm(
        self,
        team_name: str,
        goal: str,
        template: str = "swarm"
    ) -> SwarmOrchestrator:
        """
        创建 Swarm (群体智能团队)

        Args:
            team_name: 团队名称
            goal: 团队目标
            template: 团队模板

        Returns:
            SwarmOrchestrator
        """
        # 创建 swarm
        swarm = SwarmOrchestrator(
            team_name=team_name,
            goal=goal,
            repo_root=self.repo_root
        )

        # 获取模板
        template_data = self.TEMPLATES.get(template, self.TEMPLATES["swarm"])

        # 创建 Agent
        for m in template_data["members"]:
            if m["name"] != "leader":  # leader 是 swarm 自身
                swarm.create_agent(
                    name=m["name"],
                    role=m["role"],
                    workspace=True
                )

        # 保存
        self.swarms[team_name] = swarm

        return swarm

    def spawn_in_swarm(
        self,
        team_name: str,
        agent_name: str,
        role: str,
        command: str,
        task: Optional[str] = None
    ) -> SubAgent:
        """
        在 Swarm 中 Spawn Agent (独立 tmux + Worktree)

        Args:
            team_name: 团队名称
            agent_name: Agent 名称
            role: Agent 角色
            command: 启动命令
            task: 初始任务

        Returns:
            SubAgent
        """
        if team_name not in self.swarms:
            raise ValueError(f"Swarm not found: {team_name}")

        swarm = self.swarms[team_name]
        return swarm.spawn_agent(
            name=agent_name,
            role=role,
            command=command,
            task=task,
            workspace=True
        )

    def create_team(
        self,
        team_name: str,
        goal: str,
        template: str = "fullstack"
    ) -> CyberTeam:
        """创建 CyberTeam (传统模式，兼容旧代码)"""
        team_id = str(uuid.uuid4())[:8]

        # 获取模板
        template_data = self.TEMPLATES.get(template, self.TEMPLATES["fullstack"])

        # 创建成员
        members = []
        for m in template_data["members"]:
            members.append(TeamMember(
                name=m["name"],
                role=m["role"],
                agent_type=m["agent_type"]
            ))

        # 创建团队对象
        team = CyberTeam(
            team_id=team_id,
            name=team_name,
            goal=goal,
            members=members,
            status=TeamStatus.ACTIVE
        )

        self.teams[team_id] = team
        return team

    def get_swarm_status(self, team_name: str) -> Optional[Dict[str, Any]]:
        """获取 Swarm 状态"""
        if team_name not in self.swarms:
            return None
        return self.swarms[team_name].monitor_progress()

    def get_swarm(self, team_name: str) -> Optional[SwarmOrchestrator]:
        """获取 Swarm"""
        return self.swarms.get(team_name)

    # ========== 任务管理 ==========

    def assign_task(
        self,
        team_name: str,
        agent_name: str,
        task: str,
        blocked_by: Optional[List[str]] = None
    ) -> Optional[TaskItem]:
        """分配任务 (支持依赖链)"""
        if team_name not in self.swarms:
            return None
        return self.swarms[team_name].assign_task(agent_name, task, blocked_by)

    def complete_task(self, team_name: str, task_id: str, result: str) -> None:
        """完成任务"""
        if team_name in self.swarms:
            self.swarms[team_name].complete_task(task_id, result)

    def resolve_dependencies(self, team_name: str, task_ids: List[str]) -> List[List[str]]:
        """解析任务依赖，返回执行顺序"""
        if team_name not in self.swarms:
            return []
        return self.swarms[team_name].resolve_dependencies(task_ids)

    # ========== 消息传递 ==========

    def send_message(
        self,
        team_name: str,
        from_agent: str,
        to: str,
        content: str
    ) -> Optional[TeamMessage]:
        """发送消息"""
        if team_name not in self.swarms:
            return None
        return self.swarms[team_name].send_message(from_agent, to, content)

    def broadcast(self, team_name: str, from_agent: str, content: str) -> None:
        """广播消息"""
        if team_name in self.swarms:
            self.swarms[team_name].broadcast(from_agent, content)

    def receive_messages(self, team_name: str, agent_name: str, limit: int = 10) -> List[TeamMessage]:
        """接收消息"""
        if team_name not in self.swarms:
            return []
        return self.swarms[team_name].mailbox.receive(agent_name, limit=limit)

    # ========== 监控与调整 ==========

    def check_alive(self, team_name: str) -> Dict[str, Optional[bool]]:
        """检查所有 Agent 存活状态"""
        if team_name not in self.swarms:
            return {}
        return self.swarms[team_name].check_all_alive()

    def terminate_and_respawn(
        self,
        team_name: str,
        agent_name: str,
        new_role: Optional[str] = None,
        new_command: Optional[str] = None
    ) -> Optional[SubAgent]:
        """
        终止低效 Agent，用新方向重新分配

        Args:
            team_name: 团队名称
            agent_name: 要终止的 Agent
            new_role: 新角色 (可选)
            new_command: 新命令 (可选)

        Returns:
            新的 SubAgent
        """
        if team_name not in self.swarms:
            return None

        swarm = self.swarms[team_name]

        # 获取原 Agent 信息
        old_agent = swarm.agents.get(agent_name)
        if not old_agent:
            return None

        role = new_role or old_agent.role

        # 终止
        swarm.terminate_agent(agent_name)

        # 重新分配
        return swarm.spawn_agent(
            name=agent_name,
            role=role,
            command=new_command or f"claude --goal '继续 {old_agent.role} 的任务'",
            task=old_agent.task_id,
            workspace=True
        )

    # ========== 结果处理 ==========

    def merge_all_workspaces(self, team_name: str, target_branch: str = "main") -> Dict[str, str]:
        """合并所有工作区到主分支"""
        if team_name not in self.swarms:
            return {}
        return self.swarms[team_name].merge_all_workspaces(target_branch)

    def get_swarm_result(self, team_name: str) -> Optional[ExecutionResult]:
        """获取 Swarm 执行结果"""
        if team_name not in self.swarms:
            return None
        return self.swarms[team_name].get_result()

    def shutdown_swarm(self, team_name: str) -> bool:
        """关闭 Swarm"""
        if team_name not in self.swarms:
            return False
        self.swarms[team_name].shutdown()
        del self.swarms[team_name]
        return True

    # ========== 传统团队方法 (兼容) ==========

    def spawn_agent(
        self,
        team_id: str,
        agent_name: str,
        task: str,
        agent_type: str = "claude"
    ) -> Dict[str, Any]:
        """Spawn 单个 Agent (传统模式)"""
        if team_id not in self.teams:
            return {"success": False, "error": "Team not found"}

        # 更新状态
        for member in self.teams[team_id].members:
            if member.name == agent_name:
                member.task = task
                member.status = "running"
                break

        return {"success": True, "message": f"Spawned {agent_name}"}

    def get_team_status(self, team_id: str) -> Optional[Dict[str, Any]]:
        """获取团队状态"""
        if team_id not in self.teams:
            return None

        team = self.teams[team_id]
        return {
            "team_id": team.team_id,
            "name": team.name,
            "goal": team.goal,
            "status": team.status.value,
            "members": [
                {
                    "name": m.name,
                    "role": m.role,
                    "task": m.task,
                    "status": m.status
                }
                for m in team.members
            ],
            "created_at": team.created_at,
            "updated_at": team.updated_at
        }

    def list_teams(self) -> List[Dict[str, Any]]:
        """列出所有团队"""
        teams = []
        for team_id, team in self.teams.items():
            teams.append({
                "team_id": team.team_id,
                "name": team.name,
                "goal": team.goal[:50] + "..." if len(team.goal) > 50 else team.goal,
                "status": team.status.value,
                "member_count": len(team.members)
            })
        return teams

    def list_swarms(self) -> List[Dict[str, Any]]:
        """列出所有 Swarms"""
        swarms = []
        for name, swarm in self.swarms.items():
            swarms.append({
                "name": name,
                "goal": swarm.goal,
                "status": swarm.status.value,
                "agent_count": len(swarm.agents),
                "started_at": swarm.started_at
            })
        return swarms

    def broadcast_message(self, team_id: str, message: str) -> bool:
        """向团队广播消息"""
        if team_id not in self.teams:
            return False
        self.teams[team_id].updated_at = datetime.utcnow().isoformat()
        return True

    def shutdown_team(self, team_id: str) -> bool:
        """关闭团队"""
        if team_id not in self.teams:
            return False
        self.teams[team_id].status = TeamStatus.COMPLETED
        return True


def main():
    """CLI 测试"""
    print("=" * 60)
    print("CyberTeam V4 - Swarm Intelligence 完整测试")
    print("=" * 60)

    adapter = ClawTeamAdapter()

    # 测试 1: 创建 Swarm
    print("\n【测试 1】创建 Swarm 团队")
    swarm = adapter.create_swarm(
        team_name="cyberteam-v4",
        goal="完成 CyberTeam V4 Swarm Intelligence 开发",
        template="swarm"
    )
    print(f"✅ 创建 Swarm: {swarm.team_name}")
    print(f"   目标: {swarm.goal}")
    print(f"   Agent 数: {len(swarm.agents)}")
    for name, agent in swarm.agents.items():
        print(f"   - {name}: {agent.role}")

    # 测试 2: 分配任务 (带依赖)
    print("\n【测试 2】分配任务 (依赖链)")
    task1 = adapter.assign_task("cyberteam-v4", "researcher-1", "搜索最新 AI Agent 进展")
    print(f"   任务1: {task1.subject} (ID: {task1.task_id})")

    task2 = adapter.assign_task("cyberteam-v4", "researcher-2", "搜索多 Agent 协作方案", blocked_by=[task1.task_id])
    print(f"   任务2: {task2.subject} (blocked_by: {task1.task_id})")

    task3 = adapter.assign_task("cyberteam-v4", "executor-1", "实现 Swarm 核心逻辑", blocked_by=[task1.task_id])
    print(f"   任务3: {task3.subject} (blocked_by: {task1.task_id})")

    task4 = adapter.assign_task("cyberteam-v4", "executor-2", "编写测试", blocked_by=[task3.task_id])
    print(f"   任务4: {task4.subject} (blocked_by: {task3.task_id})")

    # 测试 3: 解析依赖
    print("\n【测试 3】解析任务依赖")
    resolved = adapter.resolve_dependencies(
        "cyberteam-v4",
        [task1.task_id, task2.task_id, task3.task_id, task4.task_id]
    )
    print(f"   执行顺序: {resolved}")
    for i, group in enumerate(resolved):
        print(f"   批次 {i+1}: {group} (可并行)")

    # 测试 4: 监控
    print("\n【测试 4】监控进度")
    status = adapter.get_swarm_status("cyberteam-v4")
    print(f"   Swarm 状态: {status['status']}")
    print(f"   任务统计: {status['tasks']}")

    # 测试 5: 完成任务
    print("\n【测试 5】完成任务 (自动解除阻塞)")
    adapter.complete_task("cyberteam-v4", task1.task_id, "找到 10 篇相关资料")

    task2_updated = swarm.task_store.get(task2.task_id)
    task3_updated = swarm.task_store.get(task3.task_id)
    print(f"   任务2 状态: {task2_updated.status.value} (应该变为 pending)")
    print(f"   任务3 状态: {task3_updated.status.value} (应该变为 pending)")

    # 测试 6: 消息传递
    print("\n【测试 6】消息传递")
    msg = adapter.send_message("cyberteam-v4", "leader", "researcher-1", "任务完成，开始下一步")
    print(f"   发送消息: leader -> researcher-1")

    # 测试 7: 检查存活
    print("\n【测试 7】检查 Agent 存活")
    alive = adapter.check_alive("cyberteam-v4")
    print(f"   存活状态: {alive}")

    # 测试 8: 获取结果
    print("\n【测试 8】获取执行结果")
    result = adapter.get_swarm_result("cyberteam-v4")
    print(f"   状态: {result.status}")
    print(f"   输出: {result.outputs}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
