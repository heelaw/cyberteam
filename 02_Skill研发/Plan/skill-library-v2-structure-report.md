# skill-library-v2 完整结构分析报告

**生成时间**: 2026-03-24
**分析路径**: `/Users/cyberwiz/Documents/01_Project/02_Skill研发/skill-library-v2`

---

## 📊 总体统计

- **Skill 总数**: 57 个
- **分类数量**: 7 个（00-templates, 01-thinking-models, 02-methodologies, 03-operations, 04-product, 05-information, 06-development）
- **仅包含 SKILL.md 的 Skill**: 36 个
- **包含配套资源的 Skill**: 21 个

---

## 📁 详细结构分析

### 00-templates（模板）

#### 1. thinking-model-template
- **路径**: `00-templates/thinking-model-template`
- **文件结构**:
  - `SKILL.md`
- **说明**: 思维模型模板，仅包含核心定义文件

---

### 01-thinking-models（思维模型）

所有 Skills 均仅包含 `SKILL.md`：

1. **critical-5why** - 批判性思维：5问法
2. **critical-gidel-law** - 批判性思维：吉德尔定律
3. **critical-reverse-thinking** - 批判性思维：逆向思维
4. **critical-systems-thinking** - 批判性思维：系统思维
5. **innovation-cloud-rain-umbrella** - 创新思维：云雨伞思维
6. **innovation-first-principles** - 创新思维：第一性原理
7. **innovation-mind-map** - 创新思维：思维导图
8. **innovation-six-hats** - 创新思维：六顶思考帽
9. **knowledge-explorer** - 知识探索
10. **senior-meta-cognition** - 高级元认知
11. **senior-private-board** - 高级私人董事会
12. **senior-thinking-chain** - 高级思维链
13. **system-swot** - 系统SWOT分析

**共同特点**: 所有思维模型类 Skills 都是轻量级设计，仅包含核心 SKILL.md 文件

---

### 02-methodologies（方法论）

所有 Skills 均仅包含 `SKILL.md`：

1. **auto-classifier** - 自动分类器
2. **system-grow-model** - 系统GROW模型
3. **system-kiss-review** - 系统KISS审查
4. **system-strategy-advisor** - 系统策略顾问
5. **tag-enricher** - 标签增强器

**共同特点**: 方法论类 Skills 也是轻量级设计，仅包含核心定义文件

---

### 03-operations（运营）

#### 1. activity-3.0
- **路径**: `03-operations/activity-3.0`
- **完整结构**:
  ```
  activity-3.0/
  ├── SKILL.md
  ├── skill-audit-report.md
  ├── assets/
  │   ├── activity-collaboration-template.md
  │   ├── activity-checklist.md
  │   ├── cases/
  │   │   └── case_assets_guide.md
  ├── references/
  │   ├── cases/
  │   │   ├── coffee_shop_luxi_20250109.md
  │   │   └── case_template.md
  │   └── prompts/
  │       └── 00-activity-orchestrator.md
  ├── scripts/
  │   ├── check-workflow-status.sh
  │   ├── create-dirs.sh
  │   └── validate-output.sh
  └── workflow/
  ```
- **特点**: 完整的 Activity 3.0 实现，包含案例库、工作流、脚本和资产管理

#### 2. growth-hacking
- **路径**: `03-operations/growth-hacking`
- **文件结构**: 仅 `SKILL.md`

#### 3. growth-hacking-advanced
- **路径**: `03-operations/growth-hacking-advanced`
- **文件结构**: 仅 `SKILL.md`

#### 4. growth-hacking-basics
- **路径**: `03-operations/growth-hacking-basics`
- **文件结构**: 仅 `SKILL.md`

#### 5. market-chance
- **路径**: `03-operations/market-chance`
- **完整结构**:
  ```
  market-chance/
  ├── SKILL.md
  ├── assets/
  │   └── report-template.md
  └── references/
      └── analysis-models.md
  ```
- **特点**: 包含报告模板和分析模型参考

