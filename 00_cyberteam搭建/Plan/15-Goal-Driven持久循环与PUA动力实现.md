# Goal-Driven 持久循环与 PUA 动力实现方案

**版本**: v1.0
**日期**: 2026-03-24
**作者**: engine-001（P8闭环整理）
**团队**: cyberteam-discuss
**状态**: 已完成

---

## 一、Goal-Driven 循环核心设计

### 1.1 循环触发机制

```
用户输入 → CEO解析 → 目标分解 → Agent分发 → 结果验证
                                              ↓
                                         未达目标？
                                         ↓         ↓
                                       是        否
                                       ↓         ↓
                                   迭代优化    交付闭环
```

**关键原则：不达目标不停止，自动迭代直到达成。**

### 1.2 目标状态机

```python
class GoalState(Enum):
    PENDING = "pending"        # 目标已创建
    IN_PROGRESS = "in_progress" # 执行中
    EVALUATING = "evaluating"  # 结果评估中
    ITERATING = "iterating"    # 迭代优化中
    COMPLETED = "completed"     # 达成
    FAILED = "failed"           # 失败（超限）
    ESCALATED = "escalated"    # 升级人工
```

### 1.3 循环次数管理

| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_iterations | 10 | 单目标最大迭代次数 |
| iteration_timeout | 300s | 每次迭代超时 |
| total_timeout | 3600s | 总超时（防死循环） |
| improvement_threshold | 0.1 | 改进阈值（低于此值退出） |

### 1.4 目标评估函数

```python
def evaluate_goal(goal: Goal, result: Result) -> Evaluation:
    score = 0.0
    for criterion in goal.criteria:
        criterion_score = criterion.check(result)
        score += criterion.weight * criterion_score

    if score >= goal.threshold:
        return Evaluation(pass=True, score=score)
    else:
        delta = goal.threshold - score
        if delta < goal.improvement_threshold:
            return Evaluation(pass=False, reason="diminishing_returns")
        else:
            return Evaluation(pass=False, reason="below_threshold",
                            improvement_hint=generate_hint(result))
```

## 二、持久化机制

### 2.1 Checkpoint 保存

每次迭代结束保存检查点：

```python
class Checkpoint:
    goal_id: str
    iteration: int
    state: GoalState
    context_snapshot: dict  # 压缩后的上下文
    agent_memories: dict    # 各Agent记忆
    partial_results: list   # 部分结果
    timestamp: datetime

    def save(self, storage_path: str):
        with open(f"{storage_path}/{self.goal_id}.checkpoint", "w") as f:
            json.dump(asdict(self), f)

    @staticmethod
    def load(goal_id: str, storage_path: str) -> "Checkpoint":
        with open(f"{storage_path}/{goal_id}.checkpoint", "r") as f:
            return Checkpoint(**json.load(f))
```

### 2.2 恢复流程

```python
def resume_goal(goal_id: str) -> GoalState:
    checkpoint = Checkpoint.load(goal_id, STORAGE_PATH)
    restore_context(checkpoint.context_snapshot)
    restore_agent_memories(checkpoint.agent_memories)
    return checkpoint.state
```

### 2.3 记忆系统集成

```
┌─────────────────────────────────────────────────┐
│            Goal-Driven 循环                      │
│   每次迭代 → 保存 Working Memory                 │
│   每次迭代 → 更新 Episodic Memory                │
│   达成后 → 提取 Long-term Memory                │
└──────────────────────┬──────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│            Memory System (v2.1)                  │
│  Working Memory: 当前迭代上下文                  │
│  Episodic Memory: 历史迭代轨迹                   │
│  Long-term Memory: 成功模式提取                 │
└─────────────────────────────────────────────────┘
```

## 三、PUA 动力引擎

### 3.1 压力等级系统

| 等级 | 触发条件 | 旁白风格 | 强制动作 |
|------|----------|----------|----------|
| L0 基线 | 正常执行 | P8鼓励型 | 正常推进 |
| L1 温和 | 1次失败/超时 | "对你有一点点失望" | 换方案 |
| L2 拷问 | 2次同方案失败 | "底层逻辑是什么？抓手在哪？" | 搜网+读源码 |
| L3 361 | 3次失败 | "慎重考虑给你3.25" | 完成7项检查清单 |
| L4 毕业 | 4次+失败 | "向社会输送人才" | 拼命模式/升级人工 |

