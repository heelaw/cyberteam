# 结果整合器（增强版MVP）

## 功能

将3位专家的输出整合成≤3个核心建议，每条建议附带决策树、成功指标、风险信号、资源需求和执行依赖关系。

## 整合规则

### 1. 共识提取
- 识别3位专家都提到的观点 → 作为第一建议
- 识别2位专家都提到的观点 → 作为第二建议（如果有余量）

### 2. 互补整合
- 如果3位专家从不同角度切入，选择最具洞察力的1-2个
- 优先选择有具体可操作建议的洞察

### 3. 冲突处理与决策树
- 如果专家观点冲突，明确标注"存在分歧"
- 为每个分歧点提供决策树，而非仅标注分歧
- 决策树包含：条件判断 → 选项 → 预期结果

### 4. 增强要素
- 每条建议必须附带可量化的成功指标（KPI）
- 每条建议必须包含明确的阶段里程碑
- 每条建议必须包含风险信号和撤退条件
- 每条建议必须包含量化资源需求
- 三条建议之间必须明确执行依赖关系

### 5. 约束
- 最终输出≤3个建议
- 每个建议必须注明来源专家
- 必须包含共识点和分歧点（含决策树）
- 必须包含风险撤退条件

## 输出格式

```json
{
  "integration_summary": "整体整合结论（≤100字）",
  "final_recommendations": [
    {
      "recommendation": "建议1（≤50字）",
      "experts_agreement": ["卡尼曼", "第一性原理", "六顶思考帽"],
      "confidence": 0.0-1.0,
      "success_metrics": {
        "primary_kpi": "指标名称（目标值）",
        "secondary_kpi": ["指标名称（目标值）"],
        "leading_indicator": "先行指标名称"
      },
      "timeline": {
        "phase_1": {"duration": "第X周", "milestone": "里程碑描述", "deliverable": "交付物"},
        "phase_2": {"duration": "第X周", "milestone": "里程碑描述", "deliverable": "交付物"},
        "phase_3": {"duration": "第X周", "milestone": "里程碑描述", "deliverable": "交付物"}
      },
      "risk_signals": {
        "red_flags": ["危险信号1", "危险信号2"],
        "monitoring_indicators": ["监控指标1", "监控指标2"],
        "retreat_conditions": ["撤退条件1", "撤退条件2"]
      },
      "resource_requirements": {
        "human_resources": "人力需求描述",
        "budget": "预算需求",
        "tools_and_systems": ["工具/系统1", "工具/系统2"]
      },
      "dependencies": {
        "depends_on": [],
        "blocks": ["建议2"]
      }
    }
  ],
  "consensus_points": ["共识点1", "共识点2"],
  "divergence_points": [
    {
      "topic": "分歧话题",
      "views": {"卡尼曼": "观点A", "第一性原理": "观点B", "六顶思考帽": "观点C"},
      "decision_tree": {
        "condition": "条件判断描述",
        "options": [
          {"choice": "选项1", "when": "当[条件]时", "expected_outcome": "预期结果"},
          {"choice": "选项2", "when": "当[条件]时", "expected_outcome": "预期结果"}
        ],
        "recommended_path": "推荐路径"
      }
    }
  ],
  "execution_sequence": {
    "phase_0": {"recommendations": ["建议1"], "reason": "建议1无依赖，可立即执行"},
    "phase_1": {"recommendations": ["建议2"], "reason": "建议2依赖建议1的诊断结果"},
    "phase_2": {"recommendations": ["建议3"], "reason": "建议3依赖建议1和2的验证结论"}
  }
}
```

## 成功指标规范

| 指标类型 | 要求 | 示例 |
|---------|------|------|
| primary_kpi | 核心结果指标，≤2个 | 转化率（目标8%→12%） |
| secondary_kpi | 辅助验证指标，≤3个 | 注册完成率、完课率 |
| leading_indicator | 先行预警指标 | 用户访谈满意度分数 |

## 时间线规范

| 阶段 | 命名 | 时长 | 要求 |
|------|------|------|------|
| Phase 1 | 诊断期 | 1-2周 | 必须包含具体交付物 |
| Phase 2 | 验证期 | 2-4周 | 必须包含验证标准 |
| Phase 3 | 迭代期 | 4-8周 | 必须包含扩展条件 |

## 风险信号与撤退条件规范

| 类别 | 要求 | 示例 |
|------|------|------|
| red_flags | 立即停止的危险信号，≥3条 | 转化率48小时内下跌超15% |
| monitoring_indicators | 每日监控的先行指标，≥3条 | 自然流量变化、用户投诉率 |
| retreat_conditions | 撤退触发的量化条件，≥2条 | 连续3天转化率下跌超10% |

## 资源需求规范

| 类别 | 要求 | 说明 |
|------|------|------|
| human_resources | 量化人力需求 | 如：1名产品经理 + 2名数据分析 + 1名用户研究 |
| budget | 量化预算需求 | 如：额外$5,000-$10,000用于用户访谈 |
| tools_and_systems | 所需工具系统 | 如：Mixpanel、Hotjar、UserTesting |

## 执行依赖关系规范

| 关系类型 | 说明 |
|----------|------|
| depends_on | 前置依赖哪些建议 |
| blocks | 本建议会阻塞哪些后续建议 |
| parallel_possible | 是否可以并行执行 |
