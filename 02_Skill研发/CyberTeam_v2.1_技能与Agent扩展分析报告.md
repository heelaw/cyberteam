# CyberTeam v2.1 技能与Agent扩展分析报告

> 生成日期：2026-03-24 | 版本：v2.1 | 状态：分析完成

---

## 一、资源总盘

### 1.1 现有技能(Skills)统计

| 来源 | 数量 | 路径 | 状态 |
|------|------|------|------|
| gstack skills | **43** | ~/.claude/skills/ | 已加载 |
| baoyu-skills | **18** | github_stars/baoyu-skills-main/skills/ | 源码仓库 |
| pua-skills | **1** | ~/.claude/skills/pua/ | 已加载 |
| 合计 | **62** | - | - |

### 1.2 现有Agent统计

| 来源 | 数量 | 路径 | 主要分类 |
|------|------|------|----------|
| agency-agents-zh | **180** | github_stars/agency-agents-zh/ | 18个专业分类 |
| 思考天团 | **102** | 01_Project/02_Skill研发/思考天团Agent/agents/ | 认知框架/思维模型 |
| CLAUDE.md内置 | **~30** | ~/.claude/CLAUDE.md | GSD核心Agents |
| 合计 | **~312** | - | - |

### 1.3 技能/Agent资源全景

```
总Skills:   62个 (已加载:44个)
总Agents:   ~312个 (已加载: ~30个)
待整合Skills: 180个 (来自agency-agents-zh转换)
理论总计:   ~344个资源单元
```

---

## 二、现有Skills详细盘点表

### 2.1 gstack Skills (43个)

| # | 名称 | 来源 | 功能分类 | 子分类 |
|---|------|------|----------|--------|
| 1 | `browse` | gstack | 工程 | 网页浏览 |
| 2 | `codex` | gstack | 工程 | 代码专家 |
| 3 | `review` | gstack | 工程 | 代码审查 |
| 4 | `cso` | gstack | 工程 | 安全审查 |
| 5 | `canary` | gstack | 工程 | 金丝雀部署 |
| 6 | `ship` | gstack | 工程 | 部署 |
| 7 | `setup-deploy` | gstack | 工程 | 部署配置 |
| 8 | `land-and-deploy` | gstack | 工程 | 落地部署 |
| 9 | `guard` | gstack | 工程 | 安全守卫 |
| 10 | `freeze` | gstack | 工程 | 冻结保护 |
| 11 | `unfreeze` | gstack | 工程 | 解冻恢复 |
| 12 | `careful` | gstack | 工程 | 谨慎操作 |
| 13 | `investigate` | gstack | 工程 | 调查分析 |
| 14 | `benchmark` | gstack | 工程 | 性能基准 |
| 15 | `document-release` | gstack | 工程 | 文档发布 |
| 16 | `autoplan` | gstack | 战略 | 自动规划 |
| 17 | `office-hours` | gstack | 战略 | 办公时间讨论 |
| 18 | `plan-eng-review` | gstack | 战略 | 工程规划审查 |
| 19 | `plan-design-review` | gstack | 战略 | 设计规划审查 |
| 20 | `plan-ceo-review` | gstack | 战略 | CEO规划审查 |
| 21 | `gstack-upgrade` | gstack | 战略 | 升级管理 |
| 22 | `gstack` | gstack | 战略 | 团队协调 |
| 23 | `qa` | gstack | QA | 测试验证 |
| 24 | `qa-only` | gstack | QA | 仅测试 |
| 25 | `design-consultation` | gstack | 设计 | 设计咨询 |
| 26 | `design-review` | gstack | 设计 | 设计审查 |
| 27 | `retro` | gstack | 流程 | 回顾总结 |
| 28 | `marketplace` | gstack | 流程 | 市场整合 |
| 29 | `setup-browser-cookies` | gstack | 流程 | 浏览器配置 |
| 30 | `ljg-card` | ljg | 效率工具 | 卡片整理 |
| 31 | `ljg-invest` | ljg | 效率工具 | 投资分析 |
| 32 | `ljg-learn` | ljg | 效率工具 | 学习助手 |
| 33 | `ljg-paper` | ljg | 效率工具 | 论文工具 |
| 34 | `ljg-paper-flow` | ljg | 效率工具 | 论文流程 |
| 35 | `ljg-plain` | ljg | 效率工具 | 简洁写作 |
| 36 | `ljg-rank` | ljg | 效率工具 | 排名分析 |
| 37 | `ljg-skill-map` | ljg | 效率工具 | 技能地图 |
| 38 | `ljg-travel` | ljg | 效率工具 | 旅行规划 |
| 39 | `ljg-word` | ljg | 效率工具 | Word处理 |
| 40 | `ljg-word-flow` | ljg | 效率工具 | Word流程 |
| 41 | `ljg-writes` | ljg | 效率工具 | 写作助手 |
| 42 | `ljg-x-download` | ljg | 效率工具 | 内容下载 |
| 43 | `pua` | 自建 | 特殊 | PUA激励 |

