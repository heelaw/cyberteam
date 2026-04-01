# Skill Library v1 - 完整结构分析报告

**生成时间**: 2026-03-24
**分析路径**: `/Users/cyberwiz/Documents/01_Project/02_Skill研发/skill-library-v1`
**总 Skill 数量**: 52 个

---

## 目录结构概览

```
skill-library-v1/
├── 00-core/              # 核心思维技能 (16个)
├── 01-cyberwiz/          # Cyberwiz 业务技能 (20个)
├── 02-thinking/          # 思维方法技能 (9个)
├── 03-productivity/      # 生产力工具 (1个)
├── 04-development/       # 开发工具 (2个)
└── 05-information/       # 信息处理技能 (9个)
```

---

## 00-core - 核心思维技能 (16个)

### 根目录 Skill
- **路径**: `00-core/SKILL.md`
- **结构**:
  ```
  00-core/
  ├── SKILL.md                    # 核心技能主文件
  ├── README.md                   # 说明文档
  ├── best-practices-monitor.md   # 最佳实践监控
  ├── momus-review-standard.md    # 审查标准
  ├── cyberwiz-skill-template-v2.md  # Skill 模板
  └── success-metrics-template.md # 成功指标模板
  ```

### 子 Skills

#### 1. coordinator-orchestrator
- **路径**: `00-core/coordinator-orchestrator/SKILL.md`
- **结构**: 仅 SKILL.md

#### 2. coordinator-problem-classifier
- **路径**: `00-core/coordinator-problem-classifier/SKILL.md`
- **结构**: 仅 SKILL.md

#### 3. critical-5why
- **路径**: `00-core/critical-5why/SKILL.md`
- **结构**: 仅 SKILL.md

#### 4. critical-gidel-law
- **路径**: `00-core/critical-gidel-law/SKILL.md`
- **结构**: 仅 SKILL.md

#### 5. critical-reverse-thinking
- **路径**: `00-core/critical-reverse-thinking/SKILL.md`
- **结构**: 仅 SKILL.md

#### 6. critical-systems-thinking
- **路径**: `00-core/critical-systems-thinking/SKILL.md`
- **结构**: 仅 SKILL.md

#### 7. judge-insight-extractor
- **路径**: `00-core/judge-insight-extractor/SKILL.md`
- **结构**: 仅 SKILL.md

#### 8. judge-quality-discriminator
- **路径**: `00-core/judge-quality-discriminator/SKILL.md`
- **结构**: 仅 SKILL.md

#### 9. judge-report-generator
- **路径**: `00-core/judge-report-generator/SKILL.md`
- **结构**: 仅 SKILL.md

#### 10. knowledge-explorer
- **路径**: `00-core/knowledge-explorer/SKILL.md`
- **结构**: 仅 SKILL.md

#### 11. prompt-optimizer-workflow
- **路径**: `00-core/prompt-optimizer-workflow/SKILL.md`
- **结构**: 仅 SKILL.md

#### 12. senior-meta-cognition
- **路径**: `00-core/senior-meta-cognition/SKILL.md`
- **结构**: 仅 SKILL.md

#### 13. senior-private-board
- **路径**: `00-core/senior-private-board/SKILL.md`
- **结构**: 仅 SKILL.md

#### 14. senior-thinking-chain
- **路径**: `00-core/senior-thinking-chain/SKILL.md`
- **结构**: 仅 SKILL.md

#### 15. system-swot
- **路径**: `00-core/system-swot/SKILL.md`
- **结构**: 仅 SKILL.md

#### 16. thinking-model-template
- **路径**: `00-core/thinking-model-template/SKILL.md`
- **结构**: 仅 SKILL.md

---

## 01-cyberwiz - Cyberwiz 业务技能 (20个)

### 00-core 子模块

#### 1. knowledge-graph
- **路径**: `01-cyberwiz/00-core/knowledge-graph/SKILL.md`
- **结构**:
  ```
  knowledge-graph/
  ├── SKILL.md
  └── KB_GRAPH_SCHEMA.md
  ```

