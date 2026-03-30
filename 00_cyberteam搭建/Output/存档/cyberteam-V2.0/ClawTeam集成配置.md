# CyberTeam ClawTeam 集成配置

---

## 一、集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    CyberTeam 系统架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   用户输入                                                       │
│       │                                                          │
│       ▼                                                          │
│   ┌─────────────────┐                                           │
│   │   CEO Agent      │ ←── 思维框架（100个）                    │
│   │   (主持人)      │ ←── 运营Experts（45+个）                │
│   └────────┬────────┘                                           │
│            │                                                      │
│            ▼                                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              ClawTeam 协作层                             │   │
│   │  • team/ - 团队管理                                       │   │
│   │  • task/ - 任务管理                                       │   │
│   │  • inbox/ - 消息传递                                     │   │
│   │  • spawn/ - Agent启动                                    │   │
│   │  • board/ - 看板监控                                      │   │
│   └─────────────────────────────────────────────────────────┘   │
│            │                                                      │
│            ▼                                                      │
│   ┌─────────────────┐                                           │
│   │   执行层Agents  │ ←── 思维专家 + 运营专家 + 执行专家        │
│   └─────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、ClawTeam 命令参考

### 2.1 团队管理

```bash
# 创建团队
clawteam team spawn-team cyberteam -d "CyberTeam运营团队"

# 查看团队状态
clawteam team status cyberteam
```

### 2.2 任务管理

```bash
# 创建任务
clawteam task create cyberteam "增长分析" -o growth-agent
clawteam task create cyberteam "文案撰写" -o copywriter-agent

# 创建有依赖的任务
clawteam task create cyberteam "渠道策略" --blocked-by <task-id>

# 更新任务状态
clawteam task update cyberteam <task-id> --status completed

# 查看任务看板
clawteam board show cyberteam
```

### 2.3 消息传递

```bash
# 发送消息给Agent
clawteam inbox send cyberteam growth-agent "请完成增长分析"

# 查看收件箱
clawteam inbox list cyberteam
```

### 2.4 Agent启动

```bash
# 启动Agent（tmux模式）
clawteam spawn tmux claude --team cyberteam --agent-name growth-expert --agent-type expert

# 启动Agent（subprocess模式）
clawteam spawn subprocess claude --team cyberteam --agent-name copywriter --agent-type expert
```

### 2.5 看板监控

```bash
# 静态看板
clawteam board show cyberteam

# 实时监控（每5秒刷新）
clawteam board live cyberteam --interval 5
```

---

## 三、CyberTeam 配置文件

### 3.1 团队配置

```yaml
# config/cyberteam.yaml
team:
  name: "cyberteam"
  description: "CyberTeam AI运营团队"

# 团队成员（Agent配置）
members:
  - name: "ceo"
    type: "orchestrator"
    role: "主持人"

  - name: "growth-agent"
    type: "expert"
    role: "增长专家"
    source: "项目组1"

  - name: "copywriter-agent"
    type: "expert"
    role: "文案专家"
    source: "项目组1"

  - name: "user-agent"
    type: "expert"
    role: "用户专家"
    source: "项目组1"

  # ... 其他成员
```

### 3.2 任务模板

```yaml
# config/task-templates.yaml
templates:
  增长方案:
    - task: "增长分析"
      agent: "增长Agent"
      duration: 30

    - task: "指标制定"
      agent: "北极星指标Agent"
      depends_on: ["增长分析"]
      duration: 20

    - task: "渠道策略"
      agent: "渠道推广Agent"
      depends_on: ["指标制定"]
      duration: 20

    - task: "文案配合"
      agent: "文案Agent"
      depends_on: ["渠道策略"]
      duration: 15

  转化优化:
    - task: "数据分析"
      agent: "数据驱动Agent"
      duration: 20

    - task: "文案优化"
      agent: "文案Agent"
      depends_on: ["数据分析"]
      duration: 15

    - task: "方案汇总"
      agent: "CEO"
      depends_on: ["文案优化"]
      duration: 10
```

---

## 四、代码集成

### 4.1 Python SDK 使用

