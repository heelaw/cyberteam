# Q67: ClawTeam集成适配器设计

**问题**: 如何将思考天团嫁接到ClawTeam执行框架？包括协议转换、任务调度、状态同步？

**修正历史**:
- 2026-03-22 C7修复: inbox send 使用 `--task task_subject` 替代 `--type task_assignment`
- 2026-03-21 第三轮验证后修正：
  - P0: 所有 `claw` 前缀改为 `cyberteam`，重写 TaskBridge 基于实际 CLI
  - P0: EXPERT_TYPE_MAP 替换3个虚构专家（ai_board→porter_five_forces, five_dimension→mckinsey_7s, manager_leap→kotter_change）
  - P1: _check_convergence 实现真实收敛逻辑
  - P1: 存储路径统一为 `thinking-team/workspace/`
  - P2: StateSynchronizer storage path 同步修正

---

## 一、集成架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        思考天团 → ClawTeam 集成                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌──────────────┐         ┌──────────────┐         ┌─────────────┐ │
│    │   思考天团   │         │  适配器层    │         │  ClawTeam   │ │
│    │   (协调层)   │◀───────▶│              │◀───────▶│  (执行层)   │ │
│    └──────────────┘         └──────────────┘         └─────────────┘ │
│                                                                         │
│    • 意图识别              • 协议转换              • 任务管理         │
│    • 专家路由              • 格式适配              • Agent调度        │
│    • 结果整合              • 状态同步              • 实时看板         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 数据流

```
用户问题
    │
    ▼
┌─────────────────┐
│   思考天团      │  意图识别 + 专家匹配
│  (Host Agent)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ ExpertAgent     │     │ Adapter         │
│ 协议格式        │────▶│ 转换            │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│ TaskSpec        │     │ ClawTeam        │
│ (思考天团)      │     │ Task + Spawn    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│ spawn_workers   │────▶│ spawn tmux claude│
│                 │     │ + inbox send     │
└─────────────────┘     └─────────────────┘
```

---

## 二、协议转换

### 2.1 思考天团 → ClawTeam

```python
# adapter/thinking_to_claw.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class ExpertTaskSpec:
    """思考天团任务规格"""
    expert_id: str
    prompt: str
    context: Dict = None
    dependencies: List[str] = None

@dataclass
class ClawTaskSpec:
    """ClawTeam任务规格"""
    task_id: str
    subject: str          # task create 的 subject
    description: str      # task create 的 -d description
    owner: str            # 负责的 agent-name
    agent_type: str       # spawn --agent-type
    context: Dict = None
    blocked_by: List[str] = None  # --blocked-by

class ThinkingToClawAdapter:
    """思考天团 → ClawTeam 适配器"""

    # 专家类型映射 (第三轮修正: 替换3个虚构专家框架)
    # 原 ai_board → porter_five_forces (波特五力模型)
    # 原 five_dimension → mckinsey_7s (麦肯锡7S框架)
    # 原 manager_leap → kotter_change (科特变革八步)
    EXPERT_TYPE_MAP = {
        "kahneman": "analyst",
        "first_principle": "strategist",
        "six_hats": "debater",
        "swot_tows": "strategist",
        "five_why": "analyst",
        "goldlin": "strategist",
        "grow": "coach",
        "kiss": "simplifier",
        "mckinsey": "analyst",
        "porter_five_forces": "tech_advisor",
        "reverse_thinking": "critic",
        "mckinsey_7s": "evaluator",
        "wbs": "planner",
        "kotter_change": "leader"
    }

    def convert_task(
        self,
        question_id: str,
        expert_task: ExpertTaskSpec,
        owner: str,
        mode: str = "parallel"
    ) -> ClawTaskSpec:
        """转换任务格式"""

        # 生成 task_id (ClawTeam task JSON 文件名中的 ID)
        task_id = f"{question_id}_{expert_task.expert_id}"

        # 构建 ClawTeam task subject 和 description
        instructions = self._build_instructions(expert_task)

        # 确定 agent type
        agent_type = self.EXPERT_TYPE_MAP.get(
            expert_task.expert_id,
            "general-purpose"
        )

        return ClawTaskSpec(
            task_id=task_id,
            subject=f"专家分析: {expert_task.expert_id}",
            description=instructions,
            owner=owner,
            agent_type=agent_type,
            context=expert_task.context or {},
            blocked_by=expert_task.dependencies or []
        )

    def convert_tasks(
        self,
        question_id: str,
        expert_tasks: List[ExpertTaskSpec],
        mode: str = "parallel"
    ) -> List[ClawTaskSpec]:
        """批量转换任务"""

        tasks = []
        # 并行模式: 每个任务分配独立 worker name
        # 链式模式: 顺序依赖链
        for idx, task in enumerate(expert_tasks):
            owner = f"expert_{task.expert_id}"
            converted = self.convert_task(question_id, task, owner, mode)

            # 链式模式: 前一个任务的 task_id 作为 blocked-by
            if mode == "chain" and tasks:
                converted.blocked_by = [tasks[-1].task_id]

            tasks.append(converted)

        return tasks

    def _build_instructions(self, expert_task: ExpertTaskSpec) -> str:
        """构建专家指令"""

        expert_prompts = {
            "kahneman": """你是一位认知心理学和决策科学专家。
请从认知偏差的角度分析用户问题。

分析维度：
1. 锚定效应 - 用户是否过度依赖初始信息？
2. 确认偏差 - 是否只收集支持自己观点的数据？
3. 损失厌恶 - 用户对损失的敏感度如何？
4. 心理账户 - 用户如何心理上账户分类？

请输出：
- 识别的主要认知偏差
- 每个偏差的具体表现
- 克服这些偏差的建议""",

            "first_principle": """你是一位第一性原理思维专家。
请从本质出发重构问题。

分析步骤：
1. 剥离假设 - 列出所有默认假设
2. 本质分解 - 分解到最基本要素
3. 重新组合 - 从零构建新方案
4. 成本重构 - 重新评估成本结构

请输出：
- 识别的主要假设
- 本质要素分解
- 创新方案建议""",

            # ... 其他专家
        }

        base_prompt = expert_prompts.get(
            expert_task.expert_id,
            f"请以{expert_task.expert_id}专家的角度分析以下问题"
        )

        return f"""
{base_prompt}

---
用户问题：
{expert_task.prompt}

---
请进行深入分析，输出结构化的见解。
"""
```

