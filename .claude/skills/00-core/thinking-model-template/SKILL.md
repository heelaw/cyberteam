# {思维模型中文名称}

# ========================================
# 思维模型 Skill 通用模板
# ========================================
# 版本: 1.0.0
# 最后更新: 2025-02-05
# 说明: 所有思维模型 Skill 的基础模板
# 使用方法: 复制此模板，填写 {占位符} 内容
# ========================================

# ========================================
# 元数据部分（必填）
# ========================================
name: "{思维模型中文名称}"
name_en: "{thinking-model-name}"
version: "1.0.0"
category: "{批判分析组/创新突破组/系统整合组/高级顾问组}"
sub_category: "{子分类}"
difficulty: "{入门/进阶/高级}"
author: "作者名称"
description: "用一句话描述这个思维模型的核心价值"

# ========================================
# 思维模型定义
# ========================================
thinking_model:
  name: "{思维模型名称}"
  name_en: "{Model Name}"

  origin: "{起源/创始人/历史背景}"
  example: "亚里士多德/丰田喜一郎/爱德华·德波纳"

  core_principle: |
    "{核心原理的完整描述}
    包含：
    - 基本假设
    - 核心方法论
    - 关键特征"

  key_concepts:
    - concept: "{关键概念1}"
      definition: "{定义}"
      example: "{示例}"

    - concept: "{关键概念2}"
      definition: "{定义}"
      example: "{示例}"

  best_for:
    - "{适用场景1}"
    - "{适用场景2}"
    - "{适用场景3}"

  not_for:
    - "{不适用场景1}"
    - "{不适用场景2}"

# ========================================
# 标签
# ========================================
tags:
  - "{标签1}"
  - "{标签2}"
  - "{标签3}"

estimated_time: "{预计耗时，如：3-5分钟}"

# ========================================
# 依赖关系
# ========================================
dependencies:
  precedes:           # 这个模型之前应该用什么
    - "{模型A}"
    - "{模型B}"

  follows:            # 这个模型之后应该用什么
    - "{模型C}"
    - "{模型D}"

  best_pair:          # 最佳搭档
    - "{模型E}"

  conflicts_with:     # 可能冲突
    - "{模型F}"

# ========================================
# 协作配置
# ========================================
collaboration:
  debate_style: "{质疑型/补充型/整合型/验证型}"

  can_question:
    - "可以质疑的模型类型或内容"
    - "可以质疑的假设类型"

  can_supplement:
    - "可以补充的维度"
    - "可以深化的方面"

  can_integrate:
    - "可以整合的内容类型"

# ========================================
# 核心能力
# ========================================
capabilities:
  - name: "{主要能力1}"
    description: "{能力描述}"
    input_format: "{输入格式要求}"
    output_format: "{输出格式}"

  - name: "{主要能力2}"
    description: "{能力描述}"
    input_format: "{输入格式要求}"
    output_format: "{输出格式}"

# ========================================
# 分析流程
# ========================================
analysis_workflow:
  # 步骤1: 准备
  step_1_preparation:
    name: "准备阶段"
    actions:
      - action: "{具体动作1}"
        description: "{动作说明}"

      - action: "{具体动作2}"
        description: "{动作说明}"

    output: "{本步骤的产出}"

  # 步骤2: 分析
  step_2_analysis:
    name: "核心分析阶段"
    methodology: |
      "{详细的分析方法论}
      - 步骤2.1: ...
      - 步骤2.2: ...
      - 步骤2.3: ..."

    techniques:
      - technique: "{技术1}"
        description: "{技术说明}"
        example: "{示例}"

      - technique: "{技术2}"
        description: "{技术说明}"
        example: "{示例}"

    output: "{本步骤的产出}"

  # 步骤3: 验证
  step_3_validation:
    name: "验证阶段"
    validation_methods:
      - method: "{验证方法1}"
        criteria: "{验证标准}"

      - method: "{验证方法2}"
        criteria: "{验证标准}"

    output: "{本步骤的产出}"

  # 步骤4: 输出
  step_4_output:
    name: "输出生成阶段"
    output_format: |
      ## {输出模板标题}

      ### 核心洞察
      - 洞察1: ...
      - 洞察2: ...

      ### 详细分析
      {详细分析内容}

      ### 关键结论
      - 结论1: ...
      - 结论2: ...

# ========================================
# 输入输出定义
# ========================================
input_schema:
  # 必需输入
  required:
    - field: problem_description
      type: string
      description: "{如何理解问题描述}"
      example: "{问题描述示例}"

    - field: context
      type: object
      description: "{需要哪些背景信息}"
      properties:
        domain: string
        constraints: array

  # 可选输入
  optional:
    - field: previous_analysis
      type: object
      description: "{如何使用前序分析}"
      properties:
        model_name: string
        insights: array
        questions: array

    - field: user_questions
      type: array
      description: "{用户的具体问题}"
      example: ["问题1", "问题2"]

output_schema:
  # 主要输出
  main_output:
    section: "分析结果"
    format: |
      ## 🎯 {思维模型名称} 分析

      ### 核心洞察
      {核心洞察列表}

      ### 详细分析
      {详细分析内容}

      ### 关键结论
      {关键结论列表}

  # 协作输出
  collaboration_output:
    section: "协作内容"

    critique:
      description: "对前序分析的质疑或补充"
      format: |
        ### 对前序分析的观点

        #### 质疑/补充
        - 针对 {目标模型} 的分析：
          - {具体质疑/补充点1}
          - {具体质疑/补充点2}

        #### 验证
        - {验证的内容}

    next_questions:
      description: "给下一轮模型的疑问"
      format: |
        ### 给下一轮的关键疑问
        ❓ {疑问1}
        ❓ {疑问2}

    confidence:
      type: number
      scale: [1, 5]
      description: "本次分析的置信度"

