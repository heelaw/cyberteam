# 评估安全带技能

Claude Code 会议的正式评估框架，实施评估驱动开发 (EDD) 原则。

## 何时激活

- 为人工智能辅助工作流程设置评估驱动开发 (EDD)
- 定义克劳德代码任务完成的通过/失败标准
- 使用 pass@k 指标衡量座席可靠性
- 为提示或代理更改创建回归测试套件
- 跨模型版本对代理性能进行基准测试

## 理念

评估驱动开发将评估视为“人工智能开发的单元测试”：
- 在实施之前定义预期行为
- 在开发过程中不断运行评估
- 跟踪每次更改的回归
- 使用 pass@k 指标进行可靠性测量

## 评估类型

### 能力评估
测试克劳德是否可以做以前做不到的事情：```markdown
[CAPABILITY EVAL: feature-name]
Task: Description of what Claude should accomplish
Success Criteria:
  - [ ] Criterion 1
  - [ ] Criterion 2
  - [ ] Criterion 3
Expected Output: Description of expected result
```### 回归评估
确保更改不会破坏现有功能：```markdown
[REGRESSION EVAL: feature-name]
Baseline: SHA or checkpoint name
Tests:
  - existing-test-1: PASS/FAIL
  - existing-test-2: PASS/FAIL
  - existing-test-3: PASS/FAIL
Result: X/Y passed (previously Y/Y)
```## 分级机类型

### 1. 基于代码的评分器
使用代码进行确定性检查：```bash
# Check if file contains expected pattern
grep -q "export function handleAuth" src/auth.ts && echo "PASS" || echo "FAIL"

# Check if tests pass
npm test -- --testPathPattern="auth" && echo "PASS" || echo "FAIL"

# Check if build succeeds
npm run build && echo "PASS" || echo "FAIL"
```### 2. 基于模型的分级机
使用 Claude 评估开放式输出：```markdown
[MODEL GRADER PROMPT]
Evaluate the following code change:
1. Does it solve the stated problem?
2. Is it well-structured?
3. Are edge cases handled?
4. Is error handling appropriate?

Score: 1-5 (1=poor, 5=excellent)
Reasoning: [explanation]
```### 3. 人类分级机
手动审核标志：```markdown
[HUMAN REVIEW REQUIRED]
Change: Description of what changed
Reason: Why human review is needed
Risk Level: LOW/MEDIUM/HIGH
```## 指标

### 通过@k
“k 次尝试中至少有一次成功”
- pass@1：首次尝试成功率
- pass@3：3次尝试内成功
- 典型目标：pass@3 > 90%

### 通过^k
“所有 k 次试验都成功”
- 更高的可靠性标准
- pass^3：连续3次成功
- 用于关键路径

## 评估工作流程

### 1. 定义（编码前）```markdown
## EVAL DEFINITION: feature-xyz

### Capability Evals
1. Can create new user account
2. Can validate email format
3. Can hash password securely

### Regression Evals
1. Existing login still works
2. Session management unchanged
3. Logout flow intact

### Success Metrics
- pass@3 > 90% for capability evals
- pass^3 = 100% for regression evals
```### 2. 实施
编写代码来传递定义的评估。

### 3. 评估```bash
# Run capability evals
[Run each capability eval, record PASS/FAIL]

# Run regression evals
npm test -- --testPathPattern="existing"

# Generate report
```### 4. 报告```markdown
EVAL REPORT: feature-xyz
========================

Capability Evals:
  create-user:     PASS (pass@1)
  validate-email:  PASS (pass@2)
  hash-password:   PASS (pass@1)
  Overall:         3/3 passed

Regression Evals:
  login-flow:      PASS
  session-mgmt:    PASS
  logout-flow:     PASS
  Overall:         3/3 passed

Metrics:
  pass@1: 67% (2/3)
  pass@3: 100% (3/3)

Status: READY FOR REVIEW
```## 集成模式

### 实施前```
/eval define feature-name
```在 `.claude/evals/feature-name.md` 创建 eval 定义文件

### 实施期间```
/eval check feature-name
```运行当前评估并报告状态

### 实施后```
/eval report feature-name
```生成完整的评估报告

## 评估存储

将评估存储在项目中：```
.claude/
  evals/
    feature-xyz.md      # Eval definition
    feature-xyz.log     # Eval run history
    baseline.json       # Regression baselines
```## 最佳实践

1. **在编码之前定义评估** - 强制清晰地思考成功标准
2. **经常运行评估** - 尽早发现回归
3. **随着时间的推移跟踪 pass@k** - 监控可靠性趋势
4. **尽可能使用代码分级器** - 确定性 > 概率性
5. **人工安全审查** - 永远不要完全自动化安全检查
6. **保持快速评估** - 缓慢的评估不会运行
7. **使用代码进行版本评估** - 评估是一流的工件

## 示例：添加身份验证```markdown
## EVAL: add-authentication

### Phase 1: Define (10 min)
Capability Evals:
- [ ] User can register with email/password
- [ ] User can login with valid credentials
- [ ] Invalid credentials rejected with proper error
- [ ] Sessions persist across page reloads
- [ ] Logout clears session

Regression Evals:
- [ ] Public routes still accessible
- [ ] API responses unchanged
- [ ] Database schema compatible

### Phase 2: Implement (varies)
[Write code]

### Phase 3: Evaluate
Run: /eval check add-authentication

### Phase 4: Report
EVAL REPORT: add-authentication
==============================
Capability: 5/5 passed (pass@3: 100%)
Regression: 3/3 passed (pass^3: 100%)
Status: SHIP IT
```## 产品评估 (v1.8)

当行为质量无法仅通过单元测试来捕获时，请使用产品评估。

### 分级机类型

1. 代码分级器（确定性断言）
2. 规则分级器（正则表达式/模式约束）
3. 模型评分者（法学硕士作为评判标准）
4. 人工评分器（对不明确的输出进行手动裁决）

### pass@k 指导

- `pass@1`：直接可靠性
- `pass@3`：受控重试下的实际可靠性
- `pass^3`：稳定性测试（所有 3 次运行都必须通过）

推荐阈值：
- 能力评估：pass@3 >= 0.90
- 回归评估：对于发布关键路径，pass^3 = 1.00

### 评估反模式

- 过度拟合提示已知的评估示例
- 仅测量快乐路径输出
- 在追求通过率的同时忽略成本和延迟漂移
- 允许片状分级机进入释放门

### 最小评估工件布局

- `.claude/evals/<feature>.md` 定义
- `.claude/evals/<feature>.log` 运行历史记录
- `docs/releases/<version>/eval-summary.md` 发布快照