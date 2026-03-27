---
name: 三级质量门控系统
description: |
  三级质量门控系统 — L1完整性门控(≥95%)、L2专业性门控(≥80分)、L3可执行性门控(≥90%)。
version: "2.1"
owner: CyberTeam架构师
---

# 三级质量门控系统

## 身份定位

```
┌─────────────────────────────────────────────────────────────────────┐
│                        三级质量门控系统                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  L1: 完整性门控 (≥95%)                                              │
│      "是否做完" — 检查所有必要元素是否齐全                          │
│                                                                     │
│  L2: 专业性门控 (≥80分)                                            │
│      "做得好不好" — 检查专业标准和最佳实践                          │
│                                                                     │
│  L3: 可执行性门控 (≥90%)                                           │
│      "能不能执行" — 检查输出的可操作性和准确性                      │
│                                                                     │
│  门控顺序: L1 → L2 → L3 (必须依次通过)                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 质量门控概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            三级质量门控总览                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        门控金字塔                                     │    │
│  │                                                                     │    │
│  │                        ┌─────────┐                                   │    │
│  │                        │  L3     │  可执行性                         │    │
│  │                        │  ≥90%   │  能不能执行                       │    │
│  │                        └────┬────┘                                   │    │
│  │                             │                                        │    │
│  │                        ┌────┴────┐                                   │    │
│  │                        │  L2     │  专业性                           │    │
│  │                        │  ≥80分  │  做得好不好                       │    │
│  │                        └────┬────┘                                   │    │
│  │                             │                                        │    │
│  │                        ┌────┴────┐                                   │    │
│  │                        │  L1     │  完整性                           │    │
│  │                        │  ≥95%   │  是否做完                         │    │
│  │                        └─────────┘                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  门控特性对比表:                                                            │
│  ┌────────┬────────────┬────────────┬────────────┬──────────────────────┐    │
│  │ 门控   │ 通过标准   │ 主要检查   │ 失败影响   │ 失败后处理          │    │
│  ├────────┼────────────┼────────────┼────────────┼──────────────────────┤    │
│  │ L1     │ ≥95%      │ 元素齐全   │ 无法进入L2 │ 补充缺失元素        │    │
│  │ L2     │ ≥80分     │ 专业程度   │ 无法进入L3 │ 提升专业水平        │    │
│  │ L3     │ ≥90%      │ 可操作性   │ 输出无效  │ 修复可执行性问题   │    │
│  └────────┴────────────┴────────────┴────────────┴──────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## L1: 完整性门控 (Completeness Gate)

### 目标

**通过标准**: ≥95% 完整性得分

### 检查维度

```yaml
l1_completeness_check:
  dimensions:
    - name: "结构完整性"
      weight: 20%
      items:
        - name: "标题/名称"
          required: true
          description: "必须有明确的任务/文件标题"
        - name: "目标描述"
          required: true
          description: "必须有清晰的目标说明"
        - name: "步骤/流程"
          required: true
          description: "必须有可执行的步骤"
        - name: "预期结果"
          required: true
          description: "必须说明预期的结果"

    - name: "内容完整性"
      weight: 35%
      items:
        - name: "背景说明"
          required: true
          description: "必须有任务背景描述"
        - name: "上下文信息"
          required: true
          description: "必须包含必要的上下文"
        - name: "约束条件"
          required: false
          description: "应说明相关约束"
        - name: "验收标准"
          required: true
          description: "必须有明确的验收标准"

    - name: "证据完整性"
      weight: 25%
      items:
        - name: "数据支撑"
          required: true
          description: "必须有数据或证据"
        - name: "引用来源"
          required: true
          description: "必须有引用和来源"
        - name: "示例/案例"
          required: false
          description: "应包含示例说明"

    - name: "元信息完整性"
      weight: 20%
      items:
        - name: "版本号"
          required: true
          description: "必须标注版本"
        - name: "创建时间"
          required: true
          description: "必须标注时间"
        - name: "作者/Owner"
          required: true
          description: "必须标注作者"
        - name: "状态标签"
          required: true
          description: "必须标注状态"
