# Goal-Driven Skill

## 基本信息

| 属性 | 内容 |
|------|------|
| **Skill名称** | goal-driven |
| **版本** | v1.0 |
| **来源** | goal-driven-main |
| **核心逻辑** | Master-Subagent 循环，目标驱动持续执行 |

---

## 核心原理

### 伪代码

```
Goal: [最终目标]
Criteria: [成功标准]

while (criteria not met):
    let subagent work on solving the problem and achieving the Goal
    if (subagent.is_idle() or subagent.claims_done()):
        evaluation_result = evaluate(current_result, criteria)
        if (not evaluation_result.passed):
            subagent.continue_working()  # PUA 驱动继续
        else:
            goal_reached = True
```

### 核心概念

| 概念 | 说明 |
|------|------|
| **Goal** | 整个系统的终极目标，所有 subagent 的核心任务 |
| **Criteria** | 明确的条件集合，让 master agent 能够判断任务是否完成 |
| **Subagent** | 负责持续工作以解决问题的 agent |
| **Master Agent** | subagent 的唯一控制者，独立评估目标是否达成 |

---

## 使用方式

### 1. 定义 Goal

```
Goal: 构建完整的 CyberTeam 系统
```

### 2. 定义 Criteria

```
Criteria:
- 系统可运行
- 功能完整（CEO + Agent Team + PUA 监督 + 目标驱动）
- 测试通过
- 代码质量达标
```

### 3. 启动循环

```python
while not goal_reached:
    subagent.work()

    # 检查是否需要继续
    if subagent.is_idle() or subagent.claims_done():
        result = evaluate(current_output, criteria)

        if not result.passed:
            # PUA 驱动继续工作
            pua_supervisor.trigger()
            subagent.continue_working()
        else:
            goal_reached = True
            break
```

---

## 在 CyberTeam 中的应用

### 集成到 CEO

CEO 在启动 Agent Team 后，持续监控进度：

1. **定期检查**：subagent 是否活跃
2. **评估结果**：当前输出是否满足 criteria
3. **PUA 触发**：如果输出不足，触发 PUA 监督
4. **循环继续**：直到 criteria 全部满足

### Criteria 示例

| 任务 | Criteria |
|------|----------|
| 构建系统 | 代码可运行 + 单元测试通过 + 文档完整 |
| 分析问题 | 分析报告完整 + 建议可行 + 风险识别 |
| 设计方案 | 设计文档 + 技术选型理由 + 实施计划 |

---

## 与 PUA 监督的集成

### 触发条件

| 条件 | 动作 |
|------|------|
| subagent.is_idle() | PUA: "怎么停了？继续干活！" |
| subagent.claims_done() 但不满足 criteria | PUA: "这就算完成了？重新做！" |
| 进度缓慢 | PUA: "别人都能做完，为什么你不行？" |

### 集成代码

```python
class GoalDriven:
    def __init__(self, goal, criteria):
        self.goal = goal
        self.criteria = criteria
        self.pua = PUASupervisor()

    def execute(self, agent_team):
        while not self.criteria_met():
            results = agent_team.work()

            if agent_team.is_idle():
                self.pua.trigger("任务怎么停了？继续干活！")
                continue

            if not self.evaluate(results):
                self.pua.trigger("这就是你的产出？太敷衍了吧！重新做！")
                agent_team.retry()

        return self.final_output()
```

---

## 注意事项

1. **Criteria 必须明确**：越具体越好判断
2. **循环必须有退出条件**：防止无限循环
3. **PUA 是驱动手段**：不是侮辱，是激励
4. **持续直到达成**：不达目标誓不罢休