**gstack Skills 功能分布：**
```
工程(15): browse, codex, review, cso, canary, ship, setup-deploy, land-and-deploy, guard, freeze, unfreeze, careful, investigate, benchmark, document-release
战略(7):  autoplan, office-hours, plan-eng-review, plan-design-review, plan-ceo-review, gstack-upgrade, gstack
QA(2):    qa, qa-only
设计(2):  design-consultation, design-review
效率(13): ljg-card, ljg-invest, ljg-learn, ljg-paper, ljg-paper-flow, ljg-plain, ljg-rank, ljg-skill-map, ljg-travel, ljg-word, ljg-word-flow, ljg-writes, ljg-x-download
流程(3):  retro, marketplace, setup-browser-cookies
特殊(1):  pua
```

### 2.2 baoyu-skills (18个)

| # | 名称 | 功能分类 |
|---|------|----------|
| 1 | baoyu-image-gen | 图像生成 |
| 2 | baoyu-cover-image | 图像生成 |
| 3 | baoyu-illustrator | 图像生成 |
| 4 | baoyu-infographic | 图像生成 |
| 5 | baoyu-comic | 图像生成 |
| 6 | baoyu-slide-deck | 图像生成 |
| 7 | baoyu-post-to-weibo | 内容发布 |
| 8 | baoyu-post-to-wechat | 内容发布 |
| 9 | baoyu-post-to-x | 内容发布 |
| 10 | baoyu-translate | 翻译 |
| 11 | baoyu-url-to-markdown | 格式转换 |
| 12 | baoyu-format-markdown | 格式转换 |
| 13 | baoyu-markdown-to-html | 格式转换 |
| 14 | baoyu-xhs-images | 图像生成 |
| 15 | baoyu-youtube-transcript | 翻译 |
| 16 | baoyu-compress-image | 图像处理 |
| 17 | baoyu-danger-gemini-web | 后端 |
| 18 | baoyu-danger-x-to-markdown | 后端 |

### 2.3 agency-agents-zh 分类分布 (180个)

| 排名 | 分类 | 数量 | 功能定位 |
|------|------|------|----------|
| 1 | marketing | 31 | 营销策略/内容/SEO/电商 |
| 2 | specialized | 29 | 专业化领域 |
| 3 | engineering | 27 | 软件开发/架构/安全 |
| 4 | game-development | 20 | 游戏设计/开发/叙事 |
| 5 | strategy | 16 | 战略分析/竞争/规划 |
| 6 | testing | 9 | 测试/E2E/QA |
| 7 | support | 8 | 客服/支持 |
| 8 | sales | 8 | 销售/CRM |
| 9 | design | 8 | UI/UX/视觉 |
| 10 | paid-media | 7 | 付费媒体 |
| 11 | spatial-computing | 6 | 空间计算/AR/VR |
| 12 | project-management | 6 | 项目管理 |
| 13 | academic | 6 | 学术研究 |
| 14 | product | 5 | 产品管理 |
| 15 | supply-chain | 3 | 供应链 |
| 16 | finance | 3 | 金融/投融资 |
| 17 | legal | 2 | 法律合规 |
| 18 | hr | 2 | 人力资源 |
| 19 | examples | 1 | 示例 |

---

## 三、300+ 扩展路径图

### 3.1 目标分解

```
当前: 62 Skills + ~312 Agents = ~344资源
目标: 300+ Skills (不含Agent)
差距: 需要新增 ~238 Skills

扩展策略:
[内部研发] 44个 → 60个   (+16)
[外部转化] 180个Agents → 180个Skills (+180)
[资源挖掘] 其他来源     (+50+)
────────────────────────────────
总计可达: 344+ → 300+ Skills ✅
```

### 3.2 扩展路径