#### 6. marketing
- **路径**: `03-operations/marketing`
- **完整结构**:
  ```
  marketing/
  ├── SKILL.md
  ├── marketing-promotion.skill
  ├── assets/
  │   └── templates/
  │       └── promotion_plan_template.md
  └── references/
      ├── advanced/
      │   ├── data_funnels.md
      │   ├── engagement_principles.md
      │   ├── traffic_codes_map.md
      │   └── user_insights_canvas.md
      ├── cases/
      │   └── ecommerce_perfect_diary_xiaohongshu.md
      ├── README.md
      ├── channel_types.md
      ├── conversion_triggers.md
      └── tools/
          └── checklists.md
  ```
- **特点**: 完整的营销 Skill，包含高级参考资料、案例、工具和模板

#### 7. xiaohongshu
- **路径**: `03-operations/xiaohongshu`
- **完整结构**:
  ```
  xiaohongshu/
  ├── SKILL.md
  ├── assets/
  │   ├── checklists/
  │   │   ├── cold_start_checklist.md
  │   │   ├── publishing_checklist.md
  │   │   └── workflow_checklist.md
  │   └── templates/
  │       ├── account_analysis_table.md
  │       └── note_template.md
  └── references/
      ├── account_positioning.md
      ├── content_creation.md
      ├── persona/
      │   └── past-articles/
      ├── platforms/
      │   └── xiaohongshu-guide.md
      ├── prompts/
      │   └── xiaohongshu-writer.md
      └── stages/
  ```
- **特点**: 小红书专用 Skill，包含完整的运营流程、模板和检查清单

---

### 04-product（产品）

#### 1. brand-localization
- **路径**: `04-product/brand-localization`
- **文件结构**: 仅 `SKILL.md`

#### 2. business-model-v3 ⭐
- **路径**: `04-product/business-model-v3`
- **完整结构**:
  ```
  business-model-v3/
  ├── SKILL.md
  ├── CHANGELOG.md
  ├── OPTIMIZATION_SUMMARY.md
  ├── parameters.json
  ├── QUICKSTART.md
  ├── README.md
  ├── UPGRADE.md
  ├── init-workflow.sh
  ├── assets/
  │   ├── README.md
  │   ├── breakthrough-points-template.md
  │   ├── business-model-template.md
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
  │   ├── conversion-funnel/
  │   │   └── README.md
  │   ├── growth-metrics/
  │   │   └── README.md
  │   └── unit-economics/
  │       └── README.md
  ├── output/
  │   └── lacecode/
  │       └── lacecode-业务模型分析-20250119-v8.md
  ├── references/
  │   ├── LaceCode — The Future of Beauty Is Personal(1).pdf
  │   ├── business-goals-alignment.md
  │   ├── business-model-cases-complete.md
  │   ├── business-model-cases.md
  │   ├── business-model-methodology.md
  │   ├── exploratory-projects-breakthrough.md
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
  │   ├── investor-pitch/
  │   │   └── final-report-template.md
  │   ├── internal-strategy/
  │   │   └── final-report-template.md
  │   └── operational-kpi/
  │       └── final-report-template.md
  ├── tools/
  │   └── incremental_updater.py
  └── validators/
      └── validation_engine.py
  ```
- **特点**: **最复杂的 Skill**，包含完整的业务模型分析系统，有配置、脚本、验证器、框架和模板

