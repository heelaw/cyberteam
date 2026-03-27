# CyberTeam v2.1 — AI 多智能体协作系统

> **一句话交代，整个团队干活。**
> 让 AI 团队像人类团队一样协作。

**版本**: v2.1
**日期**: 2026-03-23
**状态**: 全面交付完成 ✅

---

## 目录

- [核心定位](#核心定位)
- [快速开始](#快速开始)
- [架构设计](#架构设计)
- [Agent 体系](#agent-体系)
- [Skill 体系](#skill-体系)
- [核心引擎](#核心引擎)
- [v2.1 增强模块](#v21-增强模块)
- [使用方法](#使用方法)
- [工作流程](#工作流程)
- [配置说明](#配置说明)
- [扩展指南](#扩展指南)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)

---

## 核心定位

### 问题与解法

| 维度 | 传统方式 | CyberTeam 方式 |
|------|----------|----------------|
| 任务分配 | 人工拆解、人工协调 | 一句话交代，Agent 自动分解 |
| 质量控制 | 人工 Review | Dev-QA 三级质量门控 |
| 执行动力 | 依赖 AI 自觉 | PUA 压力引擎持续驱动 |
| 协作效率 | 串行执行 | 8 大专家 + 6 部门并行 |
| 交付保障 | 无标准 | 验收标准 → 验证 → 闭环 |

### 核心创新

- **Goal-Driven 自主循环**: 不达目标不停止，Agent 自主驱动直到交付
- **PUA 动力引擎**: L0-L4 压力升级，确保每个 Agent 全力以赴
- **Dev-QA 循环引擎**: 证据驱动评分，3 次重试 + 自动升级
- **三级质量门控**: L1 完整性 ≥95% → L2 专业度 ≥80% → L3 可执行性 ≥90%

---

## 快速开始

### Step 0: 安装 CyberTeam CLI

```bash
# 方式1: 使用产品包自带 wrapper (推荐)
cp scripts/cyberteam ~/.local/bin/cyberteam
chmod +x ~/.local/bin/cyberteam

# 方式2: 使用 alias
echo 'alias cyberteam="clawteam"' >> ~/.zshrc
source ~/.zshrc

# 验证安装
cyberteam --version
```

### 方式一：CyberTeam 团队模式（推荐）

```bash
# 1. 创建团队
cyberteam team spawn-team cyberteam-ops -d "CyberTeam v2.1 自主运营"

# 2. Spawn CEO
cyberteam spawn --team cyberteam-ops --agent-name "cyberteam-ceo" \
  --task "使用 CyberTeam v2.1 CEO Agent 定义，一句话交代任务，让整个团队协作完成"

# 3. 查看看板
cyberteam board show cyberteam-ops

# 4. 监控进度
cyberteam board live cyberteam-ops --interval 5
```

### 方式二：直接使用 Agent 定义

```bash
# 1. 部署 Agent 文件
cp -r agents/ ~/.claude/agents/
cp -r skills/ ~/.claude/skills/

# 2. 调用 CEO
/ceo

# 3. 调用专家
/investor-agent
/strategy-agent
/incentive-agent
```

---

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CyberTeam v2.1                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────────────────────────────────────────────┐     │
│   │            Web Dashboard (v2.1 新增)                      │     │
│   │      可视化监控 · 看板视图 · 消息流 · 统计卡片              │     │
│   └─────────────────────────┬───────────────────────────────┘     │
│                             │                                       │
│   ┌─────────────────────────▼───────────────────────────────┐     │
│   │                     CEO (Master)                        │     │
│   │              顶层目标 · 资源调度 · 最终交付              │     │
│   └─────────────────────────┬───────────────────────────────┘     │
│                             │                                     │
│   ┌─────────────────────────▼───────────────────────────────┐     │
│   │  Supervisor Layer + Execution Monitor (v2.1 增强)         │     │
│   │      5min心跳 · 自动重启 · 循环检测 · Mentor干预        │     │
│   └─────────────────────────┬───────────────────────────────┘     │
│                             │                                     │
│              ┌──────────────┼──────────────────┐                   │
│              ▼              ▼                  ▼                   │
│   ┌────────────────┐ ┌────────────┐ ┌─────────────────┐          │
│   │   8 大专家      │ │  6 部门    │ │   3 核心引擎    │          │
│   │                │ │            │ │                 │          │
│   │ 👤 投资人专家   │ │ 📦 产品部  │ │ 🔄 Dev-QA循环  │          │
│   │ 👤 策略专家    │ │ 📦 运营部  │ │ 💪 PUA动力引擎 │          │
│   │ 👤 激励专家    │ │ 🎨 设计部  │ │ 🚦 三级质量门控│          │
│   │ 👤 框架专家    │ │ 💻 开发部  │ │                 │          │
│   │ 👤 规划专家    │ │ 👥 人力部  │ └─────────────────┘          │
│   │ 👤 活动专家    │ │ 💰 财务部  │                          │   │
│   │ 👤 新媒体专家  │ │            │                          │   │
│   │ 👤 团队管理专家│ └────────────┘                          │   │
│   └────────────────┘                                          │   │
│                             │                                 │   │
│   ┌─────────────────────────▼───────────────────────────────┐   │   │
│   │   Goal-Driven Subagent Loop (v2.1 增强)              │   │   │
│   │ 不达目标不停止 · 记忆系统 · 上下文压缩 · 持续迭代      │   │   │
│   └─────────────────────────────────────────────────────────┘   │   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 协作流程

```
用户输入
    │
    ▼
┌───────────┐
│  CEO     │ ← 一句话任务
└─────┬─────┘
      │ 分解目标
      ▼
┌───────────┐  并行  ┌───────────┐  ┌───────────┐
│ 专家 Agent │──────→│ 部门 Agent │──→│ Dev-QA   │
└───────────┘        └───────────┘  └─────┬─────┘
                                          │ 评分
                                          ▼
                                   ┌───────────┐
                                   │  达成?    │
                                   └─────┬─────┘
                                    Y/N      │
                                    │         │ (No)
                                交付      ┌───▼───┐
                                          │ 重试?  │
                                          └───┬───┘
                                              │ 3次
                                              ▼
                                        PUA 升级
```

---

## Agent 体系

### 15 个核心 Agent 总览

#### CEO (Master) × 1

| Agent | 文件 | 核心职责 |
|-------|------|----------|
| **CyberTeam CEO** | `agents/ceo/ceo.md` | 顶层目标设定 · 资源调度 · 最终交付 · PUA 监督 |

#### 8 大运营专家

| Agent | 文件 | 核心职责 |
|-------|------|----------|
| **投资人专家** | `agents/experts/investor-agent.md` | TAM/SAM/SOM 规模分析 · 六维评估框架 |
| **策略专家** | `agents/experts/strategy-agent.md` | 竞争策略 · 市场破局 · 增长飞轮 |
| **激励专家** | `agents/experts/incentive-agent.md` | 用户激励体系 · 增长飞轮 · 留存策略 |
| **框架专家** | `agents/experts/framework-agent.md` | 框架思维 · 问题拆解 · MECE 分析 |
| **规划专家** | `agents/experts/planning-agent.md` | 工作规划 · 里程碑设定 · 进度追踪 |
| **活动专家** | `agents/experts/activity-agent.md` | 活动策划 · 运营日历 · 事件营销 |
| **新媒体专家** | `agents/experts/newmedia-agent.md` | 内容矩阵 · 平台运营 · 短文案写作 |
| **团队管理专家** | `agents/experts/teamwork-agent.md` | 协作流程 · 知识管理 · 效率优化 |

#### 6 个通用部门

| Agent | 文件 | 核心职责 |
|-------|------|----------|
| **产品部** | `agents/departments/product-agent.md` | 需求分析 · PRD 输出 · 优先级排序 |
| **运营部** | `agents/departments/ops-agent.md` | 用户运营 · 内容运营 · 活动运营 |
| **设计部** | `agents/departments/design-agent.md` | UI/UX 设计 · 品牌视觉 · 设计系统 |
| **开发部** | `agents/departments/eng-agent.md` | 技术方案 · 代码实现 · 测试验证 |
| **人力部** | `agents/departments/hr-agent.md` | 招聘 JD · 培训计划 · 绩效评估 |
| **财务部** | `agents/departments/finance-agent.md` | 预算规划 · 成本分析 · ROI 评估 |

#### 10 个中国平台专家（扩展包）

| Agent | 文件 | 核心职责 |
|-------|------|----------|
| **抖音专家** | `agents/china-platforms/douyin-agent.md` | 短视频策略 · 直播运营 · 抖音算法 |
| **小红书专家** | `agents/china-platforms/xiaohongshu-agent.md` | 种草内容 · 博主合作 · KOL 策略 |
| **微信专家** | `agents/china-platforms/wechat-agent.md` | 公众号 · 小程序 · 私域运营 |
| **B站专家** | `agents/china-platforms/bilibili-agent.md` | UP主运营 · B站算法 · 弹幕文化 |
| **百度SEO专家** | `agents/china-platforms/baidu-seo-agent.md` | 百度收录 · 排名优化 · ICP合规 |
| **私域运营专家** | `agents/china-platforms/private-domain-agent.md` | 企业微信 · SCRM · 社群运营 |
| **淘宝专家** | `agents/china-platforms/taobao-agent.md` | 店铺运营 · 直播带货 · 618/双11 |
| **京东专家** | `agents/china-platforms/jd-agent.md` | 自营体系 · 京东物流 · 品质运营 |
| **拼多多专家** | `agents/china-platforms/pinduoduo-agent.md` | 低价策略 · 社交裂变 · 工厂直供 |
| **快手专家** | `agents/china-platforms/kuaishou-agent.md` | 下沉市场 · 老铁文化 · 快手电商 |

---

## Skill 体系

### 59 个配套 Skill 总览

#### 核心引擎 Skill × 4

| Skill | 路径 | 核心功能 |
|-------|------|----------|
| **Dev-QA 循环引擎** | `skills/engines/dev-qa-loop-engine.md` | 证据收集 → 五维评分 → 3次重试 → 自动升级 |
| **PUA 动力引擎** | `skills/engines/pua-power-engine.md` | L0-L4 压力升级 · 阿里/字节/华为等多味道 |
| **三级质量门控** | `skills/engines/quality-gate-system.md` | L1完整性≥95% → L2专业度≥80% → L3可执行性≥90% |
| **引擎说明** | `skills/engines/README.md` | 三大引擎协作原理 |

#### 专家配套 Skill × 30

| 专家 | Skill 数量 | 核心 Skill |
|------|-----------|------------|
| 投资人专家 | 4 | 市场规模分析 · 六维评估 · 投资条款 · 风险评估 |
| 策略专家 | 4 | 竞争分析 · 增长策略 · 市场破局 · 案例拆解 |
| 激励专家 | 4 | 增长飞轮 · 留存策略 · 激励设计 · 用户分层 |
| 框架专家 | 4 | MECE分析 · 金字塔原理 · 框架思维 · 问题树 |
| 规划专家 | 4 | 里程碑设定 · 进度追踪 · 风险预警 · 复盘方法 |
| 活动专家 | 4 | 活动策划 · 运营日历 · 事件营销 · 效果追踪 |
| 新媒体专家 | 4 | 内容矩阵 · 短文案 · 数据分析 · 平台运营 |
| 团队管理专家 | 2 | 协作流程 · 知识管理 |

#### 平台配套 Skill × 26

| 平台 | Skill 数量 |
|------|-----------|
| 抖音 | 3 |
| 小红书 | 3 |
| 微信 | 3 |
| B站 | 2 |
| 百度SEO | 2 |
| 私域运营 | 3 |
| 淘宝/京东/拼多多/快手 | 各2 |

#### 工具类 Skill × 3

| Skill | 路径 | 核心功能 |
|-------|------|----------|
| **端到端测试** | `skills/端到端测试/SKILL.md` | E2E 测试 · Playwright · 覆盖率报告 |
| **测试驱动开发** | `skills/测试驱动开发/SKILL.md` | TDD 工作流 · 红绿重构 · 验收测试 |
| **发布管理** | `skills/发布管理/SKILL.md` | 版本管理 · 灰度发布 · 回滚机制 |

#### 原则与方法论 × 3

| 文件 | 内容 |
|------|------|
| `principals/boil-the-lake.md` | 完整性原则 — AI 时代完整性边际成本接近零 |
| `principals/ethos.md` | 工程伦理 — 搜索优先于构建 |
| `templates/agent-preamble.md` | Agent 标准开头 · 会话追踪 · Gstack 感知 |

---

## 核心引擎

### 1. Dev-QA 循环引擎

```
证据收集 → 五维评分 → 三次重试 → 自动升级
```

**五维评分体系**：

| 维度 | 权重 | 说明 |
|------|------|------|
| 完整性 | 30% | 需求覆盖率，是否遗漏关键点 |
| 专业度 | 25% | 输出质量，是否符合行业标准 |
| 可执行性 | 25% | 方案是否可落地 |
| 创新性 | 10% | 是否有独特洞察 |
| 商业价值 | 10% | 是否创造实际价值 |

**重试机制**：

```
第1次: 温和反馈，要求补充证据
第2次: 明确指出问题，要求重做
第3次: 升级到 PUA 引擎，启动 L2 压力模式
```

### 2. PUA 动力引擎

**五级压力体系**：

| 等级 | 触发条件 | 行为特征 |
|------|----------|----------|
| **L0** | 正常状态 | 高标准 · 主动闭环 · 数据驱动 |
| **L1** | 第2次失败 | 温和失望 · 切换方案 |
| **L2** | 第3次失败 | 灵魂拷问 · 搜索+源码+假设 |
| **L3** | 第4次失败 | 3.25警告 · 7项检查清单 |
| **L4** | 第5次+ | 毕业警告 · 拼命模式 |

**味道体系**：

| 味道 | 关键词 | 适用场景 |
|------|--------|----------|
| 🟠 阿里味 | 底层逻辑 · 顶层设计 · 抓手 · 闭环 | 默认 · 战略规划 |
| 🟡 字节味 | ROI · 追求极致 · Context not Control | 增长黑客 · 数据驱动 |
| 🔴 华为味 | 烧不死的鸟是凤凰 · 自我批判 | 攻坚克难 · 压力测试 |
| 🟢 腾讯味 | 赛马机制 · 小步快跑 | 快速试错 · 产品迭代 |
| 🟣 拼多多味 | 本分 · 拼命不是拼凑 | 降本增效 · 执行力 |

### 3. 三级质量门控

```
Gate 1: 完整性验证 (≥95%)
  └── 所有需求点是否覆盖？关键场景是否包含？
      └── 不通过 → 打回重做

Gate 2: 专业度验证 (≥80%)
  └── 输出是否符合行业标准？术语是否准确？
      └── 不通过 → 打回重做

Gate 3: 可执行性验证 (≥90%)
  └── 方案是否可落地？资源是否充足？
      └── 不通过 → 调整方案
```

---

## 使用方法

### 场景 1: CyberTeam 团队模式（推荐）

```bash
# 启动 CyberTeam 团队
cyberteam launch \
  --template multi-agent \
  --goal "一句话交代任务，让 CyberTeam v2.1 自动分解、协作、交付"

# 查看团队状态
cyberteam board show cyberteam-ops

# 查看任务进度
cyberteam task list cyberteam-ops --status pending

# 监控实时日志
cyberteam board live cyberteam-ops --interval 3

# 发送任务
cyberteam inbox send cyberteam-ops cyberteam-ceo \
  "分析 CyberTeam v2.1 的投资价值，输出报告"
```

### 场景 2: 单个 Agent 调用

```bash
# 调用 CEO
/ceo "使用 CyberTeam 打造一个 AI 产品"

/investor-agent "分析 AI Agent 市场规模"
/strategy-agent "制定增长策略"
/newmedia-agent "规划新媒体内容矩阵"
```

### 场景 3: 集成 gstack Browse

```bash
# 安装 Browse 模块
cd modules/browse
./setup

# 启动持久化浏览器
~/.claude/skills/browse/browse.sh start

# 在工作流中使用
browse goto "https://github.com"
browse screenshot /tmp/screenshot.png
```

---

## v2.1 增强模块

> 基于 PentAGI 竞品分析，新增 4 个核心模块，全面提升 CyberTeam 的记忆、监控、可视化和上下文管理能力。

### 模块总览

| 模块 | 技术栈 | 路径 | 定位 | 行数 |
|------|--------|------|------|------|
| **Memory System** | Go | `modules/memory/` | 长期/工作/经验记忆 | 2,882 |
| **Execution Monitor** | Python | `modules/monitor/` | 循环检测+Mentor干预 | 1,935 |
| **Web Dashboard** | React+TS | `modules/dashboard/` | 可视化监控面板 | 2,237 |
| **Context Compression** | Python | `modules/context/` | 上下文压缩+Token预算 | 2,364 |

### 模块 1: Memory System（记忆系统）

```
用户输入 → Memory Manager → Long-term/Working/Episodic
                                ↓
                         语义搜索 + 经验复用
```

**三大核心组件**：
- **Long-term Memory**：向量存储（pgvector）+ 语义搜索 + Redis 缓存 + Fallback 机制
- **Working Memory**：当前任务上下文 + Agent 状态 + 会话管理
- **Episodic Memory**：历史成功模式 + 模式提取 + 经验复用

**集成方式**：

```python
from modules.memory import MemorySystem

memory = MemorySystem(
    vector_store="pgvector",
    redis_cache=True,
)

# Agent 启动时加载记忆
context = memory.load_context(agent_id="expert-investor")

# 任务完成后存储经验
memory.store_episodic(
    agent_id="expert-investor",
    task_type="market-analysis",
    success_pattern=result,
)
```

### 模块 2: Execution Monitor（执行监控系统）

```
Tool Call → Loop Detector → Mentor Agent → 干预建议
     ↓
Tool Limits Controller
```

**三大核心组件**：
- **Loop Detector**：精确匹配 / 模糊匹配 / 频率分析 / 状态停滞检测
- **Mentor Agent**：根因诊断 + 解决方案建议 + 自动干预 + 人工升级
- **Tool Limits**：全局/Agent/工具三级限制 + 速率限制 + 冷却机制

**集成方式**：

```python
from modules.monitor import ExecutionMonitor

monitor = ExecutionMonitor(
    loop_threshold=5,
    mentor_enabled=True,
)

# 每次工具调用后检测
result = monitor.check(
    agent_id="arch-001",
    tool_name="Read",
    call_sequence=current_sequence,
)

if result.is_loop:
    suggestion = monitor.get_intervention(result)
    print(f"Mentor 建议: {suggestion}")
```

### 模块 3: Web Dashboard（可视化监控面板）

```
┌──────────────┬──────────────┬──────────────┐
│   概览页面    │   看板视图    │  Agent监控   │
├──────────────┼──────────────┼──────────────┤
│   消息流      │   设置页面    │   统计卡片   │
└──────────────┴──────────────┴──────────────┘
```

**技术栈**：React 18 + TypeScript + Vite + Tailwind CSS + Radix UI + Zustand

**启动方式**：

```bash
cd modules/dashboard
npm install
npm run dev
# 访问 http://localhost:5173
```

### 模块 4: Context Compression（上下文压缩系统）

```
对话链 → Chain AST → Section Summarizer
                        ↓
              Token Budget Manager
                        ↓
              5级压缩策略 (none→aggressive)
```

**核心组件**：
- **Conversation Chain AST**：结构化对话链抽象
- **Section Summarizer**：段落压缩（保留关键信息）
- **QA Summarizer**：问答对提取与摘要
- **Token Budget Manager**：实时预算监控 + 自动压缩触发

**集成方式**：

```python
from modules.context import (
    ConversationChain,
    BudgetManager,
    CompressionLevel,
)

chain = ConversationChain(max_tokens=100000)
budget = BudgetManager(chain, warning=0.8, critical=0.95)

# 自动压缩
if budget.should_compress():
    chain.compress(level=CompressionLevel.MEDIUM)
```

### 集成架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    CyberTeam v2.1                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [Web Dashboard] ← HTTP/WebSocket → [Board API]            │
│         ↓                                                   │
│   [Supervisor] ← 状态报告 ← [Execution Monitor]              │
│         ↓              ↑                                    │
│   [Subagent Loop] ← 上下文 ← [Context Compression]           │
│         ↓              ↑                                    │
│   [Agent 协作] ← 记忆搜索 ← [Memory System]                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 快速启用

```bash
# 安装所有模块依赖
pip install redis pgvector  # Memory System
pip install numpy          # Monitor
pip install tiktoken        # Context Compression

# 验证模块
python -c "from modules.memory import MemorySystem; print('memory: OK')"
python -c "from modules.monitor import ExecutionMonitor; print('monitor: OK')"
python -c "from modules.context import ConversationChain; print('context: OK')"

# 启动 Dashboard
cd modules/dashboard && npm install && npm run dev
```

---

## 工作流程

### 标准工作流程

```
1. 任务输入 (用户)
   │
   ▼
2. CEO 接收并分解目标
   │   - 分析任务类型
   │   - 选择合适的专家 Agent
   │   - 设定验收标准
   │
   ▼
3. 专家 Agent 并行执行
   │   - 各自产出专业内容
   │   - 收集证据
   │
   ▼
4. Dev-QA 循环评估
   │   - 五维评分
   │   - 不达标打回重试
   │
   ▼
5. PUA 引擎监督
       - 持续跟踪进度
       - 压力升级（如需）
       - 确保交付
   │
   ▼
6. 质量门控验收
       - L1 完整性
       - L2 专业度
       - L3 可执行性
   │
   ▼
7. 交付
```

### 自主循环模式

```
Goal: 不达目标不停止
 │
 ▼
 ┌─────────────────────────────────────────┐
 │  while (!goalAchieved) {               │
 │    execute()  →  evaluate()  → retry() │
 │    if (stuck) → escalate() → pressure() │
 │  }                                     │
 └─────────────────────────────────────────┘
```

---

## 配置说明

### CyberTeam 团队配置

```yaml
# ~/.clawteam/teams/cyberteam-ops/config.json
# (框架层路径，CyberTeam CLI wrapper 对外统一品牌)
{
  "name": "cyberteam-ops",
  "description": "CyberTeam v2.1 自主运营",
  "leadAgentId": "cyber-lead-001",
  "members": [
    { "name": "cyberteam-ceo", "role": "leader" },
    { "name": "expert-investor", "role": "worker" },
    { "name": "expert-strategy", "role": "worker" },
    { "name": "expert-incentive", "role": "worker" },
    { "name": "expert-framework", "role": "worker" },
    { "name": "expert-planning", "role": "worker" },
    { "name": "expert-activity", "role": "worker" },
    { "name": "expert-newmedia", "role": "worker" },
    { "name": "expert-teamwork", "role": "worker" },
    { "name": "qa-engineer", "role": "supervisor" },
    { "name": "pua-supervisor", "role": "supervisor" }
  ]
}
```

### Agent 路由配置

```yaml
# config/routing.yaml
task_types:
  market_analysis:
    - investor-agent
    - strategy-agent

  content_creation:
    - newmedia-agent
    - design-agent

  technical:
    - eng-agent
    - framework-agent

  operations:
    - activity-agent
    - ops-agent
    - teamwork-agent
```

### PUA 引擎配置

```yaml
# 在 Agent 定义中启用 PUA
pua:
  enabled: true
  default_flavor: "alibaba"
  escalation:
    l1_on_failures: 2
    l2_on_failures: 3
    l3_on_failures: 4
    l4_on_failures: 5
```

---

## 扩展指南

### 扩展 1: 添加新平台 Agent

```bash
# 1. 创建 Agent 定义
cat > agents/china-platforms/your-platform-agent.md << 'EOF'
# Your Platform Agent

## 基本信息
- name: your-platform-agent
- type: china-platform
- version: 1.0

## 核心能力
- 平台特性分析
- 运营策略制定
- 内容规划

## 配套 Skill
- skills/china-platforms/your-platform/*.md
EOF

# 2. 创建配套 Skill
mkdir -p skills/china-platforms/your-platform
cat > skills/china-platforms/your-platform/SKILL.md << 'EOF'
# Your Platform Skill
...
EOF

# 3. 注册到路由配置
# 编辑 config/routing.yaml 添加新平台
```

### 扩展 2: 自定义 PUA 味道

编辑 `skills/engines/pua-power-engine.md` 添加新味道：

```markdown
## 新味道: XX公司味

**关键词**: 关键词1 · 关键词2 · 关键词3

**旁白风格**:
> [🟣 XX味] 旁白内容...

**适用场景**:
- 场景1
- 场景2
```

### 扩展 3: 集成新工具

编辑 `modules/multi-tool-adapter.py` 添加新工具支持：

```python
# 添加新工具适配器
class NewToolAdapter(BaseAdapter):
    name = "new-tool"
    supported_tools = ["tool1", "tool2"]

    def convert(self, tool_call: dict) -> dict:
        # 转换逻辑
        pass
```

### 扩展 4: 启用 v2.1 增强模块

#### 启用 Memory System

在 Agent 初始化时注入记忆能力：

```python
from modules.memory import MemorySystem

memory = MemorySystem(vector_store="pgvector")
agent = spawn_agent(
    name="investor-expert",
    memory=memory,  # 自动注入记忆能力
)
```

#### 启用 Execution Monitor

在 Supervisor 层集成循环检测：

```python
from modules.monitor import ExecutionMonitor

monitor = ExecutionMonitor(
    loop_threshold=3,
    mentor_enabled=True,
)

# 集成到 Supervisor
class EnhancedSupervisor(Supervisor):
    def __init__(self):
        self.monitor = ExecutionMonitor()
        super().__init__()

    def on_tool_call(self, agent_id, tool, args):
        result = self.monitor.check(agent_id, tool, args)
        if result.is_loop:
            self.apply_intervention(result)
```

#### 启用 Context Compression

在长对话中自动压缩上下文：

```python
from modules.context import BudgetManager, CompressionLevel

budget = BudgetManager(chain, warning=0.8, critical=0.95)

# 自动监控
budget.monitor()  # 超出阈值时自动压缩
```

#### 启用 Web Dashboard

```bash
# 启动 Web Dashboard（独立服务）
cd modules/dashboard
npm install
npm run dev
# 配置 cyberteam board serve --port 8080 接入
```

---

## 常见问题

### Q1: Agent 无响应怎么办？

```bash
# 检查 Agent 状态
cyberteam team status cyberteam-ops

# 重启挂起的 Agent
cyberteam spawn --resume --agent-name expert-investor

# 查看日志
cyberteam board log cyberteam-ops --agent expert-investor
```

### Q2: Dev-QA 评分过低？

- 检查输出是否包含**数据证据**
- 确保**关键场景**全覆盖
- 验证术语**专业度**
- 补充**可执行**的方案细节

### Q3: 如何调整 PUA 压力等级？

在 Agent 定义中调整 `pua.escalation` 配置：

```yaml
pua:
  escalation:
    l1_on_failures: 1   # 更敏感
    l2_on_failures: 2
```

### Q4: 如何添加新的 Agent？

1. 在 `agents/` 下创建新 Agent 定义
2. 创建配套 Skill（如需）
3. 注册到 `config/routing.yaml`
4. 重新部署

### Q5: v2.1 新模块需要额外依赖吗？

| 模块 | 依赖 | 安装方式 |
|------|------|----------|
| Memory System | `redis`, `pgvector` | `pip install redis pgvector` |
| Execution Monitor | `numpy` | `pip install numpy` |
| Context Compression | `tiktoken` | `pip install tiktoken` |
| Web Dashboard | Node 16+ | `cd modules/dashboard && npm install` |

### Q6: 如何验证模块是否正常工作？

```bash
# Python 模块
python -c "from modules.memory import MemorySystem; print('Memory: OK')"
python -c "from modules.monitor import ExecutionMonitor; print('Monitor: OK')"
python -c "from modules.context import ConversationChain; print('Context: OK')"

# Web Dashboard
cd modules/dashboard && npm run build && echo "Dashboard: OK"
```

---

## 贡献指南

### 贡献流程

1. **Fork** 本仓库
2. 创建 **Feature Branch** (`feature/your-feature`)
3. 提交 **Agent/Skill 定义**
4. 运行 **Dev-QA 自检**
5. 提交 **Pull Request**

### Agent 定义规范

```markdown
# Agent Name

## 基本信息
- name: agent-name
- type: expert|department|china-platform
- version: 1.0

## 核心能力
- 能力1
- 能力2

## 配套 Skill
- path/to/skill.md

## 验收标准
- 标准1
- 标准2

## 输出格式
- 格式说明
```

### Skill 定义规范

```markdown
# Skill Name

## 基本信息
- name: skill-name
- version: 1.0
- agent: agent-name

## 触发条件
- 条件1

## 执行流程
1. 步骤1
2. 步骤2

## 输出标准
- 标准1
- 标准2
```

---

## 完整目录结构

```
CyberTeam-v2.1/
├── README.md                          ← 本文件
├── agents/
│   ├── ceo/
│   │   └── ceo.md                    ← CEO 总指挥 (v2.1)
│   ├── experts/                       ← 8 大运营专家
│   │   ├── investor-agent.md
│   │   ├── strategy-agent.md
│   │   ├── incentive-agent.md
│   │   ├── framework-agent.md
│   │   ├── planning-agent.md
│   │   ├── activity-agent.md
│   │   ├── newmedia-agent.md
│   │   └── teamwork-agent.md
│   ├── departments/                  ← 6 个通用部门
│   │   ├── product-agent.md
│   │   ├── ops-agent.md
│   │   ├── design-agent.md
│   │   ├── eng-agent.md
│   │   ├── hr-agent.md
│   │   └── finance-agent.md
│   └── china-platforms/              ← 10 个中国平台专家
│       ├── douyin-agent.md
│       ├── xiaohongshu-agent.md
│       ├── wechat-agent.md
│       ├── bilibili-agent.md
│       ├── baidu-seo-agent.md
│       ├── private-domain-agent.md
│       ├── taobao-agent.md
│       ├── jd-agent.md
│       ├── pinduoduo-agent.md
│       └── kuaishou-agent.md
├── skills/
│   ├── engines/                      ← 3 大核心引擎
│   │   ├── dev-qa-loop-engine.md
│   │   ├── pua-power-engine.md
│   │   ├── quality-gate-system.md
│   │   └── README.md
│   ├── china-platforms/              ← 26 个平台 Skill
│   │   ├── douyin/*.md
│   │   ├── xiaohongshu/*.md
│   │   ├── wechat/*.md
│   │   └── ...
│   ├── 端到端测试/
│   │   └── SKILL.md
│   ├── 测试驱动开发/
│   │   └── SKILL.md
│   └── 发布管理/
│       └── SKILL.md
├── scripts/                          ← 集成脚本
│   ├── install.sh
│   ├── agent-converter.py
│   ├── multi-tool-adapter.py
│   ├── workflow-engine.py
│   ├── config-generator.py
│   ├── cyberteam                     ← CyberTeam CLI Wrapper (推荐安装)
│   └── README.md
├── modules/
│   ├── browse/                       ← gstack Browse 模块
│   │   ├── SKILL.md
│   │   ├── browse.sh
│   │   ├── browse-server.py
│   │   └── README.md
│   └── ...
├── principles/                       ← 原则与方法论
│   ├── boil-the-lake.md
│   └── ethos.md
├── templates/
│   └── agent-preamble.md
├── workflows/
│   └── cyberteam-workflow.md
├── config/
│   └── routing.yaml
└── validation/                        ← 验证报告
    ├── investor/
    ├── strategy/
    ├── newmedia/
    └── ...
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| **v2.1** | 2026-03-24 | 四大增强模块：Memory System + Execution Monitor + Web Dashboard + Context Compression（基于 PentAGI 竞品分析） |
| **v2.0** | 2026-03-23 | 全面交付：50 Agent + 59 Skill + 3 引擎 + gstack 集成 |
| **v1.0** | 2026-03-22 | CEO 重构：Goal-Driven + PUA 双引擎 |
| **v1.0** | 2026-03-20 | 初始版本：15 Agent 定义 |

---

## 许可证

MIT License

---

**一句话交代，整个团队干活。**
*让 AI 团队像人类团队一样协作。*

---

*CyberTeam v2.1 | 2026-03-23 | 全面交付完成 ✅*