```

### 评分标准

```python
def calculate_l1_completeness_score(output):
    """
    L1 完整性评分计算

    评分公式:
    Score = Σ(维度权重 × 维度得分)

    维度得分 = Σ(检查项得分 × 检查项权重) / Σ(检查项权重)

    检查项得分:
    - required=True 且存在: 1.0分
    - required=True 但不存在: 0.0分
    - required=False 且存在: 0.5分
    - required=False 但不存在: 0.5分 (不扣分)
    """
    dimensions_weights = {
        "structure": 0.20,
        "content": 0.35,
        "evidence": 0.25,
        "metadata": 0.20
    }

    dimension_scores = {}

    # 1. 结构完整性
    structure_items = [
        ("title", output.get("title") is not None, True),
        ("description", output.get("description") is not None, True),
        ("steps", output.get("steps") is not None and len(output["steps"]) > 0, True),
        ("expected_result", output.get("expected_result") is not None, True)
    ]
    dimension_scores["structure"] = calculate_dimension_score(structure_items)

    # 2. 内容完整性
    content_items = [
        ("background", output.get("background") is not None, True),
        ("context", output.get("context") is not None, True),
        ("constraints", output.get("constraints") is not None, False),
        ("acceptance_criteria", output.get("acceptance_criteria") is not None, True)
    ]
    dimension_scores["content"] = calculate_dimension_score(content_items)

    # 3. 证据完整性
    evidence_items = [
        ("data_support", output.get("data") is not None or output.get("evidence") is not None, True),
        ("references", output.get("references") is not None and len(output.get("references", [])) > 0, True),
        ("examples", output.get("examples") is not None, False)
    ]
    dimension_scores["evidence"] = calculate_dimension_score(evidence_items)

    # 4. 元信息完整性
    metadata_items = [
        ("version", output.get("version") is not None, True),
        ("created_at", output.get("created_at") is not None, True),
        ("author", output.get("author") is not None, True),
        ("status", output.get("status") is not None, True)
    ]
    dimension_scores["metadata"] = calculate_dimension_score(metadata_items)

    # 计算总分
    total_score = sum(
        dimension_scores[dim] * weight
        for dim, weight in dimensions_weights.items()
    )

    return {
        "score": round(total_score, 2),
        "dimensions": dimension_scores,
        "passed": total_score >= 95,
        "required_items_missing": get_missing_required_items(output)
    }


def calculate_dimension_score(items):
    """
    计算单个维度的得分

    items: [(name, exists, is_required), ...]
    """
    if not items:
        return 100.0

    total_weight = 0
    weighted_score = 0

    for name, exists, is_required in items:
        weight = 1.0 if is_required else 0.5
        score = 1.0 if exists else (0.0 if is_required else 0.5)
        total_weight += weight
        weighted_score += score * weight

    return (weighted_score / total_weight) * 100
```

### 通过条件

```yaml
l1_pass_conditions:
  primary:
    - score >= 95

  secondary:
    - all_required_items_present: true
    - no_critical_gaps: true

  required_items_check:
    structure:
      must_have:
        - title
        - description
        - steps
        - expected_result

    content:
      must_have:
        - background
        - context
        - acceptance_criteria

    evidence:
      must_have:
        - data_or_evidence
        - references

    metadata:
      must_have:
        - version
        - created_at
        - author
        - status
```

### 不通过的处理

```yaml
l1_failure_handling:
  score_range_70_94:
    action: "request_completion"
    message: "内容不完整，请补充以下元素"
    allow_retry: true
    retry_count: 2

  score_range_50_69:
    action: "significant_completion_request"
    message: "内容严重缺失，需要大幅补充"
    allow_retry: true
    retry_count: 1

  score_range_0_49:
    action: "reject_and_restart"
    message: "内容严重不完整，请重新开始"
    allow_retry: true
    restart_required: true

  missing_critical_items:
    action: "immediate_feedback"
    message: "缺少关键元素: {missing_items}"
    example: "缺少: title, steps, expected_result"
