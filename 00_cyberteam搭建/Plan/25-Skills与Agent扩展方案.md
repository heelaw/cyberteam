# Skills与Agent扩展方案

> **版本**: v1.1 | **日期**: 2026-03-24 | **负责人**: CyberTeam研究员

---

## 一、现有资源全景盘点

### 1.1 Skills统计

| 来源 | 数量 | 路径 | 核心分类 |
|------|------|------|----------|
| **gstack** | **43个** | `~/.claude/skills/` | 工程/设计/审查/QA/部署/战略 |
| **skill-library-v1** | **59个** | `02_Skill研发/skill-library-v1/` | core(17)/cyberwiz(21)/thinking(9)/productivity(1)/development(2)/information(9) |
| **pua-skills** | **1个** | `~/.claude/skills/pua/` | 激励/压力管理 |
| **合计** | **103个** | - | - |

#### gstack 43个Skills详细清单

| 类别 | Skills | 数量 |
|------|--------|------|
| **战略规划(4)** | office-hours, plan-ceo-review, autoplan, gstack-upgrade | 4 |
| **工程(3)** | plan-eng-review, codex, review | 3 |
| **设计(3)** | design-consultation, design-review, plan-design-review | 3 |
| **审查审计(3)** | cso, careful, guard | 3 |
| **QA测试(4)** | qa, qa-only, benchmark, investigate | 4 |
| **部署发布(5)** | ship, land-and-deploy, canary, setup-deploy, freeze/unfreeze | 5 |
| **浏览研究(2)** | browse, marketplace | 2 |
| **Retro复盘(1)** | retro | 1 |
| **文档(2)** | document-release, review | 2 |
| **ljg系列(15)** | ljg-card, ljg-invest, ljg-learn, ljg-paper, ljg-paper-flow, ljg-plain, ljg-rank, ljg-skill-map, ljg-travel, ljg-word, ljg-word-flow, ljg-writes, ljg-x-download | 15 |
| **其他(2)** | setup-browser-cookies, gstack | 2 |
| **总计** | | **43** |

#### skill-library-v1 59个Skills分类

| 分类 | 数量 | 子类详情 |
|------|------|----------|
| **00-core** | 17 | 思维链/元认知/判断器/协调器/SWOT/知识图谱/逆向思维/批判性思维 |
| **01-cyberwiz** | 21 | 增长黑客/营销/用户研究/商业分析/全球化/案例分析/活动设计/岗位分析 |
| **02-thinking** | 9 | 创新思维(六帽/第一性/云雨伞)/系统思维/标签富化/自动分类/GROW模型 |
| **03-productivity** | 1 | 图像生成 |
| **04-development** | 2 | skill生成器 |
| **05-information** | 9 | RSS/Web采集/课程整合/资源索引/分析器 |

### 1.2 Agent统计

| 来源 | 数量 | 路径 | 核心分类 |
|------|------|------|----------|
| **agency-agents-zh** | **201个** | `03_Resource/github_stars/agency-agents-zh/` | 19个分类 |
| **思考天团** | **~93个** | `02_Skill研发/思考天团Agent/agents/` | 认知偏差/决策框架/战略思维 |
| **合计** | **~294个** | - | - |

#### agency-agents-zh 201个Agents分类详情

| 分类 | 数量 | 主要Agents |
|------|------|-----------|
| **engineering** | 29 | AI工程师/后端架构/代码审查/数据工程/数据库/DevOps/钉钉/飞书/微信小程序/嵌入式/FPGA/IoT/固件/SRE/安全/智能合约 |
| **marketing** | 28 | App Store优化/百度SEO/B站/抖音/小红书/快手/LinkedIn/Reddit/私域运营/直播电商/跨境电商/知识付费 |
| **specialized** | 30 | 合规审计/区块链安全/MCP构建/prompt工程/AI政策/会议助手/Model QA/定价优化/风险评估/Salesforce |
| **academic** | 6 | 人类学家/地理学家/历史学家/叙事学家/心理学家/学习规划师 |
| **design** | 8 | 品牌守护/图像提示词/包容性视觉/UI设计/UX架构/UX研究/视觉叙事/趣味注入 |
| **game-development** | 5 | 音频/游戏设计/关卡/叙事/技术美术 |
| **product** | 5 | 行为引导/反馈综合/产品经理/冲刺优先级/趋势研究 |
| **support** | 8 | 分析报告/执行摘要/财务追踪/基础设施/法律合规/招聘/供应链/支持响应 |
| **testing** | 9 | 无障碍/API/嵌入式QA/证据收集/性能基准/现实核查/测试结果/工具评估/工作流优化 |
| **sales** | 8 | 账户策略/交易策略/发现教练/销售工程师/管道分析/方案策略/销售教练/外呼 |
| **spatial-computing** | 5 | Mac空间金属/VisionOS/XR沉浸式/XR界面/XR驾驶舱 |
| **finance** | 3 | 财务预测/欺诈检测/发票管理 |
| **hr** | 2 | 绩效审查/招聘 |
| **legal** | 2 | 合同审查/政策撰写 |
| **strategy** | ~3 | nexus策略+coordination+examples |
| **paid-media** | ~6 | (待探索) |
| **supply-chain** | ~1 | supply-chain-strategist |