### 2.2 ClawTeam → 思考天团

```python
# adapter/claw_to_thinking.py
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ClawTaskResult:
    """ClawTeam任务结果"""
    task_id: str
    status: str       # pending/in_progress/completed/failed/blocked
    output: str = ""  # 从 inbox 获取
    error: str = None
    duration: float = 0
    metadata: Dict = None

@dataclass
class ExpertOutput:
    """思考天团专家输出"""
    expert_id: str
    output: str
    key_findings: List[str]
    consensus_points: List[str] = None
    disagreements: List[str] = None

class ClawToThinkingAdapter:
    """ClawTeam → 思考天团 适配器"""

    def convert_result(
        self,
        claw_result: ClawTaskResult,
        expert_id: str
    ) -> ExpertOutput:
        """转换结果格式"""

        extracted_expert = self._extract_expert_id(claw_result.task_id, expert_id)
        output = claw_result.output or ""
        key_findings = self._extract_findings(output)

        return ExpertOutput(
            expert_id=extracted_expert,
            output=output,
            key_findings=key_findings
        )

    def convert_results(
        self,
        claw_results: List[ClawTaskResult],
        expected_experts: List[str]
    ) -> Dict[str, ExpertOutput]:
        """批量转换结果"""

        outputs = {}

        for expert in expected_experts:
            # 找到对应的 ClawTeam 结果
            matching = [
                r for r in claw_results
                if expert in r.task_id
            ]

            if matching:
                outputs[expert] = self.convert_result(matching[0], expert)

        return outputs

    def _extract_expert_id(self, task_id: str, fallback: str) -> str:
        """提取专家ID

        P2修正: 增加格式验证，确保返回的是已知专家框架ID
        """
        import re

        VALID_EXPERTS = {
            "kahneman", "first_principle", "six_hats", "swot_tows",
            "five_why", "goldlin", "grow", "kiss", "mckinsey",
            "porter_five_forces", "reverse_thinking", "mckinsey_7s",
            "wbs", "kotter_change"
        }

        # 尝试从 task_id 提取: question_expertid
        # 格式: q_20260321_143022_001_kahneman
        parts = task_id.split("_")
        if len(parts) >= 2:
            candidate = parts[-1]  # 取最后一段
            # 验证: 必须是已知的专家ID，且只含字母下划线
            if candidate in VALID_EXPERTS and re.match(r'^[a-z_]+$', candidate):
                return candidate

        # 回退: 使用已验证的fallback
        return fallback

    def _extract_findings(self, output: str) -> List[str]:
        """提取关键发现"""
        findings = []

        lines = output.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("1.", "2.", "3.", "•", "-", "●")):
                finding = line.lstrip("1234567890.●-● ").strip()
                if finding and len(finding) > 10:
                    findings.append(finding)

        return findings[:3]
```

