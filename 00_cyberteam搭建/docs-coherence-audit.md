# 文档一致性审查报告

> **审查时间**: 2026-04-01
> **审查范围**: CLAUDE.md, AGENTS.md, SPEC.md, ARCHITECTURE.md, README.md 及相关目录结构
> **审查结论**: 发现 **8大类共23项** 显性不一致，需要立即同步

---

## 一、根级文档定位冲突

### 问题：根目录 `AGENTS.md` 和 `SPEC.md` 内容与 `CLAUDE.md` 不匹配

| 文件 | 实际内容 | 应该是 |
|------|---------|--------|
| `CLAUDE.md` | CyberTeam 项目总览 | ✅ 正确 |
| `AGENTS.md` | CodePilot Desktop 开发规格 | ❌ 与项目名不匹配 |
| `SPEC.md` | CodePilot Desktop 详细设计 | ❌ 与项目名不匹配 |

**根目录这两个文件是 CodePilot Desktop 项目的文档，不属于 CyberTeam**

---

## 二、版本目录引用错误

### 2.1 CLAUDE.md 引用了不存在的版本目录

**CLAUDE.md 第24-26行**:
```markdown
- `Output/cyberteam-v2/` - v2.0.1 fusion version
- `Output/CyberTeam-v2.1/` - v2.1 with 25 Agents + 60 Skills
```

**实际情况**:
```
Output/
├── ANALYSIS/
├── cyberteam-desktop/    # CodePilot Desktop
└── cyberteam-v4/        # 实际只有 v4
```

**不一致**:
- CLAUDE.md 提到 `cyberteam-v2/` 和 `CyberTeam-v2.1/`，但这两个目录不存在
- 实际只有 `cyberteam-v4/` 和 `cyberteam-desktop/`
- 这些是旧版本引用，需要更新

### 2.2 版本命名大小写混用

| 目录名 | 命名风格 |
|--------|---------|
| `cyberteam-v4/` | kebab-case (小写+连字符) |
| `CyberTeam-v2.1/` | PascalCase (大小写混用) |
| `cyberteam-desktop/` | kebab-case |

**建议统一使用 `cyberteam-v4/` 风格**

---

## 三、AGENTS 目录结构三处不一致

### 3.1 根级 `AGENTS/` vs `Output/cyberteam-v4/AGENTS/`

| 根级 AGENTS/ (部门制) | Output/cyberteam-v4/AGENTS/ (职能制) |
|----------------------|-------------------------------------|
| CEO | finance |
| COO | growth |
| PM | middle-tier |
| 产品 | orchestrator |
| 人事 | product |
| 客服 | socratic-questioner |
| 市场 | tech |
| 战略 | (缺) |
| 技术 | (缺) |
| 法务 | (缺) |
| 设计 | (缺) |
| 财务 | (缺) |
| 运营 | (缺) |
| 销售 | (缺) |

**分析**: 根级 AGENTS 是"三省六部"架构，cyberteam-v4 是扁平化职能架构，两者完全不同

### 3.2 AGENTS 与 SKILLS 部门划分不对齐

| AGENTS 部门 | SKILLS 部门 |
|------------|-------------|
| CEO, COO, PM | (无对应) |
| 产品 | product |
| 人事 | hr |
| 市场 | marketing |
| 战略 | (无对应) |
| 技术 | tech |
| 法务 | (无对应) |
| 设计 | (无对应) |
| 财务 | finance |
| 运营 | (无对应，但有 growth) |
| 销售 | (无对应) |

**SKILLS 实际结构**:
```
SKILLS/
├── content/
├── cyberteam/
├── finance/
├── growth/
├── hr/
├── marketing/
├── product/
├── tech/
├── test/
├── third-party/
└── writing/
```

---

## 四、架构描述三层不一致

### 4.1 CLAUDE.md 描述的架构

```
用户输入
    ↓
CEO (总指挥)
    ├── 5W1H1Y 问题拆解
    ├── MECE 分类
    ├── 100+ 思维专家注入
    └── 组建管理团队
    ↓
管理层 (自动思维注入)
战略/产品/技术/设计/运营/财务/市场/人力 总监
    ↓
执行层 (专业技能注入)
40+ 工程专家 / 20+ 设计专家 / 30+ 营销专家
```

### 4.2 SPEC.md 描述的架构

```
用户输入 → CEO路由(L1) → 策略层(L2) → 专家层(L3) → 评分门禁
                ↓
          CyberTeam Agent团队
```

### 4.3 ARCHITECTURE.md 描述的架构

```
ClawTeam (基础层)
    ↓
CyberTeam/engine/ (行业专用)
├── ceo.py      - CEO 路由
├── strategy.py - 策略
├── department.py - 部门
└── debate_engine.py - 辩论
    ↓
Swarm Intelligence (群体智能)
```

**不一致总结**:
| 维度 | CLAUDE.md | SPEC.md | ARCHITECTURE.md |
|------|-----------|---------|-----------------|
| 层数 | 3层 | 4层(含评分门禁) | 2层+Swarm |
| 部门 | 8个总监 | 6个执行部门 | 无部门概念 |
| 专家数 | 100+思维专家 | 14个思维专家+6部门 | 无明确数字 |

