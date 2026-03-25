# Investigate Skill

## 基本信息

| 属性 | 内容 |
|------|------|
| **Skill名称** | investigate |
| **版本** | v1.0 |
| **来源** | gstack investigate |
| **核心原则** | Iron Law: No fixes without root cause |

---

## 核心原则

### Iron Law

> **NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

在修复任何问题之前，必须先进行根因分析。

---

## 调查流程

### Phase 1: Investigate（调查）

```
目标：收集所有相关信息

步骤：
1. 问题描述复述
2. 环境信息收集
3. 复现步骤确认
4. 相关日志/错误信息收集
```

### Phase 2: Analyze（分析）

```
目标：理解问题本质

步骤：
1. 问题分类（Bug/设计/配置/性能/安全）
2. 影响范围评估
3. 紧急程度判断
4. 相关组件分析
```

### Phase 3: Hypothesize（假设）

```
目标：形成根因假设

步骤：
1. 提出可能的根因
2. 假设验证计划
3. 排除不可能的原因
4. 优先假设排序
```

### Phase 4: Implement（实施）

```
目标：验证并修复

步骤：
1. 验证根因假设
2. 实施修复方案
3. 验证修复效果
4. 记录经验教训
```

---

## 根因分析框架

### 5Why 分析

```
问题：[描述问题]

Why 1: 为什么会发生？
→ [原因1]

Why 2: 为什么会这样？
→ [原因2]

Why 3: 为什么会这样？
→ [原因3]

Why 4: 为什么会这样？
→ [原因4]

Why 5: 根本原因是什么？
→ [根因]
```

### 鱼骨图分析

```
                    问题
                      │
        ┌─────────────┼─────────────┐
        │             │             │
      方法          机器         材料
        │             │             │
        ▼             ▼             ▼
     [因素]        [因素]        [因素]

        │             │             │
      环境         人员         管理
        │             │             │
        ▼             ▼             ▼
     [因素]        [因素]        [因素]
```

---

## 在 CyberTeam 中的应用

### 场景

1. **Agent 执行遇到问题**：分析为什么失败
2. **计划审核发现风险**：识别潜在风险根因
3. **PUA 触发后**：理解为什么 Agent 产出不足

### 代码示例

```python
class Investigator:
    def investigate(self, problem):
        # Phase 1: 调查
        facts = self.collect_facts(problem)

        # Phase 2: 分析
        analysis = self.analyze(facts)

        # Phase 3: 假设
        hypothesis = self.form_hypothesis(analysis)

        # Phase 4: 实施
        solution = self.implement(hypothesis)

        return {
            'root_cause': hypothesis.root_cause,
            'solution': solution,
            'evidence': hypothesis.evidence
        }
```

---

## 输出格式

```
## 根因分析报告

### 问题描述
[问题详细描述]

### 调查发现
- 环境信息：...
- 复现步骤：...
- 错误信息：...

### 根因分析
#### 5Why 分析
- Why 1: ...
- Why 2: ...
- Why 3: ...
- Why 4: ...
- Why 5: [根本原因]

#### 鱼骨图
[图表展示]

### 解决方案
- 修复方案：...
- 验证计划：...
- 预防措施：...

### 经验教训
- 学到什么：...
- 如何改进：...
```

---

## 注意事项

1. **不修复无根因**：没有找到根因前不实施修复
2. **证据支持**：每个结论都需要证据
3. **验证假设**：修复后必须验证根因假设正确
4. **记录经验**：形成知识库，防止重复问题