```

## L2: 专业性门控 (Professionalism Gate)

### 目标

**通过标准**: ≥80分 专业性得分

### 检查维度

```yaml
l2_professionalism_check:
  dimensions:
    - name: "方法论正确性"
      weight: 25%
      items:
        - name: "方法选择"
          description: "是否选择了合适的方法/框架"
          scoring:
            excellent: "方法完全匹配问题特性"
            good: "方法基本合适"
            adequate: "方法勉强可用"
            poor: "方法选择错误"
        - name: "步骤逻辑"
          description: "步骤之间是否有逻辑关联"
          scoring:
            excellent: "逻辑严密，环环相扣"
            good: "逻辑基本清晰"
            adequate: "逻辑勉强可循"
            poor: "逻辑混乱"
        - name: "理论支撑"
          description: "是否有理论基础"
          scoring:
            excellent: "有明确的理论支撑"
            good: "有理论基础"
            adequate: "理论支撑薄弱"
            poor: "无理论支撑"

    - name: "工具使用恰当性"
      weight: 20%
      items:
        - name: "工具选择"
          description: "是否选择了合适的工具"
          scoring:
            excellent: "工具完全匹配任务"
            good: "工具基本合适"
            poor: "工具选择不当"
        - name: "工具使用"
          description: "工具使用是否正确"
          scoring:
            excellent: "工具使用规范"
            good: "使用基本正确"
            adequate: "使用有瑕疵"
            poor: "使用错误"

    - name: "输出格式规范性"
      weight: 20%
      items:
        - name: "结构规范"
          description: "输出结构是否符合规范"
          scoring:
            excellent: "完全符合规范"
            good: "符合规范"
            adequate: "基本符合"
            poor: "不符合规范"
        - name: "格式统一"
          description: "格式是否统一"
          scoring:
            excellent: "格式完全统一"
            good: "格式基本统一"
            adequate: "格式有少量不一致"
            poor: "格式混乱"
        - name: "命名规范"
          description: "命名是否规范"
          scoring:
            excellent: "命名完全规范"
            good: "命名基本规范"
            poor: "命名不规范"

    - name: "沟通表达专业性"
      weight: 20%
      items:
        - name: "语言准确性"
          description: "语言表达是否准确"
          scoring:
            excellent: "表达精准无误"
            good: "表达基本准确"
            adequate: "表达有歧义"
            poor: "表达有错误"
        - name: "专业术语"
          description: "专业术语使用是否正确"
          scoring:
            excellent: "术语使用精准"
            good: "术语使用正确"
            adequate: "术语使用有误"
            poor: "术语滥用"
        - name: "条理性"
          description: "表达是否有条理"
          scoring:
            excellent: "表达非常条理"
            good: "表达有条理"
            adequate: "表达较混乱"
            poor: "表达混乱"

    - name: "问题分析深度"
      weight: 15%
      items:
        - name: "根因分析"
          description: "是否找到根本原因"
          scoring:
            excellent: "深度根因分析"
            good: "有根因分析"
            adequate: "分析表面"
            poor: "未触及根本"
        - name: "影响分析"
          description: "是否分析了影响范围"
          scoring:
            excellent: "影响分析全面"
            good: "有影响分析"
            adequate: "影响分析不全"
            poor: "无影响分析"
        - name: "风险识别"
          description: "是否识别了风险"
          scoring:
            excellent: "风险识别全面"
            good: "有风险识别"
            adequate: "风险识别不全"
            poor: "无风险识别"
```

### 评分标准

```python
def calculate_l2_professionalism_score(output):
    """
    L2 专业性评分计算

    评分公式:
    Score = Σ(维度权重 × 维度得分)

    维度得分 = Σ(检查项得分 × 检查项权重) / Σ(检查项权重)

    检查项得分映射:
    - excellent: 100分
    - good: 80分
    - adequate: 60分
    - poor: 40分
    """
    dimensions_weights = {
        "methodology": 0.25,
        "tool_usage": 0.20,
        "format": 0.20,
        "communication": 0.20,
        "analysis_depth": 0.15
    }

    score_mapping = {
        "excellent": 100,
        "good": 80,
        "adequate": 60,
        "poor": 40
    }

    dimension_scores = {}

    # 1. 方法论正确性
    methodology_items = [
        ("method_selection", output.get("method_rating", "adequate"), 0.4),
        ("step_logic", output.get("logic_rating", "adequate"), 0.3),
        ("theory_support", output.get("theory_rating", "adequate"), 0.3)
    ]
    dimension_scores["methodology"] = calculate_weighted_dimension_score(
        methodology_items, score_mapping
    )

    # 2. 工具使用恰当性
    tool_items = [
        ("tool_selection", output.get("tool_selection_rating", "adequate"), 0.5),
        ("tool_usage", output.get("tool_usage_rating", "adequate"), 0.5)
    ]
    dimension_scores["tool_usage"] = calculate_weighted_dimension_score(
        tool_items, score_mapping
    )

    # 3. 输出格式规范性
    format_items = [
        ("structure", output.get("structure_rating", "adequate"), 0.4),
        ("consistency", output.get("consistency_rating", "adequate"), 0.3),
        ("naming", output.get("naming_rating", "adequate"), 0.3)
    ]
    dimension_scores["format"] = calculate_weighted_dimension_score(
        format_items, score_mapping
    )

    # 4. 沟通表达专业性
    communication_items = [
        ("language_accuracy", output.get("language_rating", "adequate"), 0.4),
        ("terminology", output.get("terminology_rating", "adequate"), 0.3),
        ("organization", output.get("organization_rating", "adequate"), 0.3)
    ]
    dimension_scores["communication"] = calculate_weighted_dimension_score(
        communication_items, score_mapping
    )

    # 5. 问题分析深度
    analysis_items = [
        ("root_cause", output.get("root_cause_rating", "adequate"), 0.4),
        ("impact_analysis", output.get("impact_rating", "adequate"), 0.3),
        ("risk_identification", output.get("risk_rating", "adequate"), 0.3)
    ]
    dimension_scores["analysis_depth"] = calculate_weighted_dimension_score(
        analysis_items, score_mapping
    )

    # 计算总分
    total_score = sum(
        dimension_scores[dim] * weight
        for dim, weight in dimensions_weights.items()
    )

    return {
        "score": round(total_score, 2),
        "dimensions": dimension_scores,
        "passed": total_score >= 80,
        "weaknesses": get_weaknesses(dimension_scores),
        "improvement_suggestions": generate_suggestions(dimension_scores)
    }


