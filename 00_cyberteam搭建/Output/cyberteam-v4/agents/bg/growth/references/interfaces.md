# interfaces - 增长BG Agent

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `task` | Task | CEO路由分配的任务对象 |
| `intent` | Intent | 任务意图类型 |
| `context` | Context | 任务执行上下文 |
| `roi_requirements` | object | ROI要求（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `result` | ExecutionResult | 任务执行结果 |
| `deliverables` | Deliverable[] | 产出的交付物 |
| `metrics` | Metrics | 效果指标数据 |
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
| 内容运营 | "发布一篇小红书文案" | 文案内容 + 配图建议 |
| 活动策划 | "策划一场增长活动" | 活动方案 + SOP |
| 用户增长 | "提升DAU 20%" | 增长策略 + 执行计划 |
| 数据分析 | "分析本月GMV下降原因" | 分析报告 + 建议 |
| 社媒运营 | "运营抖音账号" | 内容计划 + 发布排期 |

## 调用示例

```python
from agents.bg.growth import GrowthBG

growth = GrowthBG()
result = growth.execute(task={
    "type": "内容运营",
    "description": "发布一篇产品推广小红书",
    "target": "18-25岁女性",
    "product": "智能手表"
})

# 返回示例
{
    "status": "completed",
    "deliverables": [
        {"type": "文案", "content": "..."},
        {"type": "配图建议", "content": "..."}
    ],
    "metrics": {"预计转化率": "3-5%"}
}
```
