# interfaces - 监控中台

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `agent_id` | string | 被监控的Agent ID |
| `operation_history` | Operation[] | 操作历史记录 |
| `task_id` | string | 关联任务ID（可选） |
| `alert_rules` | AlertRule[] | 告警规则配置（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `loop_detection` | LoopDetection | 循环检测结果 |
| `progress_view` | ProgressView | 全局进度视图 |
| `alerts` | Alert[] | 触发的告警列表 |
| `system_health` | SystemHealth | 系统健康状态 |

## LoopDetection 结构

```yaml
LoopDetection:
  has_loop: boolean          # 是否检测到循环
  loop_type: enum            # INFINITE_LOOP/OSCILLATION/SPIRAL/RETRY_LOOP/SLOW_CONVERGENCE
  depth: float              # 循环深度
  period: int               # 循环周期长度
  break_point: string       # 建议突破点
  confidence: float        # 检测置信度 (0-1)
```

## Alert 结构

```yaml
Alert:
  id: string               # 告警唯一ID
  severity: enum            # P0(紧急)/P1(高)/P2(中)/P3(低)
  type: enum                # 告警类型
  message: string           # 告警消息
  agent_id: string         # 关联Agent
  task_id: string          # 关联任务
  timestamp: datetime       # 触发时间
  status: enum             # pending/acknowledged/resolved/escalated
```

## ProgressView 结构

```yaml
ProgressView:
  summary:
    total: int             # 总任务数
    by_status: dict        # 各状态任务数
    by_priority: dict      # 各优先级任务数
  completion:
    overall_percentage: float
    estimated_time: datetime
  bottlenecks: Bottleneck[]
  risks: Risk[]
  recommendations: string[]
```

## 循环类型检测

| 类型 | 代码 | 特征 | 危害等级 |
|------|------|------|----------|
| 死循环 | INFINITE_LOOP | 相同操作无限重复 | 严重 |
| 振荡循环 | OSCILLATION | 两个状态交替 | 高 |
| 螺旋循环 | SPIRAL | 逐渐恶化重复 | 高 |
| 无效重试 | RETRY_LOOP | 失败后重复同样操作 | 中 |
| 搜索循环 | SEARCH_LOOP | 重复搜索无进展 | 低 |
| 收敛过慢 | SLOW_CONVERGENCE | 进展速度过慢 | 低 |

## 调用示例

```python
from agents.middle-tier.monitoring import MonitoringHub

monitor = MonitoringHub()

# 循环检测
loop_result = monitor.detect_loop(
    agent_id="gsd-executor-001",
    operation_history=[
        {"type": "search", "target": "file", "result": "not_found"},
        {"type": "search", "target": "file", "result": "not_found"},
        {"type": "search", "target": "file", "result": "not_found"}
    ]
)

# 返回示例
{
    "has_loop": True,
    "loop_type": "RETRY_LOOP",
    "depth": 3.0,
    "break_point": "建议更换搜索策略或检查文件是否存在",
    "confidence": 0.92
}
```

## 告警规则示例

```python
alert_rules = [
    {"name": "agent_loop_detected", "condition": "loop_depth > 3", "severity": "P1"},
    {"name": "task_timeout", "condition": "elapsed > estimate * 1.5", "severity": "P2"},
    {"name": "deadlock_detected", "condition": "circular_dependency", "severity": "P0"}
]
```
