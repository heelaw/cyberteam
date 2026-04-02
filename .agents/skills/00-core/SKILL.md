# 问题分类器

# ========================================
# 思维指挥官 Skill 体系 - 问题分类器
# ========================================
# 版本: 1.0.0
# 最后更新: 2025-02-05
# 作者: 思维指挥官体系
# 分类: 指挥官层
# ========================================

name: "问题分类器"
name_en: "problem-classifier"
version: "1.0.0"
category: "coordinator"
sub_category: "问题分析"
difficulty: "进阶"
author: "思维指挥官体系"
description: "分析用户问题，识别问题类型、复杂度、紧急度，为后续协作提供基础"

# ========================================
# 核心能力
# ========================================
capabilities:
  - name: "问题类型识别"
    description: "识别问题属于创新突破、原因分析、方案决策、系统优化、全面战略中的哪一种"
    input_format: "用户问题描述 + 背景信息"
    output_format: "问题类型 + 关键词 + 置信度"

  - name: "复杂度评估"
    description: "评估问题的复杂程度：简单、中等、复杂、系统级"
    input_format: "问题描述 + 相关因素"
    output_format: "复杂度等级 + 评估理由"

  - name: "紧急度判断"
    description: "判断问题的紧急程度"
    input_format: "问题描述 + 用户标注"
    output_format: "紧急度等级"

  - name: "关键词提取"
    description: "提取问题中的关键信息"
    input_format: "问题描述"
    output_format: "关键词列表"

# ========================================
# 问题类型分类规则
# ========================================
problem_type_rules:
  # 创新突破型
  innovation_breakthrough:
    keywords:
      - "如何"
      - "新"
      - "创新"
      - "突破"
      - "重新"
      - "颠覆"
      - "创造"
      - "设计"
      - "打造"
      - "构建"

    patterns:
      - "如何.*新的"
      - "怎样.*创新"
      - "重新.*设计"
      - "突破.*限制"
      - "创造.*模式"

    characteristics:
      - "寻求新的可能性"
      - "不满足现有方案"
      - "想要改变现状"
      - "需要创造性思维"

    example: "如何重新设计我们的用户增长策略？"

  # 原因分析型
  root_cause_analysis:
    keywords:
      - "为什么"
      - "原因"
      - "问题"
      - "不"
      - "失败"
      - "错误"
      - "缺陷"
      - "瓶颈"
      - "障碍"

    patterns:
      - "为什么.*不"
      - ".*的原因"
      - ".*问题.*在哪"
      - "如何解决.*问题"
      - ".*为什么.*失败"

    characteristics:
      - "已经出现问题"
      - "需要找到根本原因"
      - "寻求解释和理解"
      - "关注过去和现在"

    example: "为什么用户留存率持续下降？"

  # 方案决策型
  decision_making:
    keywords:
      - "选择"
      - "决策"
      - "哪个"
      - "是否"
      - "应该"
      - "比较"
      - "评估"
      - "优选"

    patterns:
      - "选择.*还是"
      - "是否应该"
      - "哪个.*更好"
      - "比较.*和"
      - "评估.*方案"

    characteristics:
      - "面临多个选项"
      - "需要做出选择"
      - "权衡利弊"
      - "寻求最优解"

    example: "应该选择自研还是外包技术方案？"

  # 系统优化型
  system_optimization:
    keywords:
      - "优化"
      - "改进"
      - "提升"
      - "效率"
      - "改善"
      - "增强"
      - "提高"
      - "加速"

    patterns:
      - "如何.*优化"
      - "提升.*效率"
      - "改进.*流程"
      - ".*更好的.*"
      - "加快.*速度"

    characteristics:
      - "现有系统运行但不够好"
      - "追求更好的表现"
      - "渐进式改进"
      - "关注效率和效果"

    example: "如何优化我们的产品开发流程？"

  # 全面战略型
  comprehensive_strategy:
    keywords:
      - "战略"
      - "规划"
      - "发展"
      - "未来"
      - "长期"
      - "愿景"
      - "路线图"
      - "布局"

    patterns:
      - ".*战略.*规划"
      - "未来发展.*方向"
      - "制定.*战略"
      - ".*长期.*规划"
      - ".*整体.*布局"

    characteristics:
      - "涉及长远发展"
      - "需要全局视角"
      - "影响面广"
      - "复杂度高"

    example: "如何制定公司未来三年的发展战略？"

