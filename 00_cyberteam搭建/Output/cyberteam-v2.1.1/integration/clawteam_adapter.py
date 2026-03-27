# CyberTeam v2 - ClawTeam 集成适配器 v2

"""
ClawTeam 集成适配器
将 CyberTeam v2 与 ClawTeam CLI 无缝集成
"""

import subprocess
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ClawTeamConfig:
    """ClawTeam 配置"""
    workspace_root: str = "~/.cyberteam/workspace"
    team_prefix: str = "cyber"
    default_model: str = "claude-opus-4-6"
    auto_cleanup: bool = True


# 管理层角色配置
MANAGEMENT_ROLES = {
    "strategy": {
        "name": "战略总监",
        "agent_type": "general-purpose",
        "focus": "战略规划、竞争分析、商业模式",
        "triggers": ["战略", "竞争", "规划", "商业模式"]
    },
    "product": {
        "name": "产品总监",
        "agent_type": "general-purpose",
        "focus": "产品规划、需求管理、产品迭代",
        "triggers": ["产品", "功能", "需求", "迭代"]
    },
    "tech": {
        "name": "技术总监",
        "agent_type": "general-purpose",
        "focus": "技术架构、技术选型、研发管理",
        "triggers": ["技术", "架构", "开发", "代码"]
    },
    "design": {
        "name": "设计总监",
        "agent_type": "general-purpose",
        "focus": "设计战略、设计系统、用户体验",
        "triggers": ["设计", "UI", "UX", "品牌"]
    },
    "ops": {
        "name": "运营总监",
        "agent_type": "general-purpose",
        "focus": "运营策略、流程优化、效率提升",
        "triggers": ["运营", "流程", "效率", "优化"]
    },
    "finance": {
        "name": "财务总监",
        "agent_type": "general-purpose",
        "focus": "财务规划、成本控制、投资决策",
        "triggers": ["财务", "成本", "预算", "投资"]
    },
    "marketing": {
        "name": "市场总监",
        "agent_type": "general-purpose",
        "focus": "市场策略、品牌推广、增长获客",
        "triggers": ["市场", "品牌", "增长", "获客"]
    },
    "hr": {
        "name": "人力总监",
        "agent_type": "general-purpose",
        "focus": "人才战略、组织设计、文化建设",
        "triggers": ["人才", "组织", "团队", "招聘"]
    }
}