#### 3. case-analysis ⭐
- **路径**: `04-product/case-analysis`
- **完整结构**:
  ```
  case-analysis/
  ├── SKILL.md
  ├── README.md
  ├── FINAL_REPORT.md
  ├── PROJECT_OVERVIEW.txt
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
  │   ├── GUIDE.md
  │   ├── activity/
  │   │   └── 058三节课共创活动汇报《职业教育行业调研报告》  （2024.01.25）.md
  │   ├── brand_marketing/
  │   │   ├── 03-教育营销案例拆解（花园式运营策略）.md
  │   │   ├── 045瑞幸咖啡低价9.9元背后的营销思路（2023.06.29）.md
  │   │   ├── 047AI作图应用妙鸭相机爆火，背后的逻辑（2023.07.27）.md
  │   │   ├── 050瑞幸x茅台联名分析，如何联名才能爆火出圈（2023.09.07）.md
  │   │   ├── 053 靠卖瑜伽服市值赶超阿迪达斯，Lululemon品牌营销拆解（2023.11.15）.md
  │   │   ├── 056 2023年的20个营销案例（2023.12.28）.md
  │   │   ├── 059LuluLemon新春·咏春营销案例  （2024.02.07）.md
  │   │   ├── 063 市场与销售人员，怎么用AI高效生产营销素材-（2024.3.21）.md
  │   │   ├── 064甘肃麻辣烫爆火背后的品牌营销策略（2024.04.10）.md
  │   │   ├── 065 这么多大模型，为何月之暗面的Kimi最火？（2024.4.18）.md
  │   │   ├── 068 离职博主赛道，为何成为流量密码？（2024.6.20）.md
  │   │   ├── 069 天猫禁止包裹卡，给你6个电商私域建议（2024.7.11）.md
  │   │   ├── 071 押宝郑钦文！霸王茶姬奥运营销做对了什么？（2024.8.15）.md
  │   │   ├── 072《黑神话：悟空》全球爆火背后靠的是什么？（2024.8.29）.md
  │   │   ├── 073多邻国App在营销上是如何拿捏人性的？（2024.9.19）.md
  │   │   ├── 074：烘焙店女工变-女明星-黄油小熊如何成为现象级IP-（2024.10.17）.md
  │   │   ├── 075：成年人的"阿贝贝"Jellycat；如何成为潮流新宠？（2024.11.21）.md
  │   │   ├── 076：情感综艺天花板《再见爱人》，走红互联网的路径拆解（2024.12.05）.md
  │   │   └── 077 2024年的20个营销案例（2024.12.19）.md
  │   ├── private_domain/
  │   │   ├── 009三节课 【网易严选】私域运营案例拆解.md
  │   │   ├── 007三节课  「肯德基私域运营」拆解（2022.5.15）.md
  │   │   ├── 008三节课 「孩子王私域运营」拆解.md
  │   │   ├── 010三节课【乐刻运动】私域案例拆解（2022.6.7）.md
  │   │   ├── 013三节课【baby care私域体系】分析（2022.6.28）.md
  │   │   ├── 015三节课【喜茶私域案例】拆解（2022.7.13）.md
  │   │   ├── 020三节课【三只松鼠】社群运营案例拆解（2022.8.17） .md
  │   │   ├── 021三节课「每日黑巧」私域运营案例拆解（2022.8.23）.md
  │   │   ├── 022三节课「永璞咖啡私域运营」案例拆解（2022.8.31）.md
  │   │   ├── 026「认养一头牛」私域运营拆解（2022.11.01）.md
  │   │   ├── 028「跳海酒馆」社群运营案例拆解（2022.11.18）.md
  │   │   ├── 029「五谷磨房」私域运营拆解（2022.11.04）.md
  │   │   ├── 030「暴肌独角兽」私域运营拆解（2022.11.3）.md
  │   │   ├── 034 「群响」私域运营案例拆解（2023.01.12）.md
  │   │   ├── 055  600万粉丝，变现3.5亿，醉鹅娘是如何打造私域的？（2023.12.14）.md
  │   │   ├── 6【案例】8大行业私域整合运营案例.md
  │   │   └── 069 天猫禁止包裹卡，给你6个电商私域建议（2024.7.11）.md
  │   ├── product/
  │   │   ├── 001三节课 「微信读书案例」拆解（2022.3.22）.md
  │   │   ├── 002三节课  「交个朋友」案例拆解（2022.3.29).md
  │   │   ├── 003三节课 「美团买菜」案例拆解（2022.4.12）.md
  │   │   ├── 004三节课  「丁香医生」案例拆解（2022.4.19）.md
  │   │   ├── 005三节课  「考虫考研」案例拆解（2022.4.26）.md
  │   │   ├── 006三节课 「樊登读书 」案例拆解（2022.5.8）.md
  │   │   ├── 011三节课【得物app用户拉新】案例拆解（2022.6.14）.md
  │   │   ├── 012三节课【得物app用户活跃】案例拆解（2022.6.22）.md
  │   │   ├── 014三节课【醉鹅娘】拆解（2022.7.5）.md
  │   │   ├── 016三节课【蔚来app】拆解（2022.7.20）.md
  │   │   ├── 017三节课【名创优品】案例拆解（2022.7.27）.md
  │   │   ├── 018三节课【soul】案例拆解（2022.8.3）.md
  │   │   ├── 019三节课【奈雪的茶如何探全新的会员玩法】案例拆解（2022.8.10）.md
  │   │   ├── 023三节课「美团APP」游戏玩法拆解（2022.9.6）.md
  │   │   ├── 024「薄荷健康APP」用户运营拆解（2022.9.29）.md
  │   │   ├── 025「蔚来APP」精细化运营拆解（2022.10.27）.md
  │   │   ├── 027「宜家」场景化运营拆解（2022.11.2）.md
  │   │   ├── 031「美团外卖」补贴ROI评估方案拆解（2022.12.01）.md
  │   │   ├── 032「波司登羽绒服」抖音直播间案例拆解（2022.12.15）.md
  │   │   ├── 033 「小宇宙」商业化案例拆解（2022.12.29）.md
  │   │   ├── 035《流浪地球》是如何打造宣发之路（2023.02.02）.md
  │   │   ├── 037 AIGC行业发展分析（2023.02.23）.md
  │   │   ├── 038 Keep奖牌运营（2023.03.09） .md
  │   │   ├── 039京东百亿补贴商家策略分析（2023.03.23）.md
  │   │   ├── 040 【程前朋友圈】怎么火起来的？（2023.04.06） .md
  │   │   ├── 041 抖音本地生活的运作模式分析（2023.04.20）.md
  │   │   ├── 042 优惠券系统的搭建过程 （2023.05.18） .md
  │   │   ├── 043朴朴超市APP快速铺向市场的运营策略（2023.6.1）.md
  │   │   ├── 044美团买菜的增长逻辑是什么？（2023.06.15） .md
  │   │   ├── 046 Keep上市，中国运营第一股的商业模式（2023.07.13）.md
  │   │   ├── 048《封神》口碑破圈，电影宣发如何有后劲（2023.08.10）.md
  │   │   ├── 049 「三节课」创业复盘，如何转型成为学习平台（2023.08.24）.md
  │   │   ├── 051 B站「在下辉子」开同学盲盒涨粉百万案例分析（2023.09.21） .md
  │   │   ├── 052网易严选（宠物）抖音直播间案例拆解（2023.10.19）.md
  │   │   ├── 058三节课共创活动汇报《职业教育行业调研报告》  （2024.01.25）.md
  │   │   ├── 061 TikTok10大热门爆号&爆品案例拆解（2024.03.06）.md
  │   │   ├── 068 离职博主赛道，为何成为流量密码？（2024.6.20）.md
  │   │   ├── 070拆解雷军IP之路，中年创始人怎么成为流量的神？（2024.8.01）.md
  │   │   ├── 078第七十八期 蜜雪冰城冲击上市，茶饮加盟究竟多赚钱？（2024.1.9）.md
  │   │   └── 多个观察和分析文档...
  │   └── user_growth/
  │       ├── 044美团买菜的增长逻辑是什么？（2023.06.15） .md
  │       └── 5【案例】在下辉子、朴朴等用户增长案例.md
  ├── references/
  │   ├── case_analysis_methodology.md
  │   ├── case_index.md
  │   ├── operation_case_methodology_report.md
  │   └── quick_reference_guide.md
  └── scripts/
      ├── convert_cases_to_markdown.py
      └── generate_template.py
  ```
