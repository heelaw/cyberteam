#!/bin/bash

# 创建活动运营工作流所需的目录结构
# 此脚本应在用户的当前工作目录 (CWD) 中运行
WORKFLOW_DIR="./workflow"

echo "🔧 正在创建活动运营工作流目录结构..."
echo "工作流目录：$(pwd)/$WORKFLOW_DIR"
echo "=================================="

# 创建阶段目录
mkdir -p "$WORKFLOW_DIR/00-init"
mkdir -p "$WORKFLOW_DIR/01-goal-analysis"
mkdir -p "$WORKFLOW_DIR/02-play-design"
mkdir -p "$WORKFLOW_DIR/03-mechanism-design"
mkdir -p "$WORKFLOW_DIR/04-execution-plan"
mkdir -p "$WORKFLOW_DIR/05-promotion-plan"
mkdir -p "$WORKFLOW_DIR/06-data-monitoring"
mkdir -p "$WORKFLOW_DIR/07-closure-review"

echo "✅ 活动运营工作流目录结构已创建完成！"
echo "目录位置：$(pwd)/$WORKFLOW_DIR"
echo "包含以下阶段目录："
echo "- 00-init: 工作流初始化"
echo "- 01-goal-analysis: 目标与发力点分析"
echo "- 02-play-design: 活动玩法设计"
echo "- 03-mechanism-design: 支线玩法与机制设计"
echo "- 04-execution-plan: 活动执行计划"
echo "- 05-promotion-plan: 预热与推广方案"
echo "- 06-data-monitoring: 数据监测与优化方案"
echo "- 07-closure-review: 活动收尾与复盘"
echo "=================================="
