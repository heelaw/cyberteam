# CyberTeam ClawTeam 集成方案

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

## 二、核心命令

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
# 启动Agent（subprocess模式）
clawteam spawn subprocess claude --team cyberteam --agent-name growth-expert --agent-type expert
```

### 2.5 看板监控

```bash
# 静态看板
clawteam board show cyberteam

# 实时监控（每5秒刷新）
clawteam board live cyberteam --interval 5
```

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

## 四、Agent 协作配置

### 4.1 默认任务流

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

## 五、集成注意事项

### 5.1 模块名Bug修复

ClawTeam源码有模块名问题，需要修复后才能正常使用：

```python
# 问题：代码引用 'cyberteam' 但目录是 'clawteam'

# 解决方案1：创建软链接
ln -s clawteam cyberteam
```

### 5.2 环境变量配置

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

**版本**：v1.0
**创建日期**：2026-03-23