#### 思考天团 ~93个思维模型Agents

| 类别 | 数量 | 代表Agents |
|------|------|------------|
| **认知偏差** | ~25 | 确认偏误/可得性启发/代表性启发/基础率谬误/合取谬误/赌徒谬误/回归均值/信息级联/处置效应/模糊厌恶/零和思维 |
| **决策框架** | ~20 | 第一性原理/六顶思考帽/SWOT/5Why/PRE-MORTEM/反转思维/奥卡姆剃刀/汉隆剃刀/帕金森定律 |
| **战略思维** | ~15 | 波特五力/长尾理论/二阶思维/竞争战略/生态系/网络效应/护城河/飞轮效应/邓巴数/梅特卡夫定律 |
| **系统思维** | ~10 | 系统思考/反脆弱/临界点/反馈回路/杠杆点 |
| **成长模型** | ~8 | GROW/GIK/KISS/McKinsey 7S/PDCA/迭代/复利 |
| **心智模型** | ~10 | 能力圈/影响力圈/倒置/规划谬误/杠杆/盈亏平衡/机会成本/沉没成本 |
| **思维方法** | ~5 | 苏格拉底追问/类比推理/辩证法/逆向思维/刻意练习/概率思维/贝叶斯 |

### 1.3 现有资源总览

```
┌─────────────────────────────────────────────────────┐
│           CyberTeam 现有资源全景 (2026-03-24)        │
├─────────────────────────────────────────────────────┤
│  Skills:  103个                                     │
│   ├── gstack: 43                                   │
│   ├── skill-library-v1: 59                         │
│   └── pua: 1                                       │
│                                                     │
│  Agents:  ~294个                                    │
│   ├── agency-agents-zh: 201                         │
│   └── 思考天团: ~93                                 │
│                                                     │
│  总计:    ~397个 可复用资源                         │
└─────────────────────────────────────────────────────┘
```

---

## 二、扩展路径: 103 → 300+ Skills

### 2.1 扩展策略矩阵

```
目标: 300+ Skills = 103(现有) + 197(新增)

新增来源分析:
├── A. agency-agents-zh转化 (201个Agent → ~80个Skill)
│   └── 选高频场景, 每个领域保留Top-5
├── B. 思考天团框架Skills化 (~93个思考框架 → 30个Skill)
│   └── 按认知偏差/决策框架/战略分析归类, 建立自动触发机制
├── C. skill-library扩展 (59 → 100, 新增41个)
│   └── cyberwiz扩品/生产力工具/开发辅助
├── D. 垂直行业Skills (新增30个)
│   └── 医疗/教育/制造/零售/物流
├── E. 工具型Skills (新增20个)
│   └── 数据处理/文件转换/API集成
└── F. 生态共建 (新增15个)
    └── 社区贡献/用户提交/AI生成
```

