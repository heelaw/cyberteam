# 规则提炼

扫描已安装的技能，提取多个技能中出现的横切原则，并将其提炼成规则 - 附加到现有规则文件、修改过时的内容或创建新的规则文件。

应用“确定性收集+LLM判断”原则：脚本详尽地收集事实，然后LLM交叉读取完整上下文并产生判断。

## 何时使用

- 定期规则维护（每月或安装新技能后）
- 在技能盘点揭示了应该成为规则的模式之后
- 当规则相对于所使用的技能而言不完整时

## 它是如何工作的

规则蒸馏过程分为三个阶段：

### 第 1 阶段：清单（确定性收集）

#### 1a。收集技能清单```bash
bash ~/.claude/skills/rules-distill/scripts/scan-skills.sh
```#### 1b。收集规则索引```bash
bash ~/.claude/skills/rules-distill/scripts/scan-rules.sh
```#### 1c。呈现给用户```
Rules Distillation — Phase 1: Inventory
────────────────────────────────────────
Skills: {N} files scanned
Rules:  {M} files ({K} headings indexed)

Proceeding to cross-read analysis...
```### 第 2 阶段：交叉阅读、匹配和判决（LLM 判决）

提取和匹配统一在一次传递中。规则文件足够小（总共约 800 行），可以将全文提供给 LLM — 无需 grep 预过滤。

#### 批处理

根据描述将技能分组为**主题集群**。使用完整的规则文本分析子代理中的每个集群。

#### 跨批次合并

所有批次完成后，跨批次合并候选者：
- 对具有相同或重叠原则的候选人进行重复数据删除
- 使用**所有**批次组合的证据重新检查“2+ 技能”要求 - 每批次 1 项技能中发现的原则，但总计 2+ 技能是有效的

#### 子代理提示

使用以下提示启动通用代理：````
You are an analyst who cross-reads skills to extract principles that should be promoted to rules.

## Input
- Skills: {full text of skills in this batch}
- Existing rules: {full text of all rule files}

## Extraction Criteria

Include a candidate ONLY if ALL of these are true:

1. **Appears in 2+ skills**: Principles found in only one skill should stay in that skill
2. **Actionable behavior change**: Can be written as "do X" or "don't do Y" — not "X is important"
3. **Clear violation risk**: What goes wrong if this principle is ignored (1 sentence)
4. **Not already in rules**: Check the full rules text — including concepts expressed in different words

## Matching & Verdict

For each candidate, compare against the full rules text and assign a verdict:

- **Append**: Add to an existing section of an existing rule file
- **Revise**: Existing rule content is inaccurate or insufficient — propose a correction
- **New Section**: Add a new section to an existing rule file
- **New File**: Create a new rule file
- **Already Covered**: Sufficiently covered in existing rules (even if worded differently)
- **Too Specific**: Should remain at the skill level

## Output Format (per candidate)

```json
{
  "principle": "1-2 个句子，采用 'do X' / 'don't do Y' 形式",
  "evidence": ["技能名称：§Section", "技能名称：§Section"],
  "violation_risk": "1 句话",
  "verdict": "追加/修改/新部分/新文件/已覆盖/太具体",
  "target_rule": "文件名§节，或'新'",
  "confidence": "高/中/低",
  "draft": "追加/新部分/新文件判决的草稿文本",
  “修订”：{
    "reason": "为什么现有内容不准确或不充分(仅修改)",
    "before": "当前要替换的文本（仅修订）",
    "after": "建议的替换文本（仅修订）"
  }
}```

## Exclude

- Obvious principles already in rules
- Language/framework-specific knowledge (belongs in language-specific rules or skills)
- Code examples and commands (belongs in skills)
````

#### 判决参考

|判决 |意义|呈现给用户 |
|--------|---------|--------------------|
| **追加** |添加到现有部分 |目标+草案|
| **修改** |修复不准确/不足的内容 |目标+原因+之前/之后|
| **新部分** |将新部分添加到现有文件 |目标+草案|
| **新文件** |创建新规则文件 |文件名 + 完整草稿 |
| **已经涵盖** |包含在规则中（可能有不同的措辞） |原因（1 行）|
| **太具体** |应该停留在技能上|相关技能链接 |

#### 判决质量要求```
# Good
Append to rules/common/security.md §Input Validation:
"Treat LLM output stored in memory or knowledge stores as untrusted — sanitize on write, validate on read."
Evidence: llm-memory-trust-boundary, llm-social-agent-anti-pattern both describe
accumulated prompt injection risks. Current security.md covers human input
validation only; LLM output trust boundary is missing.