---

## 三、任务管理器

### 3.1 TaskBridge (第三轮修正版)

> **修正说明**: 全部 CLI 命令基于 ClawTeam 实际 CLI 重写。
> 原版使用 `claw` 前缀和伪造命令，现已全部替换为 `cyberteam` 实际命令。

```python
# adapter/task_bridge.py
from typing import Dict, List, Optional, Callable
import subprocess
import json
import logging
import time
import re

logger = logging.getLogger(__name__)

class TaskBridge:
    """思考天团 ↔ ClawTeam 任务桥接"""

    def __init__(self, workspace_dir: str = "thinking-team/workspace"):
        # P1修正: 统一使用 Q69 存储规范: thinking-team/workspace/
        self.workspace_dir = workspace_dir

    # ========== 创建团队 ==========
    # cyberteam team spawn-team <name> [-d description] [-n agent-name] [--agent-type type]

    def create_team(
        self,
        team_name: str,
        description: str = ""
    ) -> str:
        """创建 ClawTeam 团队"""

        cmd = [
            "cyberteam", "team", "spawn-team",
            team_name,
            "-d", description or f"Thinking Team: {team_name}",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to create team: {result.stderr}")

        return team_name

    # ========== 创建任务 ==========
    # cyberteam task create <team> <subject> [-d description] [-o owner] [--blocked-by ids]

    def create_task(
        self,
        team_name: str,
        subject: str,
        description: str = "",
        owner: str = "",
        blocked_by: List[str] = None
    ) -> str:
        """创建单个 ClawTeam 任务，返回 task_id"""

        cmd = [
            "cyberteam", "task", "create",
            team_name,
            subject,
            "-d", description,
        ]

        if owner:
            cmd.extend(["-o", owner])

        if blocked_by:
            cmd.extend(["--blocked-by", ",".join(blocked_by)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to create task: {result.stderr}")

        # cyberteam task create 输出 task JSON，解析 task ID
        return self._extract_task_id_from_output(result.stdout)

    def create_tasks(
        self,
        team_name: str,
        task_specs: List[Dict]
    ) -> List[str]:
        """批量创建任务，返回 task_id 列表"""

        task_ids = []

        for spec in task_specs:
            task_id = self.create_task(
                team_name=team_name,
                subject=spec["subject"],
                description=spec.get("description", ""),
                owner=spec.get("owner", ""),
                blocked_by=spec.get("blocked_by")
            )
            task_ids.append(task_id)

        return task_ids

    # ========== Spawn Worker Agent ==========
    # cyberteam spawn <backend> <command...> --team <team> --agent-name <name> --agent-type <type>
    # spawn 后 Agent 通过 inbox 接收任务指令

    def spawn_worker(
        self,
        team_name: str,
        agent_name: str,
        agent_type: str,
        task_id: str,
        task_subject: str,
        task_instructions: str
    ) -> bool:
        """Spawn 一个 worker agent，并通过 inbox 发送任务指令"""

        # 1. Spawn agent process
        spawn_cmd = [
            "cyberteam", "spawn",
            "tmux", "claude",          # backend=tmux, command=claude
            "--team", team_name,
            "--agent-name", agent_name,
            "--agent-type", agent_type,
        ]

        spawn_result = subprocess.run(
            spawn_cmd,
            capture_output=True,
            text=True
        )

        if spawn_result.returncode != 0:
            logger.warning(f"Failed to spawn worker {agent_name}: {spawn_result.stderr}")
            return False

        # 2. 发送任务指令到 worker inbox
        # (spawn 后 cyberteam 自动设置 CLAWTEAM_AGENT_* 环境变量)
        inbox_msg = self._build_task_message(task_id, task_subject, task_instructions)

        inbox_cmd = [
            "cyberteam", "inbox", "send",
            team_name,
            agent_name,
            inbox_msg,
            "--task", task_subject  # P0修复: 使用 --task 而非 --type，以创建 TaskStore 条目
        ]

        inbox_result = subprocess.run(
            inbox_cmd,
            capture_output=True,
            text=True
        )

        if inbox_result.returncode != 0:
            logger.warning(f"Failed to send task to {agent_name}: {inbox_result.stderr}")
            return False

        return True

    def spawn_workers(
        self,
        team_name: str,
        claw_tasks: List[Dict]
    ) -> List[str]:
        """批量 spawn workers"""

        spawned_names = []

        for task in claw_tasks:
            success = self.spawn_worker(
                team_name=team_name,
                agent_name=task["owner"],
                agent_type=task["agent_type"],
                task_id=task["task_id"],
                task_subject=task["subject"],
                task_instructions=task["description"]
            )

            if success:
                spawned_names.append(task["owner"])

        return spawned_names

    def _build_task_message(self, task_id: str, subject: str, instructions: str) -> str:
        """构建 inbox 任务消息"""
        return json.dumps({
            "task_id": task_id,
            "subject": subject,
            "instructions": instructions,
            "format": "expert_analysis"
        }, ensure_ascii=False)

    # ========== 监控任务 ==========
    # cyberteam task list <team> [--status STATUS] [--owner NAME]
    # cyberteam task get <team> <task-id>

    def get_task_status(self, team_name: str, task_id: str) -> Dict:
        """获取单个任务状态"""

        cmd = [
            "cyberteam", "task", "get",
            team_name, task_id
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"task_id": task_id, "status": "unknown", "error": result.stderr}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"task_id": task_id, "status": "unknown", "raw": result.stdout}

    def list_task_statuses(
        self,
        team_name: str,
        status: str = None,
        owner: str = None
    ) -> List[Dict]:
        """列出团队所有任务状态"""

        cmd = [
            "cyberteam", "--json", "task", "list",
            team_name
        ]

        if status:
            cmd.extend(["--status", status])
        if owner:
            cmd.extend(["--owner", owner])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return []

        try:
            output = json.loads(result.stdout)
            # JSON 格式可能是 {"tasks": [...]} 或直接的列表
            if isinstance(output, list):
                return output
            return output.get("tasks", [])
        except json.JSONDecodeError:
            return []

    # ========== 等待任务完成 ==========
    # cyberteam task wait <team> [--timeout SECONDS] [--poll-interval SECONDS]
    # 注: cyberteam task wait 无 --team 参数，team 从 config 读取
    #     轮询实现方式: 反复调用 task list 直到所有任务完成或超时

    def wait_for_tasks(
        self,
        team_name: str,
        task_ids: List[str],
        timeout: float = 300,
        poll_interval: float = 5
    ) -> Dict[str, Dict]:
        """等待任务完成 (轮询实现)"""

        results = {}
        start_time = time.time()
        pending = set(task_ids)

        while pending and (time.time() - start_time) < timeout:
            # 批量查询所有任务状态
            all_tasks = self.list_task_statuses(team_name)

            task_map = {t.get("id", ""): t for t in all_tasks}

            for task_id in list(pending):
                task = task_map.get(task_id, {})
                task_status = task.get("status", "unknown")

                if task_status in ["completed", "failed", "cancelled"]:
                    results[task_id] = {
                        "task_id": task_id,
                        "status": task_status,
                        "owner": task.get("owner", ""),
                        "subject": task.get("subject", ""),
                    }
                    pending.remove(task_id)

            if pending:
                time.sleep(poll_interval)

        # 超时的任务
        for task_id in pending:
            results[task_id] = {
                "task_id": task_id,
                "status": "timeout",
                "error": f"Task timeout after {timeout}s"
            }

        return results

    # ========== 获取结果 ==========
    # cyberteam inbox peek <team> [--agent NAME]
    # worker 完成任务后将结果发送到 leader inbox

    def get_task_output(self, team_name: str, worker_name: str) -> str:
        """从 worker inbox 获取任务输出"""

        cmd = [
            "cyberteam", "inbox", "peek",
            team_name,
            "--agent", worker_name,
            "--limit", "5"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return ""

        # 解析 inbox 消息，查找 task result 类型
        try:
            messages = json.loads(result.stdout) if result.stdout.strip().startswith("[") else []
            for msg in messages:
                if msg.get("type") == "task_result":
                    return msg.get("content", "")
        except (json.JSONDecodeError, TypeError):
            pass

        return result.stdout

    def get_all_outputs(
        self,
        team_name: str,
        worker_names: List[str]
    ) -> Dict[str, str]:
        """获取所有 worker 的输出"""

        outputs = {}

        for worker_name in worker_names:
            outputs[worker_name] = self.get_task_output(team_name, worker_name)

        return outputs

    # ========== 清理 ==========
    # cyberteam team cleanup <team> [--force]

    def cleanup_team(self, team_name: str, force: bool = False):
        """清理团队及其所有数据"""

        cmd = [
            "cyberteam", "team", "cleanup",
            team_name
        ]

        if force:
            cmd.append("--force")

        subprocess.run(
            cmd,
            capture_output=True
        )

    # ========== 看板监控 ==========
    # cyberteam board show <team>
    # cyberteam board live <team> [--interval SECONDS]

    def get_board_state(self, team_name: str) -> Dict:
        """获取看板状态"""

        cmd = [
            "cyberteam", "--json", "board", "show",
            team_name
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {}

    # ========== 辅助方法 ==========

    def _extract_task_id_from_output(self, output: str) -> str:
        """从 cyberteam task create 输出中提取 task ID"""
        # JSON 输出: {"id": "xxx", "subject": "...", ...}
        try:
            data = json.loads(output)
            return data.get("id", "")
        except json.JSONDecodeError:
            pass

        # 回退: 从文本输出中提取
        # 格式: task-{id}.json 或纯 ID
        match = re.search(r'task[_-]?([a-zA-Z0-9_-]+)', output)
        if match:
            return match.group(1)

        return output.strip().split("\n")[0] if output.strip() else ""
```

