# CyberTeam Execution Monitor v2.1

基于 PentAGI Execution Monitoring 设计的 Agent 执行监控系统。

## 功能

### 1. Loop Detection - 循环检测
- **精确匹配**: 检测完全相同的工具调用序列重复
- **模糊匹配**: 检测相似但不完全相同的调用模式
- **频率分析**: 检测单个工具的过度使用
- **状态停滞**: 检测 Agent 状态停滞

### 2. Mentor/Adviser Agent - 智能干预
- **诊断问题**: 分析循环和问题的根本原因
- **提供建议**: 给出具体的解决方案建议
- **自动干预**: 根据配置自动执行干预操作
- **升级处理**: 必要时升级给人工处理

### 3. Tool Call Limits - 工具调用限制
- **全局限制**: 限制总调用次数
- **Agent 限制**: 限制单个 Agent 调用次数
- **工具限制**: 限制单个工具调用次数
- **速率限制**: 限制单位时间内的调用频率
- **冷却机制**: 达到限制后进入冷却期

## 安装

```python
import sys
sys.path.insert(0, 'Output/CyberTeam-v2.1/modules')

from monitor import ExecutionMonitor
```

## 使用方法

### 基本使用

```python
from monitor import ExecutionMonitor

# 创建监控器
monitor = ExecutionMonitor()

# 启动监控
monitor.start(agent_id="agent-1")

# 在每次工具调用前检查
result = monitor.check(
    agent_id="agent-1",
    tool_name="read",
    arguments={"file": "test.py"}
)

if not result.allowed:
    print(f"调用被阻止: {result.warnings}")
    return

# 执行工具
data = read_file("test.py")

# 记录工具调用结果
monitor.record(
    agent_id="agent-1",
    tool_name="read",
    arguments={"file": "test.py"},
    result=data
)

# 获取监控状态
status = monitor.get_status(agent_id="agent-1")
print(status)

# 停止监控
monitor.stop(agent_id="agent-1")
```

### 自定义配置

```python
from monitor import create_monitor, MonitorConfig

# 方式1: 使用默认配置
monitor = create_monitor()

# 方式2: 自定义配置
config = MonitorConfig(
    loop_detection=LoopDetectionConfig(
        enabled=True,
        min_repeat_count=3,
        similarity_threshold=0.7
    ),
    intervention=InterventionConfig(
        enabled=True,
        auto_intervention=True,
        mentor_mode="adviser"
    ),
    limits=ToolLimitsConfig(
        global_max_calls=1000,
        per_agent_max_calls=100,
        per_tool_max_calls=50
    )
)

monitor = ExecutionMonitor(config)
```

### 注册回调

```python
def on_alert(alert):
    print(f"告警: {alert.message}")

def on_intervention(agent_id, result):
    print(f"干预 {agent_id}: {result.message}")

def on_limit_reached(agent_id, result):
    print(f"限制达到 {agent_id}: {result.reason}")

monitor.register_callbacks(
    on_alert=on_alert,
    on_intervention=on_intervention,
    on_limit_reached=on_limit_reached
)
```

## 目录结构

```
monitor/
├── __init__.py          # 主模块入口
├── monitor.py           # ExecutionMonitor 主类
├── config/
│   ├── __init__.py
│   └── monitor_config.py  # 配置类
├── detector/
│   ├── __init__.py
│   └── loop_detector.py    # 循环检测器
├── intervention/
│   ├── __init__.py
│   └── mentor_agent.py     # Mentor/Adviser Agent
├── limits/
│   ├── __init__.py
│   └── tool_limits.py      # 工具调用限制
└── utils/
    ├── __init__.py
    └── __init__.py         # 工具函数
```

## 配置参数

### LoopDetectionConfig

| 参数 | 默认值 | 说明 |
|------|--------|------|
| enabled | True | 是否启用 |
| max_sequence_length | 20 | 跟踪的调用序列长度 |
| similarity_threshold | 0.7 | 相似度阈值 |
| min_repeat_count | 3 | 最小重复次数 |
| window_size | 10 | 滑动窗口大小 |
| check_interval | 5 | 检查间隔 |

### InterventionConfig

| 参数 | 默认值 | 说明 |
|------|--------|------|
| enabled | True | 是否启用 |
| auto_intervention | True | 自动干预 |
| mentor_mode | "adviser" | 干预模式 |
| max_retries | 3 | 最大重试次数 |
| escalation_timeout | 300 | 升级超时(秒) |

### ToolLimitsConfig

| 参数 | 默认值 | 说明 |
|------|--------|------|
| enabled | True | 是否启用 |
| global_max_calls | 1000 | 全局最大调用次数 |
| per_agent_max_calls | 100 | 单个Agent最大调用次数 |
| per_tool_max_calls | 50 | 单个工具最大调用次数 |
| per_minute_limit | 30 | 每分钟最大调用次数 |
| burst_limit | 10 | 突发限制 |
| warning_threshold | 0.8 | 警告阈值 |
| hard_stop_threshold | 50 | 硬性停止阈值 |
| cooldown_period | 60 | 冷却期(秒) |

## 干预动作

| 动作 | 说明 |
|------|------|
| NONE | 无动作，继续执行 |
| WARN | 警告 |
| RETRY | 重试 |
| CONTEXT_REFRESH | 刷新上下文 |
| ALTERNATIVE | 更换方法 |
| ESCALATE | 升级处理 |
| STOP | 停止执行 |

## 许可证

MIT License
