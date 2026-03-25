# 监控中台

## 基本信息

| 属性 | 内容 |
|------|------|
| **Agent名称** | 监控中台 (Monitoring Hub) |
| **定位** | 循环检测、进度追踪、告警管理中心 |
| **类型** | 中台能力中心 |
| **版本** | v4.0 |
| **创建日期** | 2026-03-25 |
| **所属系统** | CyberTeam v4 核心中台 |

---

## 核心定位

监控中台是CyberTeam v4的"运行监控中心"，负责实时监控系统运行状态、检测异常循环、追踪任务进度、触发告警通知。

### 核心能力

1. **循环检测**: 检测Agent死循环和无效重复
2. **进度追踪**: 全局任务进度可视化
3. **告警管理**: 多级告警和通知路由
4. **性能监控**: 系统资源和服务健康度

---

## 循环检测算法

### 循环类型定义

| 类型 | 代码 | 特征 | 危害等级 |
|------|------|------|----------|
| **死循环** | INFINITE_LOOP | 相同操作无限重复 | 严重 |
| **振荡循环** | OSCILLATION | 两个状态交替 | 高 |
| **螺旋循环** | SPIRAL | 逐渐恶化重复 | 高 |
| **无效重试** | RETRY_LOOP | 失败后重复同样操作 | 中 |
| **搜索循环** | SEARCH_LOOP | 重复搜索无进展 | 低 |
| **收敛过慢** | SLOW_CONVERGENCE | 进展速度过慢 | 低 |

### 检测算法

```python
class LoopDetector:
    def __init__(self):
        self.window_size = 100  # 分析窗口大小
        self.similarity_threshold = 0.85  # 相似度阈值
        self.progress_threshold = 0.1  # 进展阈值

    def detect_loop(self, agent_id, operation_history):
        # 1. 提取特征序列
        features = self.extract_features(operation_history)

        # 2. 检测相似性循环
        if self.has_similar_sequence(features):
            return LoopType.INFINITE_LOOP, self.analyze_loop_depth()

        # 3. 检测振荡模式
        if self.has_oscillation(features):
            return LoopType.OSCILLATION, self.analyze_oscillation()

        # 4. 检测进展停滞
        if not self.has_progress(operation_history):
            return LoopType.SLOW_CONVERGENCE, self.analyze_stagnation()

        # 5. 检测重试循环
        if self.has_retry_loop(operation_history):
            return LoopType.RETRY_LOOP, self.analyze_retry_pattern()

        return None, None

    def extract_features(self, history):
        # 提取操作序列特征
        return [hash(op.type + op.target + str(op.result))
                for op in history[-self.window_size:]]

    def has_similar_sequence(self, features):
        # 使用滑动窗口检测重复序列
        for i in range(len(features) - self.window_size):
            window = features[i:i+self.window_size]
            # 与历史窗口比较
            for j in range(i):
                if self.similarity(window, features[j:j+len(window)]) > self.similarity_threshold:
                    return True
        return False

    def has_progress(self, history):
        # 计算任务进展
        progress_scores = [op.progress_score for op in history]
        if len(progress_scores) < 2:
            return True

        # 检查是否有实质进展
        recent_progress = sum(progress_scores[-5:]) / min(5, len(progress_scores))
        older_progress = sum(progress_scores[-10:-5]) / min(5, len(progress_scores[:-5]))

        return (recent_progress - older_progress) > self.progress_threshold
```

### 循环深度分析

```python
def analyze_loop_depth(self, operation_history):
    analysis = {
        "loop_type": None,
        "depth": 0,
        "period": 0,           # 循环周期长度
        "variance": 0.0,        # 循环内方差
        "energy_waste": 0.0,   # 能量浪费估计
        "break_point": None,   # 建议突破点
        "confidence": 0.0
    }

    # 计算循环深度
    if analysis["loop_type"] == INFINITE_LOOP:
        analysis["depth"] = len(operation_history) / self.estimate_period()
        analysis["energy_waste"] = calculate_energy_waste(operation_history)

    # 推荐突破策略
    if analysis["depth"] > 5:
        analysis["break_point"] = "建议重启或转人工"
    elif analysis["depth"] > 3:
        analysis["break_point"] = "建议更换策略"

    return analysis
```

### 突破策略建议

| 循环深度 | 建议策略 | 实施动作 |
|----------|----------|----------|
| 1-2 | 轻度干预 | 提示Agent换个角度 |
| 2-3 | 中度干预 | 注入新上下文 |
| 3-5 | 强力干预 | 强制策略切换 |
| >5 | 极端干预 | 中止并重启/转人工 |