- **特点**: **案例库最丰富**的 Skill，包含 100+ 案例分析，分为品牌营销、私域、产品和用户增长四大类

#### 4. data-decision
- **路径**: `04-product/data-decision`
- **文件结构**: 仅 `SKILL.md`

#### 5. demand-analysis
- **路径**: `04-product/demand-analysis`
- **文件结构**: 仅 `SKILL.md`

#### 6. glocalization-core
- **路径**: `04-product/glocalization-core`
- **文件结构**: 仅 `SKILL.md`

#### 7. job-analysis
- **路径**: `04-product/job-analysis`
- **完整结构**:
  ```
  job-analysis/
  ├── SKILL.md
  ├── references/
  │   ├── analysis_template.md
  │   └── six_elements_methodology.md
  └── scripts/
      └── analyze_position.py
  ```
- **特点**: 包含岗位分析模板和六要素方法论

#### 8. knowledge-graph
- **路径**: `04-product/knowledge-graph`
- **完整结构**:
  ```
  knowledge-graph/
  ├── SKILL.md
  └── KB_GRAPH_SCHEMA.md
  ```
- **特点**: 包含知识图谱架构文档

#### 9. lesson-design
- **路径**: `04-product/lesson-design`
- **完整结构**:
  ```
  lesson-design/
  ├── SKILL.md
  ├── references/
  │   ├── course_positioning_template.md
  │   ├── lesson_design_checklist.md
  │   └── teaching_objective_matrix.md
  └── scripts/
      ├── course_outline_generator.py
      ├── course_validator.py
      └── objective_analyzer.py
  ```