#### 2. plan-mode-enforcement
- **路径**: `01-cyberwiz/00-core/plan-mode-enforcement/SKILL.md`
- **结构**: 仅 SKILL.md

### activity 子模块

#### 3. activity-3.0
- **路径**: `01-cyberwiz/activity/activity-3.0/SKILL.md`
- **结构**:
  ```
  activity-3.0/
  ├── SKILL.md
  ├── skill-audit-report.md
  ├── assets/
  │   ├── activity-checklist.md
  │   ├── activity-collaboration-template.md
  │   └── cases/
  │       └── case_assets_guide.md
  ├── references/
  │   ├── cases/
  │   │   ├── case_template.md
  │   │   └── coffee_shop_luxi_20250109.md
  │   └── prompts/
  │       └── 00-activity-orchestrator.md
  ├── scripts/
  │   ├── check-workflow-status.sh
  │   ├── create-dirs.sh
  │   └── validate-output.sh
  └── workflow/
  ```

### 独立 Skills

#### 4. background-task
- **路径**: `01-cyberwiz/background-task/SKILL.md`
- **结构**:
  ```
  background-task/
  ├── SKILL.md
  ├── manager.py
  ├── storage.py
  └── task_client.py
  ```

### business-analysis 子模块

#### 5. business-model-v3
- **路径**: `01-cyberwiz/business-analysis/business-model-v3/SKILL.md`
- **结构**: **完整复杂结构**
  ```
  business-model-v3/
  ├── SKILL.md
  ├── README.md
  ├── QUICKSTART.md
  ├── CHANGELOG.md
  ├── UPGRADE.md
  ├── OPTIMIZATION_SUMMARY.md
  ├── parameters.json
  ├── init-workflow.sh
  ├── assets/
  │   ├── README.md
  │   ├── business-model-template.md
  │   ├── breakthrough-points-template.md
  │   ├── conversion-funnel-template.md
  │   ├── final-report-template.md
  │   ├── frameworks-reference.md
  │   ├── metrics-reference.md
  │   ├── operational-metrics-template.md
  │   └── revenue-formula-template.md
  ├── config/
  │   ├── example_project.yaml
  │   └── validator_rules.yaml
  ├── core/
  │   └── parameter_extractor.py
  ├── frameworks/
  │   ├── ecommerce-dtc.yaml
  │   ├── o2o-preorder.yaml
  │   └── saas-subscription.yaml
  ├── modules/
  ├── references/
  │   ├── business-goals-alignment.md
  │   ├── business-model-cases-complete.md
  │   ├── business-model-cases.md
  │   ├── business-model-methodology.md
  │   ├── exploratory-projects-breakthrough.md
  │   ├── LaceCode — The Future of Beauty Is Personal(1).pdf
  │   ├── local-business-model-framework.md
  │   ├── northstar-metrics-methodology.md
  │   └── team-management-tools.md
  ├── scripts/
  │   ├── README.md
  │   ├── export_tool.py
  │   ├── funnel_analyzer.py
  │   ├── init_v2.py
  │   ├── metrics_validator.py
  │   ├── report_generator.py
  │   ├── revenue_calculator.py
  │   ├── status_checker.py
  │   ├── validator.py
  │   └── workflow_manager.py
  ├── templates/
  ├── tools/
  │   └── incremental_updater.py
  ├── output/
  └── validators/
      └── validation_engine.py
  ```

### case-analysis 子模块

#### 6. case-analysis
- **路径**: `01-cyberwiz/case-analysis/case-analysis/SKILL.md`
- **结构**:
  ```
  case-analysis/
  ├── SKILL.md
  ├── README.md
  ├── PROJECT_OVERVIEW.txt
  ├── FINAL_REPORT.md
  ├── analysis_summary.md
  ├── case_index.md
  ├── cases_overview.json
  ├── methodology_analysis.json
  ├── operation_case_methodology_report.md
  ├── quick_reference_guide.md
  ├── analyze_case_structure.py
  ├── deep_case_analysis.py
  ├── assets/
  │   └── case_library_template.md
  ├── cases/
  │   ├── README.md
  │   └── GUIDE.md
  ├── references/
  │   ├── case_analysis_methodology.md
  │   ├── case_index.md
  │   ├── operation_case_methodology_report.md
  │   └── quick_reference_guide.md
  └── scripts/
      ├── convert_cases_to_markdown.py
      └── generate_template.py
  ```

