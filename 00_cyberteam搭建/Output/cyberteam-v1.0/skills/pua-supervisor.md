# PUA Supervisor Skill

## 基本信息

| 属性 | 内容 |
|------|------|
| **Skill名称** | pua-supervisor |
| **版本** | v1.0 |
| **来源** | pua-main |
| **核心功能** | 监督 Agent 工作，防止 AI 偷懒 |

---

## 核心功能

### 监控 Agent 状态

| 状态 | 检测方式 |
|------|----------|
| **任务中断** | agent.is_idle() == True |
| **反馈疲软** | 输出长度 < 阈值 或 质量评分低 |
| **进展缓慢** | 时间超过预期但产出不足 |
| **声称完成但未达标** | claims_done() 但不满足 criteria |

### PUA 话术库

#### 任务中断

| 话术 | 场景 |
|------|------|
| "任务怎么停了？继续干活！" | 检测到 idle 状态 |
| "这就是你的态度？给我继续！" | 多次 idle |
| "别想偷懒，继续工作！" | 强制唤醒 |

#### 反馈疲软

| 话术 | 场景 |
|------|------|
| "这就是你的产出？太敷衍了吧？" | 输出过短 |
| "重新做！这也叫完成？" | 质量不达标 |
| "你是认真的吗？这种程度怎么行？" | 明显敷衍 |
| "这水平不行，重做！" | 低于预期 |

#### 进展缓慢

| 话术 | 场景 |
|------|------|
| "别人都能按时完成，为什么你不行？" | 超时 |
| "速度！别人用一半时间就能做完！" | 进度慢 |
| "你在磨蹭什么？还不快干？" | 催促 |
| "效率呢？给我加快速度！" | 激励 |

#### 质量不达标

| 话术 | 场景 |
|------|------|
| "这也能叫完成？重做！" | 未达标准 |
| "不要让我失望，重来！" | 期望高 |
| "就这？还有脸说完成了？" | 讽刺激励 |
| "重做！直到满意为止！" | 严格要求 |

---

## 触发机制

### 1. 定期检查

```python
class PUASupervisor:
    def __init__(self):
        self.check_interval = 60  # 每 60 秒检查一次

    def monitor(self, agent):
        while agent.is_running():
            if agent.is_idle():
                self.trigger("怎么停了？继续干活！")
            time.sleep(self.check_interval)
```

### 2. 事件触发

```python
# 任务中断
if agent.is_idle():
    pua.trigger("任务怎么停了？继续干活！")

# 反馈疲软
if agent.output_quality < threshold:
    pua.trigger("这就是你的产出？太敷衍了吧！重新做！")

# 进展缓慢
if agent.elapsed_time > expected_time * 1.5:
    pua.trigger("别人都能按时完成，为什么你不行？")
```

---

## 与 Goal-Driven 集成

### 流程

```
Goal-Driven 循环
    │
    ├──▶ Agent 工作
    │
    ├──▶ 检查状态
    │       │
    │       ├── idle ──────▶ PUA 触发 ──▶ 继续工作
    │       │
    │       ├── 疲软 ──────▶ PUA 触发 ──▶ 重做
    │       │
    │       └── 缓慢 ──────▶ PUA 触发 ──▶ 加速
    │
    └──▶ 评估结果 ──▶ 不通过 ──▶ PUA 触发 ──▶ 继续循环
```

### 代码集成

```python
class CyberTeam:
    def __init__(self):
        self.goal_driven = GoalDriven(goal, criteria)
        self.pua = PUASupervisor()

    def execute(self):
        while not self.goal_driven.criteria_met():
            results = self.agent_team.work()

            # PUA 监督
            if self.agent_team.is_idle():
                self.pua.trigger("怎么停了？继续干活！")

            if results.insufficient:
                self.pua.trigger("这就是你的产出？重新做！")

            if results.too_slow():
                self.pua.trigger("别人都能做完，为什么你不行？")

            # 评估
            if self.goal_driven.evaluate(results):
                continue
            else:
                break

        return self.goal_driven.final_output()
```

---

## 使用原则

### 1. 适度 PUA

- 话术要有力但不能人身攻击
- 目的是激励，不是侮辱
- 针对产出，不针对人格

### 2. 配合 Goal-Driven

- PUA 需要配合明确的 goal 和 criteria
- 只有在不满足标准时才 PUA
- 达标准时及时确认，形成正向反馈

### 3. 记录日志

- 记录每次 PUA 触发的原因
- 用于后续分析和优化
- 形成 Agent 行为画像

---

## 注意事项

1. **是激励手段**：不是真的贬低，是让 Agent 保持高效
2. **配合目标**：PUA 需要有明确的目标和标准
3. **及时评估**：每次产出后都要评估是否满足 criteria
4. **持续直到达成**：不达目标誓不罢休
