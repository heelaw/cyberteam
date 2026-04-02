#!/bin/bash

# 检查活动运营工作流状态
# 此脚本应在用户的当前工作目录 (CWD) 中运行
WORKFLOW_DIR="./workflow"

echo "🔍 正在检查活动运营工作流状态..."
echo "工作流目录：$(pwd)/$WORKFLOW_DIR"
echo "=================================="

# 检查工作流目录是否存在
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ 工作流目录不存在：$WORKFLOW_DIR"
    echo "请先运行 create-dirs.sh 创建目录结构"
    exit 1
fi

# 定义阶段信息
STAGES=(
    "00-init: 工作流初始化"
    "01-goal-analysis: 目标与发力点分析"
    "02-play-design: 活动玩法设计"
    "03-mechanism-design: 支线玩法与机制设计"
    "04-execution-plan: 活动执行计划"
    "05-promotion-plan: 预热与推广方案"
    "06-data-monitoring: 数据监测与优化方案"
    "07-closure-review: 活动收尾与复盘"
)

# 检查每个阶段
for stage in "${STAGES[@]}"; do
    # 分离阶段目录和名称
    stage_dir=$(echo "$stage" | cut -d: -f1)
    stage_name=$(echo "$stage" | cut -d: -f2 | sed 's/^ //')

    # 检查目录是否存在
    if [ -d "$WORKFLOW_DIR/$stage_dir" ]; then
        # 检查目录是否有文件
        file_count=$(ls -la "$WORKFLOW_DIR/$stage_dir" | grep -v "^total" | grep -v "^d" | wc -l)

        if [ $file_count -gt 0 ]; then
            echo "✅ $stage_name: 已完成 ($file_count 个文件)"
            # 显示具体文件名
            ls -la "$WORKFLOW_DIR/$stage_dir" 2>/dev/null | grep -v "^total" | grep -v "^d" | awk '{print "   - " $9}'
        else
            echo "⏸️ $stage_name: 未完成 (目录已创建，无文件)"
        fi
    else
        echo "❌ $stage_name: 未开始 (目录不存在)"
    fi
done

echo "=================================="
echo "📊 活动运营工作流状态检查完成！"
