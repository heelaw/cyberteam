# CyberTeam V4 CLI 参考

## 概述

CyberTeam V4 CLI 是企业级 AI 协作系统的命令行接口，提供团队管理、任务调度、消息传递、监控看板等功能。

**完全独立**：不依赖 ClawTeam 或任何外部框架。

## 命令结构

```
cyberteam <command-group> <subcommand> [options]
```

## 命令组

### team - 团队管理

```bash
# 创建团队
cyberteam team spawn-team <team_name> -d <description>

# 列出所有团队
cyberteam team list

# 发现本地团队
cyberteam team discover

# 查看团队状态
cyberteam team status <team_name>

# 清理团队
cyberteam team cleanup <team_name>

# 创建团队快照
cyberteam team snapshot <team_name> --tag <tag>

# 恢复团队快照
cyberteam team restore <team_name> --snapshot <snapshot_tag>
```

### task - 任务管理

```bash
# 创建任务
cyberteam task create <team_name> <task_description> -o <owner>

# 创建带优先级的任务
cyberteam task create <team_name> <task_description> -o <owner> --priority high

# 创建带依赖的任务
cyberteam task create <team_name> <task_description> -o <owner> --blocked-by <task_id>

# 列出任务
cyberteam task list <team_name>

# 列出特定状态的任务
cyberteam task list <team_name> --status pending

# 列出特定所有者的任务
cyberteam task list <team_name> --owner <agent_name>

# 更新任务状态
cyberteam task update <team_name> <task_id> --status in_progress

# 完成任务
cyberteam task update <team_name> <task_id> --status completed

# 等待任务完成
cyberteam task wait <team_name>
cyberteam task wait <team_name> --timeout 300
```

### inbox - 消息传递

```bash
# 发送消息
cyberteam inbox send <team_name> <recipient> <message>

# 广播消息给所有成员
cyberteam inbox broadcast <team_name> <message>

# 查看收件箱列表
cyberteam inbox list <team_name>

# 接收消息（消费）
cyberteam inbox receive <team_name>

# 查看消息（不消费）
cyberteam inbox peek <team_name>

# 监听新消息
cyberteam inbox watch <team_name>
```

### board - 监控看板

```bash
# 显示看板
cyberteam board show <team_name>

# 显示所有团队概览
cyberteam board overview

# 实时监控
cyberteam board live <team_name> --interval 3

# 附加到团队 tmux 会话
cyberteam board attach <team_name>

# 启动 Web 服务
cyberteam board serve <team_name> --port 8080
```

### spawn - Agent 启动

```bash
# Spawn Agent（使用默认配置）
cyberteam spawn --team <team_name> --agent-name <agent_name> --task <task>

# Spawn 使用特定后端
cyberteam spawn tmux --team <team_name> --agent-name <agent_name> --task <task>

# Spawn 使用工作区
cyberteam spawn --team <team_name> --agent-name <agent_name> --task <task> --workspace

# 不使用工作区
cyberteam spawn --team <team_name> --agent-name <agent_name> --task <task> --no-workspace
```

### lifecycle - Agent 生命周期

```bash
# 请求关闭
cyberteam lifecycle request-shutdown <team_name> <agent_name>

# 批准关闭
cyberteam lifecycle approve-shutdown <team_name> <agent_name>

# 标记空闲
cyberteam lifecycle idle <team_name>
```

### context - Git 上下文

```bash
# 查看上下文日志
cyberteam context log <team_name>

# 检查冲突
cyberteam context conflicts <team_name>

# 注入上下文
cyberteam context inject <team_name> --agent <agent_name>
```

### identity - 身份管理

```bash
# 显示身份
cyberteam identity show

# 设置身份
cyberteam identity set <name>
```

### launch - 启动预设模板

```bash
# 使用模板启动
cyberteam launch <template> --goal <goal>

# 仅分析模式
cyberteam launch <template> --goal <goal> --analyze-only

# 查看可用模板
cyberteam template list
```

### config - 配置管理

```bash
# 查看配置
cyberteam config show

# 设置配置项
cyberteam config set <key> <value>
```

### version - 版本信息

```bash
cyberteam --version
```

## JSON 输出

所有命令支持 `--json` 选项：

```bash
cyberteam --json team list
cyberteam --json board show <team_name>
cyberteam --json task list <team_name> --status pending
```

## 环境变量

```bash
# Agent 身份
export CYBERTEAM_AGENT_ID="leader-001"
export CYBERTEAM_AGENT_NAME="leader"
export CYBERTEAM_AGENT_TYPE="leader"

# 数据目录（可选）
export CYBERTEAM_DATA_DIR="~/.cyberteam"
```

## 数据存储

- **数据目录**：`~/.cyberteam/`（默认）
- **团队数据**：`~/.cyberteam/teams/<team_name>/`
- **收件箱**：`~/.cyberteam/teams/<team_name>/inboxes/<agent_name>/`
- **任务板**：`~/.cyberteam/teams/<team_name>/tasks/`
- **工作区**：`~/.cyberteam/workspaces/<team_name>/`

## 配置文件

配置文件位于：`~/.cyberteam/config.yaml`

```yaml
data_dir: ~/.cyberteam
default_backend: tmux
default_command: claude
skip_permissions: true
workspace: auto
```