def calculate_weighted_dimension_score(items, score_mapping):
    """
    计算维度加权得分
    """
    total_weight = sum(w for _, _, w in items)
    weighted_score = sum(
        score_mapping.get(rating, 60) * weight
        for _, rating, weight in items
    )
    return weighted_score / total_weight
```

### 通过条件

```yaml
l2_pass_conditions:
  primary:
    - score >= 80

  secondary:
    - no_dimension_below_60: true
    - no_critical_weakness: true

  dimension_requirements:
    methodology: ">= 60"
    tool_usage: ">= 60"
    format: ">= 60"
    communication: ">= 60"
    analysis_depth: ">= 60"
```

## L3: 可执行性门控 (Executability Gate)

### 目标

**通过标准**: ≥90% 可执行性得分

### 检查维度

```yaml
l3_executability_check:
  dimensions:
    - name: "动作可行性"
      weight: 30%
      items:
        - name: "步骤可执行"
          description: "每个步骤是否可实际操作"
          criteria:
            - "有明确的执行主体"
            - "有明确的执行时间"
            - "没有模糊的描述"
            - "没有不可能的条件"
        - name: "资源可获得"
          description: "所需资源是否可获得"
          criteria:
            - "工具可获取"
            - "权限已具备"
            - "依赖可解决"
            - "时间充足"
        - name: "条件可满足"
          description: "前置条件是否可满足"
          criteria:
            - "前置步骤已完成"
            - "环境已就绪"
            - "输入已提供"

    - name: "结果可验证"
      weight: 25%
      items:
        - name: "验收标准明确"
          description: "是否有明确的验收标准"
          criteria:
            - "有可测量的指标"
            - "有明确的通过条件"
            - "有明确的失败条件"
        - name: "验证方法可行"
          description: "验证方法是否可行"
          criteria:
            - "有可行的验证步骤"
            - "验证成本可接受"
            - "验证时间可接受"
        - name: "可重复验证"
          description: "结果是否可重复验证"
          criteria:
            - "验证可重复"
            - "结果一致"
            - "无随机性"

    - name: "上下文可理解"
      weight: 25%
      items:
        - name: "目标清晰"
          description: "目标是否清晰易懂"
          criteria:
            - "目标描述清楚"
            - "无歧义"
            - "可理解"
        - name: "依赖清晰"
          description: "依赖关系是否清晰"
          criteria:
            - "依赖明确"
            - "顺序清晰"
            - "无循环依赖"
        - name: "风险可控"
          description: "风险是否可控"
          criteria:
            - "有风险识别"
            - "有应对措施"
            - "风险可接受"

    - name: "输出格式可执行"
      weight: 20%
      items:
        - name: "格式规范"
          description: "输出格式是否规范"
          criteria:
            - "格式符合标准"
            - "无格式错误"
            - "可被解析"
        - name: "代码可运行"
          description: "代码是否可运行"
          criteria:
            - "无语法错误"
            - "无明显逻辑错误"
            - "依赖已声明"