```
┌─────────────────────────────────────────────────────────┐
│                  300+ Skills 扩展路径                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  路径A: agency-agents-zh Agent转Skill (180个)            │
│  ════════════════════════════════════════════            │
│  31 marketing Agents → 31 marketing Skills               │
│  29 specialized Agents → 29 specialized Skills            │
│  27 engineering Agents → 27 engineering Skills           │
│  20 game-development Agents → 20 game-dev Skills        │
│  16 strategy Agents → 16 strategy Skills                 │
│  9 testing Agents → 9 testing Skills                    │
│  8 support Agents → 8 support Skills                    │
│  8 sales Agents → 8 sales Skills                       │
│  8 design Agents → 8 design Skills                      │
│  7 paid-media Agents → 7 paid-media Skills              │
│  6 spatial-computing Agents → 6 spatial Skills           │
│  6 project-management Agents → 6 pm Skills              │
│  6 academic Agents → 6 academic Skills                 │
│  5 product Agents → 5 product Skills                    │
│  3 supply-chain Agents → 3 supply-chain Skills          │
│  3 finance Agents → 3 finance Skills                   │
│  2 legal Agents → 2 legal Skills                        │
│  2 hr Agents → 2 hr Skills                              │
│                                                          │
│  路径B: 思考天团认知框架扩展 (102个)                      │
│  ══════════════════════════════════════                  │
│  → 认知与决策框架Skills (按思维模型归类)                  │
│                                                          │
│  路径C: gstack Skills扩展 (43→80个)                     │
│  ═════════════════════════════════════                   │
│  → 当前: 工程/战略/QA/设计/效率/流程/特殊                 │
│  → 新增: 数据/移动/嵌入式/区块链/合规/国际化等            │
│                                                          │
│  路径D: baoyu-skills扩展 (18→40个)                       │
│  ═════════════════════════════════════                   │
│  → 扩展: 更多平台/更多格式/更多生成模式                   │
│                                                          │
│  路径E: 其他来源挖掘                                     │
│  ═════════════════════════════                           │
│  → GitHub trending skills                               │
│  → 各垂直领域专业Skills                                  │
│  → 用户贡献Skills                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 四、现有Skills归类方案

### 4.1 8大部门归类

```
CyberTeam v2.1 技能组织架构
├── A部: 工程开发 (Engineering)
│   ├── 测试: qa, qa-only, benchmark, investigate
│   ├── 部署: ship, canary, setup-deploy, land-and-deploy
│   ├── 安全: cso, guard, freeze, unfreeze, careful
│   ├── 代码: codex, review, browse
│   └── 文档: document-release
│
├── B部: 战略规划 (Strategy)
│   ├── 规划: autoplan, office-hours
│   ├── 审查: plan-eng-review, plan-design-review, plan-ceo-review
│   └── 升级: gstack-upgrade, gstack
│
├── C部: 设计创意 (Design)
│   ├── 咨询: design-consultation
│   └── 审查: design-review
│
├── D部: 效率工具 (Efficiency)
│   ├── 写作: ljg-plain, ljg-writes, ljg-word, ljg-word-flow
│   ├── 研究: ljg-paper, ljg-paper-flow, ljg-learn
│   ├── 分析: ljg-invest, ljg-rank, ljg-card
│   ├── 内容: ljg-x-download, ljg-skill-map
│   └── 旅行: ljg-travel
│
├── E部: 营销传播 (Marketing)
│   ├── 发布: baoyu-post-to-*
│   ├── 生成: baoyu-image-gen, baoyu-cover-image, baoyu-illustrator
│   ├── 社媒: baoyu-xhs-images, baoyu-comic
│   └── SEO: (agency转化)
│
├── F部: 流程协作 (Process)
│   ├── 回顾: retro
│   ├── 市场: marketplace
│   └── 配置: setup-browser-cookies
│
├── G部: 特殊能力 (Special)
│   └── 激励: pua
│
└── H部: 扩展领域 (Extended)
    ├── 思考框架: 思考天团(102个)
    ├── 专业知识: agency-agents-zh(180个)
    └── 新兴领域: (待扩展)