```python
from clawteam import ClawTeam

# 初始化
ct = ClawTeam()

# 创建团队
ct.create_team("cyberteam", description="CyberTeam运营团队")

# 添加Agent
ct.add_agent("growth-agent", "增长Agent", "expert")
ct.add_agent("copywriter-agent", "文案Agent", "expert")

# 创建任务
task1 = ct.create_task("cyberteam", "增长分析", "growth-agent")
task2 = ct.create_task("cyberteam", "文案撰写", "copywriter-agent")

# 设置依赖
ct.add_dependency(task2.id, task1.id)

# 发送消息
ct.send_message("cyberteam", "growth-agent", "请分析增长策略")

# 启动Agent
ct.spawn_agent("claude", team="cyberteam", agent_name="growth-expert")

# 查看状态
status = ct.get_team_status("cyberteam")
print(status)
```

### 4.2 CLI 包装脚本

```bash
#!/bin/bash
# cyberteam-cli

case "$1" in
  start)
    echo "启动CyberTeam..."
    clawteam team spawn-team cyberteam -d "CyberTeam运营团队"
    ;;

  task)
    shift
    clawteam task create cyberteam "$@"
    ;;

  send)
    AGENT=$2
    shift 2
    clawteam inbox send cyberteam "$AGENT" "$@"
    ;;

  status)
    clawteam board show cyberteam
    ;;

  live)
    clawteam board live cyberteam --interval 5
    ;;

  *)
    echo "用法: $0 {start|task|send|status|live}"
    exit 1
    ;;
esac
```

---

## 五、Agent 协作配置

### 5.1 默认任务流

```json
{
  "workflows": {
    "增长方案": {
      "description": "完整的增长方案制定流程",
      "steps": [
        {
          "name": "问题分析",
          "agent": "ceo",
          "action": "analyze",
          "input": "${user_input}"
        },
        {
          "name": "增长分析",
          "agent": "growth-agent",
          "action": "analyze",
          "input": "用户需求",
          "parallel": true
        },
        {
          "name": "指标制定",
          "agent": "north-star-agent",
          "action": "define",
          "depends_on": ["增长分析"],
          "parallel": true
        },
        {
          "name": "策略制定",
          "agent": "strategy-agent",
          "action": "plan",
          "depends_on": ["指标制定"],
          "parallel": true
        },
        {
          "name": "文案配合",
          "agent": "copywriter-agent",
          "action": "write",
          "depends_on": ["策略制定"],
          "parallel": true
        },
        {
          "name": "结果聚合",
          "agent": "ceo",
          "action": "aggregate",
          "depends_on": ["策略制定", "文案配合"]
        }
      ]
    }
  }
}
```

---

## 六、环境变量配置

```bash
# .env
CLAWTEAM_DATA_DIR=~/.cyberteam
CLAWTEAM_TEAM=cyberteam

# Agent配置
GROWTH_AGENT_MODEL=sonnet
COPYWRITER_AGENT_MODEL=sonnet

# 看板配置
BOARD_REFRESH_INTERVAL=5

# 日志配置
LOG_LEVEL=INFO
```

---

## 七、集成注意事项

### 7.1 模块名Bug修复

ClawTeam源码有模块名问题，需要修复后才能正常使用：

```python
# 问题：代码引用 'cyberteam' 但目录是 'clawteam'

# 解决方案1：创建软链接
ln -s clawteam cyberteam

# 解决方案2：修改导入
# 将 cli/commands.py 中的 'from cyberteam import __version__'
# 改为 'from clawteam import __version__'
```

### 7.2 替代方案

如果无法修复，可以使用简化版本：

```python
# 简化版任务管理（不依赖ClawTeam）
class SimpleTaskManager:
    def __init__(self):
        self.tasks = {}

    def create_task(self, name, agent, depends_on=None):
        task_id = uuid.uuid4().hex[:8]
        self.tasks[task_id] = {
            'name': name,
            'agent': agent,
            'status': 'pending',
            'depends_on': depends_on or []
        }
        return task_id

    def update_status(self, task_id, status):
        self.tasks[task_id]['status'] = status
```

---

**版本**：v1.0
**创建日期**：2026-03-23