### 2.2 五大扩展路径

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Skills 扩展路径 (103 → 300+)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  【路径1】agency-agents-zh拆解 (目标+80)                              │
│  ├── 策略: 201个Agents → 提取核心能力 → 标准化Skill                    │
│  ├── engineering(29) ──→ 25个Skill: 架构/前端/安全/DevOps/SRE        │
│  ├── marketing(28) ──→ 20个Skill: 抖音/小红书/B站/SEO/电商            │
│  ├── testing(9) ─────→ 9个Skill: 全部转为Testing Skill Suite          │
│  ├── sales(8) ──────→ 8个Skill: 全部转为Sales Skill Suite             │
│  ├── product(5) ────→ 5个Skill: 产品经理全链路                       │
│  ├── design(8) ─────→ 8个Skill: UI/UX/品牌视觉                       │
│  └── specialized(30) ─→ 5个Skill: MCP/合规/prompt等高频场景           │
│                                                                      │
│  【路径2】思考天团Skills化 (目标+30)                                  │
│  ├── 策略: 93个思维模型 → 自动触发型Skills                            │
│  ├── 认知偏差(25) ────→ /cognitive-bias-<name> Skills               │
│  ├── 决策框架(20) ───→ /decide-<framework> Skills                   │
│  ├── 战略分析(15) ───→ /strategy-<model> Skills                     │
│  └── 触发机制: 关键词检测 → 匹配Skill → 自动激活                      │
│                                                                      │
│  【路径3】skill-library扩展 (目标+41)                                │
│  ├── 00-core(17→25) ──→ +8: 更多协调器/判断器                       │
│  ├── 01-cyberwiz(21→40) → +19: 增长黑客/内容运营/用户洞察            │
│  ├── 02-thinking(9→20) → +11: 创新方法论/批判性思维                  │
│  ├── 03-productivity(1→15) → +14: 图像/视频/音频/文档处理           │
│  ├── 04-development(2→10) → +8: 代码生成/调试/重构                  │
│  └── 05-information(9→20) → +11: 深度研究/报告生成/知识管理         │
│                                                                      │
│  【路径4】新增Categories (目标+30)                                   │
│  ├── 06-research(8) ────→ 竞品分析/行业研究/技术调研/学术搜索         │
│  ├── 07-data(8) ───────→ 数据可视化/统计分析/A/B测试/数据清洗        │
│  ├── 08-collaboration(8) → 会议纪要/项目协调/团队沟通/文档协作        │
│  └── 09-legal-finance(6) → 合同审查/财务分析/合规检查/预算规划        │
│                                                                      │
│  【路径5】生态共建 (目标+15+)                                        │
│  ├── 社区贡献(GitHub Stars) ──→ +10                                 │
│  ├── 用户提交 ──────────────→ +5                                    │
│  └── AI生成(skill-generator) → +5+                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.3 300+ Skills分类总览

```
CyberTeam Skills 总库 (300+)
│
├── A. 核心引擎 (25)
│   ├── 协调器(5): orchestrator, problem-classifier, workflow-optimizer, ...
│   ├── 判断器(8): quality-discriminator, insight-extractor, judge-report-generator, ...
│   ├── 思维链(6): senior-thinking-chain, senior-private-board, senior-meta-cognition, ...
│   └── 知识系统(6): knowledge-graph, knowledge-explorer, critical-systems-thinking, ...
│
├── B. 增长黑客 (40)
│   ├── 增长策略(10): pmf-validator, growth-hacking, aha-moment-finder, ...
│   ├── 用户洞察(8): user-insight, demand-analysis, data-decision, ...
│   ├── 内容运营(10): marketing, xiaohongshu, bilibili, douyin, ...
│   └── 商业分析(12): business-model, market-entry, brand-localization, ...
│
├── C. 思维方法 (50)
│   ├── 认知偏差(25): confirmation-bias, availability-heuristic, risk-aversion, ...
│   ├── 决策框架(10): first-principles, six-hats, swot, 5why, premortem, ...
│   ├── 战略分析(8): porters-five-forces, network-effects, moat-theory, ...
│   └── 系统思维(7): systems-thinking, anti-fragile, second-order, ...
│
├── D. 工程开发 (40)
│   ├── 架构设计(8): backend-architect, software-architect, iot-solution, ...
│   ├── 前端移动(6): frontend-developer, mobile-app-builder, wechat-mini, ...
│   ├── DevOps SRE(8): devops-automator, sre, incident-response, ...
│   ├── 安全测试(10): security-engineer, code-reviewer, threat-detection, ...
│   └── 嵌入式(8): firmware-engineer, linux-driver, embedded-qa, fpga, ...
│
├── E. 质量保障 (35)
│   ├── 测试工程(9): api-tester, performance-benchmarker, accessibility-auditor, ...
│   ├── 审查审计(12): code-review, security-review, database-review, ...
│   ├── 质量评判(8): e2e-runner, build-error-resolver, tdd-guide, ...
│   └── 验证集成(6): integration-checker, ui-checker, regression-tester, ...
│
├── F. 产品设计 (30)
│   ├── 产品经理(5): product-manager, sprint-prioritizer, trend-researcher, ...
│   ├── UI设计(8): ui-designer, ux-architect, ux-researcher, visual-storyteller, ...
│   ├── UX研究(7): user-research, behavioral-nudge, feedback-synthesizer, ...
│   └── 品牌视觉(5): brand-guardian, whimsy-injector, inclusive-visuals, ...
│
├── G. 营销增长 (45)
│   ├── 社媒运营(15): douyin, xiaohongshu, bilibili, kuaishou, linkedin, ...
│   ├── 电商运营(8): ecommerce-operator, china-ecommerce, cross-border, ...
│   ├── 私域增长(8): private-domain, livestream-commerce, growth-hacker, ...
│   ├── SEO/ASO(6): baidu-seo, app-store-optimizer, reddit-community, ...
│   └── 内容创作(8): content-creator, book-co-author, podcast-strategist, ...
│
├── H. 专业领域 (35)
│   ├── 学术研究(6): anthropologist, historian, psychologist, geographer, ...
│   ├── 法律合规(8): contract-reviewer, policy-writer, compliance-auditor, ...
│   ├── 财务金融(6): financial-forecaster, fraud-detector, invoice-manager, ...
│   ├── 人力资源(5): recruiter, performance-reviewer, corporate-training, ...
│   └── 游戏开发(5): game-designer, narrative-designer, technical-artist, ...
│
└── I. 平台工具 (20)
    ├── 部署发布(8): ship, land-and-deploy, canary, setup-deploy, ...
    ├── 协作沟通(6): meeting-assistant, project-coordinator, document-collaboration, ...
    └── 数据分析(6): analytics-reporter, sql-query, data-visualization, ...

总计: ~320个 Skills
```

