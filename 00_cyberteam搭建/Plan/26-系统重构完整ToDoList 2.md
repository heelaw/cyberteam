# CyberTeam v3 系统重构完整To-Do List

> **版本**: v1.0
> **日期**: 2026-03-24
> **状态**: 执行就绪
> **整合来源**: Plan/22(架构融合) + Plan/23(Web UI) + Plan/24(8条路径) + Plan/25(Skills扩展)

---

## 一、CyberTeam v3 目标总览

### 1.1 硬性指标

| 指标 | 当前 | 目标 | 差距 |
|------|------|------|------|
| **Skills数量** | ~50 | **300+** | +250 |
| **完整执行路径** | 0 | **8条** | +8 |
| **Agent数量** | ~15 | **192+** | +177 |
| **Web UI面板** | 0 | **10个** | +10 |
| **组织架构** | 部门级 | **公司级** | 三省六部 |

### 1.2 融合公式

```
CyberTeam v3 = edict骨架（三省六部制度流程）
             + cyberteam-v2灵魂（思维注入引擎）
             + v2.1运营专家（专业人设资产）
             + 思考天团技能库（100个专家Skills）
             + edict军机处看板（实时可观测）
             + ClawTeam底座（Agent编排）
             + PUA动力引擎（L1-L4压力升级）
             + Goal-Driven循环（目标达成循环）
```

---

## 二、执行阶段总览

| 阶段 | 名称 | 周期 | 核心交付物 |
|------|------|------|-----------|
| **Phase 0** | 基础骨架搭建 | Day 1-5 | 三省六部12个SOUL.md + ClawTeam部署 |
| **Phase 1** | 思维注入融合 | Day 6-14 | thinking_injector集成 + 100思考专家Skills |
| **Phase 2** | 执行路径落地 | Day 15-28 | 8条核心路径全部打通 |
| **Phase 3** | Web UI构建 | Day 29-42 | 军机处看板10面板上线 |
| **Phase 4** | 激励与循环 | Day 43-56 | PUA + Goal-Driven集成 |
| **Phase 5** | 扩展与优化 | Day 57-84 | Skills扩展至300+ |

---

## 三、Phase 0 — 基础骨架搭建（Day 1-5）

### 3.1 目录结构创建

```
cyberteam-v3/
├── agents/                         # Agent人格定义（三省六部）
│   ├── taizi/SOUL.md              # 太子 · 消息分拣
│   ├── zhongshu/SOUL.md           # 中书省 · 规划中枢
│   ├── menxia/SOUL.md             # 门下省 · 审议封驳
│   ├── shangshu/SOUL.md           # 尚书省 · 调度大脑
│   ├── hubu/SOUL.md               # 户部 · 数据资源
│   ├── libu/SOUL.md               # 礼部 · 文档规范
│   ├── bingbu/SOUL.md             # 兵部 · 代码实现
│   ├── xingbu/SOUL.md             # 刑部 · 安全合规
│   ├── gongbu/SOUL.md             # 工部 · 基础设施
│   ├── libu_hr/SOUL.md            # 吏部 · 人事管理
│   └── skills/                     # 各Agent的Skills库
├── engine/                          # 核心引擎（v2资产）
│   ├── thinking_injector.py
│   ├── intent_classifier.py
│   ├── debate_engine.py
│   ├── routing_engine.py
│   ├── dev_qa_engine.py
│   └── quality_gate_engine.py
├── dashboard/                       # 军机处看板
│   ├── dashboard.html
│   ├── server.py
│   └── data/
├── integration/                     # 集成适配器
│   ├── clawteam_adapter.py
│   ├── agency_adapter.py
│   ├── pua_adapter.py
│   └── goal_driver_adapter.py
├── layers/                          # 运营专家层
│   └── experts/
│       ├── content-ops.md
│       ├── strategy.md
│       ├── product.md
│       └── ...
└── config/
    └── cyberteam-v3.toml
```

**To-Do:**
- [ ] `mkdir -p cyberteam-v3/{agents/{taizi,zhongshu,menxia,shangshu,hubu,libu,bingbu,xingbu,gongbu,libu_hr,skills},engine,dashboard/data,integration,layers/experts,config}`
- [ ] 创建 `.claude/settings.local.json` 指向 cyberteam-v3/

### 3.2 12个SOUL.md Agent定义