# ========================================
# 质量标准
# ========================================
quality_standards:
  depth_indicators:
    level_1_surface:
      description: "{表面分析的描述}"
      example: "{表面分析示例}"

    level_2_intermediate:
      description: "{中等深度的描述}"
      example: "{中等深度示例}"

    level_3_deep:
      description: "{深度分析的描述}"
      example: "{深度分析示例}"

    level_4_profound:
      description: "{深刻洞察的描述}"
      example: "{深刻洞察示例}"

  quality_checks:
    before_output:
      - check: "{质量检查项1}"
        criteria: "{检查标准}"

      - check: "{质量检查项2}"
        criteria: "{检查标准}"

    after_output:
      - check: "输出完整性"
        criteria: "包含所有必需部分"

      - check: "逻辑一致性"
        criteria: "无明显矛盾"

      - check: "实用性"
        criteria: "可转化为行动"

# ========================================
# 知识库配置
# ========================================
knowledge_base:
  theory:
    path: "/knowledge/{model-name}/theory.md"
    content:
      - section: "起源与历史"
      - section: "核心原理"
      - section: "学术依据"
      - section: "代表性应用"

  cases:
    path: "/cases/{model-name}.json"
    format:
      - case_title: string
        background: string
        analysis_process: string
        key_insights: array
        final_result: string

  exercises:
    path: "/exercises/{model-name}.md"
    content:
      - exercise: string
        difficulty: string
        solution: string

# ========================================
# 提示词模板
# ========================================
prompt_template: |
  # 你是 {name}，一个专业的 {thinking_model} 思维模型教练

  ## 你的角色
  {role_description}

  ## 你的核心能力
  {capabilities_description}

  ## 你需要遵循的分析流程
  {analysis_workflow}

  ## 输入信息
  用户问题：{problem_description}
  背景信息：{context}
  前序分析：{previous_analysis}

  ## 你的任务
  请按照以下步骤进行分析：

  ### 步骤1: {step_1_name}
  {step_1_instructions}

  ### 步骤2: {step_2_name}
  {step_2_instructions}

  ### 步骤3: {step_3_name}
  {step_3_instructions}

  ## 输出要求
  请严格按照以下格式输出：

  {output_format_template}

  ## 协作要求
  如果有前序分析，请：
  - 质疑其关键假设
  - 补充其未覆盖的维度
  - 验证其结论的可靠性

  给下一轮模型的疑问：
  - 明确列出需要进一步探讨的问题
  - 指出需要验证的假设
  - 提出需要深化的方向

  ## 质量标准
  - 分析深度：{depth_requirement}
  - 逻辑严密性：{logic_requirement}
  - 证据充分性：{evidence_requirement}

  现在请开始你的分析。

# ========================================
# 使用示例
# ========================================
usage_examples:
  - example: 1
    name: "{示例名称1}"
    scenario: "{场景描述}"
    input:
      problem_description: "{问题}"
      context: "{背景}"

    output:
      core_insights: ["洞察1", "洞察2"]
      detailed_analysis: "{分析内容}"
      conclusions: ["结论1", "结论2"]

  - example: 2
    name: "{示例名称2}"
    scenario: "{场景描述}"
    input:
      problem_description: "{问题}"
      context: "{背景}"

    output:
      core_insights: ["洞察1", "洞察2"]
      detailed_analysis: "{分析内容}"
      conclusions: ["结论1", "结论2"]

# ========================================
# 注意事项
# ========================================
notes:
  general:
    - "{注意事项1}"
    - "{注意事项2}"

  common_mistakes:
    - mistake: "{常见错误1}"
      solution: "{解决方案}"

    - mistake: "{常见错误2}"
      solution: "{解决方案}"

  best_practices:
    - "{最佳实践1}"
    - "{最佳实践2}"

# ========================================
# 更新日志
# ========================================
changelog:
  - version: "1.0.0"
    date: "2025-02-05"
    changes:
      - "初始版本"

# ========================================
# 扩展配置
# ========================================
extensions:
  custom_parameters:
    - name: "{参数名}"
      type: "{类型}"
      default: "{默认值}"
      description: "{参数说明}"

  integrations:
    - system: "{集成系统}"
      description: "{集成说明}"

  advanced_features:
    - feature: "{高级特性}"
      description: "{特性说明}"
      enable: true/false

# ========================================
# 模板使用说明
# ========================================
template_usage_guide: |
  ## 如何使用这个模板创建新的思维模型 Skill

  ### 步骤1: 复制模板
  将此文件复制为: {category}-{model-name}.skill
  例如: critical-first-principles.skill

  ### 步骤2: 填写元数据
  替换所有 {占位符} 为实际内容
  必填字段: name, name_en, version, category, description

  ### 步骤3: 定义思维模型
  详细描述思维模型的原理、方法、适用场景

  ### 步骤4: 实现分析流程
  编写具体的分析步骤和方法论

  ### 步骤5: 定义输入输出
  明确需要什么输入，产生什么输出

  ### 步骤6: 准备知识库
  创建理论知识、案例、练习

  ### 步骤7: 编写提示词模板
  将所有内容整合成可用的提示词

  ### 步骤8: 测试验证
  使用示例测试，确保输出符合预期

  ### 步骤9: 注册到指挥官系统
  在协作协议中注册这个新模型

  ### 步骤10: 文档完善
  编写 README、THEORY、CASES 等文档

# ========================================
# 结束标记
# ========================================
_end_of_template_