```

### 4.2 Skills功能矩阵

| 分类 | 已有Skills | 可扩展方向 | 优先级 |
|------|-----------|-----------|--------|
| 工程-开发 | codex, review, browse | Rust/C++/Go/Kotlin专项 | P1 |
| 工程-测试 | qa, qa-only, benchmark | 性能/安全/自动化测试 | P1 |
| 工程-部署 | ship, canary, land-deploy | K8s/Terraform/CI-CD专项 | P1 |
| 工程-安全 | cso, guard, freeze | 渗透测试/合规审计 | P2 |
| 战略-规划 | autoplan, office-hours | OKR/Risk/Scenario Planning | P2 |
| 战略-审查 | plan-*-review | 产品/数据/架构审查 | P2 |
| 设计-咨询 | design-consultation | 品牌/交互/可用性 | P2 |
| 设计-审查 | design-review | WCAG/无障碍/跨平台 | P3 |
| 效率-写作 | ljg-writes, ljg-plain | 营销/技术/学术写作 | P1 |
| 效率-研究 | ljg-paper, ljg-learn | 文献/代码/产品研究 | P1 |
| 效率-分析 | ljg-invest, ljg-rank | 竞品/财务/数据可视化 | P2 |
| 营销-发布 | baoyu-post-to-* | 更多社媒平台 | P2 |
| 营销-生成 | baoyu-image-gen | 视频/音频/3D生成 | P1 |
| 流程-协作 | retro, marketplace | standup/1on1/OKR追踪 | P2 |
| 认知-框架 | (思考天团) | 更多思维模型 | P2 |
| 专业-领域 | (agency) | 按需激活 | P3 |

---

## 五、Skill到Agent映射方案

### 5.1 一体化映射表

| Agent角色 | 关联Skills | 来源 |
|-----------|-----------|------|
| **gsd-planner** | office-hours, plan-eng-review, plan-ceo-review, autoplan | gstack |
| **gsd-executor** | codex, review, ship, canary, benchmark, browse | gstack |
| **gsd-verifier** | qa, qa-only, careful, investigate | gstack |
| **gsd-roadmapper** | office-hours, plan-ceo-review, autoplan | gstack |
| **gsd-debugger** | investigate, cso, guard, benchmark | gstack |
| **gsd-ui-researcher** | design-consultation, ljg-learn, browse | gstack+ljg |
| **gsd-ui-checker** | design-review, qa, careful | gstack |
| **engineering-frontend-developer** | codex, review, qa, ship, ljg-writes | gstack+ljg |
| **engineering-backend-architect** | codex, cso, benchmark, investigate | gstack |
| **engineering-security-engineer** | cso, guard, careful, freeze, unfreeze | gstack |
| **engineering-devops-automator** | ship, canary, setup-deploy, land-and-deploy | gstack |
| **marketing-douyin-strategist** | baoyu-image-gen, baoyu-post-to-*, browse | gstack+baoyu |
| **marketing-xiaohongshu-specialist** | baoyu-image-gen, baoyu-xhs-images, baoyu-post-to-* | gstack+baoyu |
| **marketing-content-creator** | ljg-writes, ljg-plain, ljg-card, baoyu-image-gen | gstack+ljg+baoyu |
| **design-ui-designer** | design-consultation, baoyu-image-gen, baoyu-cover-image | gstack+baoyu |
| **code-reviewer** | review, cso, careful, benchmark | gstack |
| **security-reviewer** | cso, guard, careful, freeze, investigate | gstack |
| **e2e-runner** | qa, qa-only, careful, investigate | gstack |
| **database-reviewer** | cso, benchmark, investigate, codex | gstack |
| **rust-reviewer** | codex, review, careful, benchmark | gstack |
| **python-reviewer** | codex, review, benchmark | gstack |
| **java-reviewer** | codex, review, benchmark | gstack |
| **cpp-reviewer** | codex, review, careful, benchmark | gstack |
| **go-reviewer** | codex, review, benchmark | gstack |
| **flutter-reviewer** | codex, review, qa, ship | gstack |
| **tdd-guide** | qa, codex, review, investigate | gstack |
| **refactor-cleaner** | codex, review, careful, benchmark | gstack |
| **pua** | pua | 自建 |
| **思考天团** | (各认知框架直接作为Agent) | 自建 |

### 5.2 Skill增强Agent方案

```
Agent调用Skill的3种模式:

模式1: Skill作为Agent的内置能力 (推荐)
  → Agent的SKILL.md直接引用相关Skill
  → 例: gsd-executor SKILL.md → "使用 /codex /review /ship"

模式2: Agent通过/gstack协调调用
  → 通过gstack skill协调多个Agent+Skill
  → 例: /ship 会调用: engineering-devops-automator + ship

