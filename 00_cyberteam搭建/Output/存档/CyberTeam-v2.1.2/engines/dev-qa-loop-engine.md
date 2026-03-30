---
name: Dev-QA循环引擎
description: |
  Dev-QA循环引擎 — 自主闭环的质量保障系统，包含证据收集器、评分系统、重试机制、升级路径。
version: "2.1"
owner: CyberTeam架构师
---

# Dev-QA循环引擎

## 身份定位

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Dev-QA循环引擎                                │
├─────────────────────────────────────────────────────────────────────┤
│  用途: 自主闭环的质量保障系统                                       │
│  核心: 证据收集 → 评分 → 重试 → 升级                               │
│  特点: 全自动化、可追溯、可持续优化                                 │
└─────────────────────────────────────────────────────────────────────┘
```

## 架构设计

### 循环流程

```
                         ┌──────────────────────────────────────────┐
                         │              外部触发                    │
                         │   (CEO调用 / Agent自检 / 定时触发)       │
                         └──────────────────┬───────────────────────┘
                                            │
                                            ▼
                         ┌──────────────────────────────────────────┐
                         │              INIT 状态                    │
                         │         初始化上下文和目标                │
                         └──────────────────┬───────────────────────┘
                                            │
                                            ▼
                         ┌──────────────────────────────────────────┐
                         │         COLLECTING 状态                   │
                         │            证据收集                        │
                         │   ┌─────────────────────────────────┐     │
                         │   │  代码质量扫描  │  功能测试       │     │
                         │   │  安全漏洞扫描  │  性能基准       │     │
                         │   │  依赖审计      │  覆盖率分析     │     │
                         │   └─────────────────────────────────┘     │
                         └──────────────────┬───────────────────────┘
                                            │
                                            ▼
                         ┌──────────────────────────────────────────┐
                         │           SCORING 状态                    │
                         │              评分计算                      │
                         │   ┌─────────────────────────────────┐     │
                         │   │  维度得分  │  综合得分  │  PASS?  │     │
                         │   └─────────────────────────────────┘     │
                         └──────────────────┬───────────────────────┘
                                            │
                          ┌──────────────────┴──────────────────┐
                          │                                      │
                          ▼                                      ▼
                   ┌──────────────┐                       ┌──────────────┐
                   │   PASSED     │                       │  RETRYING    │
                   │   通过检查    │                       │   重试中      │
                   └──────────────┘                       └───────┬──────┘
                                                                     │
                                                                     ▼
                                                        ┌────────────────────────┐
                                                        │   重试策略选择         │
                                                        │  ┌──────────────────┐  │
                                                        │  │ 智能重试          │  │
                                                        │  │ 方案调整          │  │
                                                        │  │ 指数退避          │  │
                                                        │  └──────────────────┘  │
                                                        └───────────┬────────────┘
                                                                    │
                                                                    ▼
                                                        ┌────────────────────────┐
                                                        │   达到最大重试次数?     │
                                                        └───────────┬────────────┘
                                                                    │
                                                     ┌───────────────┴───────────────┐
                                                     │                               │
                                                     ▼                               ▼
                                            ┌──────────────┐                 ┌──────────────┐
                                            │   ESCALATED  │                 │    循环      │
                                            │   升级到CEO   │                 │   重试       │
                                            └──────────────┘                 └──────┬───────┘
                                                                                    │
                                                                                    ▼
                                                                           返回 COLLECTING
```

### 核心组件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Dev-QA 核心组件                                  │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│  证据收集器     │    评分系统      │   重试控制器     │      升级判定器       │
│  Evidence       │  Scoring        │  Retry          │  Escalation           │
│  Collector      │  System         │  Controller     │  Manager              │
├─────────────────┼─────────────────┼─────────────────┼───────────────────────┤
│ - 代码质量      │ - 多维度评分    │ - 最大3次重试   │ - 升级条件判定       │
│ - 功能测试      │ - 综合评分      │ - 指数退避      │ - 升级路径选择       │
│ - 安全扫描      │ - PASS/FAIL     │ - 智能方案调整  │ - 上下文打包         │
│ - 性能测试      │ - 详细报告      │ - 审计日志      │ - CEO回调            │
│ - 覆盖率分析    │                 │                 │                       │
└─────────────────┴─────────────────┴─────────────────┴───────────────────────┘
```

