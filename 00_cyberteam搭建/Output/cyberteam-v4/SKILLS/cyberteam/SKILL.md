---
name: CyberTeam V4 - 企业级AI协作系统
description: >
  CyberTeam V4 是一个完整的企业级 AI 协作系统，模拟真实公司的组织架构，
  实现多 Agent 并行处理和智能协作。

  当用户需要完成复杂商业任务、需要多部门协作分析、需要进行战略规划、
  需要执行全渠道营销方案、需要进行产品/运营/技术决策时使用此 skill。

  触发场景包括但不限于：
  - "为XX品牌制定营销方案"
  - "分析XX产品的竞争优势"
  - "制定季度OKR"
  - "协调多部门完成项目"
  - "进行市场调研和用户分析"
  - "制定618/双11大促方案"
  - "组建专项团队解决XX问题"
  - "启动专家会议讨论XX"
  - 任何需要 CEO→COO→专家 协作流程的任务

  提供完整的企业 AI 协作能力：问题拆解、策略制定、专家讨论、风险预案、方案汇总。
version: 4.0.0
---

# CyberTeam V4 - 企业级AI协作系统

CyberTeam V4 是独立完整的企业级 AI 协作系统，不依赖任何外部框架。
它模拟真实公司的组织架构，通过 CEO→COO→专家 的协作流程，
实现多 Agent 并行处理和智能决策。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户输入                              │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    👑 CEO（总指挥）                          │
│  • 5W1H1Y 问题拆解                                           │
│  • MECE 分类                                                │
│  • 目标对齐                                                  │
│  • 资源分配                                                  │
│  • 方案审核                                                  │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    🎯 COO（运营总监）                         │
│  • 策略制定                                                  │
│  • 专家协调                                                  │
│  • 风险预案                                                  │
│  • 多轮讨论主持                                              │
│  • 汇总汇报                                                  │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    📋 专家团队（执行层）                      │
│                                                              │
│  增长事业部   │  内容运营   │  电商运营   │  用户研究        │
│  品牌营销     │  数据分析   │  技术架构   │  财务预算        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 核心特性

- **完全独立**：不依赖 ClawTeam 或其他外部框架
- **真实协作**：通过 MailboxManager 实现 Agent 间消息传递
- **流程规范**：CEO→COO→专家 标准协作流程
- **多轮讨论**：支持专家间的多轮迭代讨论
- **风险预案**：自动生成风险评估和保底措施

## 协作流程（强制执行）

### 第一层：CEO→COO 战略对齐

**必须完成的对齐项**：

| 对齐项 | CEO 明确 | COO 确认 |
|--------|----------|----------|
| 北极星指标 | 最终看什么指标？优先级？ | 复述理解 |
| 约束条件 | 预算/时间/渠道/调性/禁止项 | 明确边界 |
| 风险偏好 | 保守/平衡/激进？ | 理解授权范围 |
| 资源配置 | 各渠道预算分配？ | 知道能调动什么 |

### 第二层：COO→专家策略讨论

**策略讨论必须覆盖四大议题**：

| 议题 | 讨论内容 | 专家必须回答 |
|------|----------|--------------|
| 卖点方向 | 提炼与目标用户匹配的卖点 | 用户痛点？主打什么？ |
| 用户场景 | 用户从看到内容到转化经历哪些场景？ | 决策旅程？流失点？ |
| 渠道策略 | 各渠道如何分工定位？ | 小红书/抖音/微信各做什么？ |
| 转化策略 | 如何确保转化？ | 转化路径？优惠设计？ |

### 第三层：专家内部分歧讨论（深度碰撞）

**必须讨论的风险预案内容**：

| 讨论项 | 必须明确 |
|--------|----------|
| 效果预测 | 保守/正常/乐观估计 + 置信度 |
| 风险识别 | 可能有哪些风险？概率和影响？ |
| 保底措施 | 如果效果不好，应该怎么办？（分三层） |
| 预警机制 | 如何判断效果是否达预期？检查节点？ |

### 第四层：COO→CEO 汇报

**汇报必须包含**：

| 汇报项 | 必须包含 |
|--------|----------|
| 策略摘要 | 卖点/渠道/用户/转化 |
| 预期效果 | 保守/正常/乐观 + 置信度 |
| 风险预案 | 主要风险 + 保底措施 |
| 需要授权 | 哪些需要 CEO 拍板？ |
| 请求支持 | 需要 CEO 提供什么支持？ |

## 强制产出文件

| 节点 | 强制产出 | 文件位置 |
|------|----------|----------|
| 1. CEO-COO对齐 | 对齐记录 | `01_Agent会议纪要/对话记录/对话_01_CEO对齐_[日期].md` |
| 2. 策略讨论 | 策略讨论记录 | `01_Agent会议纪要/对话记录/对话_02_策略讨论_[日期].md` |
| 3. 风险预案 | 风险预案记录 | `01_Agent会议纪要/对话记录/对话_03_风险预案_[日期].md` |
| 4. COO汇报 | CEO批准 | `01_Agent会议纪要/对话记录/对话_04_CEO汇报_[日期].md` |
| 5. 设计联动 | 设计任务单 | `02_计划方案/设计任务分发/` |
| 6. 文案产出 | 符合规范的文案 | `03_最终输出/文案产出/` |
| 7. CEO汇总 | 最终报告 | `03_最终输出/汇总方案/` |

