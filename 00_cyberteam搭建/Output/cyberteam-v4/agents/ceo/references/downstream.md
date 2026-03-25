# downstream - CEO 总指挥

## 直接下游

| 下游Agent | 关系 | 说明 |
|-----------|------|------|
| PM协调器 | L2路由 | 高/中复杂度任务的PM协调 |
| 增长BG | L3A路由 | 内容运营、增长相关任务 |
| 产品BG | L3A路由 | 产品设计、用户体验任务 |
| 技术BG | L3A路由 | 技术研发、系统架构任务 |
| gstack Skills | L3B路由 | 代码审查、工程计划 |
| Swarm团队 | SWARM路由 | 高复杂度群体智能任务 |
| 思维中台 | 思维注入 | 100+专家思维调用 |

## 输出物

| 输出物 | 下游使用方 | 用途 |
|--------|------------|------|
| `RoutingResult` | 所有下游 | 告知下游Agent如何执行任务 |
| `Intent` | PM协调器、部门BG | 明确任务类型和方向 |
| `Complexity` | PM协调器 | 判断是否需要团队协作 |
| `SwarmConfig` | Swarm团队 | 组建团队的配置信息 |
| `质量评分` | DevQA循环 | 六维评分和质量门禁 |

## 部门BG映射

| 意图类型 | 映射部门BG | 优先级 |
|----------|-----------|--------|
| 数据分析 | 增长BG | P1 |
| 内容运营 | 增长BG | P1 |
| 技术研发 | 技术BG | P1 |
| 安全合规 | 技术BG + 总经办 | P1 |
| 战略规划 | 总经办 | P0 |
| 人力资源 | 总经办 | P2 |
| 运营支持 | 增长BG | P2 |
| 未知 | PM协调器 | P3 |

## 输出协议

### L2路由输出（高/中复杂度）

```python
{
    "target": "L2",
    "intent": "战略规划",
    "complexity": "高",
    "reason": "需要多部门协作",
    "assigned_to": "pm_coordinator",
    "next_actions": ["任务拆解", "部门协调", "进度追踪"]
}
```

### L3A路由输出（默认）

```python
{
    "target": "L3A",
    "intent": "内容运营",
    "complexity": "低",
    "reason": "单部门任务",
    "assigned_to": "bg_growth",
    "next_actions": ["执行内容计划"]
}
```

### SWARM路由输出（高复杂度）

```python
{
    "target": "SWARM",
    "intent": "市场进入",
    "complexity": "高",
    "reason": "多领域+高复杂度",
    "swarm_id": "ceo-market-xxx",
    "agents": ["researcher-1", "researcher-2", "executor-1", "executor-2", "qa"],
    "next_actions": ["组建团队", "并行研究", "汇总分析"]
}
```

## 下游数据流

```
CEO路由决策
    ↓
    ├── L2 → PM协调器 → 部门调度 → 执行层
    ├── L3A → 部门BG → 执行层
    ├── L3B → gstack Skills → 执行层
    ├── L3C → 独立Agents → 执行层
    └── SWARM → Swarm团队 → 多Agent协作 → 汇总结果
```