### 3.2 状态同步器

```python
# adapter/state_sync.py
from typing import Dict, Callable, List
import threading
import time
import json
import logging
import os

logger = logging.getLogger(__name__)

class StateSynchronizer:
    """状态同步器 - 同步 ClawTeam 状态到思考天团"""

    def __init__(self, task_bridge: TaskBridge, sync_interval: float = 2):
        self.task_bridge = task_bridge
        self.sync_interval = sync_interval
        self._running = False
        self._thread = None
        self._callbacks: Dict[str, Callable] = {}

    def start_sync(
        self,
        team_name: str,
        task_ids: List[str],
        on_update: Callable = None,
        on_complete: Callable = None
    ):
        """开始同步"""

        self._running = True
        self._callbacks = {
            "update": on_update,
            "complete": on_complete
        }

        self._thread = threading.Thread(
            target=self._sync_loop,
            args=(team_name, task_ids,)
        )
        self._thread.daemon = True
        self._thread.start()

    def stop_sync(self):
        """停止同步"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _sync_loop(self, team_name: str, task_ids: List):
        """同步循环"""

        pending = set(task_ids)
        results = {}

        while self._running and pending:
            for task_id in list(pending):
                try:
                    status = self.task_bridge.get_task_status(team_name, task_id)

                    if self._callbacks.get("update"):
                        self._callbacks["update"](task_id, status)

                    task_status = status.get("status", "unknown")
                    if task_status in ["completed", "failed", "cancelled"]:
                        results[task_id] = status
                        pending.remove(task_id)

                except Exception as e:
                    logger.error(f"Error syncing task {task_id}: {e}")

            time.sleep(self.sync_interval)

        if self._callbacks.get("complete"):
            self._callbacks["complete"](results)

    # ========== 文件同步 ==========
    # P1修正: 存储路径统一为 thinking-team/workspace/

    def sync_to_file(self, task_id: str, output_file: str):
        """同步到文件"""

        output = self.task_bridge.get_task_output(
            team_name=self._extract_team_from_task_id(task_id),
            worker_name=self._extract_worker_from_task_id(task_id)
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            f.write(output)

    def sync_board_state(self, question_id: str, team_name: str, task_ids: List):
        """同步看板状态到文件"""

        states = {}

        for task_id in task_ids:
            states[task_id] = self.task_bridge.get_task_status(team_name, task_id)

        # P1修正: 使用 Q69 统一存储路径
        board_file = f"{self.task_bridge.workspace_dir}/tasks/{question_id}/board.json"

        os.makedirs(os.path.dirname(board_file), exist_ok=True)
        with open(board_file, "w") as f:
            json.dump(states, f, indent=2)

    def _extract_team_from_task_id(self, task_id: str) -> str:
        """从 task_id 提取 team_name"""
        parts = task_id.split("_")
        return parts[0] if parts else "thinking-team"

    def _extract_worker_from_task_id(self, task_id: str) -> str:
        """从 task_id 提取 worker name"""
        parts = task_id.split("_")
        if len(parts) >= 2:
            return f"expert_{parts[1]}"
        return ""
```