## 详细设计

### 1. 证据收集器 (Evidence Collector)

#### 收集维度

| 维度 | 收集指标 | 工具/方法 | 输出格式 |
|------|----------|-----------|----------|
| **代码质量** | 圈复杂度、重复率、代码风格 | SonarQube、ESLint、Pylint | JSON |
| **功能正确性** | 测试通过率、边界覆盖 | Pytest、Jest、Go test | JSON |
| **安全性** | 漏洞数、敏感信息泄露、CVE | Snyk、Semgrep、OWASP | JSON |
| **性能** | 响应时间、吞吐量、资源占用 | JMeter、Locust、wrk | JSON |
| **可维护性** | 依赖健康度、技术债务 | Dependabot、CodeClimate | JSON |

#### 证据格式标准

```yaml
evidence:
  version: "1.0"
  timestamp: "2026-03-23T10:30:00Z"
  target:
    type: "agent" | "skill" | "system"
    name: "组件名称"
    version: "版本号"
  dimensions:
    code_quality:
      score: 85
      metrics:
        complexity: 12
        duplications: 2.3
        style_violations: 15
      issues: []
    functional:
      score: 92
      test_pass_rate: 0.98
      coverage: 0.87
    security:
      score: 95
      vulnerabilities: 0
      cves: 0
    performance:
      score: 88
      avg_response_time: 120
      throughput: 1000
    maintainability:
      score: 78
      debt_ratio: 0.05
  collector_version: "1.0"
  raw_outputs: {}
```

### 2. 评分系统 (Scoring System)

#### 评分维度权重

| 维度 | 权重 | 最低要求 | 理想值 |
|------|------|----------|--------|
| 代码质量 (CQ) | 25% | 70分 | 90分 |
| 功能完整性 (FC) | 30% | 80分 | 95分 |
| 安全性 (SEC) | 25% | 85分 | 100分 |
| 性能 (PERF) | 10% | 70分 | 90分 |
| 可维护性 (MAIN) | 10% | 65分 | 85分 |

#### 综合评分公式

```
总分 = (CQ × 0.25) + (FC × 0.30) + (SEC × 0.25) + (PERF × 0.10) + (MAIN × 0.10)
```

#### PASS/FAIL 判定标准

| 判定 | 综合分 | 条件 |
|------|--------|------|
| **PASS** | ≥80分 | 所有维度≥最低要求，且综合分≥80 |
| **CONDITIONAL PASS** | 70-79分 | 可接受，但需记录改进项 |
| **FAIL** | <70分 | 任何维度<60分，或综合分<70 |

#### 维度单项判定

```python
def evaluate_dimension(score, min_requirement, weight):
    """
    单维度评估
    返回: (pass: bool, warning: bool, details: str)
    """
    if score >= min_requirement:
        return (True, False, f"通过 ({score}≥{min_requirement})")
    elif score >= min_requirement - 10:
        return (False, True, f"警告 ({score}<{min_requirement})")
    else:
        return (False, False, f"严重 ({score}<<{min_requirement})")

def calculate_overall_score(evidence):
    """
    综合评分计算
    """
    weights = {
        'code_quality': 0.25,
        'functional': 0.30,
        'security': 0.25,
        'performance': 0.10,
        'maintainability': 0.10
    }

    min_requirements = {
        'code_quality': 70,
        'functional': 80,
        'security': 85,
        'performance': 70,
        'maintainability': 65
    }

    total = 0
    dimension_results = {}
    all_pass = True
    any_critical = False

    for dim, weight in weights.items():
        score = evidence['dimensions'][dim]['score']
        min_req = min_requirements[dim]

        is_pass, is_warning, detail = evaluate_dimension(score, min_req, weight)

        dimension_results[dim] = {
            'score': score,
            'weight': weight,
            'weighted_score': score * weight,
            'pass': is_pass,
            'warning': is_warning,
            'detail': detail
        }

        total += score * weight

        if not is_pass and not is_warning:
            any_critical = True
        if not is_pass:
            all_pass = False

    return {
        'overall_score': round(total, 2),
        'dimensions': dimension_results,
        'pass': all_pass and total >= 80,
        'conditional_pass': not all_pass and total >= 70,
        'fail': any_critical or total < 70
    }
```