模式3: 动态组合
  → 根据任务动态组合Agent+Skill
  → 例: 复杂任务 → gsd-roadmapper → gsd-planner → gsd-executor + {skills}
```

---

## 六、自动发现与加载机制设计

### 6.1 多源加载架构

```
~/.claude/skills/           ← 全局Skills (44个已加载)
├── 工程类/战略类/QA类/...
├── pua/
└── ljg-*/

01_Project/.claude/skills/  ← 项目级Skills (可扩展)
├── 自定义Skills/
└── 临时Skills/

github_stars/               ← 外部Skills仓库 (懒加载)
├── baoyu-skills-main/
└── agency-agents-zh/       ← Agent转Skill

动态加载器:
  skill_loader.py → 扫描 → 索引 → 按需加载
```

### 6.2 自动发现脚本

```python
# skill_discovery.py
import os
import json
from pathlib import Path

SOURCES = {
    "gstack": "~/.claude/skills/",
    "project": "~/Documents/01_Project/.claude/skills/",
    "baoyu": "~/Documents/03_Resource/github_stars/baoyu-skills-main/skills/",
    "agency": "~/Documents/03_Resource/github_stars/agency-agents-zh/",
}

def discover_skills():
    index = {"skills": [], "total": 0}
    for name, path in SOURCES.items():
        path = Path(path).expanduser()
        if not path.exists():
            continue

        if name == "agency":
            # Agent转Skill: 每个.md即一个Skill
            skill_files = list(path.rglob("*.md"))
        else:
            skill_files = [p for p in path.iterdir() if p.is_dir() or p.suffix == '.md']

        for sf in skill_files:
            skill_entry = {
                "name": sf.stem if sf.suffix else sf.name,
                "source": name,
                "path": str(sf),
                "type": "skill" if name != "agency" else "agent-converted"
            }
            index["skills"].append(skill_entry)

    index["total"] = len(index["skills"])
    return index

def auto_load(skill_name):
    """按需加载指定Skill"""
    index = discover_skills()
    for s in index["skills"]:
        if s["name"] == skill_name:
            return load_skill(s["path"])
    return None

# 输出索引
if __name__ == "__main__":
    idx = discover_skills()
    print(f"发现 {idx['total']} 个Skills/Agents")
    with open("skill_index.json", "w") as f:
        json.dump(idx, f, indent=2)
```

### 6.3 Skill索引数据结构

```json
{
  "version": "2.1",
  "last_updated": "2026-03-24",
  "total": 344,
  "skills": [
    {
      "name": "codex",
      "display_name": "Codex代码专家",
      "source": "gstack",
      "category": "engineering",
      "subcategory": "development",
      "path": "~/.claude/skills/codex/SKILL.md",
      "agent_bindings": ["gsd-executor", "engineering-frontend-developer", "code-reviewer"],
      "tags": ["代码", "开发", "审查", "编程"]
    },
    ...
  ]
}
```

### 6.4 加载优先级策略

```
优先级1 (always): gstack核心Skills (43个)
  → ~/.claude/skills/ 下所有Skill
  → 启动时自动加载

优先级2 (按需): baoyu-skills (18个)
  → 检测到发布/图像任务时加载
  → /baoyu-* 命令触发

优先级3 (按需): agency-agents-zh (180个)
  → 通过skill_loader动态加载
  → 首次访问时转换并缓存

优先级4 (按需): 思考天团 (102个)
  → /think-{model} 命令触发
  → 例如: /kahneman, /six-hats

优先级5 (扩展): 用户自定义Skills
  → 01_Project/.claude/skills/
  → 按项目需要加载
