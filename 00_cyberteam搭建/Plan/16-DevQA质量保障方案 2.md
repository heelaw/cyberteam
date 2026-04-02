# Dev-QA 质量保障方案（v2.0）

**版本**: v2.0
**日期**: 2026-03-24
**作者**: quality-expert → P8更新整理
**团队**: cyberteam-discuss
**状态**: 已完成

---

## 一、核心架构：Dev-QA 循环

### 1.1 循环流程

```
┌────────────────────────────────────────────────────────────┐
│                      Dev-QA Loop                           │
│                                                            │
│  ┌─────────┐   提交    ┌──────────┐   验证    ┌─────────┐ │
│  │ Developer│ ───────→│ Evidence  │ ────────→│ Pass?   │ │
│  │  Agent   │          │ Collector │          │          │ │
│  └────┬────┘          └──────────┘          └────┬────┘ │
│       ↑                                           │       │
│       │  修复           ┌──────────┐             │       │
│       └─────────────────│ Fix &    │             │       │
│         最多3次重试      │ Resubmit │             │       │
│                         └──────────┘             │       │
│                                              ┌───┴───┐   │
│                                              │ Y / N │   │
│                                              └───┬───┘   │
│                                                  │       │
│                              ┌──────────────────┘       │
│                              ↓                           │
│                     ┌────────────────┐                   │
│                     │ Pass → 交付闭环 │                   │
│                     │ Fail → 升级机制 │                   │
│                     └────────────────┘                   │
└────────────────────────────────────────────────────────────┘
```

### 1.2 三级质量门控

| 门控级别 | 检查内容 | 阈值 | 工具 |
|---------|---------|------|------|
| **L1 基础** | Lint、格式、导入、Schema验证 | 100% | ESLint/ruff/schema-checker |
| **L2 功能** | 单元测试、集成测试、API契约 | ≥80分 | pytest/jest/spectral |
| **L3 端到端** | E2E测试、性能、安全、可用性 | ≥90% | Playwright/k6/owasp-zap |

### 1.3 PASS/FAIL 判定

```python
class QualityGate:
    L1_THRESHOLD = 1.0    # 100% 通过
    L2_THRESHOLD = 0.8    # 80分
    L3_THRESHOLD = 0.9    # 90% 通过
    MAX_RETRIES = 3

    def evaluate(self, artifacts: list[Artifact]) -> GateResult:
        l1_score = self.run_l1_checks(artifacts)
        if l1_score < self.L1_THRESHOLD:
            return GateResult(fail=True, level=1,
                            reason="L1 checks failed",
                            suggestions=self.get_l1_suggestions())

        l2_score = self.run_l2_checks(artifacts)
        if l2_score < self.L2_THRESHOLD:
            return GateResult(fail=True, level=2,
                            reason="L2 score below 80",
                            suggestions=self.get_l2_suggestions())

        l3_score = self.run_l3_checks(artifacts)
        if l3_score < self.L3_THRESHOLD:
            return GateResult(fail=True, level=3,
                            reason="L3 coverage below 90%",
                            suggestions=self.get_l3_suggestions())

        return GateResult(pass=True, level=3,
                         scores={"l1": l1_score,
                                "l2": l2_score,
                                "l3": l3_score})
```

## 二、防无限循环机制

### 2.1 硬性上限

| 保护层 | 限制 | 动作 |
|--------|------|------|
| 单次修复 | 3次重试 | 第3次失败 → 升级 |
| L1检查 | 5次修复循环 | 强制升级 |
| L2检查 | 3次修复循环 | 强制升级 |
| L3检查 | 2次修复循环 | 强制升级 |
| 全链路 | 10次总循环 | 强制升级人工 |

### 2.2 超时保护

```python
TIMEOUT_CONFIG = {
    "l1_check_timeout": 30,    # 秒
    "l2_check_timeout": 300,   # 秒
    "l3_check_timeout": 600,   # 秒
    "fix_timeout": 120,        # 秒/次
    "total_loop_timeout": 1800, # 秒（30分钟）
}
```

### 2.3 强制升级条件

```python
ESCALATION_TRIGGERS = [
    "max_retries_exceeded",
    "timeout_exceeded",
    "pua_level_4_triggered",
    "circular_dependency_detected",
    "resource_exhaustion",
    "inconsistent_state",
]
```

## 三、自动化检查流程

