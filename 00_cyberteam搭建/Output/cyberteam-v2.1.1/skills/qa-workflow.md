# CyberTeam QA工作流

## 完整测试周期

```
需求 → 设计 → 开发 → 单元测试 → 集成测试 → E2E测试 → 发布
  |       |       |         |           |          |         |
  v       v       v         v           v          v         v
缺陷    评审    TDD      CI检查      API测试    Playwright  灰度
报告            先行                                    发布
```

## 各阶段职责

| 阶段 | 负责人 | 工具 | 质量标准 |
|------|--------|------|----------|
| 单元测试 | 开发 | Jest/Vitest | 100%覆盖 |
| 集成测试 | 开发 | Supertest | 核心路径 |
| E2E测试 | QA | Playwright | 关键旅程 |
| 性能测试 | DevOps | k6/Locust | P95<500ms |
| 安全扫描 | 安全 | Snyk/Semgrep | 0高危 |

---

**版本**: v2.1 | **来源**: gstack QA | **日期**: 2026-03-23
