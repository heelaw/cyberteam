# upstream - 技术BG Agent

## 直接上游

| 上游Agent | 关系 | 说明 |
|-----------|------|------|
| CEO | 任务路由 | 技术BG的来源之一，接收CEO的L3A路由任务 |
| 产品BG | 任务协同 | 产品需求的主要来源 |
| PM协调器 | 任务协同 | 高复杂度任务时的PM协调 |
| 记忆中台 | 数据依赖 | 获取历史代码和技术文档 |

## 数据依赖

| 数据源 | 格式 | 刷新频率 | 说明 |
|--------|------|----------|------|
| 产品规格 | markdown | 每次需求 | 产品BG传递 |
| 技术栈定义 | JSON | 项目启动 | 技术选型依据 |
| 现有代码库 | 代码文件 | 实时 | 代码复用参考 |
| API文档 | OpenAPI | 每次更新 | 接口规范 |

## 技术专业上游

| 上游资源 | 接口类型 | 说明 |
|----------|----------|------|
| 系统架构师Agent | internal | 架构思维 |
| 安全专家Agent | internal | 安全设计 |
| 性能优化师Agent | internal | 性能思维 |
| DevOps工程师Agent | internal | 自动化交付 |
| 架构评审师Agent | internal | 技术评审 |

## gstack技能上游

| 上游技能 | 接口类型 | 说明 |
|----------|----------|------|
| gsd-executor | /codex | 代码执行 |
| engineering-frontend-developer | /frontend | 前端开发 |
| engineering-backend-architect | /backend | 后端架构 |
| code-reviewer | /review | 代码审查 |

## 上游数据流

```
用户输入 → CEO路由 → 技术BG
                      ↑           ↑
                  产品BG        记忆中台
              （产品需求）   （技术文档）
                  ↑           ↑
              技术专家Agent团（专业能力）
              gstack Skills（工程能力）
```
