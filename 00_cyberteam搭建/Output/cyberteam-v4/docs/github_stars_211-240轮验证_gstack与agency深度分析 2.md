# GitHub Stars 第211-240轮验证报告

**验证时间**: 2026-03-27
**验证轮次**: 第211-240轮 (完成80%)
**核心发现**: gstack QA工程流 + agency-agents 180专家体系

---

## 一、gstack - QA-first工程流深度分析

### 1.1 核心哲学：Completeness原则（煮沸湖）

gstack的核心理念是**完整性原则**：
- AI使完整性的边际成本接近零
- "足够好"是错误的直觉，"完整"只需多花几分钟
- 湖是可以煮沸的（模块100%测试、完整功能、所有边缘情况）
- 海洋不是（重写系统、添加依赖、多季度迁移）

**AI工作量压缩比**：
| 任务类型 | 人工团队 | CC+gstack | 压缩 |
|---------|---------|-----------|------|
| 样板/脚手架 | 2天 | 15分钟 | ~100倍 |
| 测试编写 | 1天 | 15分钟 | ~50倍 |
| 功能实现 | 1周 | 30分钟 | ~30倍 |
| Bug修复+回归 | 4小时 | 15分钟 | ~20倍 |

### 1.2 20+ Skills覆盖完整开发周期

```
gstack Skills体系
├── 战略规划
│   ├── office-hours        # YC办公时间——创业诊断
│   ├── plan-ceo-review    # CEO视角计划审查
│   └── plan-eng-review    # 工程视角计划审查
├── 设计
│   ├── design-consultation # 设计系统咨询
│   └── design-review      # 设计审计+修复
├── 开发
│   ├── review             # PR审查
│   ├── investigate        # 系统性调试
│   └── ship               # 部署工作流
├── QA测试
│   ├── qa                 # QA测试+修复循环
│   ├── qa-only            # 仅报告QA（无修复）
│   └── browse             # 无头浏览器QA
├── 文档
│   ├── document-release   # 发布后文档更新
│   └── retro              # 每周回顾
└── 安全
    ├── careful            # 生产操作安全
    ├── freeze            # 编辑限制
    ├── guard             # 最大安全模式
    └── unfreeze          # 解除编辑限制
```

### 1.3 三层测试体系

gstack建立了完整的三层测试体系：

```
第一层：Skill验证（免费，<1s）
├── 静态验证
├── 生成器质量检查
└── browse集成测试

第二层：E2E测试（基于diff，~$3.85/次）
└── 通过 claude -p 的端到端测试

第三层：LLM评判（~$0.15/次）
└── LLM作为裁判评估质量
```

### 1.4 SKILL.md模板生成工作流

**核心规则**：
- SKILL.md从`.tmpl`模板生成，禁止直接编辑
- 更新流程：编辑`.tmpl` → 运行`bun run gen:skill-docs` → 提交
- 平台无关设计：技能不硬编码框架命令

**编写SKILL模板的规则**：
1. 对逻辑和状态使用自然语言，不使用shell变量
2. 不硬编码分支名称，动态检测
3. 每个bash块自包含
4. 用英语表达条件

### 1.5 无头浏览器QA

gstack的`/browse`技能：
- 持久无头Chromium，首次调用自动启动（~3秒）
- 每命令约100-200ms
- 空闲30分钟后自动关闭
- 状态在调用之间保持（cookie、标签页、会话）

---

## 二、agency-agents - 144专家Agent体系

### 2.1 完整部门分类（12个部门）

| 部门 | Agent数量 | 核心领域 |
|------|----------|----------|
| Engineering | 26 | 全栈开发、安全、数据、嵌入式 |
| Design | 8 | UI/UX、品牌、视觉、包容性设计 |
| Marketing | 29+ | 增长、内容、社交媒体 |
| Paid Media | 7 | PPC、程序化广告、追踪测量 |
| Sales | 8 | 外呼、发现、deal策略、提案 |
| Product | 7+ | 产品策略、增长、产品设计 |
| Strategy | 8 | 战略咨询、商业模式、创新 |
| Engineering（细分） | 26 | IoT、FPGA、Feishu、DingTalk |
| Academic | 7 | 论文写作、研究方法 |
| Game Development | 12 | 游戏设计、Unity/Unreal |
| Specialized | 31 | 播客、新闻稿、AI推荐等 |
| Testing | 10+ | E2E、集成、渗透测试 |
| Support | 10+ | 客户成功、技术支持 |

