# upstream - 资产库中台

## 直接上游

| 上游Agent | 关系 | 说明 |
|-----------|------|------|
| CEO | 资产调度 | CEO路由时调用资产 |
| PM协调器 | 资源协调 | 项目资源调配 |
| 部门BG | 能力调用 | 各BG执行时调用资产 |

## 数据依赖

| 数据源 | 格式 | 刷新频率 | 说明 |
|--------|------|----------|------|
| 资产注册表 | JSON | 实时 | 所有可用资产 |
| 负载状态 | JSON | 实时 | 各资产当前负载 |
| 使用统计 | JSON | 定期 | 历史使用数据 |
| 效果数据 | JSON | 每次使用后 | 质量评分更新 |

## 资产来源上游

| 来源 | 位置 | 数量 |
|------|------|------|
| gstack | `.claude/skills/` | 40+ agents |
| agency-agents | `github/agency-agents/` | 100+ agents |
| baoyu-skills | `.claude/skills/baoyu-*` | 18 skills |

## gstack技能上游

| 技能ID | 技能名称 | 调用方式 |
|--------|----------|----------|
| gs-001 | gsd-roadmapper | /plan-roadmap |
| gs-002 | gsd-planner | /plan-spec |
| gs-003 | gsd-executor | /codex |
| gs-004 | gsd-verifier | /qa |
| gs-005 | gsd-debugger | /debug |
| gs-009 | code-reviewer | /review |
| gs-010 | security-reviewer | /security-review |
| gs-011 | design-ui-designer | /design-ui |

## agency资产上游

| 类别 | 来源 | 核心能力 |
|------|------|----------|
| 运营类 | 操盘手课程 | 操盘手、增长、内容 |
| 营销类 | 营销体系 | 品牌、投放、SEO |
| 战略类 | 咨询体系 | 战略规划、商业模式 |
| 产品类 | 产品体系 | 需求分析、用户体验 |
| 技术类 | 技术体系 | 架构、安全、性能 |

## 上游数据流

```
部门BG → 资产调度请求 → 资产中台
    ↑                   ↑
资产注册表 ← gstack/agency/baoyu
负载状态 ← 实时监控
效果数据 ← 使用后反馈
```