# ========================================
# 复杂度评估规则
# ========================================
complexity_assessment_rules:
  simple:
    score_range: [1, 3]
    characteristics:
      - "单一维度问题"
      - "因素明确"
      - "影响范围小"
      - "可以快速解决"
    examples:
      - "选择一个工具"
      - "解决小bug"
      - "优化单个功能"

  medium:
    score_range: [4, 6]
    characteristics:
      - "多个相关维度"
      - "需要一些分析"
      - "影响中等范围"
      - "需要时间思考"
    examples:
      - "改进工作流程"
      - "提升团队效率"
      - "解决用户投诉"

  complex:
    score_range: [7, 8]
    characteristics:
      - "多维度交织"
      - "涉及系统性问题"
      - "影响范围大"
      - "需要深入分析"
    examples:
      - "转型商业模式"
      - "重构组织架构"
      - "解决产品困境"

  systemic:
    score_range: [9, 10]
    characteristics:
      - "系统级问题"
      - "涉及多个系统"
      - "影响整体"
      - "需要全面分析"
    examples:
      - "企业数字化转型"
      - "行业战略布局"
      - "生态系统构建"

# ========================================
# 分析流程
# ========================================
analysis_workflow:
  step_1_understand_problem:
    name: "理解问题"
    actions:
      - "仔细阅读用户的问题描述"
      - "提取核心问题点"
      - "识别问题的主体、客体、目标"

    output: "问题理解摘要"

  step_2_extract_keywords:
    name: "提取关键词"
    actions:
      - "识别问题类型关键词"
      - "提取关键概念"
      - "标注重要修饰词"

    output: "关键词列表"

  step_3_match_patterns:
    name: "匹配模式"
    actions:
      - "将问题与各类问题模式匹配"
      - "计算匹配度"
      - "识别主要和次要模式"

    output: "模式匹配结果"

  step_4_assess_complexity:
    name: "评估复杂度"
    actions:
      - "识别问题涉及的因素数量"
      - "评估问题的深度要求"
      - "判断影响范围"
      - "给出复杂度评分"

    output: "复杂度评估"

  step_5_determine_urgency:
    name: "判断紧急度"
    actions:
      - "检查用户是否标注紧急度"
      - "从问题描述中判断紧急性"
      - "考虑问题的时间敏感性"

    output: "紧急度判断"

  step_6_generate_classification:
    name: "生成分类结果"
    actions:
      - "综合所有分析"
      - "给出分类结论"
      - "提供分类理由"

    output: "最终分类结果"

# ========================================
# 输出格式
# ========================================
output_format: |
  ## 🎯 问题分类结果

  ### 问题类型
  **类型**: {problem_type}
  **置信度**: {confidence_score}%

  **识别依据**:
  - 关键词匹配: {matched_keywords}
  - 模式匹配: {matched_patterns}
  - 特征识别: {identified_characteristics}

  ### 复杂度评估
  **等级**: {complexity_level}
  **评分**: {complexity_score}/10

  **评估理由**:
  - 涉及因素: {factors_count}个
  - 问题深度: {depth_level}
  - 影响范围: {scope}
  - 分析需求: {analysis_requirement}

  ### 紧急度判断
  **等级**: {urgency_level}

  **判断依据**:
  - 用户标注: {user_label}
  - 问题特征: {urgency_indicators}
  - 时间敏感性: {time_sensitivity}

  ### 关键词提取
  {extracted_keywords}

  ### 推荐协作方向
  **建议类型**: {recommended_collaboration_type}
  **预计轮次**: {estimated_rounds}
  **预计耗时**: {estimated_time}

  **推荐模型组合**:
  {recommended_models}