### 3. 重试控制器 (Retry Controller)

#### 重试策略配置

```yaml
retry_config:
  max_attempts: 3
  base_delay: 1000  # ms
  max_delay: 30000  # ms
  exponential_base: 2
  jitter: true

  retry_on:
    - type: "test_failure"
      action: "analyze_and_fix"
    - type: "timeout"
      action: "increase_timeout"
    - type: "resource_limit"
      action: "optimize_resources"
    - type: "flaky_test"
      action: "retry_specific"
```

#### 智能重试决策树

```
┌─────────────────────────────────────────────────────────────┐
│                     重试决策树                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  检测到失败                                                  │
│       │                                                      │
│       ▼                                                      │
│  分析失败类型 ──────────────────────────────────────┐       │
│       │                                              │       │
│  ┌────┴────┐   ┌──────┐   ┌───────┐   ┌────────┐   │       │
│  │测试失败 │   │超时   │   │资源限制│   │逻辑错误│   │       │
│  └────┬────┘   └───┬──┘   └───┬───┘   └────┬───┘   │       │
│       │            │          │           │       │       │
│       ▼            ▼          ▼           ▼       │       │
│  诊断失败用例   增加超时    优化资源    重新设计   │       │
│  修复后重跑     重试请求    清理缓存    方案调整   │       │
│       │            │          │           │       │       │
│       └────────────┴──────────┴───────────┴───────┘       │
│                           │                                 │
│                           ▼                                 │
│                    更新失败记录                             │
│                           │                                 │
│                           ▼                                 │
│               尝试次数 < 最大次数?                          │
│                    │         │                              │
│                   YES        NO                             │
│                    │         │                              │
│                    ▼         ▼                              │
│                 重试      触发升级                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 指数退避计算

```python
def calculate_delay(attempt, base_delay=1000, max_delay=30000, exponential_base=2, jitter=True):
    """
    计算重试延迟时间
    delay = min(base_delay * (exponential_base ^ attempt), max_delay)

    如果启用jitter: delay *= random(0.5, 1.0)
    """
    delay = min(base_delay * (exponential_base ** attempt), max_delay)

    if jitter:
        import random
        delay *= random.uniform(0.5, 1.0)

    return int(delay)

# 示例
# 尝试1: delay = 1000 * 2^1 = 2000ms (实际可能在1000-2000之间)
# 尝试2: delay = 1000 * 2^2 = 4000ms (实际可能在2000-4000之间)
# 尝试3: delay = 1000 * 2^3 = 8000ms (实际可能在4000-8000之间)
```

#### 重试审计日志

```json
{
  "audit_log": {
    "attempt_id": "retry-20260323-001",
    "target": {
      "type": "agent",
      "name": "code-reviewer",
      "version": "1.0"
    },
    "retry_history": [
      {
        "attempt": 1,
        "timestamp": "2026-03-23T10:30:00Z",
        "failure_type": "test_failure",
        "failure_detail": "2 tests failed",
        "action_taken": "analyze_and_fix",
        "delay_ms": 1500,
        "success": false
      },
      {
        "attempt": 2,
        "timestamp": "2026-03-23T10:31:30Z",
        "failure_type": "test_failure",
        "failure_detail": "1 test failed (flaky)",
        "action_taken": "retry_specific",
        "delay_ms": 3500,
        "success": true
      }
    ],
    "final_status": "PASS",
    "total_time_ms": 90000
  }
}
```

### 4. 升级判定器 (Escalation Manager)

#### 升级条件

```yaml
escalation_rules:
  conditions:
    - trigger: "max_retries_exceeded"
      description: "3次重试后仍未通过"
      priority: "high"

    - trigger: "critical_vulnerability"
      description: "发现严重安全漏洞"
      priority: "critical"

    - trigger: "score_below_threshold"
      description: "综合评分<60或任一维度<50"
      priority: "medium"

    - trigger: "timeout_loop"
      description: "同一问题反复失败"
      priority: "high"

    - trigger: "resource_exhaustion"
      description: "资源耗尽无法继续"
      priority: "critical"