---

## 四、集成执行器

### 4.1 ClawTeamExecutor

```python
# adapter/cyberteam_executor.py
from typing import Dict, List, Optional
import logging
import re

from thinking_to_claw import ThinkingToClawAdapter
from claw_to_thinking import ClawToThinkingAdapter
from task_bridge import TaskBridge
from state_sync import StateSynchronizer

logger = logging.getLogger(__name__)

class ClawTeamExecutor:
    """ClawTeam执行器 - 整合到思考天团"""

    def __init__(
        self,
        workspace_dir: str = "thinking-team/workspace",  # P1修正: Q69 统一路径
        team_name: str = "thinking-team"
    ):
        self.workspace_dir = workspace_dir
        self.team_name = team_name

        self.to_claw = ThinkingToClawAdapter()
        self.from_claw = ClawToThinkingAdapter()
        self.bridge = TaskBridge(workspace_dir)
        self.sync = StateSynchronizer(self.bridge)

    def execute(
        self,
        question_id: str,
        expert_tasks: List[Dict],
        mode: str = "parallel",
        on_progress: callable = None
    ) -> Dict:
        """
        通过 ClawTeam 执行专家任务

        执行流程:
        1. 创建团队 (spawn-team)
        2. 创建任务 (task create)
        3. Spawn workers (spawn tmux claude + inbox send)
        4. 等待完成 (轮询 task list)
        5. 获取输出 (inbox peek)
        6. 转换格式 (ClawToThinkingAdapter)
        7. 清理团队 (team cleanup)
        """

        team_name = f"{self.team_name}_{question_id}"

        # 1. 创建团队
        try:
            self.bridge.create_team(team_name, description=f"Thinking Team for {question_id}")
        except RuntimeError as e:
            # 团队可能已存在，尝试继续
            logger.warning(f"Team may already exist: {e}")

        # 2. 转换任务格式
        expert_specs = [
            {
                "expert_id": t.get("expert_id", "unknown"),
                "prompt": t.get("prompt", t.get("instructions", "")),
                "context": t.get("context"),
                "dependencies": t.get("dependencies")
            }
            for t in expert_tasks
        ]

        claw_tasks = self.to_claw.convert_tasks(
            question_id,
            expert_specs,
            mode
        )

        # 3. 创建 ClawTeam 任务
        task_specs = [
            {
                "subject": t.subject,
                "description": t.description,
                "owner": t.owner,
                "blocked_by": t.blocked_by
            }
            for t in claw_tasks
        ]

        task_ids = self.bridge.create_tasks(team_name, task_specs)

        # 4. Spawn workers 并发送任务
        spawn_specs = []
        for t, task_id in zip(claw_tasks, task_ids):
            spawn_specs.append({
                "task_id": task_id,
                "subject": t.subject,
                "description": t.description,
                "owner": t.owner,
                "agent_type": t.agent_type
            })

        spawned_workers = self.bridge.spawn_workers(team_name, spawn_specs)

        # 5. 等待完成
        if on_progress:
            self.sync.start_sync(
                team_name=team_name,
                task_ids=task_ids,
                on_update=lambda tid, status: on_progress(tid, status)
            )

        results = self.bridge.wait_for_tasks(team_name, task_ids, timeout=300)

        if on_progress:
            self.sync.stop_sync()

        # 6. 获取输出
        outputs = self.bridge.get_all_outputs(team_name, spawned_workers)

        # 7. 转换回思考天团格式
        claw_results = [
            {
                "task_id": tid,
                "status": results.get(tid, {}).get("status", "unknown"),
                "output": outputs.get(worker, ""),
                "owner": results.get(tid, {}).get("owner", worker)
            }
            for tid, worker in zip(task_ids, spawned_workers)
        ]

        expert_outputs = self.from_claw.convert_results(
            claw_results,
            [t.expert_id for t in expert_specs]
        )

        # 8. 清理
        self.bridge.cleanup_team(team_name, force=True)

        return {
            "question_id": question_id,
            "mode": mode,
            "team_name": team_name,
            "task_ids": task_ids,
            "results": results,
            "outputs": expert_outputs
        }

    def execute_chain(
        self,
        question_id: str,
        chain_tasks: List[Dict],
        on_progress: callable = None
    ) -> Dict:
        """链式执行 - 每个专家依赖前一个的输出"""

        return self.execute(
            question_id,
            chain_tasks,
            mode="chain",
            on_progress=on_progress
        )

    def execute_debate(
        self,
        question_id: str,
        debate_tasks: List[Dict],
        max_rounds: int = 3,
        convergence_threshold: float = 0.3,  # P1新增: 收敛阈值
        on_progress: callable = None
    ) -> Dict:
        """辩论模式执行 - 多轮辩论直到收敛"""

        all_outputs = []
        team_name = f"{self.team_name}_{question_id}_debate"

        try:
            self.bridge.create_team(team_name)
        except RuntimeError:
            pass

        for round_num in range(max_rounds):
            round_tasks = self._prepare_debate_round(
                debate_tasks,
                all_outputs,
                round_num
            )

            result = self.execute(
                f"{question_id}_round{round_num}",
                round_tasks,
                mode="parallel",
                on_progress=on_progress
            )

            all_outputs.append(result["outputs"])

            # P1修正: 实现真实收敛检查
            if self._check_convergence(all_outputs, threshold=convergence_threshold):
                logger.info(f"Debate converged at round {round_num + 1}")
                break

        # 清理辩论团队
        self.bridge.cleanup_team(team_name, force=True)

        return {
            "question_id": question_id,
            "rounds": all_outputs,
            "final_outputs": all_outputs[-1] if all_outputs else {},
            "converged": len(all_outputs) < max_rounds
        }

    def _prepare_debate_round(
        self,
        tasks: List[Dict],
        previous_outputs: List,
        round_num: int
    ) -> List[Dict]:
        """准备辩论轮次 - 添加前一轮输出作为上下文"""

        if round_num == 0:
            return tasks

        enriched = []

        for task in tasks:
            enriched_task = task.copy()

            if previous_outputs:
                last_round = previous_outputs[-1]
                context = self._build_debate_context(last_round, task.get("expert_id"))
                enriched_task["prompt"] = f"{task.get('prompt', '')}\n\n前一轮专家观点:\n{context}"

            enriched.append(enriched_task)

        return enriched

    def _build_debate_context(self, outputs: Dict, exclude_expert: str) -> str:
        """构建辩论上下文"""
        context_parts = []

        for expert_id, output in outputs.items():
            if expert_id != exclude_expert:
                content = output.get("output", "")
                # 截取前500字符作为上下文摘要
                if len(content) > 500:
                    content = content[:500] + "..."
                context_parts.append(f"### {expert_id}:\n{content}")

        return "\n\n".join(context_parts)

    # ========== P1修正: 实现真实收敛检查 ==========

    def _check_convergence(
        self,
        outputs: List[Dict],
        threshold: float = 0.3
    ) -> bool:
        """
        检查辩论是否收敛

        收敛条件: 连续两轮中，超过 threshold 比例的专家输出
        与前一轮相比变化很小 (用关键词重叠度衡量)

        Args:
            outputs: 各轮次的输出字典列表
            threshold: 变化率阈值 (默认30%)

        Returns:
            True 如果收敛, False 如果继续
        """

        if len(outputs) < 2:
            return False

        last_round = outputs[-1]
        prev_round = outputs[-2]

        if not last_round or not prev_round:
            return False

        # 计算每个专家的变化率
        total_experts = len(last_round)
        if total_experts == 0:
            return False

        changed_count = 0

        for expert_id, output in last_round.items():
            prev_output = prev_round.get(expert_id, {})
            if not prev_output:
                continue

            # 用关键词集合的重叠度衡量变化
            prev_keywords = set(self._extract_keywords(prev_output.get("output", "")))
            curr_keywords = set(self._extract_keywords(output.get("output", "")))

            if not prev_keywords:
                continue

            # Jaccard 相似度: |A ∩ B| / |A ∪ B|
            overlap = len(prev_keywords & curr_keywords)
            union = len(prev_keywords | curr_keywords)

            if union > 0:
                similarity = overlap / union
                # 变化率 = 1 - 相似度
                change_rate = 1 - similarity
                if change_rate > threshold:
                    changed_count += 1

        # P1修正: 变化比例 <= threshold 则收敛
        change_ratio = changed_count / total_experts
        return change_ratio <= threshold

    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本关键词 (简单实现: 名词和动词)"""
        if not text:
            return []

        # 过滤停用词和短词
        stopwords = {
            "的", "了", "是", "在", "和", "与", "对", "为", "有", "我",
            "the", "a", "an", "is", "are", "and", "or", "but", "to", "of",
            "it", "in", "on", "at", "for", "with", "as", "by", "from"
        }

        words = re.findall(r'[\w\u4e00-\u9fff]{2,}', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 1]

        return keywords
```