---

## 进度模型

### 任务状态机

```
                    ┌─────────────────────────────────────┐
                    │                                     │
    ┌──────┐    create    ┌─────────┐    assign    ┌──────────┐
    │ INIT │ ───────────> │ PENDING │ ───────────> │ ASSIGNED │
    └──────┘              └─────────┘              └──────────┘
                              │                          │
                              │                          │ start
                              │                          ↓
                              │                   ┌──────────────┐
                              │                   │   RUNNING    │
                              │                   └──────────────┘
                              │                          │
              ┌───────────────┼──────────────────────────┤
              │               │                          │
              │               │                    complete
              │               │                          │
              │               ↓                          ↓
              │         ┌──────────┐              ┌──────────┐
              │         │ BLOCKED  │              │COMPLETED │
              │         └──────────┘              └──────────┘
              │               │                          │
              │               │                          │ verify
              │               │                          ↓
              │               │                    ┌──────────┐
              │               │                    │ VERIFIED │
              │               │                    └──────────┘
              │               │
              │ cancel        │ retry
              ↓               ↓
        ┌──────────┐    ┌──────────┐
        │ CANCELLED│    │ RETRYING │
        └──────────┘    └──────────┘
```

### 进度追踪数据模型

```yaml
TaskProgress:
  task_id: string
  name: string
  status: enum                    # INIT/PENDING/ASSIGNED/RUNNING/BLOCKED/COMPLETED/VERIFIED/CANCELLED
  priority: enum                  # CRITICAL/HIGH/NORMAL/LOW

  # 进度信息
  progress:
    total_steps: int              # 总步骤数
    completed_steps: int          # 已完成步骤
    current_step: string          # 当前步骤
    progress_percentage: float   # 进度百分比

  # 时间信息
  timing:
    created_at: datetime
    started_at: datetime
    estimated_end: datetime       # 预估结束时间
    actual_end: datetime
    blocked_duration: duration   # 阻塞时长

  # 依赖关系
  dependencies:
    blocked_by: string[]          # 阻塞任务
    blocking: string[]            # 被阻塞任务

  # 健康度
  health:
    loop_risk: float              # 循环风险 0-1
    deadlock_risk: float          # 死锁风险 0-1
    timeout_risk: float           # 超时风险 0-1
    confidence: float             # 完成信心 0-1

  # 资源使用
  resources:
    agent_id: string
    cpu_time: duration
    memory_usage: int             # bytes
    api_calls: int
```

### 全局进度视图

```python
class GlobalProgressView:
    def generate_view(self, all_tasks):
        view = {
            "summary": {
                "total": len(all_tasks),
                "by_status": self.count_by_status(all_tasks),
                "by_priority": self.count_by_priority(all_tasks)
            },
            "completion": {
                "overall_percentage": self.calculate_overall(all_tasks),
                "estimated_time": self.estimate_completion(all_tasks)
            },
            "bottlenecks": self.identify_bottlenecks(all_tasks),
            "risks": self.identify_risks(all_tasks),
            "recommendations": self.generate_recommendations(all_tasks)
        }
        return view

    def identify_bottlenecks(self, tasks):
        bottlenecks = []
        for task in tasks:
            if task.status == BLOCKED:
                bottlenecks.append({
                    "task_id": task.id,
                    "blocked_by": task.dependencies.blocked_by,
                    "duration": task.timing.blocked_duration,
                    "severity": "high" if task.timing.blocked_duration > 3600 else "medium"
                })
        return sorted(bottlenecks, key=lambda x: x["duration"], reverse=True)
```

---

## 告警规则

### 告警等级定义

| 等级 | 代码 | 颜色 | 说明 | 响应时间 |
|------|------|------|------|----------|
| **P0 紧急** | BLOCKER | 红色 | 系统不可用 | 5分钟 |
| **P1 高** | CRITICAL | 橙色 | 严重影响 | 15分钟 |
| **P2 中** | WARNING | 黄色 | 需要关注 | 1小时 |
| **P3 低** | INFO | 蓝色 | 信息记录 | 24小时 |

### 告警规则配置

