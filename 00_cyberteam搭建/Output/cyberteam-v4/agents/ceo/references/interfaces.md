# interfaces - CEO 总指挥

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `user_query` | string | 用户输入的任务描述 |
| `user_context` | object | 用户上下文信息（可选） |
| `session_id` | string | 会话ID（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `routing_result` | RoutingResult | 路由决策结果 |
| `intent` | Intent | 识别出的用户意图（8种） |
| `complexity` | Complexity | 复杂度评估（高/中/低） |
| `swarm_id` | string | Swarm团队ID（高复杂度时） |
| `agents` | Agent[] | 分配的Agent列表（可选） |

## RoutingResult 结构

```yaml
RoutingResult:
  target: enum          # L2/L3A/L3B/L3C/SWARM
  intent: Intent         # 数据分析|内容运营|技术研发|安全合规|战略规划|人力资源|运营支持|未知
  complexity: Complexity # 高|中|低
  reason: string         # 路由原因说明
  swarm_id: string       # SWARM模式时返回
  agents: Agent[]        # 分配的Agent列表
```

## 调用示例

```python
from engine.ceo import CEORouter

router = CEORouter()
result = router.route("用户任务描述")

# 返回示例
{
    "target": "SWARM",
    "intent": "战略规划",
    "complexity": "高",
    "reason": "高复杂度+多领域+战略类型",
    "swarm_id": "ceo-strategy-xxx-uuid",
    "agents": ["researcher-1", "researcher-2", "executor-1", "executor-2", "qa"]
}
```

## 意图识别映射

| 意图 | 触发关键词 |
|------|------------|
| 数据分析 | 增长, 数据, 分析, 财务, ROI, 转化率, GMV, DAU, 留存, LTV |
| 内容运营 | 内容, 文案, 创作, 文章, 发布, 公众号, 小红书, 抖音, 营销, 推广 |
| 技术研发 | 开发, 代码, 功能, 实现, 修复, Bug, 架构, 测试, 部署, API |
| 安全合规 | 安全, 审计, 合规, 隐私, 漏洞, 渗透 |
| 战略规划 | 战略, 规划, 方案, 决策, 竞争, 市场, 进入 |
| 人力资源 | 招聘, 绩效, 团队, 人力, OKR |
| 运营支持 | 运营, 活动, 用户, 社群, 增长黑客 |

## 路由目标映射

| 目标 | 说明 | 触发条件 |
|------|------|----------|
| L2 | PM + Strategy 协调层 | 高/中复杂度 |
| L3A | CyberTeam 部门 | 默认路由 |
| L3B | Gstack Skills | 技术研发/代码审查 |
| L3C | 独立 Agents | 通用功能开发 |
| SWARM | Swarm 群体智能 | 高复杂度+多领域+明确要求 |
