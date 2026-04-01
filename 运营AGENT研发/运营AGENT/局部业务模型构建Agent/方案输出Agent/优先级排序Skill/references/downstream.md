# 优先级排序Skill - 下游去向

## 输出的Skills

| 下游Skill | 依赖类型 | 描述 |
|-----------|----------|------|
| 行动计划输出 | 强依赖 | 排序结果用于生成行动计划 |

## 数据输出

| 输出数据 | 类型 | 描述 | 下游使用 |
|----------|------|------|----------|
| ranked_list | Array | 排序后的解决方案列表 | 行动计划输出 |
| allocation_plan | Object | 资源分配建议 | 行动计划输出 |
| priority_summary | Object | 优先级摘要 | CEO/管理层汇报 |

## 输出配置

```yaml
downstream_outputs:
  primary:
    - skill: action-plan-output
      input: ranked_list
      output: action_plan
  secondary:
    - destination: reporting
      data: priority_summary
      format: markdown
```