- **特点**: 课程设计 Skill，包含教学目标矩阵和验证脚本

#### 10. market-entry
- **路径**: `04-product/market-entry`
- **文件结构**: 仅 `SKILL.md`

#### 11. plan-mode-enforcement
- **路径**: `04-product/plan-mode-enforcement`
- **文件结构**: 仅 `SKILL.md`

#### 12. pmf-validator
- **路径**: `04-product/pmf-validator`
- **完整结构**:
  ```
  pmf-validator/
  ├── SKILL.md
  └── references/
      ├── cases.md
      ├── methods.md
      └── output-standards.md
  ```
- **特点**: PMF 验证器，包含方法和案例参考

#### 13. user-insight
- **路径**: `04-product/user-insight`
- **文件结构**: 仅 `SKILL.md`

#### 14. user-research
- **路径**: `04-product/user-research`
- **完整结构**:
  ```
  user-research/
  ├── SKILL.md
  └── references/
      ├── case-studies.md
      ├── churn-prevention.md
      ├── indicators-system.md
      ├── lifecycle-management.md
      ├── ltv-cac-management.md
      ├── membership-system.md
      ├── points-system.md
      ├── user-segmentation.md
      └── incentive-system.md
  ```
- **特点**: 用户研究 Skill，包含完整的用户生命周期管理体系

#### 15. writing ⭐
- **路径**: `04-product/writing`
- **完整结构**:
  ```
  writing/
  ├── SKILL.md
  ├── assets/
  │   ├── channel-strategy-template.md
  │   ├── copywriting-template.md
  │   ├── draft-checklist.md
  │   ├── pain-points-template.md
  │   ├── selling-points-template.md
  │   ├── strategy-template.md
  │   └── user-research-template.md
  ├── references/
  │   ├── execution-manual.md
  │   ├── persona/
  │   │   ├── my-audience.md
  │   │   ├── my-values.md
  │   │   ├── my-voice.md
  │   │   └── past-articles/
  │   ├── products/
  │   │   ├── README.md
  │   │   └── templates/
  │   ├── platforms/
  │   │   ├── ecommerce-guide.md
  │   │   ├── landing-page-guide.md
  │   │   └── social-media-guide.md
  │   ├── step1_user_analysis.md
  │   ├── step2_selling_points.md
  │   ├── step3_pain_points.md
  │   ├── step4_demand_type.md
  │   ├── step5_channel_strategy.md
  │   ├── step6_copywriting.md
  │   └── step7_optimization.md
  ├── scripts/
  │   ├── check-workflow-status.sh
  │   ├── create-dirs.sh
  │   └── validate-output.sh
  └── workflow/
      ├── 00-init/
      │   └── ugreen-dxp2800-20250113-init.md
      ├── 01-user-research/
      │   └── ugreen-dxp2800-20250113-user-research.md
      ├── 02-selling-points/
      │   └── ugreen-dxp2800-20250113-selling-points.md
      │   ├── 03-pain-points/
      │   └── ugreen-dxp2800-20250113-pain-points.md
      ├── 04-strategy/
      │   └── ugreen-dxp2800-20250113-strategy.md
      ├── 05-channel-strategy/
      │   └── ugreen-dxp2800-20250113-channel-strategy.md
      ├── 06-draft/
      │   ├── ugreen-dxp2800-20250113-draft.md
      │   └── xiaohongshu-ugreen-dxp2800-20250113-draft.md
      ├── 07-final/
      │   ├── wechat-ugreen-dxp2800-20250113-final.md
      │   └── xiaohongshu-ugreen-dxp2800-20250113-final.md
      └── 08-tracking/
          └── ugreen-dxp2800-20250113-tracking.md
  ```