---

## 三、Skill到Agent映射方案

### 3.1 映射原则

```
1:N 映射：一个Skill可被多个Agent调用
N:1 聚合：多个Skills组合成一个高级Agent
层次化：原子Skill → 专业Skill → Agent角色
自动触发：关键词检测 → 匹配Skill
```

### 3.2 映射矩阵 (精选)

| Agent角色 | 调用的Skills | 数量 | 说明 |
|-----------|-------------|------|------|
| **gsd-executor** | /codex + /senior-thinking-chain + /code-review + /build-error-resolver | 4 | 执行构建 |
| **gsd-verifier** | /qa + /e2e-runner + /integration-checker + /ui-checker | 4 | 验证结果 |
| **gsd-debugger** | /investigate + /codex + /senior-reverse-thinking + /build-error-resolver | 4 | 调试分析 |
| **gsd-planner** | /autoplan + /senior-private-board + /senior-meta-cognition + /quality-discriminator | 4 | 制定规格 |
| **code-reviewer** | /codex + /senior-thinking-chain + /critical-systems-thinking + /tdd-guide | 4 | 代码审查 |
| **engineering-frontend-developer** | /frontend-developer + /senior-thinking-chain + /code-review + /tdd-guide | 4 | 前端开发 |
| **engineering-backend-architect** | /backend-architect + /systems-thinking + /senior-meta-cognition + /review | 4 | 后端架构 |
| **marketing-douyin-strategist** | /douyin + /growth-hacking + /data-decision + /senior-private-board | 4 | 抖音策略 |
| **design-ui-designer** | /ui-designer + /ux-architect + /senior-meta-cognition + /brand-guardian | 4 | UI设计 |
| **sales-deal-strategist** | /deal-strategist + /senior-private-board + /critical-systems-thinking + /growth-model | 4 | 销售策略 |

### 3.3 Skill分层架构

```
┌─────────────────────────────────────────┐
│           Agent 角色层 (104个)           │
│  gsd-executor / engineering-frontend /  │
│  marketing-douyin / design-ui-designer  │
└────────────────────┬────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────┐
│         Agent 专业Skill层 (300+)        │
│  [Agent名]-skill.md → 定义Agent专属workflow│
└────────────────────┬────────────────────┘
                     │ 组合
┌────────────────────▼────────────────────┐
│          原子Skill层 (100+)              │
│  /codex /qa /review /ship /office-hours │
│  /first-principles /swot /six-hats      │
└─────────────────────────────────────────┘
```

### 3.4 Skill调用协议