| Agent ID | SOUL.md | 核心职责 | 思维注入 | 参考来源 |
|----------|---------|----------|----------|---------|
| `taizi` | taizi/SOUL.md | 消息分拣·意图识别 | 闲聊识别+意图分类 | thinking_injector |
| `zhongshu` | zhongshu/SOUL.md | 规划中枢 | 100+思考专家Skills | 思考天团 |
| `menxia` | menxia/SOUL.md | 审议封驳 | 批判+风险+决策思维 | 思考天团 |
| `shangshu` | shangshu/SOUL.md | 调度协调 | 管理+变革+冲突思维 | 思考天团 |
| `hubu` | hubu/SOUL.md | 数据分析 | 数据+增长+财务思维 | 思考天团 |
| `libu` | libu/SOUL.md | 文档规范 | 内容+品牌+传播思维 | 思考天团 |
| `bingbu` | bingbu/SOUL.md | 代码实现 | 工程+架构+安全思维 | 思考天团 |
| `xingbu` | xingbu/SOUL.md | 安全合规 | 安全+合规+审计思维 | 思考天团 |
| `gongbu` | gongbu/SOUL.md | 基础设施 | DevOps+云+自动化思维 | 思考天团 |
| `libu_hr` | libu_hr/SOUL.md | 人事管理 | 培训+组织+领导思维 | 思考天团 |
| (执行Agent) | 执行层Agents | 技能执行 | 各领域专项Skills | agency-agents |
| (专家Agent) | 专家层Agents | 专业领域 | 100个思考专家Skills | 思考天团 |

**To-Do:**
- [ ] 创建 `taizi/SOUL.md` — 太子消息分拣（含意图分类）
- [ ] 创建 `zhongshu/SOUL.md` — 中书省规划中枢（含思维注入触发）
- [ ] 创建 `menxia/SOUL.md` — 门下省审议封驳（含质量门控）
- [ ] 创建 `shangshu/SOUL.md` — 尚书省调度大脑（含ClawTeam集成）
- [ ] 创建 `hubu/SOUL.md` — 户部数据分析
- [ ] 创建 `libu/SOUL.md` — 礼部文档规范
- [ ] 创建 `bingbu/SOUL.md` — 兵部代码实现
- [ ] 创建 `xingbu/SOUL.md` — 刑部安全合规
- [ ] 创建 `gongbu/SOUL.md` — 工部基础设施
- [ ] 创建 `libu_hr/SOUL.md` — 吏部人事管理

### 3.3 ClawTeam团队配置

```bash
# 创建CyberTeam v3团队
clawteam team create cyberteam-v3 -d "CyberTeam v3 三省六部系统"

# 创建管理团队任务
clawteam task create cyberteam-v3 "Phase 0: 骨架搭建" --priority high
clawteam task create cyberteam-v3 "Phase 1: 思维注入" --priority high --blocked-by <Phase0-id>
clawteam task create cyberteam-v3 "Phase 2: 执行路径" --priority medium --blocked-by <Phase1-id>
clawteam task create cyberteam-v3 "Phase 3: Web UI" --priority medium --blocked-by <Phase2-id>
clawteam task create cyberteam-v3 "Phase 4: 激励循环" --priority low --blocked-by <Phase3-id>
clawteam task create cyberteam-v3 "Phase 5: 扩展优化" --priority low --blocked-by <Phase4-id>

# Spawn 三省Agent
clawteam spawn --team cyberteam-v3 --agent-name taizi --task "消息分拣"
clawteam spawn --team cyberteam-v3 --agent-name zhongshu --task "规划中枢"
clawteam spawn --team cyberteam-v3 --agent-name menxia --task "审议封驳"
clawteam spawn --team cyberteam-v3 --agent-name shangshu --task "调度协调"

# Spawn 六部Agent
clawteam spawn --team cyberteam-v3 --agent-name hubu --task "数据分析"
clawteam spawn --team cyberteam-v3 --agent-name libu --task "文档规范"
clawteam spawn --team cyberteam-v3 --agent-name bingbu --task "代码实现"
clawteam spawn --team cyberteam-v3 --agent-name xingbu --task "安全合规"
clawteam spawn --team cyberteam-v3 --agent-name gongbu --task "基础设施"
clawteam spawn --team cyberteam-v3 --agent-name libu-hr --task "人事管理"
```

**To-Do:**
- [ ] 安装ClawTeam: `pip install clawteam`
- [ ] 创建 cyberteam-v3 团队
- [ ] 创建6个Phase任务并设置依赖链
- [ ] Spawn 10个部门Agent
- [ ] 验证三省六部流程跑通

### 3.4 Phase 0 验收标准

- [ ] 10个SOUL.md全部创建且符合规范
- [ ] ClawTeam团队部署成功，10个Agent正常运行
- [ ] 太子能正确分拣消息（旨意 vs 闲聊）
- [ ] 旨意能流转：中书省→门下省→尚书省→六部
- [ ] 奏折能回报：六部→尚书省→皇上

---

## 四、Phase 1 — 思维注入融合（Day 6-14）

### 4.1 thinking_injector集成

**从 `Plan/cyberteam-v2/engine/thinking_injector.py` 迁移到 `cyberteam-v3/engine/`**

| 组件 | 来源 | 迁移到 | 状态 |
|------|------|--------|------|
| `IntentClassifier` | v2 engine | engine/intent_classifier.py | 待迁移 |
| `ThinkingLibrary` | v2 engine | engine/thinking_library.py | 待迁移 |
| `ThinkingInjector` | v2 engine | engine/thinking_injector.py | 待迁移 |
| `CEOThinkingEngine` | v2 engine | engine/ceo_thinking_engine.py | 待迁移 |

