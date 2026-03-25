# interfaces - 产品BG Agent

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `task` | Task | CEO路由分配的任务对象 |
| `intent` | Intent | 任务意图类型（产品设计/用户体验） |
| `user_research` | UserResearch | 用户研究数据（可选） |
| `business_goals` | BusinessGoals | 业务目标（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `result` | ExecutionResult | 任务执行结果 |
| `deliverables` | Deliverable[] | 产出的交付物 |
| `product_spec` | ProductSpec | 产品规格说明 |
| `next_handoff` | Handoff | 下游交接信息（可选） |

## ExecutionResult 结构

```yaml
ExecutionResult:
  status: enum              # pending/running/completed/failed/blocked
  progress: float           # 0-100 百分比
  output: object            # 执行输出
  quality_score: float      # 0-1 质量评分
  issues: Issue[]           # 发现的问题
```

## 适用场景

| 场景 | 输入示例 | 预期输出 |
|------|----------|----------|
| 需求分析 | "分析用户登录转化率低的原因" | 需求文档 + 优先级排序 |
| 产品设计 | "设计新的会员体系" | 产品方案 + 原型描述 |
| UX优化 | "优化结账流程" | 体验优化方案 |
| 数据分析 | "分析功能使用情况" | 数据报告 + 建议 |
| 竞品分析 | "分析竞品的小红书功能" | 竞品报告 + 建议 |

## 调用示例

```python
from agents.bg.product import ProductBG

product = ProductBG()
result = product.execute(task={
    "type": "产品设计",
    "description": "设计新的用户积分体系",
    "target_users": "活跃用户",
    "business_goals": {"提升留存": "20%"}
})

# 返回示例
{
    "status": "completed",
    "deliverables": [
        {"type": "产品方案", "content": "..."},
        {"type": "功能清单", "content": "..."}
    ],
    "product_spec": {"积分规则": "...", "兑换比例": "..."}
}
```