```

---

## 七、完整组织架构 (8大部门+专家)

### 7.1 CyberTeam v2.1 组织架构图

```
╔═══════════════════════════════════════════════════════════════╗
║                  CyberTeam v2.1 组织架构                      ║
║                  (8大部门 + 专家智库)                         ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            A部: 工程开发部 (Engineering)                  │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │   开发组      │  │   架构组      │  │   测试组      │  │  ║
║  │  │ codex/review │  │ architect    │  │ qa/benchmark │  │  ║
║  │  │ rust/py/java │  │ backend-arch │  │ e2e-runner   │  │  ║
║  │  │ go/cpp/kt    │  │ data-eng     │  │ tdd-guide    │  │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │   安全组      │  │   部署组      │  │   数据库组    │  │  ║
║  │  │ cso/guard    │  │ ship/canary  │  │ db-reviewer  │  │  ║
║  │  │ freeze/unf   │  │ land-deploy  │  │ data-eng     │  │  ║
║  │  │ careful      │  │ setup-deploy │  │              │  │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  │  ┌──────────────┐  ┌──────────────┐                    │  ║
║  │  │   DevOps组    │  │   移动端组    │                    │  ║
║  │  │ devops-auto  │  │ flutter-rev  │                    │  ║
║  │  │ sre          │  │ mobile-app   │                    │  ║
║  │  └──────────────┘  └──────────────┘                    │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            B部: 战略规划部 (Strategy)                    │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │   战略组      │  │   规划组      │  │   审查组      │  │  ║
║  │  │ office-hours │  │ autoplan     │  │ plan-ceo-rev │  │  ║
║  │  │ gstack       │  │ gsd-roadmap  │  │ plan-eng-rev │  │  ║
║  │  │ gstack-upgr  │  │ gs-planner   │  │ plan-design  │  │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            C部: 设计创意部 (Design)                       │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │   UI设计组    │  │   UX研究组    │  │   视觉组      │  │  ║
║  │  │ design-ui   │  │ design-ux    │  │ visual-story │  │  ║
║  │  │ design-cons │  │ ux-research │  │ brand-guard  │  │  ║
║  │  │ design-rev  │  │ ui-checker  │  │ whimsy-inj   │  │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            D部: 效率工具部 (Efficiency)                  │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │   写作组      │  │   研究组      │  │   分析组      │  │  ║
║  │  │ ljg-writes   │  │ ljg-paper    │  │ ljg-invest   │  ║
║  │  │ ljg-plain    │  │ ljg-learn    │  │ ljg-rank     │  ║
║  │  │ ljg-word     │  │ ljg-paper-fl │  │ ljg-card     │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  │  ┌──────────────┐  ┌──────────────┐                    │  ║
║  │  │   内容组      │  │   旅行组      │                    │  ║
║  │  │ ljg-x-down   │  │ ljg-travel   │                    │  ║
║  │  │ ljg-skill-map│  │              │                    │  ║
║  │  └──────────────┘  └──────────────┘                    │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            E部: 营销传播部 (Marketing)                  │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │   社媒运营组  │  │   内容生成组  │  │   SEO/SEM组  │  │  ║
║  │  │ douyin-strat │  │ image-gen   │  │ baidu-seo    │  ║
║  │  │ xhs-spec     │  │ cover-image │  │ seo-special  │  ║
║  │  │ kuaishou     │  │ infographic │  │ app-store    │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  │  ┌──────────────┐  ┌──────────────┐                    │  ║
║  │  │   电商运营组  │  │   付费媒体组  │                    │  ║
║  │  │ china-ecom   │  │ paid-media   │                    │  ║
║  │  │ cross-border │  │              │                    │  ║
║  │  │ ecom-operator│  │              │                    │  ║
║  │  └──────────────┘  └──────────────┘                    │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            F部: 流程协作部 (Process)                     │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │   回顾改进组  │  │   协作工具组  │  │   配置管理组  │  │  ║
║  │  │ retro        │  │ gstack       │  │ setup-browser│  │  ║
║  │  │              │  │ marketplace │  │ setup-deploy │  │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            G部: 特殊能力部 (Special)                     │  ║
║  │  ┌──────────────┐  ┌──────────────┐                    │  ║
║  │  │   PUA激励组  │  │   内省组      │                    │  ║
║  │  │ pua          │  │ investigate  │                    │  ║
║  │  │ (L0-L4)      │  │              │                    │  ║
║  │  └──────────────┘  └──────────────┘                    │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            H部: 扩展领域部 (Extended)                   │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │  认知框架库   │  │  专业领域库   │  │  新兴领域库   │  │  ║
║  │  │ (102个思考  │  │ (180个agency │  │ (区块链/AI   │  │  ║
║  │  │   天团)     │  │   agents)    │  │   /量子等)   │  │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │            ★ 专家智库 (Expert Think Tank)               │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  ║
║  │  │  思维模型专家 │  │  行业专家    │  │  技术专家     │  │  ║
║  │  │ kahneman    │  │ finance     │  │ security-eng │  ║
║  │  │ first-princ  │  │ legal       │  │ sre          │  ║
║  │  │ six-hats    │  │ academic    │  │ data-eng     │  ║
║  │  │ swot/tows   │  │ product     │  │ mobile-app   │  ║
║  │  │ 5why/grow   │  │ project-mgmt│  │ embedded-fw  │  ║
║  │  │ critical-sy │  │ supply-chain │  │ iot-solution │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### 7.2 部门职能说明