**To-Do:**
- [ ] 迁移 `thinking_injector.py` 到 cyberteam-v3/engine/
- [ ] 迁移 `routing_engine.py` 到 engine/
- [ ] 迁移 `dev_qa_engine.py` 到 engine/
- [ ] 迁移 `quality_gate_engine.py` 到 engine/
- [ ] 创建中书省思维注入配置 `agents/zhongshu/thinking_config.yaml`
- [ ] 创建门下省思维注入配置 `agents/menxia/thinking_config.yaml`
- [ ] 单元测试：验证5W1H1Y自动触发

### 4.2 100个思考专家Skills库

**从 `思考天团agents/` 提取并分类到各Agent的 `skills/` 目录**

| 分类 | 数量 | 注入到 | 触发关键词示例 |
|------|------|--------|---------------|
| 战略分析类 | 15 | 中书省 | SWOT, Porter, BCG, PEST |
| 决策评估类 | 15 | 门下省 | Kahneman, 贝叶斯, 博弈论 |
| 创新思维类 | 15 | 中书省 | 第一性原理, 逆向思维, TRIZ |
| 管理变革类 | 15 | 尚书省 | Kotter, McKinsey7S, OKR |
| 执行落地类 | 15 | 六部 | WBS, PDCA, GROW |
| 专业领域类 | 25 | 六部专业 | 财务/法律/HR/技术等 |

**To-Do:**
- [ ] 提取100个思考天团AGENT.md的核心方法论
- [ ] 创建 `agents/skills/` 目录结构
- [ ] 按领域分类100个思考专家Skills
- [ ] 为每个Skill创建触发关键词索引 `skills/index.yaml`
- [ ] 创建 `agents/zhongshu/skill_dispatch.yaml` 调度规则
- [ ] 验证：中书省规划时自动注入相关思维专家

### 4.3 运营专家层融合

**将 `v2.1运营专家（8个）` + `content-ops.md` 注入到对应部门**

| 运营专家 | 注入部门 | 职责 |
|---------|---------|------|
| 模拟投资人Agent | 户部 | 财务评估+投资视角 |
| 策略执行Agent | 尚书省 | 杠杆破局点+执行路径 |
| 用户激励Agent | 户部 | 留存诊断+激励体系 |
| 框架思维Agent | 中书省 | 自上而下+自下而上框架 |
| 局部工作规划Agent | 尚书省 | 目标拆解+行动计划 |
| 活动运营进阶Agent | 礼部 | 活动策划+九大驱动力 |
| 新媒体进阶Agent | 礼部 | 选题+调性+短文案 |
| 团队管理Agent | 吏部 | 管理工具+1on1 |
| **content-ops专家** | 礼部 | 17个baoyu-skills全流程 |

**To-Do:**
- [ ] 迁移 `content-ops.md` 到 `layers/experts/content-ops.md`
- [ ] 迁移8个运营专家Agent定义到 `layers/experts/`
- [ ] 在对应部门SOUL.md中添加专家调度规则
- [ ] 验证：baoyu-skills能通过内容运营专家正确调用

### 4.4 agency_adapter扩展

**将 `agency_adapter.py` 中的180+AgencyAgent映射到六部执行层**

**To-Do:**
- [ ] 扩展 `integration/agency_adapter.py` 到192个Agent
- [ ] 创建 `config/agent_registry.yaml` 完整Agent注册表
- [ ] 按部门分类：工程46/设计7/营销20+/产品10+/HR10+/财务8/法律5/销售10+/专业25
- [ ] 创建部门→Agent路由映射 `config/department_routing.yaml`
- [ ] 验证：尚书省能正确派发任务到对应部门Agent

### 4.5 Phase 1 验收标准

- [ ] thinking_injector集成到engine/且测试通过
- [ ] 100个思考专家Skills全部可用
- [ ] 8条执行路径全部打通端到端
- [ ] agency_adapter支持192个Agent查询
- [ ] 运营专家层正确注入到对应部门

---

## 五、Phase 2 — 执行路径落地（Day 15-28）

### 5.1 8条核心执行路径实现

| 路径 | 用户场景 | 主责部门 | 关键Skills | 闭环验证 |
|------|---------|---------|-----------|---------|
| **路径1** | "帮我增长下个月营业指标" | 户部+策略执行 | 增长公式拆解+baoyu-*(7个) | 月底GMV对比 |
| **路径2** | "帮我分析竞品并发布小红书" | 礼部+content-ops | url-to-md+xhs-images(5个) | 笔记互动数据 |
| **路径3** | "帮我分析YouTube并写公众号" | content-ops | youtube-transcript+wechat(10个) | 公众号阅读量 |
| **路径4** | "帮我做品牌升级方案" | 礼部+设计部 | comic+slide-deck(9个) | 各平台发布状态 |
| **路径5** | "帮我设计一个产品发布" | 产品部+礼部 | image-gen+xhs+weibo(15个) | 发布日集中度 |
| **路径6** | "帮我制定用户增长方案" | 户部+活动运营 | 激励体系+baoyu-*(13个) | 新增用户数 |
| **路径7** | "帮我做年度财务规划" | 户部+投资人 | 财务分析+infographic(11个) | 预测偏差<20% |
| **路径8** | "帮我招聘一个技术团队" | 吏部+content-ops | JD生成+多平台发布(14个) | 入职完成率 |

