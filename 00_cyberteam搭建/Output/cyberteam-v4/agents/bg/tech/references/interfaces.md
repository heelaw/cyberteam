# interfaces - 技术BG Agent

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `task` | Task | CEO路由分配的任务对象 |
| `intent` | Intent | 任务意图类型（技术研发/架构设计） |
| `product_spec` | ProductSpec | 产品规格（来自产品BG） |
| `tech_constraints` | TechConstraints | 技术约束条件（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `result` | ExecutionResult | 任务执行结果 |
| `deliverables` | Deliverable[] | 产出的交付物 |
| `code_artifact` | CodeArtifact | 代码产物 |
| `test_result` | TestResult | 测试结果 |
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
| 功能开发 | "开发用户登录功能" | 代码 + 测试用例 |
| 架构设计 | "设计微服务架构" | 架构文档 + 组件图 |
| Bug修复 | "修复支付回调失败问题" | 修复代码 + 原因分析 |
| 性能优化 | "优化接口响应时间" | 优化方案 + 代码 |
| 安全审计 | "审计用户数据存储" | 安全报告 + 建议 |

## 调用示例

```python
from agents.bg.tech import TechBG

tech = TechBG()
result = tech.execute(task={
    "type": "功能开发",
    "description": "开发会员积分计算功能",
    "requirements": {"实时性": "<100ms", "准确性": "99.9%"},
    "tech_stack": ["Python", "Redis", "MySQL"]
})

# 返回示例
{
    "status": "completed",
    "deliverables": [
        {"type": "代码", "path": "services/points.py"},
        {"type": "测试用例", "path": "tests/test_points.py"}
    ],
    "test_result": {"覆盖率": "95%", "通过率": "100%"}
}
```