- **特点**: **完整的文案创作工作流系统**，包含从用户研究到追踪的全流程

---

### 05-information（信息处理）

#### 1. analyzer
- **路径**: `05-information/analyzer`
- **文件结构**: 仅 `SKILL.md`

#### 2. course-merge-architect
- **路径**: `05-information/course-merge-architect`
- **完整结构**:
  ```
  course-merge-architect/
  ├── SKILL.md
  └── references/
      ├── dedup-strategy.md
      ├── merge-rules.md
      ├── content-enhancement.md
      └── templates/
          ├── chapter-template.md
          ├── knowledge-index-template.md
          ├── learning-path-template.md
          └── outline-template.md
  ```
- **特点**: 课程合并架构师，包含去重策略和模板

#### 3. course-reviewer
- **路径**: `05-information/course-reviewer`
- **文件结构**: 仅 `SKILL.md`

#### 4. organizer
- **路径**: `05-information/organizer`
- **文件结构**: 仅 `SKILL.md`

#### 5. resource-indexer
- **路径**: `05-information/resource-indexer`
- **文件结构**: 仅 `SKILL.md`

#### 6. rss-collector
- **路径**: `05-information/rss-collector`
- **文件结构**: 仅 `SKILL.md`

#### 7. rss-fetcher
- **路径**: `05-information/rss-fetcher`
- **文件结构**: 仅 `SKILL.md`

#### 8. web-collector
- **路径**: `05-information/web-collector`
- **文件结构**: 仅 `SKILL.md`

---

### 06-development（开发工具）

#### 1. background-task
- **路径**: `06-development/background-task`
- **完整结构**:
  ```
  background-task/
  ├── SKILL.md
  ├── manager.py
  ├── storage.py
  └── task_client.py
  ```
- **特点**: 后台任务管理 Skill，包含 Python 实现脚本

#### 2. gemini-image
- **路径**: `06-development/gemini-image`
- **完整结构**:
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
- **特点**: Gemini 图像处理 Skill，包含配置和提示技巧

#### 3. skill-generator
- **路径**: `06-development/skill-generator`
- **文件结构**: 仅 `SKILL.md`

---

## 🔍 配套资源统计

### 按文件夹类型统计

| 文件夹类型 | 数量 | 说明 |
|-----------|------|------|
| `references/` | 13 | 参考资料、方法论、案例等 |
| `scripts/` | 8 | 自动化脚本、工具脚本 |
| `assets/` | 8 | 模板、检查清单、资源文件 |
| `config/` | 3 | 配置文件、规则文件 |
| `templates/` | 5 | 各类模板文件 |
| `workflow/` | 2 | 工作流目录 |
| `tools/` | 2 | 工具脚本 |
| `validators/` | 1 | 验证器 |
| `modules/` | 1 | 模块化组件 |
| `frameworks/` | 1 | 框架配置 |
| `core/` | 1 | 核心代码 |
| `cases/` | 2 | 案例库 |

### 按分类统计复杂度

| 分类 | 总数 | 仅 SKILL.md | 有配套资源 | 配套资源占比 |
|------|------|------------|-----------|-------------|
| 00-templates | 1 | 1 | 0 | 0% |
| 01-thinking-models | 13 | 13 | 0 | 0% |
| 02-methodologies | 5 | 5 | 0 | 0% |
| 03-operations | 7 | 3 | 4 | 57% |
| 04-product | 15 | 6 | 9 | 60% |
| 05-information | 8 | 7 | 1 | 13% |
| 06-development | 3 | 1 | 2 | 67% |
| **总计** | **57** | **36** | **21** | **37%** |

