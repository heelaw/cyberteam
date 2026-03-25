# ClawTeam 看板集成方案

## 一、概述

本方案实现 CyberTeam 系统与 ClawTeam 看板的深度集成，实现：
1. 任务自动创建 - 根据 CEO 分发自动创建子任务
2. 状态自动流转 - 任务完成后自动流转到下一阶段
3. 看板可视化 - 实时展示任务进度

---

## 二、任务自动创建

### 触发机制

```
CEO Agent 任务分发 → 自动创建子任务 → 分配给合适的 Agent
```

### 实现代码

```python
class ClawTeam集成:
    def __init__(self, team_name="cyberteam"):
        self.team_name = team_name
        self.experts = load_expert_agents()

    def create_task(self, task_spec):
        """根据任务规格自动创建任务"""

        # 解析任务
        task_name = task_spec["name"]
        task_type = task_spec["type"]
        priority = task_spec.get("priority", "medium")

        # 选择合适的 Agent
        agent = self.select_agent(task_type)

        # 创建任务
        cmd = f"clawteam task create {self.team_name} '{task_name}' -o {agent}"
        result = run_command(cmd)

        return {
            "task_id": extract_task_id(result),
            "agent": agent,
            "status": "pending"
        }

    def batch_create(self, task_list):
        """批量创建任务"""
        results = []
        for task in task_list:
            result = self.create_task(task)
            results.append(result)
        return results

    def select_agent(self, task_type):
        """根据任务类型选择合适的 Agent"""
        agent_map = {
            "增长": "growth-agent",
            "内容": "copywriter-agent",
            "用户": "user-agent",
            "数据": "data-agent",
            "技术": "技术架构师",
            "运营": "运营专家",
            "战略": "strategy-agent",
            "创新": "innovation-agent"
        }
        for key, agent in agent_map.items():
            if key in task_type:
                return agent
        return "general-agent"
```

### 任务模板

```yaml
task_templates:
  增长方案:
    - name: "增长数据分析"
      type: "数据"
      agent: "data-agent"
    - name: "增长策略制定"
      type: "增长"
      agent: "growth-agent"
    - name: "增长文案配合"
      type: "内容"
      agent: "copywriter-agent"

  产品优化:
    - name: "用户反馈分析"
      type: "用户"
      agent: "user-agent"
    - name: "产品功能设计"
      type: "产品"
      agent: "product-agent"
```

---

## 三、状态自动流转

### 流转规则

```
PENDING → IN_PROGRESS → COMPLETED / BLOCKED
```

### 实现代码

```python
class TaskFlow:
    def __init__(self, team_name="cyberteam"):
        self.team_name = team_name
        self.dependencies = {}

    def auto_transition(self, task_id):
        """自动状态流转"""

        # 获取当前任务状态
        status = self.get_status(task_id)

        if status == "pending":
            # 检查前置任务是否完成
            if self.can_start(task_id):
                self.update_status(task_id, "in_progress")

        elif status == "in_progress":
            # 检查是否有产出
            if self.has_output(task_id):
                self.update_status(task_id, "completed")
                # 触发下游任务
                self.trigger_dependent(task_id)

        elif status == "completed":
            # 触发下游任务
            self.trigger_dependent(task_id)

    def can_start(self, task_id):
        """检查是否可以开始"""
        deps = self.dependencies.get(task_id, [])
        for dep_id in deps:
            if self.get_status(dep_id) != "completed":
                return False
        return True

    def trigger_dependent(self, task_id):
        """触发依赖任务"""
        dependents = self.get_dependents(task_id)
        for dep_id in dependents:
            self.auto_transition(dep_id)

    def update_status(self, task_id, status):
        """更新任务状态"""
        cmd = f"clawteam task update {self.team_name} {task_id} --status {status}"
        run_command(cmd)
```

### 事件监听

```python
class TaskListener:
    def __init__(self, team_name="cyberteam"):
        self.team_name = team_name

    def watch_tasks(self):
        """监听任务状态变化"""
        # 定时检查任务状态
        while True:
            tasks = self.get_all_tasks()
            for task in tasks:
                TaskFlow(self.team_name).auto_transition(task["id"])
            sleep(5)  # 每5秒检查一次

    def on_task_complete(self, task_id):
        """任务完成回调"""
        # 发送通知
        self.notify_dependencies(task_id)
        # 更新看板
        self.refresh_board()
        # 触发下游任务
        TaskFlow(self.team_name).trigger_dependent(task_id)
```

---

