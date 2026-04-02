# CyberWiz 后台任务系统

## 概述

提供后台异步任务执行能力，支持并发控制、队列管理、任务状态追踪。

## 功能

### 1. 启动后台任务

创建独立后台任务，立即返回任务 ID。

**参数**:
- `action`: "launch"
- `description`: 任务描述
- `prompt`: 任务指令
- `agent`: 使用的 Agent（默认：cyberwiz）
- `model`: 模型选择（sonnet/haiku/opus）
- `skills`: 需要加载的技能列表
- `concurrency_key`: 并发控制键

**返回**:
```json
{
  "task_id": "uuid",
  "status": "pending",
  "description": "任务描述"
}
```

### 2. 查询任务状态

查询任务当前状态。

**参数**:
- `action`: "status"
- `task_id`: 任务 ID

**返回**:
```json
{
  "task_id": "uuid",
  "status": "running|completed|failed|cancelled",
  "created_at": "时间戳",
  "updated_at": "时间戳"
}
```

### 3. 等待任务完成

阻塞等待任务完成（带超时）。

**参数**:
- `action`: "wait"
- `task_id`: 任务 ID
- `timeout`: 超时时间（毫秒，默认 300000）

**返回**:
```json
{
  "task_id": "uuid",
  "status": "completed|failed",
  "output": "任务输出"
}
```

### 4. 获取任务输出

获取已完成任务的输出内容。

**参数**:
- `action`: "output"
- `task_id`: 任务 ID

### 5. 取消任务

取消正在运行的任务。

**参数**:
- `action`: "cancel"
- `task_id`: 任务 ID

### 6. 列出所有任务

列出所有后台任务。

**参数**:
- `action`: "list"
- `filter`: 过滤条件（all/running/completed/failed）

## 使用示例

```
# 启动后台任务抓取课程
skill: cyberwiz-background-task
action: launch
description: 抓取三节课课程
prompt: 帮我抓取三节课课程页面数据，保存到文件
agent: cyberwiz
skills: sanjieke

# 查询状态
skill: cyberwiz-background-task
action: status
task_id: {task_id}

# 等待完成
skill: cyberwiz-background-task
action: wait
task_id: {task_id}
timeout: 600000

# 获取输出
skill: cyberwiz-background-task
action: output
task_id: {task_id}

# 取消任务
skill: cyberwiz-background-task
action: cancel
task_id: {task_id}

# 列出任务
skill: cyberwiz-background-task
action: list
filter: running
```

## 并发控制

- 同一 `concurrency_key` 的任务会排队执行
- 默认并发数：3
- 可通过 `max_concurrency` 参数调整

## 任务状态

| 状态 | 说明 |
|------|------|
| pending | 等待执行 |
| running | 正在执行 |
| completed | 已完成 |
| failed | 执行失败 |
| cancelled | 已取消 |

## 文件结构

```
background-task/
├── SKILL.md           # 本文件
├── manager.py         # 后台任务管理器
├── task_client.py    # 任务客户端
└── storage.py        # 任务持久化