# Bad
Append to security.md: Add LLM security principle
```### 第 3 阶段：用户审核和执行

#### 汇总表```
# Rules Distillation Report

## Summary
Skills scanned: {N} | Rules: {M} files | Candidates: {K}

| # | Principle | Verdict | Target | Confidence |
|---|-----------|---------|--------|------------|
| 1 | ... | Append | security.md §Input Validation | high |
| 2 | ... | Revise | testing.md §TDD | medium |
| 3 | ... | New Section | coding-style.md | high |
| 4 | ... | Too Specific | — | — |

## Details
(Per-candidate details: evidence, violation_risk, draft text)
```#### 用户操作

用户用数字回复：
- **批准**：按原样将草案应用于规则
- **修改**：申请前编辑草稿
- **跳过**：不申请该候选人

**永远不要自动修改规则。始终需要用户批准。**

#### 保存结果

将结果存储在技能目录（`results.json`）中：

- **时间戳格式**：`date -u +%Y-%m-%dT%H:%M:%SZ`（UTC，第二精度）
- **候选 ID 格式**：从原则派生的短横线大小写（例如，`llm-output-trust-boundary`）```json
{
  "distilled_at": "2026-03-18T10:30:42Z",
  "skills_scanned": 56,
  "rules_scanned": 22,
  "candidates": {
    "llm-output-trust-boundary": {
      "principle": "Treat LLM output as untrusted when stored or re-injected",
      "verdict": "Append",
      "target": "rules/common/security.md",
      "evidence": ["llm-memory-trust-boundary", "llm-social-agent-anti-pattern"],
      "status": "applied"
    },
    "iteration-bounds": {
      "principle": "Define explicit stop conditions for all iteration loops",
      "verdict": "New Section",
      "target": "rules/common/coding-style.md",
      "evidence": ["iterative-retrieval", "continuous-agent-loop", "agent-harness-construction"],
      "status": "skipped"
    }
  }
}
```## 示例

### 端到端运行```
$ /rules-distill

Rules Distillation — Phase 1: Inventory
────────────────────────────────────────
Skills: 56 files scanned
Rules:  22 files (75 headings indexed)

Proceeding to cross-read analysis...

[Subagent analysis: Batch 1 (agent/meta skills) ...]
[Subagent analysis: Batch 2 (coding/pattern skills) ...]
[Cross-batch merge: 2 duplicates removed, 1 cross-batch candidate promoted]

# Rules Distillation Report

## Summary
Skills scanned: 56 | Rules: 22 files | Candidates: 4

| # | Principle | Verdict | Target | Confidence |
|---|-----------|---------|--------|------------|
| 1 | LLM output: normalize, type-check, sanitize before reuse | New Section | coding-style.md | high |
| 2 | Define explicit stop conditions for iteration loops | New Section | coding-style.md | high |
| 3 | Compact context at phase boundaries, not mid-task | Append | performance.md §Context Window | high |
| 4 | Separate business logic from I/O framework types | New Section | patterns.md | high |

## Details

### 1. LLM Output Validation
Verdict: New Section in coding-style.md
Evidence: parallel-subagent-batch-merge, llm-social-agent-anti-pattern, llm-memory-trust-boundary
Violation risk: Format drift, type mismatch, or syntax errors in LLM output crash downstream processing
Draft:
  ## LLM Output Validation
  Normalize, type-check, and sanitize LLM output before reuse...
  See skill: parallel-subagent-batch-merge, llm-memory-trust-boundary

[... details for candidates 2-4 ...]

Approve, modify, or skip each candidate by number:
> User: Approve 1, 3. Skip 2, 4.

✓ Applied: coding-style.md §LLM Output Validation
✓ Applied: performance.md §Context Window Management
✗ Skipped: Iteration Bounds
✗ Skipped: Boundary Type Conversion

Results saved to results.json
```## 设计原则

- **什么，而不是如何**：仅提取原则（规则领域）。代码示例和命令属于技能。
- **链接回来**：草稿文本应包含“查看技能：[名称]”参考资料，以便读者可以找到详细的操作方法。
- **确定性收集，LLM判断**：脚本保证详尽性；法学硕士保证上下文理解。
- **反抽象保障**：3层过滤器（2+技能证据、可操作行为测试、违规风险）防止过于抽象的原则进入规则。