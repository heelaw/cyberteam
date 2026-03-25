# course-to-skill-transformer 迭代方案 v2.0

> 基于自检评估报告的改进计划
> 日期：2026-03-17
> 当前版本：v1.0 → 目标版本：v2.0

---

## 一、评估结果分析

### 1.1 关键发现

| 指标 | with_skill | without_skill | 差异分析 |
|------|-----------|---------------|----------|
| 平均通过率 | 100% ✅ | 92% ⚠️ | with_skill 质量更稳定 |
| 平均耗时 | 120.7s | 129.9s | with_skill 稍快（-7%） |
| 平均 tokens | 2,666 | 1,254 | with_skill 多用 112% |
| 输出文件数 | 3个 | 1个 | with_skill 更完整 |

### 1.2 质量优势（with_skill）

✅ **完整性**：7步转化流程元数据完整
✅ **一致性**：所有测试 100% pass rate
✅ **可追溯性**：每步输入输出都有记录
✅ **自动化验证**：v2.0 合规性 + P0/P1/P2 分级

### 1.3 效率问题

⚠️ **Token 使用**：平均多用 112% tokens
⚠️ **冗余输出**：部分中间文件可以合并
⚠️ **LLM 依赖**：某些步骤可以用脚本替代

### 1.4 without_skill 的失败模式

**PMF 课程测试**：
- ❌ 缺失"内容类型识别"元数据
- ❌ 无质量验证报告
- ❌ 无方法论分级评估

**根因**：缺少系统化的转化框架，依赖 agent 自行推断

---

## 二、迭代目标

### 2.1 核心目标

1. **保持质量**：维持 100% pass rate 一致性
2. **提升效率**：Token 使用降低 30-50%
3. **增强自动化**：脚本化可计算步骤
4. **优化输出**：减少冗余，保留关键信息

### 2.2 成功标准

| 指标 | 当前值 | 目标值 |
|------|-------|-------|
| Pass Rate | 100% | ≥100% |
| 平均 tokens | 2,666 | ≤1,800 (-33%) |
| 脚本覆盖率 | 20% | ≥50% |
| 输出文件数 | 3个 | 2-3个（优化） |

---

## 三、改进策略

### 3.1 策略 A：脚本化优先（推荐）

**原则**：能用脚本的不用 LLM

| 步骤 | 当前实现 | 改进方案 | Token 节省 |
|------|---------|---------|-----------|
| Step 1: 内容类型识别 | LLM 推断 | 规则引擎 | -100 |
| Step 2: 结构提取 | LLM 解析 | Markdown 解析器 | -200 |
| Step 6: 质量验证 | LLM 自检 | Python 脚本 | -300 |

**实现**：
```python
# scripts/content_detector.py
def detect_content_type(content: str) -> dict:
    """基于规则的内容类型识别"""
    if "# 课程类型：视频" in content:
        return {"type": "transcript", "confidence": 0.95}
    # ... 更多规则

# scripts/structure_parser.py
def parse_markdown_structure(content: str) -> dict:
    """解析 Markdown 结构"""
    # 使用 markdown-it 或类似库

# scripts/quality_validator.py
def validate_v2_compliance(skill_md: str) -> dict:
    """验证 v2.0 合规性"""
    # 扩展现有 methodology_scorer.py
```

### 3.2 策略 B：Prompt 优化

**原则**：精简指令，减少冗余

**优化前**（Step 3）：
```
请仔细阅读以下课程内容，识别其中的知识点。
知识点可以分为以下类型：
1. 概念型：定义、原理、标准...
...
请输出结构化的知识点列表。
```

**优化后**：
```
识别知识点，输出 JSON：
{"knowledge_points": [{"name", "type", "content"}]}
类型：概念|方法|工具|标准
```

### 3.3 策略 C：Agent Team 专业化

**当前**：单个 agent 完成全部 7 步

**改进后**：专业化分工

```
┌─────────────────────────────────────────┐
│   Orchestrator (协调器)                │
│   - 分配任务                           │
│   - 汇总结果                           │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼────┐
│Parser │ |KP    │ |Method│ |Valid-│
│Agent  │ |Agent │ |ology │ |ator   │
│       │ │      │ │Agent │ │       │
└───────┘ └──────┘ └──────┘ └───────┘
(脚本)   (LLM)    (LLM)    (脚本)
```

**优势**：
- 每个 agent 专注单一职责
- 可并行执行部分任务
- 更容易调试和优化

### 3.4 策略 D：输出优化

**当前输出**：
1. SKILL.md
2. methodology.json
3. quality_report.json
4. step1-content-type.json
5. step2-structure.json
6. step3-knowledge-points.json
7. step4-methodologies.json

**优化后**：
1. SKILL.md（必需）
2. transformation.json（合并 2-6 步）
3. quality_report.json（保留）

---

## 四、实施计划

### Phase 1：脚本化改造（优先级：高）

**任务**：
- [ ] 创建 `scripts/content_detector.py`（Step 1）
- [ ] 创建 `scripts/structure_parser.py`（Step 2）
- [ ] 扩展 `scripts/quality_validator.py`（Step 6）

**验收**：
- Token 使用减少 30%
- 质量不降低

### Phase 2：Prompt 优化（优先级：中）

**任务**：
- [ ] 精简 Step 3-5 的 prompt
- [ ] 统一输出格式为 JSON
- [ ] 减少 example 和说明文字

**验收**：
- Token 使用减少 20%
- 输出一致性提升

### Phase 3：Agent Team 拆分（优先级：低）

**任务**：
- [ ] 设计 orchestrator
- [ ] 实现 4 个专业 agent
- [ ] 建立任务调度机制

**验收**：
- 可并行执行
- 总耗时减少 20%

---

## 五、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 脚本化降低灵活性 | 中 | 保留 LLM fallback |
| Agent 拆分增加复杂度 | 中 | 渐进式重构 |
| Prompt 优化影响质量 | 低 | 充分测试 |
| 输出合并导致信息丢失 | 低 | 保留关键字段 |

---

## 六、下一步行动

### 立即行动（今天）

1. ✅ 完成评估报告分析
2. ⏭ 创建脚本化的 Step 1 prototype
3. ⏭ 测试 token 节省效果

### 短期行动（本周）

1. 实现脚本化改造（Phase 1）
2. 运行第二轮自检评估
3. 对比 v1.0 vs v2.0 性能

### 中期行动（本月）

1. 完成 Prompt 优化（Phase 2）
2. 评估 Agent Team 拆分可行性（Phase 3）
3. 文档化最佳实践

---

*方案制定日期：2026-03-17*
*版本：v2.0 draft*
