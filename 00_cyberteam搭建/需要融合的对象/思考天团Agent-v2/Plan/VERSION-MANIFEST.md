# 思考天团 - 版本清单

**最后更新**: 2026-03-21

---

## 一、文件版本说明

### 核心定义文件（位于项目根目录）

| 文件 | 版本 | 说明 | 最后修改 |
|------|------|------|----------|
| SKILL.md | v1.0 | Skill定义入口 | 2026-03-20 |
| AGENT.md | v1.0 | Agent定义入口 | 2026-03-20 |
| WORKFLOW.md | v1.0 | 协作流程定义 | 2026-03-20 |
| 意图分类器.md | v1.0 | 路由逻辑定义 | 2026-03-20 |

### MVP验证文件（位于 MVP/ 目录）

| 文件 | 版本 | 说明 | 最后修改 |
|------|------|------|----------|
| orchestrator.md | v1.0 | 意图分类器（简化版） | 2026-03-21 |
| integrator.md | v3.0 | 结果整合器（最终版） | 2026-03-21 |
| MVP-SUMMARY.md | Final | MVP总结报告 | 2026-03-21 |

### 14专家Agent（位于 agents/ 目录）

| 专家 | 目录 | 说明 |
|------|------|------|
| 卡尼曼 | 01-kahneman/ | 行为经济学视角 |
| 第一性原理 | 02-first-principle/ | 本质还原视角 |
| 六顶思考帽 | 03-six-hats/ | 全面分析视角 |
| SWOT/TOSE | 04-swot-tows/ | 战略分析视角 |
| 5Why | 05-fivewhy/ | 根因分析 |
| Goldlin | 06-goldlin/ | 用户体验视角 |
| GROW | 07-grow/ | 目标达成视角 |
| KISS | 08-kiss/ | 简化原则视角 |
| 麦肯锡 | 09-mckinsey/ | MECE结构化分析 |
| AI-Board | 10-ai-board/ | 模拟董事视角 |
| 逆向思维 | 11-reverse-thinking/ | 反向思考视角 |
| 五维度 | 12-five-dimension/ | 多维分析视角 |
| WBS | 13-wbs/ | 工作分解视角 |
| 管理者跃迁 | 14-manager-leap/ | 管理跃迁视角 |
| 机会成本 | 15-opportunity-cost/ | 机会成本分析（P0新增） |
| 沉没成本 | 16-sunk-cost/ | 沉没成本识别（P0新增） |
| 确认偏误 | 17-confirmation-bias/ | 认知偏差识别（P0新增） |
| 批判性思维 | 18-critical-thinking/ | 质疑与验证（P0新增） |
| 系统思维 | 19-systems-thinking/ | 整体性思考（P0新增） |

### 分析报告（位于 Plan/ 目录）

| 文件 | 版本 | 说明 |
|------|------|------|
| 超大规模Agent团队分析报告.md | v1.0 | 第一轮：36仓库+22Q大规模调研 |
| 思考天团Q文件二次审查报告.md | v2.0 | 第二轮：Q文件并行扫描+5专家审查 |
| **思考天团Q文件三次审查报告.md** | v3.0 | **最终版：6专家深度复审**（本次新增） |
| 思考天团Q文件开发可行性验证报告.md | - | MVP验证报告 |

### MVP测试案例（位于 MVP/test-case/）

| 文件 | 说明 |
|------|------|
| problem-1.md | 测试问题1：在线教育平台增长停滞 |

### MVP输出报告（位于 MVP/output/）

| 文件 | 版本 | 说明 |
|------|------|------|
| mvp-result-round1.md | Round1 | 基础版分析 |
| mvp-result-round2.md | Round2 | 增强版（决策树+指标+时间线） |
| mvp-final.md | Final | 最终版（风险+资源+依赖） |
| mvp-self-eval-*.md | - | 自我评估报告 |

---

## 二、版本演变

```
v1.0 (2026-03-20)
├── 基础设计完成
├── 14专家Agent定义
├── SKILL.md / AGENT.md / WORKFLOW.md
└── 意图分类器.md

v2.0 (2026-03-21 第一轮)
├── 大规模仓库调研（36个）
├── Q文件并行扫描（55个）
└── 生成审查报告×2

v3.0 (2026-03-21 第二轮)
├── MVP跑通（三轮迭代）
├── 整合器v3.0
└── 质量评级：A级（88/110）
```

---

## 三、最终交付物清单

### 必须保留文件

**核心定义**:
- [x] SKILL.md
- [x] AGENT.md
- [x] WORKFLOW.md
- [x] 意图分类器.md

**MVP验证**:
- [x] MVP/orchestrator.md
- [x] MVP/integrator.md
- [x] MVP/MVP-SUMMARY.md
- [x] MVP/output/mvp-final.md

**专家Agent**:
- [x] agents/01-kahneman/ ~ agents/14-manager-leap/

**分析报告**:
- [x] Plan/超大规模Agent团队分析报告.md
- [x] Plan/思考天团Q文件二次审查报告.md
- [x] Plan/思考天团Q文件三次审查报告.md ← **最终版**
- [x] Plan/VERSION-MANIFEST.md ← **本文件**

### 建议清理文件

| 文件 | 原因 | 操作 |
|------|------|------|
| 参考资料/ | 中间研究材料 | 归档或删除 |
| templates/ | 可能过时 | 确认是否需要 |
| MVP/test-case/ | 测试用例 | 确认是否保留 |
| MVP/output/round1,round2 | 中间版本 | 合并到final或删除 |

---

## 四、使用指南

**启动思考天团**:
1. 读取 SKILL.md 了解入口
2. 使用 意图分类器.md 路由问题
3. 调用 agents/ 下对应专家
4. 使用 MVP/integrator.md 整合结果

**查看项目状态**:
1. 读取 VERSION-MANIFEST.md 了解文件结构
2. 查看 Plan/下最新审查报告
3. 查看 MVP/MVP-SUMMARY.md 了解MVP验证结果