```

#### 升级路径

```
┌─────────────────────────────────────────────────────────────────────┐
│                           升级路径                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  执行Agent ────────────────────────────────► CEO审查               │
│                                                                     │
│  升级包内容:                                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  1. 完整上下文 (原始请求 + 历史处理)                         │   │
│  │  2. 已尝试方案清单 (包含所有重试记录)                        │   │
│  │  3. 失败原因分析 (分类 + 根因)                               │   │
│  │  4. Dev-QA评估报告 (各维度得分)                             │   │
│  │  5. 资源使用情况 (时间、Token、调用次数)                     │   │
│  │  6. 建议的后续方向 (最多3个选项)                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 升级回调协议

```json
{
  "escalation": {
    "request_id": "esc-20260323-001",
    "timestamp": "2026-03-23T10:35:00Z",
    "escalation_level": "CEO",
    "source_agent": {
      "name": "code-reviewer",
      "version": "1.0",
      "session_id": "session-001"
    },
    "context": {
      "original_request": "审查模块X的代码质量",
      "processing_time_ms": 90000,
      "retry_count": 3,
      "final_score": {
        "overall": 65,
        "dimensions": {
          "code_quality": 68,
          "functional": 72,
          "security": 85,
          "performance": 55,
          "maintainability": 60
        }
      }
    },
    "failure_analysis": {
      "primary_cause": "performance_issues",
      "secondary_causes": ["complexity_too_high", "resource_limits"],
      "root_cause_confidence": 0.85
    },
    "attempted_solutions": [
      {
        "attempt": 1,
        "solution": "代码重构优化",
        "result": "partial_improvement",
        "score_change": "+5"
      },
      {
        "attempt": 2,
        "solution": "增加性能优化",
        "result": "no_improvement",
        "score_change": "0"
      },
      {
        "attempt": 3,
        "solution": "架构级优化",
        "result": "not_applicable",
        "reason": "超出Agent能力范围"
      }
    ],
    "recommended_actions": [
      {
        "action": "拆分模块",
        "priority": 1,
        "estimated_improvement": "+15-20"
      },
      {
        "action": "引入缓存层",
        "priority": 2,
        "estimated_improvement": "+10-15"
      },
      {
        "action": "异步处理改造",
        "priority": 3,
        "estimated_improvement": "+8-12"
      }
    ],
    "callback_url": "/api/v1/ceo/escalation/{request_id}/resolve",
    "urgency": "high"
  }
}
```

## 执行协议