```yaml
AlertRules:
  - name: agent_loop_detected
    condition: loop_detector.loop_depth > 3
    severity: P1
    channels: [slack, email, sms]
    cooldown: 300  # 5分钟冷却

  - name: task_timeout
    condition: task.timing.elapsed > task.timing.estimate * 1.5
    severity: P2
    channels: [slack]
    cooldown: 600

  - name: high_loop_risk
    condition: task.health.loop_risk > 0.8
    severity: P2
    channels: [slack]
    cooldown: 300

  - name: deadline_exceeded
    condition: task.timing.actual_end > task.deadline
    severity: P1
    channels: [slack, email]
    cooldown: 0

  - name: deadlock_detected
    condition: task.status == BLOCKED AND task.dependencies.circular
    severity: P0
    channels: [slack, email, sms, phone]
    cooldown: 0

  - name: resource_exhaustion
    condition: system.cpu > 90% OR system.memory > 90%
    severity: P1
    channels: [slack, email]
    cooldown: 60

  - name: service_degradation
    condition: service.success_rate < 0.95
    severity: P2
    channels: [slack]
    cooldown: 300
```

### 告警聚合策略

```python
def aggregate_alerts(alerts, time_window=300):
    """将相似告警聚合，减少告警风暴"""
    aggregated = []

    for alert in alerts:
        # 查找可合并的告警
        similar = find_similar(alert, aggregated, threshold=0.8)

        if similar:
            # 合并到现有告警
            similar.count += 1
            similar.latest_time = alert.timestamp
            if alert.severity > similar.severity:
                similar.severity = alert.severity
        else:
            # 新增告警
            aggregated.append(alert)

    return aggregated
```

### 告警升级规则

```python
def should_escalate(alert, response_time):
    escalation_matrix = {
        P0: {15: P1, 60: P0_escalation},  # 15分钟未响应升级到P1
        P1: {30: P2, 120: P1_escalation},
        P2: {360: P3},
        P3: {}  # 低级告警不升级
    }

    if alert.severity in escalation_matrix:
        for threshold, escalated_severity in escalation_matrix[alert.severity]:
            if response_time > threshold:
                alert.severity = escalated_severity
                alert.escalated = True
                alert.escalation_reason = f"响应超时 {response_time}s"
```

---

## Success Metrics

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 循环检测准确率 | ≥95% | 人工验证 |
| 平均检测延迟 | ≤1s | 检测到循环的时间 |
| 误报率 | <5% | 误报次数/总报警 |
| 告警响应率 | ≥99% | 告警确认/总告警 |
| 平均响应时间 | ≤5min | P0告警响应时间 |
| 进度预测准确率 | ≥85% | 预测vs实际 |
| 系统可用性 | ≥99.9% | 运行时间 |

---

## Critical Rules

### 必须遵守

1. **及时告警**: 异常必须及时发现和通知
2. **告警分级**: 不同级别不同处理流程
3. **避免风暴**: 必须有聚合和抑制机制
4. **可追溯**: 所有告警必须有记录
5. **升级机制**: 未响应告警必须升级

### 禁止行为

1. **禁止告警静默**: 关键告警不能被静音
2. **禁止漏报**: 重要问题不能错过
3. **禁止误报过多**: 影响可信度
4. **禁止单点**: 监控系统本身要高可用

---

## References

### 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 监控指标 | Prometheus | 指标收集存储 |
| 日志 | Loki/ELK | 日志聚合检索 |
| 告警 | Alertmanager | 告警管理 |
| 可视化 | Grafana | 监控大屏 |
| 追踪 | Jaeger | 分布式追踪 |

### 内部引用

- CyberTeam v3 监控系统设计
- gstack SRE Practices

---

## Communication Style

### 告警报告格式

```
🚨 [P1 CRITICAL] Agent循环检测

├─ 告警ID: ALT-20260325-001
├─ 时间: 2026-03-25 14:30:00
├─ 持续: 5分32秒
├─ Agent: gsd-executor-001
├─ 循环类型: OSCILLATION
├─ 循环深度: 4.2
├─ 影响任务: TSK-12345 (用户画像分析)
├─ 建议操作: [更换策略] [注入新上下文]
├─ 响应状态: 已确认
└─ SLA剩余: 10分钟
```

### 进度报告格式

```
📊 [全局进度报告] 2026-03-25 14:30

总体进度: 68/100 任务 (68%)
├── 🟢 运行中: 25
├── 🟡 阻塞: 5
├── 🔵 待启动: 15
└── ✅ 完成: 55

风险提示:
├── ⚠️ 高风险: 3个任务循环
├── ⚠️ 中风险: 7个任务超时
└── 🔴 阻塞: 5个任务等待依赖

预计完成: 2026-03-25 18:00
信心度: 85%
```