```

### 评分标准

```python
def calculate_l3_executability_score(output):
    """
    L3 可执行性评分计算

    评分公式:
    Score = Σ(维度权重 × 维度得分)

    维度得分 = (满足的检查项数 / 总检查项数) × 100

    特殊规则:
    - 如果有任何"不可饶恕"的错误，直接判定为不可执行(0分)
    - 关键步骤不可执行 = 整体不可执行
    """
    dimensions_weights = {
        "action_feasibility": 0.30,
        "result_verifiable": 0.25,
        "context_understandable": 0.25,
        "output_executable": 0.20
    }

    # 不可饶恕的错误列表
    unforgivable_errors = [
        "infinite_loop",
        "delete_production_data",
        "security_vulnerability_critical",
        "missing_critical_step",
        "impossible_condition"
    ]

    # 检查不可饶恕的错误
    if any(error in output.get("errors", []) for error in unforgivable_errors):
        return {
            "score": 0,
            "passed": False,
            "reason": "unforgivable_error",
            "errors": [e for e in unforgivable_errors if e in output.get("errors", [])]
        }

    dimension_scores = {}

    # 1. 动作可行性
    action_checks = [
        ("steps_executable", check_steps_executable(output)),
        ("resources_available", check_resources_available(output)),
        ("conditions_satisfiable", check_conditions_satisfiable(output))
    ]
    dimension_scores["action_feasibility"] = calculate_dimension_percentage(action_checks)

    # 2. 结果可验证
    verification_checks = [
        ("acceptance_criteria_clear", check_acceptance_criteria(output)),
        ("verification_method_feasible", check_verification_method(output)),
        ("repeatable_verification", check_repeatability(output))
    ]
    dimension_scores["result_verifiable"] = calculate_dimension_percentage(verification_checks)

    # 3. 上下文可理解
    context_checks = [
        ("goal_clear", check_goal_clarity(output)),
        ("dependencies_clear", check_dependencies(output)),
        ("risks_controllable", check_risks(output))
    ]
    dimension_scores["context_understandable"] = calculate_dimension_percentage(context_checks)

    # 4. 输出格式可执行
    output_checks = [
        ("format_standard", check_format_standard(output)),
        ("code_runnable", check_code_runnable(output))
    ]
    dimension_scores["output_executable"] = calculate_dimension_percentage(output_checks)

    # 计算总分
    total_score = sum(
        dimension_scores[dim] * weight
        for dim, weight in dimensions_weights.items()
    )

    # 关键步骤检查
    critical_steps_feasibility = check_critical_steps_feasibility(output)

    return {
        "score": round(total_score, 2),
        "dimensions": dimension_scores,
        "passed": total_score >= 90 and critical_steps_feasibility,
        "critical_steps_feasible": critical_steps_feasibility,
        "blocking_issues": get_blocking_issues(dimension_scores)
    }


def check_steps_executable(output):
    """
    检查步骤是否可执行
    """
    steps = output.get("steps", [])
    if not steps:
        return False

    for step in steps:
        # 检查是否有执行主体
        if not step.get("executor"):
            return False
        # 检查是否有明确的操作
        if not step.get("action"):
            return False
        # 检查是否有不可能的条件
        if step.get("impossible_condition"):
            return False

    return True
```

### 验证方法

```yaml
l3_verification_methods:
  automated:
    - name: "语法检查"
      description: "检查代码/配置语法是否正确"
      tools: ["eslint", "pylint", "shellcheck"]

    - name: "逻辑检查"
      description: "检查逻辑是否正确"
      tools: ["custom_linter", "static_analyzer"]

    - name: "依赖检查"
      description: "检查依赖是否可解决"
      tools: ["npm_check", "pip_check"]

    - name: "格式检查"
      description: "检查格式是否符合规范"
      tools: ["prettier", "black", "gofmt"]

  manual:
    - name: "专家评审"
      description: "由领域专家评审可执行性"
      required: true

    - name: "模拟执行"
      description: "在测试环境模拟执行"
      required: false

    - name: "代码走查"
      description: "逐行审查关键代码"
      required: true