### Dev-QA 循环状态机

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Dev-QA 状态机                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    ┌───────┐      触发       ┌──────────────┐       完成        ┌─────────┐  │
│    │ START │ ───────────► │     INIT      │ ──────────────► │  END    │  │
│    └───────┘              └───────┬────────┘                 └─────────┘  │
│                                  │                                    ▲      │
│                                  │ 执行                                 │      │
│                                  ▼                                    │      │
│                         ┌──────────────┐                             │      │
│                         │  COLLECTING   │                             │      │
│                         └───────┬────────┘                             │      │
│                                 │ 证据收集完成                          │      │
│                                 ▼                                       │      │
│                         ┌──────────────┐     评分完成        ┌──────────┐ │      │
│                         │   SCORING    │ ─────────────────► │ 报告生成 │ │      │
│                         └───────┬────────┘                   └────┬─────┘ │      │
│                                 │                                │       │      │
│                                 │ 是否通过?                       │       │      │
│                    ┌────────────┴────────────┐                    │       │      │
│                    │                         │                    │       │      │
│                   YES                       NO                   │       │      │
│                    │                         │                    │       │      │
│                    ▼                         ▼                    │       │      │
│             ┌──────────┐            ┌──────────────┐              │       │      │
│             │  PASSED  │            │   RETRYING   │              │       │      │
│             └────┬─────┘            └───────┬──────┘              │       │      │
│                  │                         │                     │       │      │
│                  │                         │ 达到最大次数?        │       │      │
│                  │                    ┌────┴────┐               │       │      │
│                  │                    │         │               │       │      │
│                  │                   YES        NO              │       │      │
│                  │                    │         │               │       │      │
│                  │                    ▼         ▼               │       │      │
│                  │             ┌──────────┐ ┌───────────┐       │       │      │
│                  │             │ESCALATED │ │  重试     │───────┘       │      │
│                  │             └────┬─────┘ └───────────┘               │      │
│                  │                  │                                  │      │
│                  │                  │ CEO处理完成                       │      │
│                  │                  └──────────────────────────────────┘      │
│                  │                                                              │
│                  │                         继续处理                            │
│                  └────────────────────────────────────────────────────────►────┘
│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 状态定义

| 状态 | 描述 | 入口条件 | 出口条件 | 可选动作 |
|------|------|----------|----------|----------|
| **INIT** | 初始化上下文和目标 | 调用开始 | 初始化完成 | 设置目标、加载配置 |
| **COLLECTING** | 证据收集中 | 初始化完成 | 收集完成 | 运行扫描、执行测试 |
| **SCORING** | 评分计算中 | 收集完成 | 评分完成 | 计算加权分、判定PASS/FAIL |
| **RETRYING** | 重试中 | 评分未通过 | 重试完成/达到上限 | 执行重试策略 |
| **PASSED** | 通过检查 | 综合分≥80 | 完成报告 | 生成通过报告 |
| **FAILED** | 失败 | 严重问题 | 触发升级 | 记录失败原因 |
| **ESCALATED** | 已升级到CEO | 达到最大重试 | CEO处理完成 | 打包升级信息 |
| **REPORTING** | 报告生成中 | 任一终态 | 报告完成 | 生成标准报告 |

### 证据标准

#### L1: 完整性标准 (必须满足)

```
证据完整性检查清单:
□ 有明确的审查目标描述
□ 覆盖所有5个评分维度
□ 每个维度至少3个具体指标
□ 有原始工具输出作为支撑
□ 有时间戳和版本标识
□ 无敏感信息泄露
```

#### L2: 准确性标准 (必须满足)

```
证据准确性检查清单:
□ 指标计算方法透明可复现
□ 评分权重配置公开
□ PASS/FAIL判定逻辑明确
□ 无人为干预痕迹
□ 结果可复现性≥95%
```

#### L3: 可追溯标准 (必须满足)

```
可追溯性检查清单:
□ 每次运行有唯一ID
□ 失败用例可定位到具体代码行
□ 重试历史完整记录
□ 升级信息完整传递
□ 审计日志不可篡改
```

## 与CEO的集成

### 输入接口

```yaml
# CEO调用Dev-QA的接口定义
ceo_to_devqa:
  endpoint: "/api/v1/devqa/execute"

  request:
    type: "object"
    properties:
      target:
        type: "string"
        enum: ["agent", "skill", "system", "workflow"]
      target_name:
        type: "string"
        description: "目标组件名称"
      target_version:
        type: "string"
        description: "目标组件版本"
      check_type:
        type: "string"
        enum: ["full", "incremental", "targeted"]
        description: "检查类型：完整/增量/定向"
      scope:
        type: "object"
        properties:
          dimensions:
            type: "array"
            items:
              enum: ["code_quality", "functional", "security", "performance", "maintainability"]
            description: "需要检查的维度"
          custom_rules:
            type: "array"
            description: "自定义检查规则"
      context:
        type: "object"
        description: "附加上下文信息"
      priority:
        type: "string"
        enum: ["low", "normal", "high", "critical"]

  response:
    type: "object"
    properties:
      execution_id:
        type: "string"
      status:
        type: "string"
        enum: ["pending", "in_progress", "completed", "failed", "escalated"]
      result:
        type: "object"
        properties:
          overall_score:
            type: "number"
          pass:
            type: "boolean"
          dimensions:
            type: "object"
          evidence:
            type: "object"
          retry_info:
            type: "object"
          escalation_info:
            type: "object"
```