```
代码提交/Artifacts
      ↓
[ L1: 快速检查 ] ──失败──→ 返回错误信息 ──重试──┐
      ↓ 通过                                    │
[ L2: 功能检查 ] ──失败──→ 详细诊断报告 ──重试──┤
      ↓ 通过                                    │
[ L3: 端到端检查 ] ──失败──→ 升级报告 ──重试──┤
      ↓ 通过                                    │
[ 质量通过 ] ──→ 交付闭环                       │
                                                 │
                              循环超限 ←────────┘
                              ↓
                        [ 升级人工处理 ]
```

## 四、Dev-QA 循环模板

### 4.1 agency-agents 集成

```yaml
# dev-qa-loop-template.yaml
name: agency-dev-qa-loop
stages:
  - id: submit
    agent: developer
    action: submit_artifacts
    evidence_required:
      - code_files
      - test_files
      - documentation

  - id: l1_validate
    agent: qa-l1
    action: run_l1_checks
    tools:
      - linter
      - formatter
      - schema-validator
    threshold: 1.0
    timeout: 30s

  - id: l2_validate
    agent: qa-l2
    action: run_l2_checks
    tools:
      - pytest
      - jest
      - api-contract-tester
    threshold: 0.8
    timeout: 300s

  - id: l3_validate
    agent: qa-l3
    action: run_l3_checks
    tools:
      - playwright
      - k6
      - owasp-zap
    threshold: 0.9
    timeout: 600s

  - id: fix_and_resubmit
    condition: failed
    agent: developer
    action: fix_issues
    max_retries: 3

  - id: escalate
    condition: max_retries_exceeded
    action: human_escalation
    recipient: quality-director
```

## 五、CyberTeam 三层质量标准

### 5.1 Agent 级别（部门Agent）

| 维度 | 标准 | 检查方式 |
|------|------|----------|
| 代码正确性 | L1 100%, L2 ≥80 | 自动检查 |
| 文档完整性 | 100% | 文件存在性检查 |
| Schema合规 | 100% | JSON Schema验证 |
| 交接完整性 | 100% | 必填字段检查 |

### 5.2 团队级别（专家Agent）

| 维度 | 标准 | 检查方式 |
|------|------|----------|
| 测试覆盖率 | ≥80% | Coverage工具 |
| 安全扫描 | 0高危/0中危 | SAST工具 |
| 性能基准 | P95 ≤阈值 | 性能测试 |
| 文档质量 | 可读性评分≥70 | 文档分析 |

### 5.3 系统级别（跨团队）

| 维度 | 标准 | 检查方式 |
|------|------|----------|
| 集成测试 | 100%通过 | E2E测试 |
| 回归测试 | 全部通过 | 回归套件 |
| 安全渗透 | 无高危漏洞 | DAST |
| 可用性 | ≥99.9% | 监控告警 |

## 六、质量报告格式

```json
{
  "report_id": "qa-20260324-001",
  "timestamp": "2026-03-24T12:00:00Z",
  "developer": "engineering-director",
  "artifacts": ["src/agent.py", "tests/test_agent.py"],
  "results": {
    "l1": {"passed": true, "score": 1.0, "duration_ms": 12400},
    "l2": {"passed": true, "score": 0.85, "duration_ms": 89000,
           "details": {"coverage": 85, "tests_passed": 42}},
    "l3": {"passed": true, "score": 0.93, "duration_ms": 234000,
           "details": {"e2e_passed": 28, "perf_ok": true}}
  },
  "overall": "PASS",
  "recommendations": []
}
```

## 七、与 ClawTeam 集成

```python
# DevQA Agent 作为 ClawTeam 团队成员
CLAWTEAM_TEAM_CONFIG = {
    "qa-l1": {
        "role": "L1 validation specialist",
        "tools": ["linter", "formatter", "schema-checker"],
        "timeout": 30,
    },
    "qa-l2": {
        "role": "L2 functional testing specialist",
        "tools": ["pytest", "jest", "contract-tester"],
        "timeout": 300,
    },
    "qa-l3": {
        "role": "L3 E2E testing specialist",
        "tools": ["playwright", "k6", "security-scanner"],
        "timeout": 600,
    },
}

# inbox 消息格式
CLAWTEAM_MESSAGES = {
    "submit": {
        "from": "developer",
        "to": "qa-l1",
        "content": {"artifacts": [...], "expectations": {...}}
    },
    "l1_result": {
        "from": "qa-l1",
        "to": "developer",
        "content": {"passed": bool, "errors": [...], "suggestions": [...]}
    },
    "escalation": {
        "from": "qa-l3",
        "to": "quality-director",
        "content": {"reason": "...", "attempts": N, "artifacts": [...]}
    }
}
```