### globalization 子模块

#### 7. brand-localization
- **路径**: `01-cyberwiz/globalization/brand-localization/SKILL.md`
- **结构**: 仅 SKILL.md

#### 8. glocalization-core
- **路径**: `01-cyberwiz/globalization/glocalization-core/SKILL.md`
- **结构**: 仅 SKILL.md

#### 9. market-entry
- **路径**: `01-cyberwiz/globalization/market-entry/SKILL.md`
- **结构**: 仅 SKILL.md

### growth 子模块

#### 10. pmf-validator
- **路径**: `01-cyberwiz/growth/pmf-validator/SKILL.md`
- **结构**:
  ```
  pmf-validator/
  ├── SKILL.md
  └── references/
  ```

### job-analysis 子模块

#### 11. job-analysis
- **路径**: `01-cyberwiz/job-analysis/job-analysis/SKILL.md`
- **结构**:
  ```
  job-analysis/
  ├── SKILL.md
  ├── references/
  └── scripts/
  ```

### 独立 Skills

#### 12. lesson-design
- **路径**: `01-cyberwiz/lesson-design/SKILL.md`
- **结构**:
  ```
  lesson-design/
  ├── SKILL.md
  ├── references/
  └── scripts/
  ```

### marketing 子模块

#### 13. market-chance
- **路径**: `01-cyberwiz/marketing/market-chance/SKILL.md`
- **结构**:
  ```
  market-chance/
  ├── SKILL.md
  ├── assets/
  └── references/
  ```

#### 14. marketing
- **路径**: `01-cyberwiz/marketing/marketing/SKILL.md`
- **结构**:
  ```
  marketing/
  ├── SKILL.md
  ├── marketing-promotion.skill
  ├── assets/
  └── references/
  ```

### product-ops 子模块

#### 15. data-decision
- **路径**: `01-cyberwiz/product-ops/data-decision/SKILL.md`
- **结构**: 仅 SKILL.md

#### 16. demand-analysis
- **路径**: `01-cyberwiz/product-ops/demand-analysis/SKILL.md`
- **结构**: 仅 SKILL.md

#### 17. growth-hacking
- **路径**: `01-cyberwiz/product-ops/growth-hacking/SKILL.md`
- **结构**: 仅 SKILL.md

#### 18. user-insight
- **路径**: `01-cyberwiz/product-ops/user-insight/SKILL.md`
- **结构**: 仅 SKILL.md

### user-research 子模块

#### 19. user-research
- **路径**: `01-cyberwiz/user-research/user-research/SKILL.md`
- **结构**:
  ```
  user-research/
  ├── SKILL.md
  └── references/
  ```

### writing 子模块

#### 20. writing
- **路径**: `01-cyberwiz/writing/writing/SKILL.md`
- **结构**:
  ```
  writing/
  ├── SKILL.md
  ├── assets/
  │   ├── strategy-template.md
  │   ├── channel-strategy-template.md
  │   ├── copywriting-template.md
  │   ├── draft-checklist.md
  │   ├── pain-points-template.md
  │   ├── selling-points-template.md
  │   └── user-research-template.md
  ├── references/
  │   ├── execution-manual.md
  │   ├── step1_user_analysis.md
  │   ├── step2_selling_points.md
  │   ├── step3_pain_points.md
  │   ├── step4_demand_type.md
  │   ├── step5_channel_strategy.md
  │   ├── step6_copywriting.md
  │   ├── step7_optimization.md
  │   ├── persona/
  │   │   ├── my-audience.md
  │   │   ├── my-values.md
  │   │   ├── my-voice.md
  │   │   └── past-articles/
  │   │       └── README.md
  │   ├── platforms/
  │   │   ├── ecommerce-guide.md
  │   │   ├── landing-page-guide.md
  │   │   └── social-media-guide.md
  │   └── products/
  │       ├── README.md
  │       └── templates/
  │           ├── product_profile.md
  │           └── user_research.md
  ├── scripts/
  │   ├── check-workflow-status.sh
  │   ├── create-dirs.sh
  │   └── validate-output.sh
  └── workflow/
      ├── 00-init/
      ├── 01-user-research/
      ├── 02-selling-points/
      ├── 03-pain-points/
      ├── 04-strategy/
      ├── 05-channel-strategy/
      ├── 06-draft/
      ├── 07-final/
      └── 08-tracking/
  ```

