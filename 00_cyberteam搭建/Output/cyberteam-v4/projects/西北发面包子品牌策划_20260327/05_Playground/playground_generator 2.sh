#!/bin/bash
# Playground 自动生成触发脚本
# 在 CyberTeam 任务完成后调用此脚本生成 Playground

PROJECT_DIR="$1"
PLAYGROUND_DIR="$2"

if [ -z "$PROJECT_DIR" ]; then
    echo "用法: ./generate_playground.sh <项目目录> [Playground目录]"
    exit 1
fi

# 默认 Playground 目录
if [ -z "$PLAYGROUND_DIR" ]; then
    PLAYGROUND_DIR="$PROJECT_DIR/05_Playground"
fi

# 创建目录
mkdir -p "$PLAYGROUND_DIR"

# 获取项目名称
PROJECT_NAME=$(basename "$PROJECT_DIR")

# 生成时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 输出文件
OUTPUT_FILE="$PLAYGROUND_DIR/活动看板_${PROJECT_NAME}_${TIMESTAMP}.html"

echo "🎯 生成 Playground..."
echo "   项目: $PROJECT_NAME"
echo "   输出: $OUTPUT_FILE"

# 调用 Python 生成器
python3 "$(dirname "$0")/generate_playground.py" \
    --project "$PROJECT_DIR" \
    --output "$OUTPUT_FILE" \
    --template "$(dirname "$0")/活动看板_v8.html"

if [ $? -eq 0 ]; then
    echo "✅ Playground 生成成功: $OUTPUT_FILE"
else
    echo "❌ Playground 生成失败"
    exit 1
fi