### 2.2 核心Agent示例

**Engineering代表**：
- Frontend Developer - React/Vue/Angular
- Backend Architect - API设计、数据库架构
- AI Engineer - ML模型、部署
- DevOps Automator - CI/CD、基础设施
- Security Engineer - 威胁建模、安全审计
- Database Optimizer - Schema设计、查询优化
- SRE - SLO、可观测性、混沌工程

**Design代表**：
- UI Designer - 视觉设计、组件库
- UX Researcher - 用户测试、行为分析
- Brand Guardian - 品牌标识、一致性
- Whimsy Injector - 趣味元素、微交互

**Marketing代表**：
- Growth Hacker - 病毒循环、快速增长
- Content Creator - 多平台内容
- TikTok Strategist - 短视频算法
- Twitter Engager - 实时互动

---

## 三、agency-agents-zh - 180专家（中国市场专项）

### 3.1 项目规模

| 类型 | 数量 | 说明 |
|------|------|------|
| 总Agent数 | 180 | 包含翻译+原创 |
| 英文翻译 | 135 | 从agency-agents翻译 |
| 中国市场原创 | 45 | ⭐标记 |
| 支持工具 | 11种 | Claude Code/Copilot/Cursor等 |

### 3.2 45个中国市场原创专家（⭐标记）

**工程部中国特色**：
| Agent | 专长 | 适用场景 |
|-------|------|----------|
| 嵌入式Linux驱动工程师 | 内核模块、设备树 | 嵌入式Linux BSP |
| FPGA/ASIC数字设计工程师 | Verilog/SystemVerilog | FPGA开发 |
| IoT方案架构师 | MQTT、边缘计算 | 物联网端到端 |
| 微信小程序开发者 | WXML/WXSS、微信支付 | 微信生态 |
| 飞书集成开发工程师 | 飞书机器人、审批流 | 飞书生态 |
| 钉钉集成开发工程师 | 钉钉机器人、酷应用 | 钉钉生态 |

**营销部中国平台（12个专家）**：
| Agent | 专长 | 适用场景 |
|-------|------|----------|
| 小红书运营⭐ | 种草笔记、爆款内容 | 小红书获客 |
| 抖音策略师⭐ | 短视频策划、直播带货 | 抖音增长 |
| 微信公众号运营⭐ | 公众号内容、社群运营 | 微信生态 |
| B站内容策略师⭐ | UP主运营、弹幕文化 | B站增长 |
| 快手策略师⭐ | 下沉市场、老铁文化 | 快手社区 |
| 百度SEO专家⭐ | 百度优化、百科/知道 | 百度搜索 |
| 私域流量运营师⭐ | 企微SCRM、用户生命周期 | 私域复购 |
| 直播电商主播教练⭐ | 直播话术、千川投放 | 直播带货 |
| 跨境电商运营专家⭐ | Amazon/Shop/Lazada | 跨境全链路 |
| 短视频剪辑指导师⭐ | 剪映/PR/达芬奇 | 剪辑技术 |
| 微信小程序运营 | 小程序推广 | 微信生态 |
| 微博策略师 | 微博热点、超话 | 微博传播 |

### 3.3 多工具支持

支持11种AI编程工具的安装脚本：
```bash
./scripts/install.sh --tool claude-code    # Claude Code
./scripts/install.sh --tool cursor         # Cursor
./scripts/install.sh --tool copilot        # GitHub Copilot
./scripts/install.sh --tool openclaw       # OpenClaw
./scripts/install.sh --tool opencode       # OpenCode
./scripts/install.sh --tool windsurf       # Windsurf
./scripts/install.sh --tool gemini-cli     # Gemini CLI
./scripts/install.sh --tool qwen           # Qwen Code
# ...
```

---

## 四、CYBERTEAM-V4融合建议（第211-240轮）

### 4.1 gstack Skills融合矩阵

| gstack Skill | 融合到CyberTeam | 功能 |
|-------------|----------------|------|
| qa | ENGINE/thinking/qa-skill | QA测试+修复循环 |
| qa-only | ENGINE/thinking/qa-only | 仅报告QA |
| browse | ENGINE/thinking/browser | 无头浏览器 |
| review | ENGINE/review/ | PR审查 |
| investigate | ENGINE/debate/ | 系统调试 |
| ship | CYBERTEAM/ops/ | 部署工作流 |
| office-hours | ENGINE/strategy/ | 战略咨询 |
| plan-ceo-review | ENGINE/strategy/ceo-review | CEO计划审查 |
| plan-eng-review | ENGINE/strategy/eng-review | 工程计划审查 |
| design-review | ENGINE/debate/design | 设计审查 |
| retro | ENGINE/ceo/retrospective | 复盘机制 |