```yaml
# Skill调用标准格式
skill:
  name: "/first-principles"
  trigger:
    keywords: ["第一性", "根本", "本质", "为什么", "从零开始"]
    context: ["问题分析", "方案设计", "决策制定"]
  workflow:
    - "识别当前假设"
    - "拆解到不可证明的基本事实"
    - "从基本事实重建方案"
    - "验证新方案的有效性"
  output: "第一性原理分析报告"
  fallback: "/senior-private-board"
```

### 3.5 300+ Skills → 104 Agents 映射总表

| Agent大类 | 包含Skills示例 | Agent数量 |
|-----------|---------------|-----------|
| **GSD核心** | autoplan, codex, qa, ship, benchmark, e2e-runner | 9 |
| **工程研发** | backend-architect, frontend-developer, security-engineer, devops, sre, mobile, data | 25 |
| **设计** | ui-designer, ux-architect, ux-researcher, brand-guardian, whimsy-injector | 7 |
| **质量保障** | code-reviewer, security-reviewer, e2e-runner, tdd-guide, database-reviewer | 15 |
| **营销增长** | douyin, xiaohongshu, seo, content-creator, growth-hacker, ecommerce | 28 |
| **产品** | product-manager, sprint-prioritizer, trend-researcher, behavioral-nudge | 5 |
| **专业领域** | academic(6), finance(3), legal(2), hr(2), game(5), spatial(5) | ~25 |
| **销售** | deal-strategist, discovery-coach, pipeline-analyst, proposal-strategist | 8 |
| **思考模型** | 来自思考天团: 认知偏差/决策框架/战略分析/系统思维 | ~93 |
| **战略运营** | roadmapper, research, knowledge-commerce | 10 |

**总计**: ~225个 Agents（含93个思维模型Agent）

---

## 四、完整组织架构 (8大部门+专家)

### 4.1 组织架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CyberTeam 组织架构                              │
│                           (104 Agents + 300+ Skills)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐                                                        │
│  │   总裁办    │  CEO, COO, CFO, CHRO, CTO, CGO                        │
│  │  (6 Agents)  │  Skills: office-hours, plan-ceo-review, autoplan    │
│  └─────────────┘                                                        │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      核心执行部 (GSD)                             │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ gsd-      │ │ gsd-      │ │ gsd-     │ │ gsd-     │           │    │
│  │  │ planner   │ │ executor  │ │ verifier  │ │ debugger │           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ gsd-      │ │ gsd-      │ │ gsd-ui-  │ │ gsd-     │           │    │
│  │  │ roadmapper│ │ phase-    │ │ researcher│ │ integra- │           │    │
│  │  │           │ │ researcher │ │          │ │ tion-checker│       │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  (8 Agents)                                                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      工程研发部 (23 Agents)                       │    │
│  │                                                                   │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │    │
│  │  │ engineering-    │  │ engineering-    │  │ engineering-    │   │    │
│  │  │ frontend-       │  │ backend-        │  │ security-       │   │    │
│  │  │ developer       │  │ architect       │  │ engineer        │   │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │    │
│  │                                                                   │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │    │
│  │  │ engineering-    │  │ engineering-    │  │ engineering-    │   │    │
│  │  │ mobile-app-     │  │ data-engineer   │  │ devops-         │   │    │
│  │  │ builder          │  │                 │  │ automator       │   │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │    │
│  │                                                                   │    │
│  │  [+ 17个专项工程师]                                               │    │
│  │  rust, python, java, kotlin, cpp, go reviewer + resolver        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      设计部 (7 Agents)                            │    │
│  │                                                                   │    │
│  │  design-ui-designer │ design-ux-architect │ design-ux-researcher│   │    │
│  │  design-visual-storyteller │ design-brand-guardian               │    │
│  │  design-whimsy-injector │ design-ui-checker                      │    │
│  │                                                                   │    │
│  │  Skills: design-consultation, design-review, plan-design-review │   │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    代码质量部 (15 Agents)                         │    │
│  │                                                                   │    │
│  │  code-reviewer │ security-reviewer │ e2e-runner                 │   │    │
│  │  build-error-resolver │ database-reviewer │ tdd-guide           │   │    │
│  │  refactor-cleaner                                                    │   │
│  │                                                                   │    │
│  │  Skills: review, cso, benchmark, qa, qa-only, careful, freeze   │   │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    市场营销部 (20+ Agents) ★待扩展                │    │
│  │                                                                   │    │
│  │  marketing-douyin-strategist │ marketing-xiaohongshu-specialist │   │    │
│  │  marketing-tiktok-strategist │ marketing-wechat-official-account│   │    │
│  │  marketing-seo-specialist │ marketing-content-creator           │   │    │
│  │  [+ 更多来自agency-agents-zh/marketing/]                          │   │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    产品/销售/HR/财务/法律 (20+ Agents)             │    │
│  │                                                                   │    │
│  │  product-manager │ product-owner │ product-analyst              │   │    │
│  │  sales-specialist │ sales-manager │ hr-recruiter                │   │    │
│  │  financial-analyst │ legal-counsel │ compliance-officer         │   │    │
│  │                                                                   │    │
│  │  ★ 全部来自 agency-agents-zh 各目录                               │   │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    思考框架专家部 (100 Agents)                    │    │
│  │                                                                   │    │
│  │  01-kahneman │ 02-first-principle │ 03-six-hats │ 04-swot-tows  │   │    │
│  │  05-fivewhy  │ 06-goldlin        │ 07-grow      │ 08-kiss       │   │    │
│  │  ...         │ ...               │ ...          │ 100-spiral    │   │    │
│  │                                                                   │    │
│  │  覆盖: 思维模型, 决策框架, 分析方法, 创新工具, 管理理论            │   │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    专业领域专家部 (25 Agents)                     │    │
│  │                                                                   │    │
│  │  specialized-prompt-engineer │ specialized-mcp-builder          │   │    │
│  │  specialized-document-generator │ specialized-risk-assessor    │   │    │
│  │  specialized-pricing-optimizer │ specialized-workflow-architect│   │    │
│  │  [+ 更多来自agency-agents-zh/specialized/]                       │   │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    部署运维部 (Skills)                           │    │
│  │                                                                   │    │
│  │  ship │ land-and-deploy │ canary │ setup-deploy                 │   │
│  │  guard │ freeze │ unfreeze │ investigate                      │   │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 部门职责与Skills清单