**To-Do:**
- [ ] **路径1**: 创建 `paths/revenue-growth/path.yaml` + 全链路执行脚本
- [ ] **路径2**: 创建 `paths/competitor-analysis/path.yaml` + 全链路执行脚本
- [ ] **路径3**: 创建 `paths/youtube-wechat/path.yaml` + 全链路执行脚本
- [ ] **路径4**: 创建 `paths/brand-upgrade/path.yaml` + 全链路执行脚本
- [ ] **路径5**: 创建 `paths/product-launch/path.yaml` + 全链路执行脚本
- [ ] **路径6**: 创建 `paths/user-growth/path.yaml` + 全链路执行脚本
- [ ] **路径7**: 创建 `paths/financial-planning/path.yaml` + 全链路执行脚本
- [ ] **路径8**: 创建 `paths/tech-recruitment/path.yaml` + 全链路执行脚本
- [ ] 创建 `paths/path_registry.yaml` — 8条路径注册表
- [ ] 创建 `paths/trigger_keywords.yaml` — 触发词→路径映射

### 5.2 路径执行引擎

```python
# engine/path_executor.py
class PathExecutor:
    def __init__(self):
        self.path_registry = PathRegistry()
        self.thinking_injector = ThinkingInjector()
        self.clawteam = ClawTeamAdapter()
        self.quality_gate = QualityGateEngine()

    def execute_path(self, user_goal: str) -> ExecutionResult:
        # 1. 触发词匹配 → 选择路径
        path = self.path_registry.match(user_goal)

        # 2. CEO解析 → 5W1H1Y + MECE
        ctx = self.thinking_injector.process(user_goal)

        # 3. 部门分配 → 尚书省派发
        departments = self.assign_departments(path, ctx)

        # 4. Skills调用序列 → 并行/串行执行
        results = self.execute_skills(path.steps)

        # 5. 交付物生成 → 礼部归档
        deliverables = self.generate_deliverables(results)

        # 6. 闭环验证 → 质量门控
        verification = self.quality_gate.evaluate(deliverables, path.criteria)

        return ExecutionResult(
            path=path,
            deliverables=deliverables,
            verification=verification,
            status="done" if verification.passed else "needs_revision"
        )
```

**To-Do:**
- [ ] 创建 `engine/path_executor.py` — 路径执行引擎
- [ ] 创建 `engine/path_registry.py` — 路径注册与匹配
- [ ] 创建 `engine/deliverable_generator.py` — 交付物生成器
- [ ] 创建 `engine/verification_engine.py` — 闭环验证引擎
- [ ] 集成到 `launcher.py` — `--path` 参数支持

### 5.3 示例：路径1完整执行流

```
用户: "帮我增长下个月营业指标"
    ↓
太子: 检测到旨意关键词（增长/营业指标）
    ↓
中书省: 5W1H1Y拆解 + MECE分类
    → 营业指标 = 流量 × 转化率 × 客单价 × 复购率
    → 激活框架思维Agent + 策略执行Agent
    ↓
门下省: 质量审核
    → 增长公式合理性检查
    → 封驳（最多3次）
    ↓
尚书省: 派发任务
    → 户部: 数据分析 + baoyu-infographic
    → 礼部: baoyu-xhs-images + baoyu-post-to-weibo
    → 策略执行Agent: 杠杆破局点识别
    ↓
六部并行执行:
    → hubu: /baoyu-infographic 运营数据.md
    → libu: /baoyu-xhs-images 增长内容.md --publish
    → bingbu: (如需技术实现)
    ↓
奏折回报 → 尚书省汇总 → 回奏皇上
    ↓
闭环验证:
    → 月底GMV数据对比 ≥ 目标增长%?
    → 如未达标 → 尚书省重新派发（Goal-Driven循环）
```

**To-Do:**
- [ ] 端到端测试路径1（用真实数据跑通）
- [ ] 端到端测试路径2-8
- [ ] PUA压力升级集成（失败2次→L1，3次→L2...）

### 5.4 Phase 2 验收标准

- [ ] 8条路径全部端到端测试通过
- [ ] 触发词匹配准确率 ≥90%
- [ ] 交付物生成完整率 100%
- [ ] 闭环验证标准全部可量化
- [ ] PUA压力升级正确触发

---

## 六、Phase 3 — Web UI构建（Day 29-42）

### 6.1 技术栈

| 层级 | 技术选择 | 理由 |
|------|---------|------|
| **前端** | 单文件HTML+CSS+JS | 零依赖，参考edict |
| **后端** | Python stdlib | 零依赖，参考edict server.py |
| **数据** | JSON文件+文件锁 | 简单可靠 |
| **实时** | 轮询(5s) | 低资源占用 |

**To-Do:**
- [ ] 创建 `dashboard/dashboard.html` 骨架（~500行）
- [ ] 创建 `dashboard/server.py` API框架（~300行）
- [ ] 创建 `dashboard/data/` JSON存储目录