### 4.2 agency-agents-zh融合矩阵

| 中国平台Agent | 融合到CyberTeam | 功能 |
|--------------|----------------|------|
| 小红书运营 | AGENTS/mkt/xiaohongshu | 种草笔记/爆款 |
| 抖音策略师 | AGENTS/mkt/douyin | 短视频/直播 |
| 微信公众号运营 | AGENTS/mkt/wechat | 公众号/社群 |
| B站内容策略师 | AGENTS/mkt/bilibili | UP主/弹幕 |
| 快手策略师 | AGENTS/mkt/kuaishou | 下沉市场 |
| 百度SEO专家 | AGENTS/mkt/baidu-seo | 百度搜索 |
| 私域流量运营师 | AGENTS/ops/private-domain | SCRM/私域 |
| 直播电商主播教练 | AGENTS/ops/livestream | 直播带货 |
| 跨境电商运营 | AGENTS/ops/cross-border | 跨境电商 |
| 微信小程序开发 | AGENTS/tech/wechat-mini | 小程序开发 |
| 飞书集成开发 | AGENTS/tech/feishu | 飞书集成 |
| 钉钉集成开发 | AGENTS/tech/dingtalk | 钉钉集成 |

### 4.3 gstack Completeness原则融入

**煮沸湖原则融入CyberTeam-v4**：

```python
# ENGINE/thinking/completeness.py
class CompletenessPrinciple:
    """
    核心原则：当AI使完整性的边际成本接近零时，总是做完整的事情。

    湖 = 可煮沸的（100%测试、完整功能、所有边缘情况）
    海 = 不可煮沸的（重写系统、多季度迁移）
    """

    def evaluate_task(self, task: Task) -> CompletenessAssessment:
        # 判断任务是"湖"还是"海"
        # 湖：模块级100%覆盖、完整功能、完整错误路径
        # 海：重写系统、向依赖添加功能、多季度迁移
        pass

    def estimate_compression(self, task: Task) -> CompressionRatio:
        # 返回人工vs AI+gstack的时间压缩比
        # 样板: ~100倍
        # 测试: ~50倍
        # 功能: ~30倍
        # Bug修复: ~20倍
        pass
```

---

## 五、验证结论（第211-240轮）

### 5.1 核心发现

1. **gstack QA工程流**: 15k stars证明的完整工程实践
   - Completeness原则是QA-first的核心
   - 20+ Skills覆盖完整开发周期
   - 三层测试体系确保质量

2. **agency-agents 144专家**: 完整的专业Agent体系
   - 12个部门分类覆盖所有领域
   - 每个Agent都有明确的专业定位

3. **agency-agents-zh 45个中国市场原创**: 中国特色专家
   - 覆盖所有主流中国平台
   - 可直接融入CyberTeam运营部

### 5.2 融合价值评估

| 来源 | 融合价值 | 优先级 | 理由 |
|------|----------|--------|------|
| gstack qa/browse | ⭐⭐⭐⭐⭐ | 最高 | 完整的QA体系 |
| gstack completeness原则 | ⭐⭐⭐⭐⭐ | 最高 | 工程质量保障 |
| agency-agents-zh 中国营销 | ⭐⭐⭐⭐⭐ | 最高 | 45个中国平台专家 |
| gstack plan/review Skills | ⭐⭐⭐⭐ | 高 | 战略+工程审查 |
| agency-agents 工程专家 | ⭐⭐⭐⭐ | 高 | 26个工程专家 |

### 5.3 下一步行动（轮次241-270）

1. **ENGINE/heartbeat/**: 实现心跳调度（来自Paperclip）
2. **ENGINE/review/**: 实现制度性审核（来自三省六部）
3. **ENGINE/context/**: 实现分层上下文（来自OpenViking）
4. **gstack Skills**: 开始融合q、browse、review等核心Skills
5. **agency-agents-zh**: 开始融合中国平台专家到AGENTS/mkt/

---

**报告时间**: 2026-03-27
**验证完成度**: 240/300轮 (80%)
**状态**: 进行中 - gstack和agency体系研究完成