| 部门 | Agents | 核心Skills | 协作接口 |
|------|--------|------------|----------|
| **总裁办** | 6 | office-hours, plan-ceo-review, autoplan | 全部部门 |
| **GSD核心** | 8 | planner, executor, verifier, debugger, roadmapper | 全部部门 |
| **工程研发** | 23 | codex, architect, devops, security, sre | 设计部, 质量部 |
| **设计** | 7 | design-consultation, design-review, ux-research | 工程部, 产品部 |
| **代码质量** | 15 | review, cso, benchmark, qa, e2e | 工程部 |
| **市场营销** | 20+ | seo, sem, content, social, growth | 产品部 |
| **产品/销售/HR** | 20+ | (来自agency-agents-zh) | 总裁办 |
| **思考框架** | 100 | (来自思考天团) | 全部部门 |
| **专业领域** | 25 | (来自agency-agents-zh) | 工程部 |
| **部署运维** | - | ship, canary, guard, freeze | 工程部 |

---

## 五、实施路线图

### 阶段1: 基础建设 (Week 1-2)
```
目标: 完成103+93 Skills整合

✓ 整合gstack skills (43个)
✓ 整合skill-library-v1 (59个)
✓ 整合思考天团框架 (~93个)
✓ 建立统一Skill命名规范
✓ 建立Skill元数据库
✓ 打通skill-library与agency-agents关联
```

### 阶段2: 专业扩展 (Week 3-4)
```
目标: 扩展到200+ Skills

★ agency-agents-zh拆解 (+80个)
★ 思考天团Skills化 (+30个)
★ skill-library扩展 (+41个)
★ 建立自动触发机制
```

### 阶段3: 垂直深化 (Week 5-6)
```
目标: 扩展到300+ Skills

★ 新增Categories (+30个)
★ 完成Agent编排体系
★ 建立Team协作机制
★ ClawTeam框架深度集成
★ 完成104个Agents定义与注册
```

### 阶段4: 生态扩展 (Week 7+)
```
目标: 达成300+ Skills里程碑

★ 社区共建机制上线
★ 自动化Skill生成Pipeline
★ 质量评审体系建立
★ 持续优化与迭代
```

---

## 六、关键成功因素