---

## 五、配置文件

### 5.1 集成配置

```yaml
# config/cyberteam_integration.yaml
# P1修正: 存储路径统一为 thinking-team/workspace/ (遵循 Q69 规范)

cyberteam:
  enabled: true
  # P1修正: Q69 统一存储根路径
  workspace_dir: "thinking-team/workspace"
  team_name: "thinking-team"

  # 执行配置
  execution:
    max_concurrent: 4
    timeout_minutes: 30
    retry_on_fail: true
    max_retries: 2
    # P1新增: 辩论模式配置
    debate:
      max_rounds: 3
      convergence_threshold: 0.3

  # 同步配置
  sync:
    interval_seconds: 2
    sync_to_file: true
    # P1修正: 遵循 Q69 存储规范
    board_file: "thinking-team/workspace/tasks/{question_id}/board.json"

  # 清理配置
  cleanup:
    auto_cleanup: true
    keep_hours: 24

  # P1修正: 专家类型映射 (替换3个虚构专家)
  expert_mapping:
    kahneman: analyst
    first_principle: strategist
    six_hats: debater
    swot_tows: strategist
    five_why: analyst
    goldlin: strategist
    grow: coach
    kiss: simplifier
    mckinsey: analyst
    # 原 ai_board → 波特五力模型 (Porter Five Forces)
    porter_five_forces: tech_advisor
    reverse_thinking: critic
    # 原 five_dimension → 麦肯锡7S框架 (McKinsey 7S)
    mckinsey_7s: evaluator
    wbs: planner
    # 原 manager_leap → 科特变革八步 (Kotter 8-Step Change)
    kotter_change: leader
```