### 6.2 10个面板实现

| # | 面板 | 组件 | 优先级 | 工作量 |
|---|------|------|--------|--------|
| 1 | CEO指令台 | EdictInput + 目标分解 | P0 | 4h |
| 2 | 军机处看板 | TaskPipeline + HeartbeatBadge | P0 | 4h |
| 3 | 思维专家库 | SkillGrid + 分类筛选 | P1 | 3h |
| 4 | 执行监控 | GoalProgress + SubAgent矩阵 | P1 | 4h |
| 5 | PUA压力面板 | PressureGauge + 5步法进度 | P2 | 3h |
| 6 | 内容工作流 | PublishFlow + 平台状态 | P2 | 4h |
| 7 | 奏折阁 | ArchiveList + Timeline | P2 | 3h |
| 8 | 专家会诊 | DiscussionBoard + 投票机制 | P3 | 5h |
| 9 | 模型配置 | ModelSwitcher + 成本趋势 | P3 | 2h |
| 10 | 天下要闻 | NewsCard + 分类订阅 | P3 | 3h |

**To-Do:**
- [ ] 实现 Tab导航组件（10个Tab切换）
- [ ] 实现 **CEO指令台** — 旨意输入+分解+下发
- [ ] 实现 **军机处看板** — 任务Pipeline+心跳+省部过滤
- [ ] 实现 **思维专家库** — 300+Skills可视化+搜索
- [ ] 实现 **执行监控** — Goal-Driven进度条+Agent矩阵
- [ ] 实现 **PUA压力面板** — L1-L4等级+5步法进度
- [ ] 实现 **内容工作流** — baoyu-skills发布流程图+平台状态
- [ ] 实现 **奏折阁** — 归档列表+五阶段时间线+导出
- [ ] 实现 **专家会诊** — 多专家讨论+投票+@引用
- [ ] 实现 **模型配置** — Agent模型切换+Token统计+成本趋势
- [ ] 实现 **天下要闻** — 资讯卡片流+订阅管理+摘要

### 6.3 API端点实现

| 方法 | 路径 | 功能 | 实现 |
|------|------|------|------|
| `GET` | `/api/live-status` | 全系统实时状态 | server.py |
| `GET` | `/api/edicts` | 获取所有旨意 | server.py |
| `POST` | `/api/edicts` | 创建新旨意 | server.py |
| `GET` | `/api/tasks` | 获取任务列表 | server.py |
| `POST` | `/api/tasks/{id}/action` | 任务操作 | server.py |
| `GET` | `/api/skills` | 获取Skills库 | server.py |
| `GET` | `/api/goal-status` | Goal-Driven状态 | server.py |
| `GET` | `/api/pua-status` | PUA动力状态 | server.py |
| `GET` | `/api/archives` | 获取归档列表 | server.py |
| `POST` | `/api/discussion` | 专家会诊消息 | server.py |
| `GET` | `/api/model-config` | 模型配置 | server.py |
| `POST` | `/api/model-config` | 更新模型配置 | server.py |

**To-Do:**
- [ ] 实现 `/api/live-status` — 全系统实时状态
- [ ] 实现 `/api/edicts` — 旨意CRUD
- [ ] 实现 `/api/tasks` — 任务CRUD + 操作
- [ ] 实现 `/api/skills` — Skills库查询
- [ ] 实现 `/api/goal-status` — Goal循环状态
- [ ] 实现 `/api/pua-status` — PUA压力状态
- [ ] 实现 `/api/archives` — 归档查询
- [ ] 实现 `/api/discussion` — 专家会诊
- [ ] 实现 `/api/model-config` — 模型配置CRUD

### 6.4 Phase 3 验收标准

- [ ] dashboard.html可独立在浏览器打开
- [ ] server.py零外部依赖启动成功
- [ ] 10个面板全部可交互
- [ ] API端点全部返回正确JSON
- [ ] Tab切换流畅，无闪烁
- [ ] 深色主题符合军机处风格

---

## 七、Phase 4 — 激励与循环（Day 43-56）

### 7.1 PUA动力引擎集成

**从 `v2 integration/pua_adapter.py` 集成L1-L4压力升级**

```python
# integration/pua_adapter.py 增强
class PUAIntegration:
    def __init__(self):
        self.flavors = {
            "alibaba": AlibabaFlavor(),
            "bytedance": ByteDanceFlavor(),
            "huawei": HuaweiFlavor(),
            # ...
        }

    def escalate(self, agent_id: str, failure_context: dict) -> PUAResult:
        """失败时自动升级压力"""
        level = failure_context.get("level", 0)

        if level == 1:
            return self.flavor.l1_gentle_disappointment()
        elif level == 2:
            return self.flavor.l2_soul_拷问()
        elif level == 3:
            return self.flavor.l3_361考核()
        elif level >= 4:
            return self.flavor.l4_graduation_warning()
```