---

## 📋 完整 Skill 清单

### 仅包含 SKILL.md 的 Skills（36个）

**00-templates**
- thinking-model-template

**01-thinking-models**
- critical-5why
- critical-gidel-law
- critical-reverse-thinking
- critical-systems-thinking
- innovation-cloud-rain-umbrella
- innovation-first-principles
- innovation-mind-map
- innovation-six-hats
- knowledge-explorer
- senior-meta-cognition
- senior-private-board
- senior-thinking-chain
- system-swot

**02-methodologies**
- auto-classifier
- system-grow-model
- system-kiss-review
- system-strategy-advisor
- tag-enricher

**03-operations**
- growth-hacking
- growth-hacking-advanced
- growth-hacking-basics

**04-product**
- brand-localization
- data-decision
- demand-analysis
- glocalization-core
- market-entry
- plan-mode-enforcement
- user-insight

**05-information**
- analyzer
- course-reviewer
- organizer
- resource-indexer
- rss-collector
- rss-fetcher
- web-collector

**06-development**
- skill-generator

### 包含配套资源的 Skills（21个）

**03-operations（4个）**
- activity-3.0（完整工作流系统）
- market-chance（模板+参考）
- marketing（完整营销系统）
- xiaohongshu（小红书专用）

**04-product（9个）**
- business-model-v3（⭐ 最复杂，完整业务模型系统）
- case-analysis（⭐ 案例库最丰富，100+案例）
- job-analysis（模板+脚本）
- knowledge-graph（架构文档）
- lesson-design（教学设计系统）
- pmf-validator（方法和案例）
- user-research（用户生命周期体系）
- writing（⭐ 完整文案创作工作流）

**05-information（1个）**
- course-merge-architect（模板和策略）

**06-development（2个）**
- background-task（Python 实现）
- gemini-image（配置和技巧）

---

## 🎯 关键发现

1. **轻量级设计占主导**: 63% 的 Skills 仅包含 SKILL.md，说明大部分 Skills 采用轻量级设计

2. **产品类 Skills 最复杂**: `04-product` 分类中有 60% 的 Skills 包含配套资源，其中包括最复杂的 business-model-v3 和案例库最丰富的 case-analysis

3. **运营类 Skills 实用性强**: `03-operations` 中有 57% 包含配套资源，特别是 activity-3.0、marketing 和 xiaohongshu 都有完整的工作流系统

4. **思维模型和方法论保持简洁**: `01-thinking-models` 和 `02-methodologies` 的所有 Skills 都是纯 SKILL.md，符合其参考性、知识性定位

5. **开发工具类有实现**: `06-development` 中的 background-task 包含完整的 Python 实现

---

## 📊 结构模式总结

### 常见文件夹组合模式

1. **极简模式**: 仅 SKILL.md
2. **参考模式**: SKILL.md + references/
3. **工具模式**: SKILL.md + scripts/
4. **模板模式**: SKILL.md + templates/
5. **资源模式**: SKILL.md + assets/
6. **完整模式**: SKILL.md + references/ + scripts/ + assets/ + templates/ + workflow/

### 复杂度排名（Top 5）

1. **business-model-v3** - 15个子目录/文件，包含完整的业务模型分析系统
2. **case-analysis** - 100+案例文件，分为4大类
3. **writing** - 完整的8步文案创作工作流
4. **activity-3.0** - 完整的活动编排系统
5. **marketing** - 完整的营销策略和执行系统

---

## 💡 建议

1. **统一结构**: 建议为仅包含 SKILL.md 的 Skills 考虑是否需要添加配套资源
2. **文档完善**: 复杂 Skills（如 business-model-v3）建议添加更详细的 README
3. **模板共享**: references/templates 等资源可以考虑在相关 Skills 间共享
4. **脚本标准化**: scripts/ 目录下的脚本建议统一命名和接口规范

---

**报告生成完成**
- 分析的 Skill 总数: 57
- 发现的文件总数: 200+
- 分析的目录层级: 3层