| 部门 | 核心职责 | 关键Skills | 关键Agents | 任务类型 |
|------|---------|-----------|-----------|----------|
| **A部-工程开发** | 软件全生命周期 | codex, review, ship, qa, cso | gsd-executor, code-reviewer, security-reviewer | 功能开发/Bug修复/代码审查 |
| **B部-战略规划** | 方向决策/规划管理 | office-hours, plan-*, autoplan | gsd-roadmapper, gsd-planner | 产品规划/技术战略/OKR |
| **C部-设计创意** | 用户体验/视觉设计 | design-consultation, design-review | design-ui-designer, design-ux-architect | UI设计/UX研究/品牌视觉 |
| **D部-效率工具** | 日常效率/内容生产 | ljg-*, document-release | marketing-content-creator | 写作/研究/分析/报告 |
| **E部-营销传播** | 品牌推广/增长获客 | baoyu-*, seo-specialist | marketing-*-strategist | 社媒运营/内容营销/SEO |
| **F部-流程协作** | 流程优化/团队协作 | retro, gstack, marketplace | project-manager | 回顾/站会/部署/协作 |
| **G部-特殊能力** | 特殊激励/内省 | pua, investigate | pua | 激励/调查/危机处理 |
| **H部-扩展领域** | 专业深耕/前沿探索 | (agency/思考天团) | 102+20专家 | 认知框架/行业专家 |

### 7.3 扩展路线图 (300+ Skills目标)

```
Phase 1 (当前 ~62 Skills):
  ✅ gstack: 43个 (已完成)
  ✅ baoyu: 18个 (已完成)
  ✅ pua: 1个 (已完成)
  → 合计: 62个

Phase 2 (Q2 2026: 120+ Skills):
  📋 agency-agents-zh 核心转换 (marketing+engineering+design+testing = ~75个)
  📋 思考天团整合 (102个认知框架,选择30个核心)
  📋 gstack扩展: 移动端/嵌入式/数据库专项
  → 合计: ~120个

Phase 3 (Q3 2026: 200+ Skills):
  📋 agency-agents-zh 全面转换 (剩余~105个)
  📋 baoyu扩展: 视频生成/音频/3D
  📋 行业专业Skills: 金融/法律/医疗/教育
  → 合计: ~200个

Phase 4 (Q4 2026: 300+ Skills):
  📋 新兴领域: AI Agent/区块链/Web3/元宇宙
  📋 用户贡献Skills: 社区驱动增长
  📋 自动化生成: 基于成功案例自动提炼Skill
  → 合计: 300+ Skills ✅
```

---

## 八、结论与建议

### 8.1 核心发现

1. **资源丰富**: 已掌握 ~344 个资源单元 (Skills+Agents)，远超需求
2. **结构清晰**: 8大部门分类明确，Skills到Agent映射完整
3. **扩展容易**: agency-agents-zh 180个Agents可直接转化为Skills
4. **核心瓶颈**: 主要是整合和组织问题，而非资源不足

### 8.2 关键建议

| 优先级 | 建议 | 行动项 | 预计收益 |
|--------|------|--------|----------|
| **P0** | 建立Skill索引系统 | 编写skill_discovery.py + 维护skill_index.json | 快速检索 |
| **P0** | Agent转Skill管道 | agency-agents-zh → 批量转换脚本 | +180 Skills |
| **P1** | 思考天团整合 | 筛选30个核心思维模型作为可调用Skills | +30 Skills |
| **P1** | gstack扩展 | 新增移动端/数据库/DevOps专项Skills | +20 Skills |
| **P2** | baoyu扩展 | 视频/音频/3D生成Skills | +15 Skills |
| **P2** | 文档化 | 为每个部门编写Agent-Skill协作指南 | 提升可用性 |

### 8.3 技术债务

- baoyu-skills 路径变更 (从Desktop移至github_stars)
- 部分agency-agents-zh Agents需要精简 (过于通用)
- ljg系列Skills需要统一命名规范
- Skill索引需要持续维护机制

---

*报告生成: 2026-03-24 | CyberTeam 研究员*