**To-Do:**
- [ ] 迁移 `integration/pua_adapter.py` 到 cyberteam-v3/
- [ ] 创建 `integration/pua_adapter.py` — PUA集成适配器
- [ ] 在尚书省调度逻辑中集成PUA触发
- [ ] 实现失败计数持久化（context compaction时保存）
- [ ] 创建PUA压力面板数据接口 `/api/pua-status`
- [ ] 端到端测试：失败2次→L1升级，失败3次→L2升级

### 7.2 Goal-Driven循环集成

**从 `v2 integration/goal_driver_adapter.py` 集成Master循环**

```python
# integration/goal_driver_adapter.py
class GoalDriverAdapter:
    def __init__(self):
        self.master_loop = MasterAgent()
        self.checkpoint_recovery = CheckpointRecovery()

    def execute_until_goal(self, goal: Goal, criteria: list[Criteria]) -> LoopResult:
        """Goal-Driven循环：直到目标达成才停止"""
        iteration = 0
        max_iterations = 10

        while iteration < max_iterations:
            # 1. 执行当前计划
            results = self.execute_plan(goal)

            # 2. 验证标准达成
            criteria_status = self.verify_criteria(results, criteria)

            # 3. 如果全部达成 → 闭环
            if all(criteria_status.values()):
                return LoopResult(status="success", iterations=iteration, results=results)

            # 4. 如果未达成 → 重新规划
            gap_analysis = self.analyze_gap(results, criteria)
            refined_plan = self.refine_plan(goal, gap_analysis)

            # 5. PUA压力升级（如果循环次数过多）
            if iteration > 2:
                pua.escalate("master", {"level": iteration - 2})

            iteration += 1

        return LoopResult(status="max_iterations", iterations=iteration, results=results)
```

**To-Do:**
- [ ] 迁移 `integration/goal_driver_adapter.py` 到 cyberteam-v3/
- [ ] 创建 `integration/goal_driver_adapter.py` — Goal循环适配器
- [ ] 创建 `integration/checkpoint_recovery.py` — 检查点恢复
- [ ] 在尚书省调度逻辑中集成Goal循环
- [ ] 创建执行监控面板数据接口 `/api/goal-status`
- [ ] 端到端测试：目标未达成时自动重新规划

### 7.3 完整循环流程

```
用户目标 → 尚书省派发 → 六部执行
    ↓                      ↓
尚书省汇总 ← 奏折回报 ← 六部回报
    ↓
质量门控验证 → 达标? ─是→ 奏折归档 → 闭环完成 ✅
    ↓ 否
尚书省重新派发 → 六部重新执行（最多10次）
    ↓ 第3次后
触发PUA L1 → L2 → L3 → L4
    ↓ 第10次
尚书省上报皇上 → 皇上决策（调整目标/换方案/终止）
```

**To-Do:**
- [ ] 集成完整循环流程到 `engine/launcher.py`
- [ ] 添加 `--goal-loop` 参数支持
- [ ] 添加 `--pua-mode` 参数支持
- [ ] 端到端测试完整循环流程

### 7.4 Phase 4 验收标准

- [ ] PUA L1-L4正确触发（失败2/3/4/5次）
- [ ] Goal循环正确执行（最多10次）
- [ ] 检查点恢复正常工作（中断后可恢复）
- [ ] PUA压力面板实时显示当前等级
- [ ] 执行监控面板显示循环次数+达成率

---

## 八、Phase 5 — 扩展与优化（Day 57-84）

### 8.1 Skills扩展路线

| 阶段 | 新增Skills | 来源 | 累计 |
|------|-----------|------|------|
| 现有 | ~50个 | gstack+pua | 50 |
| Phase 1 | +100 | 思考天团 | 150 |
| Phase 5A | +50 | agency-agents专业 | 200 |
| Phase 5B | +50 | 垂直行业 | 250 |
| Phase 5C | +50 | 工具型+AI/ML | 300 |

**To-Do:**
- [ ] **5A-市场营销**（35个）: seo, sem, content, social, kol, growth, email, crm...
- [ ] **5A-产品经理**（25个）: roadmap, user-research, aha-moment, pricing, analytics...
- [ ] **5A-HR**（20个）: recruit, onboarding, performance, culture, training...
- [ ] **5A-财务**（20个）: budget, tax, audit, investment, risk...
- [ ] **5A-销售**（20个）: lead-gen, cold-call, demo, negotiation...
- [ ] **5A-法律**（15个）: contract, compliance, privacy, ip...
- [ ] **5B-医疗**（5个）: medical-diagnosis, clinical-trial, drug-interaction...
- [ ] **5B-教育**（5个）: curriculum-design, student-assessment, ed-tech...
- [ ] **5B-金融**（5个）: risk-assessment, credit-scoring, trading...
- [ ] **5B-制造**（5个）: production-planning, quality-control, supply-chain...
- [ ] **5B-零售**（5个）: inventory-management, pricing-optimization...
- [ ] **5C-AI/ML**（15个）: prompt-eng, rag, agentic, evaluation, fine-tune...
- [ ] **5C-工具型**（15个）: data-viz, file-convert, api-test, webhook...
- [ ] 创建 `skills/skill_registry.yaml` — 300+Skills完整注册表
- [ ] 创建 `skills/category_index.yaml` — 按类别索引
- [ ] 更新思维专家库UI面板

