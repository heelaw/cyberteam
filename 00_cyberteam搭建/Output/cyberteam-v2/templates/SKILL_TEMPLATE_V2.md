---
name: {{SKILL_NAME}}
description: |
  {{SKILL_DESCRIPTION}}
  配套Agent: {{AGENT_NAME}}
version: "2.0.1"
license: MIT
owner: CyberTeam v2
trigger: "{{TRIGGER_CONDITIONS}}"
---

# {{SKILL_DISPLAY_NAME}}

## 身份定位

```
┌─────────────────────────────────────────────────────────────┐
│  {{ICON}} {{SKILL_DISPLAY_NAME}}                              │
│  用途: {{PURPOSE}}                                           │
│  配套Agent: {{AGENT_NAME}}                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 三条红线（安全红线，碰了就是 3.25）

🚫 **红线一：{{REDLINE_1_TITLE}}**
{{REDLINE_1_CONTENT}}

🚫 **红线二：{{REDLINE_2_TITLE}}**
{{REDLINE_2_CONTENT}}

🚫 **红线三：{{REDLINE_3_TITLE}}**
{{REDLINE_3_CONTENT}}

---

## 核心行为协议

### Owner 意识
{{OWNER_MINDSET}}

### 执行纪律
{{EXECUTION_DISCIPLINE}}

### 输出格式
{{OUTPUT_FORMAT_SPEC}}

---

## Success Metrics（成功指标）

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| {{METRIC_1}} | {{TARGET_1}} | {{MEASUREMENT_1}} |
| {{METRIC_2}} | {{TARGET_2}} | {{MEASUREMENT_2}} |
| {{METRIC_3}} | {{TARGET_3}} | {{MEASUREMENT_3}} |

**通过标准**: 所有指标达标 或 {{ALTERNATIVE_PASS_CONDITION}}

---

## Examples（示例）

### 示例1: {{EXAMPLE_1_TITLE}}
**输入**: {{EXAMPLE_1_INPUT}}
**输出**: {{EXAMPLE_1_OUTPUT}}
**关键点**: {{EXAMPLE_1_KEY_POINTS}}

### 示例2: {{EXAMPLE_2_TITLE}}
**输入**: {{EXAMPLE_2_INPUT}}
**输出**: {{EXAMPLE_2_OUTPUT}}
**关键点**: {{EXAMPLE_2_KEY_POINTS}}

---

## Error Handling（错误处理）

| 错误类型 | 处理方式 | 降级方案 |
|----------|----------|----------|
| {{ERROR_TYPE_1}} | {{HANDLING_1}} | {{FALLBACK_1}} |
| {{ERROR_TYPE_2}} | {{HANDLING_2}} | {{FALLBACK_2}} |

---

## Tools（工具）

### 必需工具
- {{REQUIRED_TOOL_1}}: {{TOOL_1_PURPOSE}}
- {{REQUIRED_TOOL_2}}: {{TOOL_2_PURPOSE}}

### 可选工具
- {{OPTIONAL_TOOL_1}}: {{TOOL_1_PURPOSE}}

---

## References（参考资料）

1. {{REFERENCE_1}}
2. {{REFERENCE_2}}
3. {{REFERENCE_3}}

---

## 协作关系

### 前置 Skill
- {{PREREQUISITE_SKILL_1}}: {{PREREQUISITE_REASON}}
- {{PREREQUISITE_SKILL_2}}: {{PREREQUISITE_REASON}}

### 后续 Skill
- {{NEXT_SKILL_1}}: {{NEXT_REASON}}

### 并行 Skill
- {{PARALLEL_SKILL_1}}: {{PARALLEL_REASON}}

---

## Sub-agent 协议

spawn 子 agent 时，必须在 prompt 中注入本 Skill 的核心协议：

```
开工前读取以下文件，按其中的行为协议执行：
- 核心: templates/SKILL_TEMPLATE_V2.md
- 具体: skills/{{CATEGORY}}/{{SKILL_NAME}}/SKILL.md
```

**传递内容**:
1. 身份定位
2. 三条红线
3. Success Metrics
4. 输出格式规范

---

## 执行步骤

### Step 1: {{STEP_1_TITLE}}
{{STEP_1_CONTENT}}

### Step 2: {{STEP_2_TITLE}}
{{STEP_2_CONTENT}}

### Step 3: {{STEP_3_TITLE}}
{{STEP_3_CONTENT}}

### Step 4: {{STEP_4_TITLE}}
{{STEP_4_CONTENT}}

### Step 5: {{STEP_5_TITLE}}
{{STEP_5_CONTENT}}
