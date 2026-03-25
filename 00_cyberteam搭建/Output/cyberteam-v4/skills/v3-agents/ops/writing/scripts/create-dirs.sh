#!/bin/bash

# 创建工作流所需的目录结构
WORKFLOW_DIR="../workflow"

# 创建阶段目录
mkdir -p "$WORKFLOW_DIR/00-init"
mkdir -p "$WORKFLOW_DIR/01-user-research"
mkdir -p "$WORKFLOW_DIR/02-selling-points"
mkdir -p "$WORKFLOW_DIR/03-pain-points"
mkdir -p "$WORKFLOW_DIR/04-strategy"
mkdir -p "$WORKFLOW_DIR/05-channel-strategy"
mkdir -p "$WORKFLOW_DIR/06-draft"
mkdir -p "$WORKFLOW_DIR/07-final"
mkdir -p "$WORKFLOW_DIR/08-tracking"

echo "✅ 工作流目录结构已创建完成！"
echo "目录位置：$WORKFLOW_DIR"
echo "包含以下阶段目录："
echo "- 00-init: 工作流初始化"
echo "- 01-user-research: 用户需求挖掘"
echo "- 02-selling-points: 产品卖点挖掘"
echo "- 03-pain-points: 痛点定位"
echo "- 04-strategy: 需求类型判断"
echo "- 05-channel-strategy: 场景与渠道分析"
echo "- 06-draft: 文案撰写"
echo "- 07-final: 文案优化"
echo "- 08-tracking: 效果追踪与迭代"
