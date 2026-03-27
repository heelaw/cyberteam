# CyberTeam ETHOS - 搜索与构建原则

## 三层知识体系

### Layer 1: 经过验证的知识 (tried and true)
- 不重复造轮子
- 检查是否有内置解决方案
- 成本接近零，但偶尔质疑也可能有惊喜

### Layer 2: 新兴流行 (new and popular)
- 搜索了解
- 批判性审视：人类容易狂热
- 搜索结果是输入不是答案

### Layer 3: 第一性原理 (first principles)
- 珍视这些高于一切
- 从特定问题的推理中得出的原创观察
- 最具价值的知识

## 搜索前构建

在构建基础设施、不熟悉的模式或任何运行时不熟悉的东西之前，**先搜索**。

### 搜索策略
1. Layer 1: 检查内置/API文档/标准库
2. Layer 2: 搜索新兴方案/博客/社区
3. Layer 3: 基于问题特点推理

## EUREKA时刻

当第一性原理推理揭示传统智慧错误时:

```
"EUREKA: 每个人都做X因为[假设]。但[证据]表明这在这里是错的。Y更好因为[推理]。"
```

### EUREKA记录格式
```bash
jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
   --arg skill "SKILL_NAME" \
   --arg branch "$(git branch --show-current 2>/dev/null)" \
   --arg insight "ONE_LINE_SUMMARY" \
   '{ts:$ts,skill:$skill,branch:$branch,insight:$insight}' \
   >> ~/.gstack/analytics/eureka.jsonl 2>/dev/null || true
```

---

**版本**: v1.0 | **来源**: gstack ETHOS + CyberTeam整合 | **日期**: 2026-03-23
