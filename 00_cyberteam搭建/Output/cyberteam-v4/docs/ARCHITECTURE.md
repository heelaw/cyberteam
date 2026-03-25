# CyberTeam V4 架构文档

> 版本: v4.0.0 | 更新: 2026-03-25

## 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户输入                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        engine/ (核心引擎)                                   │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐              │
│  │   ceo   │   pm   │department│strategy │ debate  │thinking │              │
│  └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘              │
│                                                                            │
│  ceo/          - CEO 路由引擎（L1）                                        │
│  pm/           - 项目管理                                                  │
│  department/   - 部门调度                                                  │
│  strategy/     - 策略设计                                                  │
│  debate/       - 辩论引擎                                                  │
│  thinking/     - 思维注入（94个思维模型）                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      agents/ (角色定义)                                     │
│  ceo/           - CEO 角色                                                 │
│  strategy/      - 策略专家                                                 │
│  pm/            - 项目经理                                                 │
│  department/    - 部门总监                                                 │
│  middle-tier/   - 中台服务                                                 │
│  bg/            - 业务BG                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    cyberteam/ (底层能力)                                     │
│  team/          - 团队管理                                                  │
│  spawn/         - Agent 生成                                                │
│  workspace/     - Git Worktree 隔离                                         │
│  transport/     - 消息传递                                                  │
│  board/         - 看板                                                      │
│  cli/           - 命令行                                                    │
│  mcp/           - MCP 工具                                                 │
│  skills/        - Skills 管理                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        skills/ (扩展工具)                                    │
│  third-party/   - 第三方 Skills                                             │
│    ├── baoyu/       - 宝珠工具集（18个）                                  │
│    ├── gstack/       - 工程技能                                            │
│    ├── superpowers/  - 超级能力                                            │
│    ├── agency/      - Agency Agents                                       │
│    └── pua/         - PUA 激励系统                                        │
│  custom/       - 自定义 Skills                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         中台/ (共享服务)                                    │
│  thinking/      - 思维注入服务                                              │
│  communication/ - 通信协作                                                  │
│  memory/        - 记忆存储                                                  │
│  monitoring/    - 监控                                                      │
│  assets/        - 资产库                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BG业务目录                                             │
│  增长BG/        - 增长业务（营销部、运营部）                                 │
│  产品BG/        - 产品业务（产品部、设计部）                                  │
│  技术BG/        - 技术业务（研发部、架构部）                                  │
│  总经办/        - 综合管理（战略部、法务部、品牌PR）                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 目录结构

```
Output/cyberteam-v4/
├── agents/               # 角色定义
│   ├── ceo/
│   ├── strategy/
│   ├── pm/
│   ├── department/
│   ├── middle-tier/
│   │   ├── thinking/
│   │   ├── communication/
│   │   ├── memory/
│   │   ├── monitoring/
│   │   └── assets/
│   └── bg/
│       ├── growth/
│       ├── product/
│       └── tech/
├── backend/              # API 服务
│   └── app/api/
├── cyberteam/           # 底层能力（来自 ClawTeam）
│   ├── board/
│   ├── cli/
│   ├── mcp/
│   ├── skills/
│   ├── spawn/
│   ├── team/
│   ├── templates/
│   ├── thinking_models/
│   ├── transport/
│   └── workspace/
├── docs/                # 文档
├── engine/              # 核心引擎
│   ├── ceo/
│   ├── debate/
│   ├── department/
│   ├── pm/
│   ├── strategy/
│   └── thinking/
├── frontend/           # 前端
├── skills/             # 扩展工具
│   ├── third-party/
│   └── custom/
├── tests/             # 测试
└── [BG业务目录]        # 业务BG
```

## 核心模块

### 1. engine/ceo - CEO 路由引擎

负责：
- 需求分拣（简单咨询 vs 正式任务）
- 意图识别（8种意图类型）
- 复杂度评估（高/中/低）
- 路由决策（L2/L3A/L3B/L3C/SWARM）
- Swarm 智能编排

### 2. engine/thinking - 思维注入系统

负责：
- 加载 94 个思维模型
- 根据任务特征自动路由选择模型
- 将思维模型注入 Agent 决策

### 3. engine/debate - 辩论引擎

负责：
- 多方案辩论
- 专家意见聚合
- 收敛到最优方案

### 4. engine/strategy - 策略设计

负责：
- 策略三角分析
- MECE 分解
- 执行计划生成

### 5. engine/pm - 项目管理

负责：
- 任务分解
- 进度跟踪
- 结果验收

## 使用示例

### 1. 启动 CyberTeam V4

```python
from engine.ceo.launcher import main

main()
```

### 2. 使用 CEO 路由

```python
from engine import CEORouter

router = CEORouter()
result = router.route("分析用户增长策略，制定Q2季度计划")

print(result.intent)        # 数据分析
print(result.target)        # SWARM
print(result.thinking_models)  # ['类比推理', '风险投资', '生态系统']
```

### 3. 使用思维注入

```python
from engine.thinking import ThinkingInjector, InjectionContext

injector = ThinkingInjector()
injector.load_models()

context = InjectionContext(
    agent_name="PM Agent",
    agent_role="产品管理",
    task="设计用户增长策略"
)

result = injector.inject_auto(context)
print(result.injected_prompt)
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 核心引擎 | Python 3.9+ |
| API 服务 | FastAPI |
| 数据库 | SQLite (async) |
| 消息队列 | 文件系统 (Mailbox) |
| 任务管理 | Task Store (SQLite) |
| Agent 生成 | tmux + Git Worktree |
| 底层框架 | ClawTeam |

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行核心测试
python -m pytest tests/test_core.py -v
```

---

*CyberTeam V4 - 企业级 AI 协作系统*