---

## 六、CLI命令

### 6.1 集成命令

```bash
# 使用 ClawTeam 执行
thinking-team execute --via cyberteam \
  --question "如何提升DAU？" \
  --experts kahneman,grow,first_principle \
  --mode parallel

# 查看 ClawTeam 状态
thinking-team cyberteam status

# 调试: 查看原始输出
thinking-team cyberteam output task_xxx

# 清理 ClawTeam
thinking-team cyberteam cleanup
```

---

## 七、总结

### 7.1 核心组件

| 组件 | 功能 | 文件 |
|------|------|------|
| ThinkingToClawAdapter | 任务格式转换 | thinking_to_claw.py |
| ClawToThinkingAdapter | 结果格式转换 | claw_to_thinking.py |
| TaskBridge | 任务操作桥接 (cyberteam CLI) | task_bridge.py |
| StateSynchronizer | 状态同步 | state_sync.py |
| ClawTeamExecutor | 整合执行器 | cyberteam_executor.py |

### 7.2 执行流程

```
思考天团意图识别
    │
    ▼
创建 ExpertTaskSpec 列表
    │
    ▼
ThinkingToClawAdapter.convert_tasks()
    │
    ▼
cyberteam team spawn-team <team>
    │
    ├─► cyberteam task create <team> <subject> [-o owner] [--blocked-by ids]
    │        (链式模式自动设置 --blocked-by)
    │
    ▼
cyberteam spawn tmux claude --team <team> --agent-name <name> --agent-type <type>
    │
    ├─► cyberteam inbox send <team> <agent> <task JSON> --task <subject>  # P0修复: 使用 --task 创建 TaskStore 条目
    │
    ▼
cyberteam task wait <team> (轮询 task list 实现)
    │
    ├─► cyberteam inbox peek <team> --agent <name>
    │
    ▼
ClawToThinkingAdapter → ExpertOutput
    │
    ▼
cyberteam team cleanup <team> --force
```

