# 优先级排序Skill - 接口协议

## 输入接口

| 接口名称 | 类型 | 描述 | 必需 |
|----------|------|------|------|
| solutions | Array | 待排序的解决方案列表 | 是 |
| criteria | Object | 评估标准配置 | 否 |
| constraints | Object | 资源约束条件 | 否 |

### solutions 结构
```yaml
solutions:
  - id: string
    name: string
    description: string
    expected_effect: string
    resource_requirements: object
    difficulty: number
```

## 输出接口

| 接口名称 | 类型 | 描述 |
|----------|------|------|
| ranked_list | Array | 排序后的解决方案列表 |
| allocation_plan | Object | 资源分配建议 |
| reasoning | Object | 排序理由 |

### ranked_list 结构
```yaml
ranked_list:
  - priority: P0/P1/P2/P3
    solution_id: string
    score: number
    key_dimensions: object
```

## 调用示例

```yaml
input:
  solutions:
    - id: "sol-001"
      name: "方案A"
      description: "优化用户体验"
      expected_effect: "提升转化率20%"
      resource_requirements:
        effort: "5人天"
        cost: "10万"
  criteria:
    impact: 0.4
    feasibility: 0.3
    urgency: 0.3
```

## 错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| E001 | 解决方案列表为空 | 返回空列表 |
| E002 | 解决方案数据不完整 | 返回缺失字段列表 |
| E003 | 评估标准配置错误 | 使用默认标准 |