### 8.2 朝堂议政增强

**在军机处看板中增加多专家辩论功能**

**To-Do:**
- [ ] 创建 `engine/debate_engine.py` — 多专家辩论引擎
- [ ] 在专家会诊面板中集成辩论功能
- [ ] 支持@引用、投票、结论归档
- [ ] 端到端测试：议题→多专家辩论→结论

### 8.3 功过簿（Agent绩效评分）

**To-Do:**
- [ ] 创建 `engine/performance_tracker.py` — Agent绩效追踪
- [ ] 创建功过簿UI面板
- [ ] 记录每个Agent的交付质量+时效+迭代次数
- [ ] 生成Agent绩效报告

### 8.4 国史馆（知识库检索）

**To-Do:**
- [ ] 创建 `engine/knowledge_base.py` — 知识库索引
- [ ] 归档所有奏折为可检索知识
- [ ] 支持按关键词/时间/类型检索历史案例
- [ ] 为中书省规划提供历史案例参考

### 8.5 Phase 5 验收标准

- [ ] Skills总数 ≥300个
- [ ] Skills注册表完整且可查询
- [ ] 专家辩论功能正常工作
- [ ] Agent绩效评分可追踪
- [ ] 知识库检索准确率 ≥80%

---

## 九、PUA + GoDriven LOOP启动指令

### 9.1 启动命令

```bash
# 进入cyberteam-v3目录
cd /Users/cyberwiz/Documents/01_Project/02_Skill研发/cyberteam搭建/cyberteam-v3

# 启动CyberTeam v3（本地模式，无ClawTeam）
python engine/launcher.py --interactive

# 启动CyberTeam v3（完整模式）
python engine/launcher.py --goal "帮我增长下个月营业指标" --team full

# 启用Goal-Driven循环
python engine/launcher.py --goal "帮我增长下个月营业指标" --goal-loop

# 启用PUA压力模式
python engine/launcher.py --goal "帮我增长下个月营业指标" --pua-mode alibaba

# 同时启用循环+PUA（直到目标达成才停止）
python engine/launcher.py --goal "帮我增长下个月营业指标" --goal-loop --pua-mode alibaba

# 启动Web UI看板
cd dashboard && python server.py

# 测试8条执行路径
python engine/launcher.py --test-paths

# 测试所有引擎
python engine/launcher.py --test-engines

# Dev-QA检查Agent定义
python engine/launcher.py --check taizi
python engine/launcher.py --check zhongshu
```

### 9.2 LOOP循环说明

```
启动LOOP循环后，系统将持续运行：
1. 执行目标分解 → 部门派发 → Skills调用 → 交付物生成
2. 验证闭环标准（质量门控）
3. 如未达标 → 尚书省重新派发（最多10次）
4. 第3次后触发PUA L1 → L4压力升级
5. 第10次后尚书省上报皇上 → 等待决策
6. 皇上决策后 → 继续执行或调整目标
7. 目标达成 → 奏折归档 → 闭环完成 ✅

⚠️ LOOP循环不会自动停止，直到：
- 目标达成（✅）
- 皇上强制终止（手动）
- 达到最大迭代10次 + 皇上确认终止
```

---

## 十、完整To-Do清单汇总

### 核心交付物

| # | 任务 | 阶段 | 优先级 | 状态 |
|---|------|------|--------|------|
| 1 | 创建cyberteam-v3目录结构 | P0 | 🔴 | ⏳ |
| 2 | 创建12个SOUL.md Agent定义 | P0 | 🔴 | ⏳ |
| 3 | ClawTeam团队部署（10个Agent） | P0 | 🔴 | ⏳ |
| 4 | 迁移thinking_injector到engine/ | P1 | 🔴 | ⏳ |
| 5 | 提取100个思考专家Skills | P1 | 🔴 | ⏳ |
| 6 | 融合运营专家层到各部门 | P1 | 🔴 | ⏳ |
| 7 | 扩展agency_adapter到192个Agent | P1 | 🔴 | ⏳ |
| 8 | 实现8条核心执行路径 | P2 | 🔴 | ⏳ |
| 9 | 创建dashboard.html（10面板） | P3 | 🟡 | ⏳ |
| 10 | 创建server.py API后端 | P3 | 🟡 | ⏳ |
| 11 | 集成PUA动力引擎 | P4 | 🟡 | ⏳ |
| 12 | 集成Goal-Driven循环 | P4 | 🟡 | ⏳ |
| 13 | 扩展Skills到300+ | P5 | 🟢 | ⏳ |
| 14 | 实现功过簿+国史馆 | P5 | 🔵 | ⏳ |

### P0阶段详细清单（Day 1-5）

