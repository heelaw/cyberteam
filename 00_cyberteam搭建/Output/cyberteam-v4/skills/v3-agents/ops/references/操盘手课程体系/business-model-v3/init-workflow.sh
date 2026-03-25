#!/bin/bash

# 工作流初始化脚本
# 用于创建业务模型梳理工作流的目录结构

echo "正在初始化业务模型梳理工作流..."

# 获取当前目录
CURRENT_DIR=$(pwd)

# 创建输出目录结构
echo "创建输出目录结构..."
mkdir -p output/00-init
mkdir -p output/01-business-model
mkdir -p output/02-revenue-formula
mkdir -p output/03-conversion-funnel
mkdir -p output/04-operational-metrics
mkdir -p output/05-breakthrough-points
mkdir -p output/06-final-report

echo "输出目录结构创建完成！"
echo ""
echo "目录结构如下："
find output -type d | sort
echo ""
echo "工作流初始化完成！您可以开始使用 /new 命令开始新的业务模型梳理工作流。"
