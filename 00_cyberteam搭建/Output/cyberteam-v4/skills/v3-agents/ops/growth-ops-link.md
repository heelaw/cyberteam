# 运营部 — 下属部门 Agent 状态总览

> **版本**: v1.0
> **更新日期**: 2026-03-24
> **维护者**: 运营总监 Agent

---

## 部门总览

| 部门 | Agent 目录 | 定义状态 | 定义进度 |
|------|-----------|----------|----------|
| 内容运营部 | `agents/content-ops/` | ✅ 完整 | v3.1 — 5角色 + writing Skill |
| **用户增长部** | `agents/growth-ops/` | 🔄 进行中 | 8轮Q&A，5/8完成 |
| **数据运营部** | `agents/data-ops/` | ⏳ 待启动 | 8轮Q&A未开始 |
| **渠道运营部** | `agents/channel-ops/` | ⏳ 待启动 | 8轮Q&A未开始 |

---

## Content Ops — 已完成 ✅

```
agents/content-ops/
├── SOUL.md                    ✅ 部门灵魂定义（v3.1）
├── README.md                  ✅ 部门入口
└── roles/
    ├── strategy-analyst.md     ✅ 策略分析师
    ├── content-planner.md      ✅ 内容策划/操盘手
    ├── copywriter.md           ✅ 文案撰写
    ├── reviewer.md             ✅ 审核校对
    └── publisher.md            ✅ 发布运营

关联 Skill：
└── skills/writing/            ✅ 完整9阶段工作流
    ├── SKILL.md               ✅ 入口
    ├── workflow/00-08/        ✅ 18个流程文档
    └── references/            ✅ 4个支撑文档
```

---

## 用户增长部 — 进行中 🔄

```
agents/growth-ops/
├── README.md                  🔄 本文件（已创建骨架）
├── SOUL.md                   ⏳ Q&A完成后生成
└── roles/                   ⏳ Q&A完成后生成

Q&A 进度（5/8轮）：
✅ 第1轮：部门使命 + 核心公式
✅ 第2轮：决策判断系统（ICE + 立项 + 协作）
✅ 第3轮：日常节奏 + 数据追踪
✅ 第4轮：团队构成 + 能力标准
✅ 第5轮：风险管理与升级机制
⏳ 第6轮：A/B测试统计 + 知识沉淀
⏳ 第7轮：跨部门接口 + 冲突仲裁
⏳ 第8轮：Agent骨架整合 + Skill映射
```

---

## 数据运营部 — 待启动 ⏳

```
agents/data-ops/
├── README.md                  ⏳ 骨架已创建
├── SOUL.md                   ⏳ 待Q&A
└── roles/                   ⏳ 待Q&A

前置条件：
├── 用户增长部Agent定义完成
└── 增长部数据埋点规范对齐
```

---

## 渠道运营部 — 待启动 ⏳

```
agents/channel-ops/
├── README.md                  ⏳ 骨架已创建
├── SOUL.md                   ⏳ 待Q&A
└── roles/                   ⏳ 待Q&A

前置条件：
├── 数据运营部Agent定义完成（需数据支撑）
└── 与内容部协作接口确定
```

---

## Agent ↔ Skill 映射（待更新）

当前 `docs/12-Agent-Skill映射.md` 中，以下部门尚未映射：

| 部门 | 待映射 Skills |
|------|---------------|
| 用户增长部 | A/B测试统计、增长实验管理 |
| 数据运营部 | 数据分析框架、BI报表 |
| 渠道运营部 | 投放优化、渠道评估 |

**更新时机**：各 Agent 定义完成后（Q&A第8轮）

---

**下一步**：继续用户增长部Q&A（第6轮 → A/B测试统计方法论 + 知识沉淀系统）