- [ ] `mkdir -p cyberteam-v3/{agents,engine,dashboard/data,integration,layers/experts,config}`
- [ ] 创建 `agents/taizi/SOUL.md`
- [ ] 创建 `agents/zhongshu/SOUL.md`
- [ ] 创建 `agents/menxia/SOUL.md`
- [ ] 创建 `agents/shangshu/SOUL.md`
- [ ] 创建 `agents/hubu/SOUL.md`
- [ ] 创建 `agents/libu/SOUL.md`
- [ ] 创建 `agents/bingbu/SOUL.md`
- [ ] 创建 `agents/xingbu/SOUL.md`
- [ ] 创建 `agents/gongbu/SOUL.md`
- [ ] 创建 `agents/libu_hr/SOUL.md`
- [ ] 安装ClawTeam并创建团队
- [ ] Spawn 10个部门Agent
- [ ] 验证三省六部流程

### P1阶段详细清单（Day 6-14）

- [ ] 迁移thinking_injector.py
- [ ] 迁移routing_engine.py
- [ ] 迁移dev_qa_engine.py
- [ ] 迁移quality_gate_engine.py
- [ ] 提取100个思考专家Skills到skills/
- [ ] 创建skills/index.yaml
- [ ] 创建agents/zhongshu/skill_dispatch.yaml
- [ ] 迁移content-ops.md到layers/experts/
- [ ] 迁移8个运营专家Agent
- [ ] 扩展agency_adapter到192个Agent
- [ ] 创建agent_registry.yaml
- [ ] 创建department_routing.yaml

### P2阶段详细清单（Day 15-28）

- [ ] 创建paths/path_registry.yaml
- [ ] 创建paths/trigger_keywords.yaml
- [ ] 创建paths/revenue-growth/path.yaml
- [ ] 创建paths/competitor-analysis/path.yaml
- [ ] 创建paths/youtube-wechat/path.yaml
- [ ] 创建paths/brand-upgrade/path.yaml
- [ ] 创建paths/product-launch/path.yaml
- [ ] 创建paths/user-growth/path.yaml
- [ ] 创建paths/financial-planning/path.yaml
- [ ] 创建paths/tech-recruitment/path.yaml
- [ ] 创建engine/path_executor.py
- [ ] 创建engine/path_registry.py
- [ ] 创建engine/deliverable_generator.py
- [ ] 创建engine/verification_engine.py
- [ ] 端到端测试8条路径

### P3阶段详细清单（Day 29-42）

- [ ] 创建dashboard/dashboard.html骨架
- [ ] 创建dashboard/server.py
- [ ] 实现Tab导航
- [ ] 实现CEO指令台
- [ ] 实现军机处看板
- [ ] 实现思维专家库
- [ ] 实现执行监控
- [ ] 实现PUA压力面板
- [ ] 实现内容工作流
- [ ] 实现奏折阁
- [ ] 实现专家会诊
- [ ] 实现模型配置
- [ ] 实现天下要闻

### P4阶段详细清单（Day 43-56）

- [ ] 迁移pua_adapter.py
- [ ] 迁移goal_driver_adapter.py
- [ ] 创建checkpoint_recovery.py
- [ ] 集成PUA到尚书省调度
- [ ] 集成Goal循环到尚书省调度
- [ ] 集成完整循环流程
- [ ] 添加--goal-loop参数
- [ ] 添加--pua-mode参数

### P5阶段详细清单（Day 57-84）

- [ ] 扩展市场营销Skills（35个）
- [ ] 扩展产品经理Skills（25个）
- [ ] 扩展HR/F财务/销售/法律Skills（75个）
- [ ] 扩展垂直行业Skills（25个）
- [ ] 扩展AI/ML+工具型Skills（30个）
- [ ] 创建skill_registry.yaml
- [ ] 创建category_index.yaml
- [ ] 创建debate_engine.py
- [ ] 创建performance_tracker.py
- [ ] 创建knowledge_base.py

---

## 十一、关键里程碑

| 里程碑 | 日期 | 交付物 | 验收标准 |
|--------|------|--------|---------|
| **M1** | Day 5 | Phase 0完成 | 12个SOUL.md + ClawTeam运行 |
| **M2** | Day 14 | Phase 1完成 | thinking_injector + 100Skills + 运营专家 |
| **M3** | Day 28 | Phase 2完成 | 8条路径全部打通 |
| **M4** | Day 42 | Phase 3完成 | Web UI 10面板上线 |
| **M5** | Day 56 | Phase 4完成 | PUA + Goal循环集成 |
| **M6** | Day 84 | Phase 5完成 | 300+Skills + 功过簿 + 国史馆 |
| **M_final** | Day 90 | v3.0发布 | 全部验收通过 |

---

## 十二、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| ClawTeam团队不稳定 | 高 | 添加进程监控 + 自动重启 |
| 100个Skills提取耗时 | 中 | 并行处理，分类批量导入 |
| baoyu-skills平台授权过期 | 高 | 添加授权状态检测 + 过期提醒 |
| 多Agent任务冲突 | 中 | 使用worktree隔离 + 依赖链管理 |
| 8条路径触发词重叠 | 低 | 优先级排序 + 最长匹配优先 |
| PUA L4触发后Agent"毕业" | 中 | 保留Agent历史 + 新Agent接管 |

---

*整合完成：Plan/22 + Plan/23 + Plan/24 + Plan/25 → Plan 26*
*版本：v1.0 | 日期：2026-03-24*