### 输出接口

```yaml
# Dev-QA返回CEO的接口定义
devqa_to_ceo:
  # PASS 情况
  pass_response:
    status: "completed"
    pass: true
    overall_score: 85
    summary: "所有检查通过"
    evidence_package:
      url: "/api/v1/devqa/evidence/{execution_id}"
      checksum: "sha256:xxx"
    next_steps: []

  # FAIL 情况 - 升级
  escalation_response:
    status: "escalated"
    pass: false
    escalation_reason: "max_retries_exceeded"
    escalation_package:
      request_id: "{escalation_id}"
      priority: "high"
      summary: "性能问题导致无法达标"
      full_context: {...}  # 完整上下文
    callback_url: "/api/v1/ceo/escalation/{id}/resolve"
```

### 回调机制

```python
# CEO回调处理协议
class CEOCallbackProtocol:
    """
    Dev-QA升级后的CEO回调协议
    """

    def on_escalation(self, escalation_package):
        """
        CEO收到升级通知后的处理
        """
        # 1. 解析升级包
        context = escalation_package['context']
        failure_analysis = escalation_package['failure_analysis']
        recommended_actions = escalation_package['recommended_actions']

        # 2. CEO决策
        decision = self.ceo_decide(failure_analysis, recommended_actions)

        # 3. 返回决策
        return {
            "decision_type": decision['type'],  # "retry_with_new_plan" | "manual_intervention" | "accept_risk" | "abort"
            "instructions": decision['instructions'],
            "callback_url": f"/api/v1/devqa/execution/{escalation_package['execution_id']}/resume"
        }

    def on_resume(self, execution_id, ceo_instructions):
        """
        Dev-QA根据CEO指令继续执行
        """
        # 解析CEO指令
        # 执行新方案
        # 继续Dev-QA流程
        pass
```

## 实现示例

### 示例1：代码审查场景

```python
"""
Dev-QA循环 - 代码审查场景
"""

# 1. 初始化
dev_qa = DevQAEngine()
execution = dev_qa.init(
    target_type="agent",
    target_name="code-reviewer",
    target_version="1.0",
    check_type="full"
)

# 2. 证据收集
evidence = dev_qa.collect_evidence(execution)

# 证据收集输出示例:
evidence = {
    "code_quality": {
        "score": 75,
        "metrics": {
            "complexity": 15,
            "duplications": 3.2,
            "style_violations": 23
        },
        "issues": [
            {"type": "high_complexity", "location": "src/parser.py:45", "value": 22},
            {"type": "duplication", "location": "src/utils.py:10-25", "copied_from": "src/helpers.py:30-45"}
        ]
    },
    "functional": {
        "score": 92,
        "test_pass_rate": 0.98,
        "coverage": 0.85,
        "failed_tests": []
    },
    "security": {
        "score": 95,
        "vulnerabilities": 0,
        "cves": 0
    },
    "performance": {
        "score": 82,
        "avg_response_time": 150,
        "throughput": 800
    },
    "maintainability": {
        "score": 70,
        "debt_ratio": 0.08
    }
}

# 3. 评分
score_result = dev_qa.score(execution, evidence)
# 综合分 = 75*0.25 + 92*0.30 + 95*0.25 + 82*0.10 + 70*0.10 = 18.75 + 27.6 + 23.75 + 8.2 + 7 = 85.3

# 评分结果:
score_result = {
    "overall_score": 85.3,
    "pass": True,
    "dimensions": {
        "code_quality": {"score": 75, "pass": True, "warning": False},
        "functional": {"score": 92, "pass": True, "warning": False},
        "security": {"score": 95, "pass": True, "warning": False},
        "performance": {"score": 82, "pass": True, "warning": False},
        "maintainability": {"score": 70, "pass": True, "warning": True}  # 刚好及格
    }
}

# 4. PASS - 生成报告
report = dev_qa.generate_report(execution, score_result)
```