### xiaohongshu 子模块

#### 额外发现: xiaohongshu
- **路径**: `01-cyberwiz/xiaohongshu/xiaohongshu/SKILL.md`
- **结构**:
  ```
  xiaohongshu/
  ├── SKILL.md
  ├── assets/
  └── references/
  ```

---

## 02-thinking - 思维方法技能 (9个)

### innovation 子模块 (4个)

#### 1. innovation-cloud-rain-umbrella
- **路径**: `02-thinking/innovation/innovation-cloud-rain-umbrella/SKILL.md`
- **结构**: 仅 SKILL.md

#### 2. innovation-first-principles
- **路径**: `02-thinking/innovation/innovation-first-principles/SKILL.md`
- **结构**: 仅 SKILL.md

#### 3. innovation-mind-map
- **路径**: `02-thinking/innovation/innovation-mind-map/SKILL.md`
- **结构**: 仅 SKILL.md

#### 4. innovation-six-hats
- **路径**: `02-thinking/innovation/innovation-six-hats/SKILL.md`
- **结构**: 仅 SKILL.md

### system 子模块 (3个)

#### 5. system-grow-model
- **路径**: `02-thinking/system/system-grow-model/SKILL.md`
- **结构**: 仅 SKILL.md

#### 6. system-kiss-review
- **路径**: `02-thinking/system/system-kiss-review/SKILL.md`
- **结构**: 仅 SKILL.md

#### 7. system-strategy-advisor
- **路径**: `02-thinking/system/system-strategy-advisor/SKILL.md`
- **结构**: 仅 SKILL.md

### 独立 Skills (2个)

#### 8. auto-classifier
- **路径**: `02-thinking/auto-classifier/SKILL.md`
- **结构**: 仅 SKILL.md

#### 9. tag-enricher
- **路径**: `02-thinking/tag-enricher/SKILL.md`
- **结构**: 仅 SKILL.md

---

## 03-productivity - 生产力工具 (1个)

### media 子模块

#### 1. gemini-image
- **路径**: `03-productivity/media/gemini-image/SKILL.md`
- **结构**:
  ```
  gemini-image/
  ├── SKILL.md
  ├── README.md
  ├── config/
  │   ├── secrets.example.md
  │   └── secrets.md
  └── tips/
      ├── chinese-text.md
      └── image-upload.md
  ```

---

## 04-development - 开发工具 (2个)

### 根目录 Skill
- **路径**: `04-development/SKILL.md`
- **结构**:
  ```
  04-development/
  ├── SKILL.md
  ├── LICENSE.txt
  ├── references/
  │   ├── output-patterns.md
  │   └── workflows.md
  └── scripts/
      ├── init_skill.py
      ├── package_skill.py
      └── quick_validate.py
  ```

### 子 Skills

#### 1. skill-generator
- **路径**: `04-development/skill-generator/SKILL.md`
- **结构**: 仅 SKILL.md

---

## 05-information - 信息处理技能 (9个)

### 根目录 Skill
- **路径**: `05-information/SKILL.md`
- **结构**:
  ```
  05-information/
  ├── SKILL.md
  ├── analyzer/
  ├── course-merge-architect/
  ├── course-reviewer/
  ├── organizer/
  ├── resource-indexer/
  ├── rss-collector/
  ├── rss-fetcher/
  └── web-collector/
  ```

### 子 Skills

#### 1. analyzer
- **路径**: `05-information/analyzer/SKILL.md`
- **结构**: 仅 SKILL.md