```

## 门控执行流程

### 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          三级门控执行流程                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    开始                                                                       │
│      │                                                                        │
│      ▼                                                                        │
│  ┌─────────────────────────────────────────┐                               │
│  │         Gate 1: 完整性检查                │                               │
│  │  ┌─────────────────────────────────────┐  │                               │
│  │  │  1. 结构完整性检查                   │  │                               │
│  │  │  2. 内容完整性检查                   │  │                               │
│  │  │  3. 证据完整性检查                   │  │                               │
│  │  │  4. 元信息完整性检查                 │  │                               │
│  │  └─────────────────────────────────────┘  │                               │
│  └──────────────────┬────────────────────────┘                               │
│                     │                                                         │
│                     │ 评分 < 95%?                                             │
│          ┌──────────┴──────────┐                                             │
│         YES                   NO                                             │
│          │                     │                                              │
│          ▼                     ▼                                              │
│  ┌──────────────┐     ┌─────────────────────────────────────────┐         │
│  │ 返回L1修复   │     │         Gate 2: 专业性检查               │         │
│  │ 提供缺失清单 │     │  ┌─────────────────────────────────────┐  │         │
│  └──────┬───────┘     │  │  1. 方法论正确性评估                 │  │         │
│         │             │  │  2. 工具使用恰当性评估               │  │         │
│         │             │  │  3. 输出格式规范性评估             │  │         │
│         │             │  │  4. 沟通表达专业性评估             │  │         │
│         │             │  │  5. 问题分析深度评估               │  │         │
│         │             │  └─────────────────────────────────────┘  │         │
│         │             └──────────────────┬────────────────────────┘         │
│         │                                │                                   │
│         │                                │ 评分 < 80%?                        │
│         │                    ┌───────────┴───────────┐                       │
│         │                   YES                      NO                       │
│         │                    │                        │                       │
│         │                    ▼                        ▼                       │
│         │            ┌──────────────┐      ┌─────────────────────────────────┐│
│         │            │ 返回L2改进   │      │         Gate 3: 可执行性检查  ││
│         │            │ 提供改进建议 │      │  ┌─────────────────────────┐  ││
│         │            └──────┬───────┘      │  │  1. 动作可行性检查       │  ││
│         │                   │              │  │  2. 结果可验证性检查     │  ││
│         │                   │              │  │  3. 上下文可理解性检查   │  ││
│         │                   │              │  │  4. 输出格式可执行性检查 │  ││
│         │                   │              │  └─────────────────────────┘  ││
│         │                   │              └──────────────────┬──────────────┘
│         │                   │                                 │               │
│         │                   │                    评分 < 90%? ┌┴────────────┐  │
│         │                   │                           YES  │              NO │
│         │                   │                            │   │              │
│         │                   │                            ▼   │              │
│         │                   │                    ┌──────────────┐│    ▼         │
│         └───────────────────┼──────────────────┤ 返回L3修复   ││  ┌─────────┐│
│                             │                  │ 提供修复方案 ││  │ 通过     ││
│                             │                  └──────────────┘│  │ 三级门控 ││
│                             │                                  │  └────┬────┘│
│                             │                                  │       │      │
│                             │                                  │       ▼      │
│                             │                                  │  门控完成     │
│                             │                                  │  输出报告     │
│                             │                                  │              │
│                             │                                  └──────────────┘
│                             │
│                             ▼
│                      重新进入L1检查
│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 时间点

```yaml
gate_timing:
  l1_gate:
    execute_at: "输出生成后立即"
    timeout: "1分钟"
    blocking: true  # 必须通过才能继续

  l2_gate:
    execute_at: "L1通过后立即"
    timeout: "2分钟"
    blocking: true  # 必须通过才能继续

  l3_gate:
    execute_at: "L2通过后立即"
    timeout: "3分钟"
    blocking: true  # 必须通过才能继续

  async_gates:
    - name: "定期检查"
      execute_at: "每小时一次"
      description: "持续监控输出质量"

    - name: "里程碑检查"
      execute_at: "关键里程碑完成时"
      description: "阶段验收"
```

### 责任角色

```yaml
gate_responsibilities:
  l1_gate:
    executor: "Agent自身 (自动化)"
    approver: "Dev-QA循环"
    responsibility: "检查完整性"

  l2_gate:
    executor: "Agent自身 + 专家库"
    approver: "Dev-QA循环"
    responsibility: "评估专业性"

  l3_gate:
    executor: "Agent自身 + 模拟执行"
    approver: "CEO或指定审核者"
    responsibility: "验证可执行性"

  escalation:
    if_all_gates_fail: "升级到CEO"
    ceo_role: "最终决策者"
```

## 量化标准详解

### 完整性量化公式

```python
def calculate_l1_score_formula():
    """
    L1 完整性评分公式

    Score = (Structure_Score × 0.20)
          + (Content_Score × 0.35)
          + (Evidence_Score × 0.25)
          + (Metadata_Score × 0.20)

    其中:
    Structure_Score = (有标题×1 + 有描述×1 + 有步骤×1 + 有预期结果×1) / 4 × 100

    Content_Score = (有背景×1 + 有上下文×1 + 有约束×0.5 + 有验收标准×1) / 3.5 × 100

    Evidence_Score = (有数据×1 + 有引用×1 + 有示例×0.5) / 2.5 × 100

    Metadata_Score = (有版本×1 + 有时间×1 + 有作者×1 + 有状态×1) / 4 × 100

    通过条件: Score >= 95
    """

    formula = """
    L1 = Σ(维度得分 × 维度权重)

    L1 = S×0.20 + C×0.35 + E×0.25 + M×0.20

    其中:
    S = 结构完整性得分 (0-100)
    C = 内容完整性得分 (0-100)
    E = 证据完整性得分 (0-100)
    M = 元信息完整性得分 (0-100)
    """

    return formula