### 示例2：功能测试场景

```python
"""
Dev-QA循环 - 功能测试场景
"""

# 1. 初始化 - 针对API agent
execution = dev_qa.init(
    target_type="agent",
    target_name="api-gateway",
    target_version="2.0",
    check_type="targeted",
    scope={
        "dimensions": ["functional", "security", "performance"]
    }
)

# 2. 证据收集 - 定向收集
evidence = dev_qa.collect_evidence(execution)

# 证据收集输出示例:
evidence = {
    "functional": {
        "score": 68,  # 未达到80的最低要求
        "test_pass_rate": 0.85,
        "coverage": 0.72,
        "failed_tests": [
            {"name": "test_auth_flow", "status": "failed", "reason": "timeout"},
            {"name": "test_rate_limit", "status": "failed", "reason": "logic_error"}
        ]
    },
    "security": {
        "score": 78,  # 未达到85的最低要求
        "vulnerabilities": 2,
        "cves": 0,
        "details": [
            {"type": "XSS", "severity": "medium", "location": "src/xss.py"},
            {"type": "SQL_INJECTION", "severity": "high", "location": "src/sql.py"}
        ]
    },
    "performance": {
        "score": 88,
        "avg_response_time": 200,
        "throughput": 950
    }
}

# 3. 评分 - FAIL
score_result = dev_qa.score(execution, evidence)
# 综合分 = 68*0.30 + 78*0.25 + 88*0.10 = 20.4 + 19.5 + 8.8 = 48.7

score_result = {
    "overall_score": 48.7,
    "pass": False,
    "dimensions": {
        "functional": {"score": 68, "pass": False, "critical": True},
        "security": {"score": 78, "pass": False, "critical": False},
        "performance": {"score": 88, "pass": True, "warning": False}
    }
}

# 4. 进入重试流程
retry_result = dev_qa.retry(execution, score_result)

# 重试1: 修复功能测试
retry_action_1 = {
    "action": "fix_functional_tests",
    "details": [
        "分析 test_auth_flow 超时原因 -> 增加超时配置",
        "分析 test_rate_limit 逻辑错误 -> 修复计数逻辑"
    ],
    "result": "tests_fixed"
}

# 重试后评分: functional 68 -> 85
# 综合分更新: 85*0.30 + 78*0.25 + 88*0.10 = 25.5 + 19.5 + 8.8 = 53.8
# 仍未达到80，但有明显改善

# 重试2: 修复安全漏洞
retry_action_2 = {
    "action": "fix_security_issues",
    "details": [
        "XSS: 添加输入 sanitization",
        "SQL_INJECTION: 使用参数化查询"
    ],
    "result": "vulnerabilities_fixed"
}

# 重试后评分: security 78 -> 92
# 综合分更新: 85*0.30 + 92*0.25 + 88*0.10 = 25.5 + 23 + 8.8 = 57.3

# 重试3: 优化代码质量
retry_action_3 = {
    "action": "optimize_code",
    "details": ["重构部分代码提升质量"],
    "result": "no_improvement"
}

# 综合分: 57.3 仍未达到80，达到最大重试次数

# 5. 触发升级
escalation = dev_qa.escalate(execution, score_result, {
    "reason": "max_retries_exceeded",
    "final_score": 57.3,
    "improvement": "+8.6 (从48.7到57.3)",
    "recommendations": [
        "需要架构级改动",
        "建议拆分为更小的模块",
        "建议引入更多测试覆盖"
    ]
})

# 升级包发送至CEO
```

---

**版本**: v2.1 | **来源**: CyberTeam架构师 | **日期**: 2026-03-23
