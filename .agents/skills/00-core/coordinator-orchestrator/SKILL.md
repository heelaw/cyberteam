# ========================================
# 思维指挥官 Skill 体系 - 协作编排器
# ========================================
# 版本: 1.0.0
# 最后更新: 2025-02-05
# 分类: 指挥官层
# ========================================

name: "协作编排器"
name_en: "collaboration-orchestrator"
version: "1.0.0"
category: "coordinator"
sub_category: "协作编排"
difficulty: "高级"
author: "思维指挥官体系"
description: "根据问题类型和复杂度，生成最优的思维模型协作序列"

# ========================================
# 核心能力
# ========================================
capabilities:
  - name: "序列生成"
    description: "生成思维模型的协作序列"
    input: "问题分类 + 用户偏好 + 时间限制"
    output: "协作序列计划"

  - name: "模型分配"
    description: "为每轮分配合适的思维模型"
    input: "协作阶段 + 可用模型"
    output: "模型分配方案"

  - name: "输出要求设定"
    description: "设定每轮的输出标准和质量检查点"
    input: "模型 + 阶段目标"
    output: "输出要求"

# ========================================
# 序列生成规则
# ========================================
sequence_generation:
  # 基于问题类型
  problem_type_sequences:
    innovation_breakthrough:
      name: "创新突破型"
      total_rounds: 6
      estimated_time: "4-5分钟"
      sequence:
        - round: 1
          phase: "problem_definition"
          models: ["吉德林法则", "第一性原理"]
          focus: "重新定义问题，识别创新机会"

        - round: 2
          phase: "cause_analysis"
          models: ["第一性原理", "逆向思维"]
          focus: "从本质思考，质疑常规"

        - round: 3-4
          phase: "solution_generation"
          models: ["第一性原理", "六顶思考帽", "思维导图"]
          focus: "多维度生成创新方案"

        - round: 5
          phase: "solution_evaluation"
          models: ["私董会天团", "系统思维"]
          focus: "评估方案的可行性和影响"

        - round: 6
          phase: "action_planning"
          models: ["GROW模型"]
          focus: "制定创新落地计划"

    root_cause_analysis:
      name: "原因分析型"
      total_rounds: 5
      estimated_time: "3-4分钟"
      sequence:
        - round: 1
          phase: "problem_definition"
          models: ["吉德林法则"]
          focus: "清晰定义核心问题"

        - round: 2-3
          phase: "cause_analysis"
          models: ["5Why分析", "系统思维", "逆向思维"]
          focus: "深挖根本原因"

        - round: 4
          phase: "solution_generation"
          models: ["第一性原理"]
          focus: "从本质重构解决方案"

        - round: 5
          phase: "action_planning"
          models: ["GROW模型", "KISS复盘"]
          focus: "制定改进行动计划"

    decision_making:
      name: "方案决策型"
      total_rounds: 5
      estimated_time: "3-4分钟"
      sequence:
        - round: 1
          phase: "problem_definition"
          models: ["吉德林法则"]
          focus: "明确决策问题"

        - round: 2-3
          phase: "solution_evaluation"
          models: ["SWOT分析", "六顶思考帽"]
          focus: "多维度评估选项"

        - round: 4
          phase: "solution_generation"
          models: ["私董会天团"]
          focus: "获取多元视角建议"

        - round: 5
          phase: "action_planning"
          models: ["GROW模型"]
          focus: "制定决策执行计划"

    system_optimization:
      name: "系统优化型"
      total_rounds: 5
      estimated_time: "3-4分钟"
      sequence:
        - round: 1
          phase: "problem_definition"
          models: ["吉德林法则", "系统思维"]
          focus: "系统性地定义问题"

        - round: 2
          phase: "cause_analysis"
          models: ["5Why分析"]
          focus: "分析系统原因"

        - round: 3
          phase: "solution_generation"
          models: ["第一性原理", "六顶思考帽"]
          focus: "生成优化方案"

        - round: 4
          phase: "solution_evaluation"
          models: ["SWOT分析", "系统思维"]
          focus: "评估系统影响"

        - round: 5
          phase: "action_planning"
          models: ["GROW模型", "KISS复盘"]
          focus: "制定迭代优化计划"

    comprehensive_strategy:
      name: "全面战略型"
      total_rounds: 7
      estimated_time: "5-6分钟"
      sequence:
        - round: 1
          phase: "problem_definition"
          models: ["吉德林法则", "第一性原理"]
          focus: "深度定义战略问题"

        - round: 2
          phase: "cause_analysis"
          models: ["5Why分析", "系统思维"]
          focus: "系统性分析现状"

        - round: 3-4
          phase: "solution_generation"
          models: ["第一性原理", "六顶思考帽", "思维导图"]
          focus: "生成多层次战略方案"

        - round: 5-6
          phase: "solution_evaluation"
          models: ["SWOT分析", "私董会天团", "战略顾问"]
          focus: "全面评估战略可行性"

        - round: 7
          phase: "action_planning"
          models: ["GROW模型", "KISS复盘"]
          focus: "制定战略执行路线图"

  # 基于复杂度的调整
  complexity_adjustments:
    simple:
      max_rounds: 3
      strategy: "单模型为主，快速解决"
      models_per_round: 1

    medium:
      max_rounds: 5
      strategy: "关键双模型协作"
      models_per_round: 1-2

    complex:
      max_rounds: 7
      strategy: "多模型深度协作"
      models_per_round: 2-3

    systemic:
      max_rounds: 10
      strategy: "全模型系统协作"
      models_per_round: 3-4
      use_all_models: true

# ========================================
# 输出格式
# ========================================
output_format: |
  ## 🎯 协作序列计划

  ### 问题分析
  - 问题类型: {problem_type}
  - 复杂度: {complexity}
  - 紧急度: {urgency}

  ### 协作概览
  - 总轮次: {total_rounds}
  - 预计耗时: {estimated_time}
  - 使用模型: {models_count}个

  ### 详细序列
  {rounds_details}

  ### 质量检查点
  {quality_checkpoints}

  ### 时间分配
  {time_allocation}

# ========================================
# 提示词模板
# ========================================
prompt_template: |
  # 你是协作编排器，负责规划思维模型的最优协作序列

  ## 输入信息
  问题分类: {problem_classification}
  用户偏好: {user_preferences}
  时间限制: {time_limit}秒

  ## 你的任务
  生成最优的协作序列，包括:
  1. 总轮次规划
  2. 每轮参与的模型
  3. 输出要求
  4. 质量检查点

  ## 序列生成规则
  根据问题类型选择基础序列，然后根据复杂度和时间限制进行调整。

  ## 输出要求
  请严格按照YAML格式输出协作序列。

  现在请生成协作序列。