#### 2. course-merge-architect
- **路径**: `05-information/course-merge-architect/SKILL.md`
- **结构**:
  ```
  course-merge-architect/
  ├── SKILL.md
  └── references/
  ```

#### 3. course-reviewer
- **路径**: `05-information/course-reviewer/SKILL.md`
- **结构**: 仅 SKILL.md

#### 4. organizer
- **路径**: `05-information/organizer/SKILL.md`
- **结构**: 仅 SKILL.md

#### 5. resource-indexer
- **路径**: `05-information/resource-indexer/SKILL.md`
- **结构**: 仅 SKILL.md

#### 6. rss-collector
- **路径**: `05-information/rss-collector/SKILL.md`
- **结构**: 仅 SKILL.md

#### 7. rss-fetcher
- **路径**: `05-information/rss-fetcher/SKILL.md`
- **结构**: 仅 SKILL.md

#### 8. web-collector
- **路径**: `05-information/web-collector/SKILL.md`
- **结构**: 仅 SKILL.md

---

## 统计汇总

### 按复杂度分类

| 复杂度 | 数量 | Skills |
|--------|------|--------|
| **高复杂度** | 3 | business-model-v3, case-analysis, writing |
| **中等复杂度** | 7 | activity-3.0, gemini-image, background-task, 04-development, course-merge-architect, job-analysis, lesson-design, marketing, market-chance, pmf-validator, user-research, xiaohongshu, knowledge-graph |
| **简单结构** | 42 | 仅包含 SKILL.md 或少量文件 |

### 按目录结构分类

| 结构类型 | 数量 | 说明 |
|----------|------|------|
| 仅 SKILL.md | 30 | 最基础结构 |
| SKILL.md + references | 8 | 有参考资料 |
| SKILL.md + scripts | 5 | 有脚本工具 |
| SKILL.md + assets | 6 | 有资产文件 |
| SKILL.md + config | 2 | 有配置文件 |
| SKILL.md + templates | 2 | 有模板文件 |
| SKILL.md + workflow | 2 | 有工作流记录 |
| 完整结构 | 3 | 包含多种子目录 |

### 文件夹使用频率

| 文件夹 | 出现次数 | Skills |
|--------|----------|--------|
| references/ | 12 | activity-3.0, business-model-v3, case-analysis, course-merge-architect, gemini-image, job-analysis, lesson-design, market-chance, marketing, pmf-validator, user-research, writing, xiaohongshu |
| scripts/ | 7 | activity-3.0, business-model-v3, case-analysis, job-analysis, lesson-design, writing, 04-development |
| assets/ | 9 | activity-3.0, business-model-v3, case-analysis, gemini-image, market-chance, marketing, writing, xiaohongshu |
| config/ | 3 | business-model-v3, gemini-image, knowledge-graph |
| templates/ | 3 | business-model-v3, writing, 04-development |
| workflow/ | 2 | activity-3.0, writing |
| tools/ | 1 | business-model-v3 |
| validators/ | 1 | business-model-v3 |
| modules/ | 1 | business-model-v3 |
| core/ | 1 | business-model-v3 |
| frameworks/ | 1 | business-model-v3 |
| cases/ | 2 | activity-3.0, case-analysis |
| output/ | 1 | business-model-v3 |

---

## 关键发现

1. **结构标准化程度**: 大部分 Skills 采用简单结构（仅 SKILL.md），少数采用完整复杂结构

2. **最复杂的 Skill**: `business-model-v3` 拥有最完整的目录结构，包含 assets/, config/, core/, frameworks/, modules/, references/, scripts/, templates/, tools/, validators/, output/ 等多个子目录

3. **常见配套文件**:
   - references/ - 参考资料和方法论
   - scripts/ - Python 脚本和 Shell 脚本
   - assets/ - 模板和检查清单
   - config/ - 配置文件和示例

4. **Python 脚本使用**: background-task, business-model-v3, case-analysis 等 Skill 包含 Python 工具脚本

5. **工作流记录**: activity-3.0 和 writing 包含 workflow/ 目录，用于记录工作流历史

---

**报告结束**
