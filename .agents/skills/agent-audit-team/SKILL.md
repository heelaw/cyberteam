name: Agent审查团触发器
name_en: agent-audit-trigger
version: 1.0.0
category: quality
sub_category: agent-review
difficulty: 基础
author: Cyberwiz
description: 当用户需要审查Agent或Skill时自动触发Agent审查团。关键词：审查、审查团、Agent审查、NEXUS标准审查、评估Agent

# ========================================
# 触发条件
# ========================================
triggers:
  - "审查"
  - "审查团"
  - "Agent审查"
  - "Skill审查"
  - "NEXUS标准"
  - "评估Agent"
  - "质量审查"
  - "用审查团"

# ========================================
# 执行逻辑
# ========================================
actions:
  - name: "识别审查需求"
    trigger: "当用户提到审查需求时"
    steps:
      - "识别用户想要审查的Agent或Skill"
      - "确定审查范围（全面审查/重点审查）"
      - "确定优先级（P0/P1/P2）"

  - name: "触发Agent审查团"
    trigger: "识别到审查需求"
    steps:
      - "加载Agent审查团领队"
      - "解析审查目标和范围"
      - "启动十一维并行审查"

# ========================================
# 使用说明
# ========================================
usage:
  command: "/skill agent-audit"
  example: "帮我审查这个项目"
  scope: "Agent/Skill质量审查"

# ========================================
# Agent审查团简介
# ========================================
about:
  team: "Agent审查团"
  members: 12
  dimensions: 11
  standards: "NEXUS"
  description: |
    Agent审查团采用NEXUS十一维标准，对Agent和Skill进行严苛审查：
    - 架构完整性 (15%)
    - 通信机制 (15%) ⭐
    - 调用机制 (15%) ⭐
    - Handoff协议 (15%) ⭐
    - 质量门禁 (15%) ⭐
    - 交付物质量 (10%)
    - Dev↔QA循环 (10%) ⭐
    - 独特个性 (5%)
    - 编排集成 (5%)
    - 证据充分性 (5%)
    - Skill配套 (5%)

    ⭐ 为NEXUS核心机制