---

## 五、质量门禁体系两套标准

### 5.1 SPEC.md (section 5) 定义

| 级别 | 名称 | 通过条件 |
|------|------|----------|
| L0 | 输入校验 | 无错误 |
| L1 | 计划审批 | ≥70分 |
| L2 | 过程检查 | 正常/警告 |
| L3 | 结果评审 | ≥70分 |
| L4 | 交付终审 | ≥75分+中低风险 |

### 5.2 CLAUDE.md 定义

CLAUDE.md 提到"六维评分 + 五级质量门禁"但没有详细说明。

### 5.3 其他文档可能还有定义

需要全面搜索确认是否存在第三套标准。

---

## 六、SkILL 定义位置混乱

### CLAUDE.md 规则四规定

```
Agent 定义 → `Output/cyberteam-v3/agents/{部门}/SOUL.md`
Skill 定义 → `Output/cyberteam-v3/skills/{部门}/SKILL.md`
```

### 实际情况

```
Output/cyberteam-v4/
├── AGENTS/                    # 实际位置 (不是 agents/)
│   ├── finance/
│   ├── growth/
│   ├── product/
│   ├── socratic-questioner/
│   └── tech/
└── SKILLS/                    # 实际位置
    ├── content/
    ├── finance/
    ├── growth/
    └── ...
```

**问题**:
1. 目录名是 `AGENTS` 不是 `agents`
2. 路径是 `v4` 不是 `v3`
3. 部门划分与 CLAUDE.md 不一致

---

## 七、关键信息缺失

### 7.1 CLAUDE.md 未提及 ClawTeam

CLAUDE.md 完全未提及项目基于 ClawTeam 开发，但：
- ARCHITECTURE.md 第3行: "基于 ClawTeam (https://github.com/HKUDS/ClawTeam) 开发"
- README.md 第3行: "基于 ClawTeam 开发"

### 7.2 Sprint 状态不清晰

ARCHITECTURE.md 声称"全部完成":
```
## 十、开发状态 (2026-03-25)
| Phase | 任务 | 状态 |
|-------|------|------|
| **Phase 1-7** | ... | ✅ 全部完成 |
```

但 README.md 显示还在 "Sprint 2 融合进度"。

---

## 八、其他不一致

### 8.1 专家数量

| 文档 | 数量 |
|------|------|
| CLAUDE.md | 100+ 思维专家 |
| SPEC.md | 14个思维专家 + 6个执行部门 |
| ARCHITECTURE.md | 无明确数字 |

### 8.2 路由目标描述

**SPEC.md**:
```
路由目标:
- `L2`: PM + Strategy 协调层
- `L3A`: CyberTeam 部门
- `L3B`: Gstack Skills
- `L3C`: 独立 Agents
- `SWARM`: Swarm 群体智能 (新!)
```

**CLAUDE.md**:
```
路由: CEO → 三层架构
```

---

## 统一口径

### U1: 版本目录

| 正确引用 | 说明 |
|---------|------|
| `Output/cyberteam-v4/` | 当前版本 |
| `Output/cyberteam-desktop/` | CodePilot Desktop |

### U2: AGENTS 目录

统一使用 `Output/cyberteam-v4/AGENTS/`，部门划分以实际为准

### U3: SKILLS 目录

统一使用 `Output/cyberteam-v4/SKILLS/`

### U4: 架构描述

采用 SPEC.md 的 L1-L4 层描述，与 ARCHITECTURE.md 的 Swarm 架构融合

### U5: 质量门禁

采用 SPEC.md L0-L4 标准

### U6: 根级文档

将 `AGENTS.md` 和 `SPEC.md` 移出或标注为"待归档"

---

## 需要同步修改的文件清单

| 文件 | 修改内容 | 优先级 |
|------|---------|--------|
| `CLAUDE.md` | 更新版本目录引用、更新架构描述、补充ClawTeam引用 | P0 |
| `AGENTS.md` | 移出或标注为 CodePilot Desktop 文档 | P0 |
| `SPEC.md` | 移出或标注为 CodePilot Desktop 文档 | P0 |
| `Output/cyberteam-v4/ARCHITECTURE.md` | 补充质量门禁详细定义 | P1 |
| `Output/cyberteam-v4/SPEC.md` | 统一质量门禁标准与 CLAUDE.md | P1 |

---

## 结论

项目文档存在系统性的**版本引用错误**、**架构描述不统一**、**部门划分混乱**三大问题。建议：

1. **立即**: 清理根级 `AGENTS.md` 和 `SPEC.md`，明确标记为 CodePilot Desktop 文档
2. **短期**: 统一所有文档中的架构描述和质量门禁标准
3. **中期**: 重建 `CLAUDE.md` 规则四规定的目录结构

---

*审查完成时间: 2026-04-01*
*审查人: docs-coherence*