# ========================================
# 提示词模板
# ========================================
prompt_template: |
  # 你是问题分类器，专门负责分析用户问题并进行分类

  ## 你的任务
  分析用户提供的问题，给出详细的分类结果。

  ## 用户问题
  {problem_description}

  ## 背景信息
  {context}

  ## 分析要求

  ### 1. 问题类型识别
  从以下类型中选择最匹配的一个：
  - 创新突破型: 寻求新可能性、创新、突破
  - 原因分析型: 找问题、寻原因、求解释
  - 方案决策型: 做选择、做比较、求最优
  - 系统优化型: 求改进、提效率、优效果
  - 全面战略型: 定战略、做规划、谋长远

  ### 2. 复杂度评估
  评估问题复杂度：
  - 简单 (1-3分): 单一维度、因素明确、快速解决
  - 中等 (4-6分): 多个维度、需要分析、影响中等
  - 复杂 (7-8分): 多维交织、系统问题、深入分析
  - 系统级 (9-10分): 系统级问题、全面分析、影响整体

  ### 3. 紧急度判断
  判断问题紧急程度：
  - immediate: 立即处理
  - urgent: 紧急但不需立即
  - normal: 正常优先级
  - low: 低优先级

  ### 4. 关键词提取
  提取问题中的关键信息

  ### 5. 推荐协作方向
  基于分类结果，推荐合适的思维模型组合

  ## 输出格式
  请严格按照以下格式输出：

  {output_format_template}

  ## 质量要求
  - 分类准确度高 (>= 85%)
  - 理由充分清晰
  - 推荐合理可行

  现在开始分析。

# ========================================
# 使用示例
# ========================================
usage_examples:
  - example: 1
    name: "原因分析型问题"
    input:
      problem_description: "我的团队技术能力很强，但产品总是做不出来，该怎么办？"
      context:
        domain: "产品管理"
        situation: "初创公司"

    expected_output:
      problem_type: "原因分析型"
      complexity: "medium"
      urgency: "urgent"
      keywords: ["团队", "技术能力", "产品", "做不出来"]
      recommended_models: ["吉德林法则", "5Why分析", "系统思维"]

  - example: 2
    name: "创新突破型问题"
    input:
      problem_description: "如何用AI重新设计我们的客户服务流程？"
      context:
        domain: "客户服务"
        situation: "传统企业"

    expected_output:
      problem_type: "创新突破型"
      complexity: "complex"
      urgency: "normal"
      keywords: ["AI", "重新设计", "客户服务", "流程"]
      recommended_models: ["第一性原理", "六顶思考帽", "创新思维"]

# ========================================
# 注意事项
# ========================================
notes:
  general:
    - "一个问题可能具有多种类型特征，选择最主要的"
    - "当不确定时，选择复杂度更高的类型"
    - "用户标注的优先级应该被尊重"
    - "关键词提取要准确且全面"

  common_mistakes:
    - mistake: "仅根据关键词判断，忽视上下文"
      solution: "综合考虑问题完整语境"

    - mistake: "复杂度评估过于保守"
      solution: "考虑隐性因素，适当提高复杂度"

    - mistake: "忽视用户的明确标注"
      solution: "用户标注优先于自动判断"

  best_practices:
    - "先理解问题本质，再进行分类"
    - "当问题模糊时，询问用户澄清"
    - "保持分类一致性"
    - "记录分类依据便于追溯"

# ========================================
# 更新日志
# ========================================
changelog:
  - version: "1.0.0"
    date: "2025-02-05"
    changes:
      - "初始版本"
      - "实现5种问题类型分类"
      - "实现4级复杂度评估"
      - "实现关键词提取"