### 7.3 第三轮验证修正清单

| 修正项 | 原问题 | 修正后 | 优先级 |
|--------|--------|--------|--------|
| CLI前缀 | 全部使用 `claw` | 全部改为 `cyberteam` | P0 |
| create_team | `claw team create --agents` | `cyberteam team spawn-team` | P0 |
| spawn_workers | `claw team spawn --agent --depends` | `cyberteam spawn + inbox send` | P0 |
| create_tasks | 无 | `cyberteam task create --blocked-by` | P0 |
| wait_for_tasks | `claw team task --status` | 轮询 `cyberteam task list` | P0 |
| EXPERT_TYPE_MAP | ai_board/five_dimension/manager_leap | porter_five_forces/mckinsey_7s/kotter_change | P0 |
| _check_convergence | 永远返回 False | 实现 Jaccard 相似度收敛检查 | P1 |
| inbox send --type | `--type task_assignment` | `--task task_subject` (创建 TaskStore 条目) | P0 |
| 存储路径 | `workspace/` | `thinking-team/workspace/` | P1 |
| expert_mapping yaml | 同上3个虚构专家 | 同上替换 | P1 |

---

**设计日期**: 2026-03-21
**文档编号**: Q67
**内容**: ClawTeam集成适配器设计
**参考**: ClawTeam CLI (cyberteam references/cli-reference.md)
**第三轮修正**: 2026-03-21