class ClawTeamAdapter:
    """ClawTeam 适配器"""

    def __init__(self, config: ClawTeamConfig = None):
        self.config = config or ClawTeamConfig()

    def _run_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
        """运行 ClawTeam 命令"""
        try:
            result = subprocess.run(
                ["clawteam"] + cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except FileNotFoundError:
            return {"success": False, "error": "ClawTeam not found. Install: npm install -g clawteam"}

    # === 团队管理 ===

    def create_team(self, team_name: str, description: str = "") -> Dict[str, Any]:
        """创建团队"""
        logger.info(f"Creating team: {team_name}")
        return self._run_command(["team", "spawn-team", team_name, "-d", description])

    def list_teams(self) -> Dict[str, Any]:
        """列出所有团队"""
        return self._run_command(["team", "list"])

    def get_team_status(self, team: str) -> Dict[str, Any]:
        """获取团队状态"""
        return self._run_command(["team", "status", "--team", team])

    def shutdown_team(self, team: str) -> Dict[str, Any]:
        """关闭团队"""
        return self._run_command(["team", "shutdown", "--team", team])

    # === Agent 管理 ===

    def spawn_agent(
        self,
        agent_name: str,
        prompt: str,
        team: str,
        agent_type: str = "general-purpose",
        model: str = None
    ) -> Dict[str, Any]:
        """Spawn 一个 Agent"""
        model = model or self.config.default_model

        # 构建 spawn 命令
        cmd = [
            "spawn",
            agent_type,
            "--agent-name", agent_name,
            "--task", prompt[:500],  # 限制长度
            "--team", team
        ]

        logger.info(f"Spawning agent: {agent_name} to team: {team}")
        return self._run_command(cmd)

    def spawn_management_team(
        self,
        team: str,
        roles: List[str],
        goal: str
    ) -> Dict[str, Any]:
        """Spawn 管理层团队"""
        results = []
        spawned = []

        for role in roles:
            if role not in MANAGEMENT_ROLES:
                logger.warning(f"Unknown role: {role}")
                continue

            config = MANAGEMENT_ROLES[role]

            # 构建 prompt
            prompt = f"""你是 CyberTeam {config['name']}。

团队目标：{goal}

你的职责：
1. 接收 CEO 分发的任务
2. 用 {config['focus']} 进行分析规划
3. 分解任务并分发执行
4. 监督执行并汇报进展

请准备好接收任务。"""

            result = self.spawn_agent(
                agent_name=role,
                prompt=prompt,
                team=team,
                agent_type=config["agent_type"]
            )

            results.append({
                "role": role,
                "name": config["name"],
                "result": result
            })

            if result["success"]:
                spawned.append(role)

        return {
            "success": len(spawned) > 0,
            "spawned": spawned,
            "total": len(roles),
            "results": results
        }

    def spawn_multiple(
        self,
        agents: List[Dict[str, str]],
        team: str
    ) -> Dict[str, Any]:
        """并行 Spawn 多个 Agent"""
        results = []
        spawned = []

        for agent in agents:
            result = self.spawn_agent(
                agent_name=agent["name"],
                prompt=agent.get("prompt", ""),
                team=team,
                agent_type=agent.get("type", "general-purpose"),
                model=agent.get("model")
            )
            results.append(result)
            if result["success"]:
                spawned.append(agent["name"])

        return {
            "success": len(spawned) == len(agents),
            "spawned": spawned,
            "total": len(agents),
            "results": results
        }

    # === 任务管理 ===

    def create_task(
        self,
        task_id: str,
        description: str,
        team: str,
        assignee: str = None
    ) -> Dict[str, Any]:
        """创建任务"""
        cmd = ["task", "create", task_id, "--description", description[:200], "--team", team]
        if assignee:
            cmd.extend(["--assignee", assignee])

        result = self._run_command(cmd)
        if result["success"]:
            logger.info(f"Task created: {task_id}")
        return result

    def assign_task(self, task_id: str, assignee: str, team: str) -> Dict[str, Any]:
        """分配任务"""
        return self._run_command([
            "task", "assign", task_id, "--to", assignee, "--team", team
        ])

    def update_task_status(self, task_id: str, status: str, team: str) -> Dict[str, Any]:
        """更新任务状态"""
        return self._run_command([
            "task", "update", task_id, "--status", status, "--team", team
        ])

    def list_tasks(self, team: str, status: str = None, owner: str = None) -> Dict[str, Any]:
        """列出团队任务"""
        cmd = ["task", "list", "--team", team]
        if status:
            cmd.extend(["--status", status])
        if owner:
            cmd.extend(["--owner", owner])
        return self._run_command(cmd)

    def distribute_tasks(
        self,
        team: str,
        tasks: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """分发任务"""
        results = []

        for task_info in tasks:
            # 创建任务
            create_result = self.create_task(
                task_id=task_info["id"],
                description=task_info.get("description", ""),
                team=team
            )

            # 分配任务
            if task_info.get("assignee") and create_result["success"]:
                assign_result = self.assign_task(
                    task_id=task_info["id"],
                    assignee=task_info["assignee"],
                    team=team
                )
            else:
                assign_result = {"success": True}

            results.append({
                "task_id": task_info["id"],
                "created": create_result["success"],
                "assigned": assign_result.get("success", False)
            })

        return {
            "success": all(r["created"] for r in results),
            "total": len(tasks),
            "results": results
        }

    # === 消息传递 ===

    def send_message(self, to: str, message: str, team: str) -> Dict[str, Any]:
        """发送消息"""
        return self._run_command([
            "message", "send", to,
            "--message", message[:500],
            "--team", team
        ])

    def get_inbox(self, team: str) -> Dict[str, Any]:
        """获取收件箱"""
        return self._run_command(["inbox", "--team", team])

    # === Worktree ===

    def launch_worktree(self, branch: str, team: str) -> Dict[str, Any]:
        """启动 Git Worktree"""
        return self._run_command([
            "worktree", "create", "--branch", branch, "--team", team
        ])

    def cleanup_worktree(self, branch: str) -> Dict[str, Any]:
        """清理 Worktree"""
        return self._run_command(["worktree", "cleanup", "--branch", branch])


class CyberTeamLauncher:
    """CyberTeam 启动器 - 封装 ClawTeam 操作"""

    def __init__(self, adapter: ClawTeamAdapter = None):
        self.adapter = adapter or ClawTeamAdapter()

    def launch(
        self,
        goal: str,
        team_name: str = None,
        management_roles: List[str] = None,
        auto_tasks: bool = True
    ) -> Dict[str, Any]:
        """启动 CyberTeam v2"""

        import datetime
        team_name = team_name or f"cyber-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"

        result = {
            "team_name": team_name,
            "goal": goal,
            "steps": [],
            "management_team": [],
            "tasks": []
        }

        # 1. 创建团队
        step1 = self.adapter.create_team(team_name, f"CyberTeam for: {goal}")
        result["steps"].append({"step": "create_team", "success": step1["success"]})

        if not step1["success"]:
            result["error"] = f"Failed to create team: {step1.get('stderr')}"
            return result

        # 2. Spawn CEO Agent
        ceo_prompt = f"""你是 CyberTeam CEO，总指挥。

目标：{goal}

请按以下流程执行：
1. 5W1H1Y 拆解用户目标
2. MECE 分类问题
3. 组建管理层团队（需要时 spawn）
4. 分发任务并监督执行
5. 持续直到达成目标

立即开始执行。"""

        ceo_result = self.adapter.spawn_agent(
            agent_name="ceo",
            prompt=ceo_prompt,
            team=team_name,
            agent_type="general-purpose"
        )
        result["steps"].append({"step": "spawn_ceo", "success": ceo_result["success"]})

        # 3. Spawn 管理层 Agents
        if management_roles:
            mgmt_result = self.adapter.spawn_management_team(
                team=team_name,
                roles=management_roles,
                goal=goal
            )
            result["steps"].append({"step": "spawn_management", "success": mgmt_result["success"]})
            result["management_team"] = mgmt_result.get("spawned", [])

            # 4. 创建并分发初始任务
            if auto_tasks and mgmt_result.get("spawned"):
                initial_tasks = self._generate_initial_tasks(goal, mgmt_result["spawned"])
                task_result = self.adapter.distribute_tasks(team_name, initial_tasks)
                result["steps"].append({"step": "distribute_tasks", "success": task_result["success"]})
                result["tasks"] = initial_tasks

        result["success"] = all(s.get("success", False) for s in result["steps"])

        return result

    def _generate_initial_tasks(self, goal: str, roles: List[str]) -> List[Dict[str, str]]:
        """生成初始任务"""
        tasks = []
        task_id = 1

        for role in roles:
            if role in MANAGEMENT_ROLES:
                config = MANAGEMENT_ROLES[role]
                tasks.append({
                    "id": f"task-{task_id:03d}",
                    "description": f"[{config['name']}] 分析 {goal[:50]}...，制定{config['focus']}方案",
                    "assignee": role
                })
                task_id += 1

        # 添加一个汇总任务
        tasks.append({
            "id": f"task-{task_id:03d}",
            "description": "[CEO] 汇总各方分析，形成完整执行计划",
            "assignee": "ceo"
        })

        return tasks


# 预定义团队配置
TEAM_PRESETS = {
    "full": ["strategy", "product", "tech", "design", "ops", "finance", "marketing", "hr"],
    "minimal": ["strategy", "product", "tech"],
    "growth": ["strategy", "product", "marketing", "ops"],
    "product_launch": ["strategy", "product", "tech", "design", "marketing"],
    "technical": ["strategy", "tech"],
    "startup": ["strategy", "product", "tech", "ops", "finance"]
}


if __name__ == "__main__":
    # 测试
    adapter = ClawTeamAdapter()

    # 检查 ClawTeam 是否可用
    status = adapter._run_command(["--version"])
    print(f"ClawTeam status: {status}")