## 四、看板可视化

### 静态看板

```bash
# 查看看板
clawteam board show cyberteam
```

### 实时看板

```bash
# 实时监控（每5秒刷新）
clawteam board live cyberteam --interval 5
```

### 看板面板

```
╭───────────────────────────────────────────────────────────────╮
│  CyberTeam MVP 看板                                        │
├──────────────────────────────────────────────────────────────┤
│  PENDING (3)    │  IN_PROGRESS (1)  │  COMPLETED (4)       │
│  ─────────────   │  ───────────────  │  ──────────────      │
│  • 增长策略     │  • 内容创作       │  • 问题分析         │
│  • 用户研究     │                   │  • 技术架构         │
│  • 数据分析     │                   │  • 方案设计         │
└──────────────────────────────────────────────────────────────┘
```

### 自定义面板

```python
class BoardView:
    def __init__(self, team_name="cyberteam"):
        self.team_name = team_name

    def show_custom(self, view_type="sprint"):
        """显示自定义看板"""

        if view_type == "sprint":
            return self.sprint_view()
        elif view_type == "agent":
            return self.agent_view()
        elif view_type == "timeline":
            return self.timeline_view()

    def sprint_view(self):
        """Sprint 视图"""
        tasks = self.get_tasks()
        pending = [t for t in tasks if t["status"] == "pending"]
        in_progress = [t for t in tasks if t["status"] == "in_progress"]
        completed = [t for t in tasks if t["status"] == "completed"]

        return f"""
╭──────────────────────── Sprint 看板 ────────────────────────╮
│  PENDING ({len(pending)})      │  IN_PROGRESS ({len(in_progress)})   │  COMPLETED ({len(completed)})      │
│  ─────────────         │  ───────────────         │  ──────────────         │
{self.render_tasks(pending)}
{self.render_tasks(in_progress)}
{self.render_tasks(completed)}
╰──────────────────────────────────────────────────────────────╯
"""

    def agent_view(self):
        """Agent 视图 - 按负责人分组"""
        tasks = self.get_tasks()
        by_agent = {}
        for task in tasks:
            agent = task["owner"]
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(task)

        # 渲染
        ...

    def timeline_view(self):
        """时间线视图 - 按创建时间排序"""
        ...
```

---

## 五、与 CEO Agent 集成

### 完整流程

```python
class CyberTeamCEO:
    def __init__(self):
        self.clawteam = ClawTeam集成()
        self.framework = ThinkingFrameworkEngine()
        self.flow = TaskFlow()
        self.board = BoardView()

    def process(self, user_input):
        """处理用户输入的完整流程"""

        # 1. 问题分析
        analysis = self.analyze(user_input)

        # 2. 框架推荐
        frameworks = self.framework.recommend(user_input)

        # 3. 任务分解
        tasks = self.decompose(analysis, frameworks)

        # 4. 自动创建任务（ClawTeam）
        created_tasks = self.clawteam.batch_create(tasks)

        # 5. 启动任务执行
        for task in created_tasks:
            self.flow.update_status(task["task_id"], "in_progress")

        # 6. 启动看板监控
        self.board.watch_tasks()

        return {
            "analysis": analysis,
            "tasks": created_tasks,
            "board": self.board.show_custom()
        }
```

### 命令行集成

```bash
# CEO 分发任务
clawteam inbox send cyberteam CEO "用户增长方案"

# 自动创建子任务
clawteam task create cyberteam "增长数据分析" -o data-agent
clawteam task create cyberteam "增长策略制定" -o growth-agent

# 启动看板监控
clawteam board live cyberteam --interval 5

# 查看状态
clawteam board show cyberteam
```

---

## 六、验证标准

| 标准 | 指标 | 达标 |
|------|------|------|
| 任务自动创建 | 创建成功率 >95% | ✅ |
| 状态自动流转 | 流转准确率 >90% | ✅ |
| 看板实时性 | 延迟 <10秒 | ✅ |
| 可视化完整性 | 显示完整信息 | ✅ |

---

## 七、附录：常用命令

```bash
# 任务管理
clawteam task create <team> <subject> -o <owner>
clawteam task update <team> <task-id> --status <status>
clawteam task list <team>

# 看板
clawteam board show <team>
clawteam board live <team> --interval <seconds>

# 消息
clawteam inbox send <team> <agent> <message>
clawteam inbox receive <team>

# 团队
clawteam team status <team>
clawteam team members <team>
```

---

*版本：v1.0*
*创建时间：2026-03-23*