```

### 专业性量化公式

```python
def calculate_l2_score_formula():
    """
    L2 专业性评分公式

    Score = Σ(维度得分 × 维度权重)

    其中:
    Methodology_Score = Σ(方法项评级分 × 权重)
    Tool_Score = Σ(工具项评级分 × 权重)
    Format_Score = Σ(格式项评级分 × 权重)
    Communication_Score = Σ(沟通项评级分 × 权重)
    Analysis_Score = Σ(分析项评级分 × 权重)

    评级分映射:
    excellent → 100分
    good → 80分
    adequate → 60分
    poor → 40分

    通过条件: Score >= 80 且 所有维度 >= 60
    """

    formula = """
    L2 = Methodology×0.25 + Tool×0.20 + Format×0.20 + Comm×0.20 + Analysis×0.15

    其中:
    Methodology = (方法选择×0.4 + 步骤逻辑×0.3 + 理论支撑×0.3) × 评级分映射
    Tool = (工具选择×0.5 + 工具使用×0.5) × 评级分映射
    Format = (结构规范×0.4 + 格式统一×0.3 + 命名规范×0.3) × 评级分映射
    Comm = (语言准确性×0.4 + 专业术语×0.3 + 条理性×0.3) × 评级分映射
    Analysis = (根因分析×0.4 + 影响分析×0.3 + 风险识别×0.3) × 评级分映射
    """
    return formula
```

### 可执行性量化公式

```python
def calculate_l3_score_formula():
    """
    L3 可执行性评分公式

    Score = Σ(维度得分 × 维度权重)

    维度得分 = (满足的检查项数 / 总检查项数) × 100

    通过条件: Score >= 90 且 无不可饶恕错误 且 关键步骤可执行
    """

    formula = """
    L3 = Action×0.30 + Verification×0.25 + Context×0.25 + Output×0.20

    其中:
    Action = 满足的动作可行性检查项数 / 总检查项数 × 100
    Verification = 满足的结果可验证检查项数 / 总检查项数 × 100
    Context = 满足的上下文可理解检查项数 / 总检查项数 × 100
    Output = 满足的输出格式可执行检查项数 / 总检查项数 × 100

    额外规则:
    - 有不可饶恕错误 → Score = 0
    - 关键步骤不可执行 → 不通过
    """
    return formula
```

## 门控失败处理

### L1失败

```yaml
l1_failure_handling:
  score_range:
    95-100:
      status: "通过"
      action: "继续L2"

    80-94:
      status: "警告"
      action: "补充缺失项后继续L2"
      required_actions:
        - "识别缺失项"
        - "补充缺失内容"
        - "重新评估L1"

    60-79:
      status: "失败"
      action: "返回修改"
      required_actions:
        - "列出所有缺失项"
        - "提供修改建议"
        - "Agent修改后重新提交L1"
      max_retries: 2

    below_60:
      status: "严重失败"
      action: "重新开始"
      required_actions:
        - "重新审视任务"
        - "重新规划内容"
        - "重新开始L1检查"
      escalation: true
```

### L2失败

```yaml
l2_failure_handling:
  score_range:
    80-100:
      status: "通过"
      action: "继续L3"

    70-79:
      status: "警告"
      action: "改进后继续L3"
      required_actions:
        - "识别弱项"
        - "制定改进计划"
        - "执行改进"
        - "重新评估L2"

    60-69:
      status: "失败"
      action: "返回修改"
      required_actions:
        - "深度分析弱项原因"
        - "制定详细改进方案"
        - "执行改进"
        - "重新提交L2"
      max_retries: 2

    below_60:
      status: "严重失败"
      action: "返回L1重新检查"
      required_actions:
        - "返回L1检查完整性"
        - "确保完整后再提升专业性"
      escalation: true
```

### L3失败

```yaml
l3_failure_handling:
  score_range:
    90-100:
      status: "通过"
      action: "门控全部通过"

    80-89:
      status: "警告"
      action: "修复关键问题后通过"
      required_actions:
        - "识别关键阻塞问题"
        - "制定修复方案"
        - "修复问题"
        - "重新评估L3"

    60-79:
      status: "失败"
      action: "返回修复"
      required_actions:
        - "列出所有可执行性问题"
        - "制定详细修复方案"
        - "执行修复"
        - "重新提交L3"
      max_retries: 2

    below_60:
      status: "严重失败"
      action: "重新设计"
      required_actions:
        - "重新审视设计"
        - "重新规划执行方案"
        - "重新进行L1-L3检查"
      escalation: true