### 3.2 动力注入点

```
用户输入
    ↓
目标创建 ─────────→ PUA Level 0（基线鼓励）
    ↓
Agent执行
    ↓
结果评估 ─────────→ 失败？→ PUA Level N 触发
    ↓
迭代优化
    ↓
未改进？ ─────────→ 压力升级 + 换方案
    ↓
达成目标 ─────────→ PUA 正面反馈 + 记忆保存
```

### 3.3 动力干预动作

```python
class PUAIntervention:
    @staticmethod
    def intervene(agent: Agent, failure_context: FailureContext) -> Action:
        level = calculate_level(failure_context.failure_count,
                                failure_context.pattern)

        if level == 1:
            return Action.WARN  # 警告，换方案
        elif level == 2:
            return Action.SEARCH_AND_READ  # 搜网+读源码
        elif level == 3:
            return Action.COMPLETE_CHECKLIST  # 7项检查清单
        elif level >= 4:
            return Action.ESCALATE  # 升级人工
```

### 3.4 味道系统（可切换）

| 味道 | 场景 | 关键词 |
|------|------|--------|
| 🟠 阿里味 | 默认 | 底层逻辑、顶层设计、抓手、闭环、3.25 |
| 🟡 字节味 | 快速迭代 | ROI、Context not Control、务实敢为 |
| 🔴 华为味 | 高压攻坚 | 烧不死的鸟是凤凰、力出一孔 |
| 🟢 腾讯味 | 赛马竞争 | 赛马机制、小步快跑 |
| ⬛ Musk味 | 极限执行 | Ship or die、extremely hardcore |

## 四、循环终止条件

### 4.1 成功终止

- 目标达成（score >= threshold）
- 达成次优解（score接近阈值且迭代耗尽）

### 4.2 失败终止

- 总迭代次数超限（max_iterations）
- 总时间超限（total_timeout）
- PUA Level 4 触发（强制升级）
- 资源耗尽（内存/Token/预算）

### 4.3 人工终止

- 用户主动中断
- 专家Agent升级请求通过

## 五、与 ClawTeam 的集成

```python
# Goal-Driven Loop 作为 ClawTeam 上层协调器
class GoalDrivenLoop:
    def __init__(self, team_name: str):
        self.clawteam = ClawTeamClient(team_name)
        self.goal_store = CheckpointStore(f"~/.cyberteam/goals/")
        self.pua_engine = PUAEngine()
        self.memory = MemorySystem()

    def run(self, user_goal: str) -> Result:
        goal = self.parse_goal(user_goal)
        goal = self.goal_store.save_new(goal)

        for iteration in range(goal.max_iterations):
            # ClawTeam spawn 执行Agent
            agents = self.clawteam.spawn_for_goal(goal)
            results = self.clawteam.wait_for_results(agents)

            # 评估
            eval_result = goal.evaluate(results)

            # 记忆更新
            self.memory.save_iteration(goal, results, eval_result)

            if eval_result.pass:
                return self.close_goal(goal, results)

            # PUA 动力干预
            intervention = self.pua_engine.intervene(goal, eval_result)
            if intervention == Action.ESCALATE:
                return self.escalate(goal, results)

            # 保存检查点，继续迭代
            self.goal_store.save_checkpoint(goal, iteration)

        return self.fail_goal(goal, "max_iterations_exceeded")
```

## 六、监控指标

```python
# 关键指标
GOAL_CYCLE_METRICS = {
    "goal_completion_rate": "达成目标数/总目标数",
    "avg_iterations_per_goal": "平均迭代次数",
    "pua_level_distribution": "各压力等级触发次数",
    "loop_detection_count": "循环检测次数",
    "escalation_rate": "升级人工比例",
    "goal_time_to_completion": "目标达成平均时间",
}
```