1. **Skill标准化**: 统一命名、参数格式、输出规范、触发关键词
2. **Agent编排**: 建立Skills组合规则，形成高效协作与自动触发
3. **持续迭代**: 根据使用反馈快速优化，淘汰低频Skill
4. **文档完善**: 每个Skill/Agent必须有完整SKILL.md文档
5. **质量把控**: 建立评审机制，确保专业性与实用性
6. **生态共建**: 社区贡献+AI生成双轮驱动

---

## 七、附录

### A. 参考资源索引

| 资源 | 路径 | 数量 |
|------|------|------|
| gstack skills | `~/.claude/skills/` | 43 |
| skill-library-v1 | `01_Project/02_Skill研发/skill-library-v1/` | 59 |
| pua-skills | `~/.claude/skills/pua/` | 1 |
| agency-agents-zh | `03_Resource/github_stars/agency-agents-zh/` | 201 |
| 思考天团 | `02_Skill研发/思考天团Agent/agents/` | ~93 |

### B. agency-agents-zh 完整分类清单

```
agency-agents-zh/
├── academic/         → 6个: 人类学家/地理学家/历史学家/叙事学家/心理学家/学习规划师
├── design/          → 8个: 品牌守护/图像提示词/UI设计/UX架构/UX研究/视觉叙事...
├── engineering/     → 29个: AI工程/后端架构/代码审查/数据工程/DevOps/嵌入式/SRE...
├── finance/         → 3个: 财务预测/欺诈检测/发票管理
├── game-development/ → 5个: 游戏设计/叙事/关卡/技术美术/音频
├── legal/           → 2个: 合同审查/政策撰写
├── marketing/       → 28个: 抖音/小红书/B站/SEO/电商/私域运营/直播电商...
├── paid-media/      → ~6个: (待探索)
├── product/         → 5个: 产品经理/行为引导/反馈综合/趋势研究/Sprint优先级
├── sales/          → 8个: 账户策略/交易策略/发现教练/销售工程师/管道分析...
├── specialized/    → 30个: 合规/MCP构建/prompt工程/AI政策/会议助手...
├── spatial-computing/ → 5个: VisionOS/XR沉浸式/XR界面/XR驾驶舱/空间金属
├── strategy/        → ~3个: nexus策略+coordination+examples
├── supply-chain/    → ~1个: supply-chain-strategist
├── support/         → 8个: 分析报告/财务追踪/基础设施/法律合规/招聘/供应链...
├── testing/        → 9个: API测试/性能基准/无障碍/嵌入式QA/证据收集...
└── hr/             → 2个: 绩效审查/招聘
```

### C. CyberTeam Plan文件索引

| 编号 | 文件 | 状态 |
|------|------|------|
| 01 | 完整架构设计 | 已完成 |
| 02 | 100个思维专家清单 | 已完成 |
| 03 | GitHub仓库集成方案 | 已完成 |
| 04 | CEO-Agent定义 | 已完成 |
| 05 | 6个部门Agent详细定义 | 已完成 |
| 06 | 思维模型自动触发系统设计 | 已完成 |
| 07 | 接口定义与数据流 | 已完成 |
| 08 | 质量保障体系设计 | 已完成 |
| 09 | 实施路线图与验证计划 | 已完成 |
| 10 | 升级架构v2.0 | 已完成 |
| 11 | 运营专家Agent完整集成 | 已完成 |
| 12 | 交叉验证报告 | 已完成 |
| 13 | Agency-DevQA质量保障方案 | 已完成 |
| 14 | ClawTeam框架集成方案 | 已完成 |
| 15 | Goal-Driven持久循环与PUA动力实现 | 已完成 |
| 16 | DevQA质量保障方案 | 已完成 |
| 17 | gstack工程大脑集成方案 | 已完成 |
| 18 | v2.0架构评审报告 | 已完成 |
| 19 | v2.1超级详细使用指南 | 已完成 |
| 20 | baoyu-skills集成方案 | 已完成 |
| 21 | 内容运营专家Agent集成方案 | 已完成 |
| 22 | 架构融合与系统整合方案 | 已完成 |
| 22 | 运营专家8条执行路径设计 | 已完成 |
| 23 | Web_UI设计方案 | 已完成 |
| 24 | 8条核心执行路径 | 已完成 |
| **25** | **Skills与Agent扩展方案** | **本文件-v1.1** |

---

*文档版本: v1.1 | 更新日期: 2026-03-24 | 如有更新请同步修改*