## 使用方式

### 通过 CyberTeam CLI

```bash
# 查看团队状态
cyberteam team list

# 创建专项团队
cyberteam team spawn-team <团队名> -d "项目描述"

# 启动专家团队
cyberteam launch <模板> --goal "目标描述"

# 查看看板
cyberteam board show <团队名>

# 查看消息
cyberteam inbox list <团队名>
```

### 通过 Python API

```python
from cyberteam.engine.ceo import CEORouter
from cyberteam.engine.coo import COOCoordinator

# CEO 路由
router = CEORouter()
result = router.route("为XX品牌制定清明节营销方案")

# COO 协调
coordinator = COOCoordinator()
coordinator.receive_ceo_task(result)
```

### 启动多 Agent 团队协作

```bash
# 创建团队
cyberteam team spawn-team ehomewei-qingming -d "清明节营销方案"

# 创建任务
cyberteam task create ehomewei-qingming "策略讨论" -o coo

# Spawn 专家 Agents
cyberteam spawn --team ehomewei-qingming --agent-name douyin-strategist --task "制定抖音渠道策略"
cyberteam spawn --team ehomewei-qingming --agent-name xhs-strategist --task "制定小红书渠道策略"
cyberteam spawn --team ehomewei-qingming --agent-name growth-expert --task "制定增长策略"

# 发送消息给专家
cyberteam inbox send ehomewei-qingming douyin-strategist "开始制定抖音策略"
cyberteam inbox send ehomewei-qingming xhs-strategist "开始制定小红书策略"
```

## 项目目录结构

每个项目必须遵循以下目录结构：

```
Output/cyberteam-v4/projects/{项目名称中文}/
├── 00_项目资料/              # 项目元数据
│   └── metadata.yaml         # 项目信息（必填）
├── 01_Agent会议纪要/          # Agent讨论与决策
│   ├── 总监决策/             # COO/总监的判断和决策
│   ├── 专家讨论/             # 各专家的分析和讨论
│   └── 对话记录/             # Agent间的对话日志
├── 02_计划方案/              # 计划与方案
│   ├── 任务分解/             # 工作任务分解
│   ├── 执行计划/             # 执行步骤
│   └── 方案选项/             # 方案A/B/C
└── 03_最终输出/              # 最终产出
    ├── 文案产出/             # 所有文案物料
    ├── 分析报告/             # 市场/用户分析
    └── 汇总方案/             # 完整方案文档
```

## 命令参考

### Team 命令组

```bash
cyberteam team spawn-team <团队名>          # 创建团队
cyberteam team list                         # 列出所有团队
cyberteam team discover                      # 发现本地团队
cyberteam team status <团队名>               # 查看团队状态
```

### Task 命令组

```bash
cyberteam task create <团队名> <任务描述>    # 创建任务
cyberteam task list <团队名>                 # 列出任务
cyberteam task update <团队名> <任务ID>      # 更新任务状态
```

### Inbox 命令组

```bash
cyberteam inbox send <团队名> <收件人> <消息>  # 发送消息
cyberteam inbox list <团队名>                  # 查看收件箱
cyberteam inbox receive <团队名>               # 接收消息（消费）
cyberteam inbox peek <团队名>                   # 查看消息（不消费）
```

### Board 命令组

```bash
cyberteam board show <团队名>      # 显示看板
cyberteam board overview           # 显示所有团队概览
cyberteam board live <团队名>      # 实时监控
```

## 重要原则

1. **禁止跳过流程**：必须严格遵循 CEO→COO→专家 协作流程
2. **强制多轮讨论**：专家不能直接出方案，必须经过讨论迭代
3. **风险预案必须**：每个方案必须包含风险识别和保底措施
4. **文件归档**：所有产出必须归档到项目目录对应位置
5. **验证诚信**：宁可报告"还没做完"，不能假装完成

## 依赖说明

CyberTeam V4 **完全独立**，不依赖任何外部框架：

| 组件 | 状态 | 说明 |
|------|------|------|
| MailboxManager | ✅ 自有 | 消息传递，完全独立实现 |
| TaskManager | ✅ 自有 | 任务管理，完全独立实现 |
| Transport | ✅ 自有 | 文件传输，完全独立实现 |
| CEO Engine | ✅ 自有 | 问题拆解，完全独立实现 |
| COO Engine | ✅ 自有 | 策略协调，完全独立实现 |

## 安装

```bash
# CyberTeam V4 随项目一起安装
cd Output/cyberteam-v4
pip install -e .

# 验证安装
cyberteam --version
```

## 附加资源

- **`references/cli-reference.md`** — 完整 CLI 命令参考
- **`references/workflows.md`** — 多 Agent 协作工作流
- **`references/architecture.md`** — 系统架构设计文档