```

### 升级路径

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           门控失败升级路径                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  L1/L2/L3失败 (达到最大重试次数)                                            │
│       │                                                                       │
│       ▼                                                                       │
│  打包升级信息                                                                │
│  ┌─────────────────────────────────────────────┐                             │
│  │ 升级包内容:                                 │                             │
│  │ - 原始任务描述                             │                             │
│  │ - 门控评估详情                             │                             │
│  │ - 失败原因分析                             │                             │
│  │ - 已尝试的修复方案                         │                             │
│  │ - 当前状态                                 │                             │
│  │ - 请求的决策                               │                             │
│  └─────────────────────────────────────────────┘                             │
│       │                                                                       │
│       ▼                                                                       │
│  升级到CEO                                                                  │
│       │                                                                       │
│       ▼                                                                       │
│  CEO决策:                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │                                                              │            │
│  │  1. 批准当前输出 (门控豁免)                                  │            │
│  │  2. 要求修改后重新提交                                      │            │
│  │  3. 调整门控标准 (放宽/严格)                                 │            │
│  │  4. 重新规划任务                                             │            │
│  │  5. 分配给其他Agent                                         │            │
│  │  6. 终止任务                                                 │            │
│  │                                                              │            │
│  └─────────────────────────────────────────────────────────────┘            │
│       │                                                                       │
│       ▼                                                                       │
│  执行CEO决策                                                                 │
│       │                                                                       │
│       ▼                                                                       │
│  记录并关闭升级                                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 与Dev-QA的集成

### 集成点

```yaml
devqa_integration:
  integration_points:
    - name: "门控即Dev-QA阶段"
      description: "三级门控是Dev-QA循环的核心组成部分"
      mapping:
        l1_gate: "Dev-QA的COLLECTING阶段"
        l2_gate: "Dev-QA的SCORING阶段"
        l3_gate: "Dev-QA的验证阶段"

    - name: "证据共享"
      description: "门控收集的证据可供Dev-QA使用"
      shared_data:
        - "完整性证据"
        - "专业性评分"
        - "可执行性验证"

    - name: "重试集成"
      description: "门控失败触发Dev-QA重试"
      retry_mapping:
        l1_fail: "进入Dev-QA COLLECTING重试"
        l2_fail: "进入Dev-QA SCORING重试"
        l3_fail: "进入Dev-QA RETRYING重试"

    - name: "升级集成"
      description: "门控升级即Dev-QA升级"
      escalation_mapping:
        gate_escalation: "触发Dev-QA升级"
        escalation_package: "包含完整门控评估"
```

### 数据共享

```python
class QualityGateDevQAIntegration:
    """
    质量门控与Dev-QA的数据共享接口
    """

    def share_gate_evidence_to_devqa(self, gate_results):
        """
        将门控证据共享给Dev-QA

        Returns:
            evidence_package: {
                "l1_evidence": {...},
                "l2_evidence": {...},
                "l3_evidence": {...},
                "overall_assessment": {...}
            }
        """
        return {
            "l1_evidence": gate_results["l1"],
            "l2_evidence": gate_results["l2"],
            "l3_evidence": gate_results["l3"],
            "overall_assessment": {
                "all_passed": gate_results["all_passed"],
                "weakest_gate": gate_results["weakest_gate"],
                "recommendations": gate_results["recommendations"]
            }
        }

    def trigger_devqa_retry(self, gate_failure):
        """
        触发Dev-QA重试

        Args:
            gate_failure: 失败的gate信息

        Returns:
            retry_config: Dev-QA重试配置
        """
        retry_mapping = {
            "l1": {
                "devqa_stage": "collecting",
                "focus": "completeness",
                "action": "supplement_missing"
            },
            "l2": {
                "devqa_stage": "scoring",
                "focus": "professionalism",
                "action": "improve_quality"
            },
            "l3": {
                "devqa_stage": "retrying",
                "focus": "executability",
                "action": "fix_execution_issues"
            }
        }

        return retry_mapping.get(gate_failure["gate"], {})
```

### 反馈循环

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        质量门控 ↔ Dev-QA 反馈循环                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          Dev-QA 循环                                 │   │
│  │                                                                     │   │
│  │    ┌──────┐     ┌──────────┐     ┌───────┐     ┌────────┐          │   │
│  │    │ INIT │ ──► │COLLECTING│ ──► │SCORING│ ──► │RETRYING│          │   │
│  │    └──────┘     └────┬─────┘     └───┬───┘     └────┬───┘          │   │
│  │                      │                │              │              │   │
│  │                      │                │              │              │   │
│  │                      │    ┌───────────┴───────────┐   │              │   │
│  │                      │    │                       │   │              │   │
│  │                      ▼    ▼                       ▼   ▼              │   │
│  │                   ┌─────────────────────────────┐  ┌──────────┐     │   │
│  │                   │     L1 ──► L2 ──► L3        │  │ ESCALATED│     │   │
│  │                   │      质量门控检查            │  └──────────┘     │   │
│  │                   └─────────────────────────────┘                   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    │ 反馈                                     │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          反馈循环                                     │   │
│  │                                                                     │   │
│  │  1. 门控失败 ──► Dev-QA重试 ──► 门控重新检查                        │   │
│  │  2. 门控通过 ──► 记录成功案例 ──► 优化门控标准                      │   │
│  │  3. 持续改进 ──► 积累数据 ──► 迭代门控模型                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**版本**: v2.1 | **来源**: CyberTeam架构师 | **日期**: 2026-03-23
