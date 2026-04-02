#!/bin/bash

# 验证活动运营工作流输出文件完整性
# 此脚本应在用户的当前工作目录 (CWD) 中运行
WORKFLOW_DIR="./workflow"

echo "🔍 正在验证活动运营工作流输出文件完整性..."
echo "工作流目录：$(pwd)/$WORKFLOW_DIR"
echo "=================================="

# 检查工作流目录是否存在
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ 工作流目录不存在：$WORKFLOW_DIR"
    echo "请先运行 create-dirs.sh 创建目录结构"
    exit 1
fi

# 定义预期的输出文件模式
EXPECTED_FILES=(
    "00-init/*-init.md"
    "01-goal-analysis/*-goal-analysis.md"
    "02-play-design/*-play-design.md"
    "03-mechanism-design/*-mechanism-design.md"
    "04-execution-plan/*-execution-plan.md"
    "05-promotion-plan/*-promotion-plan.md"
    "06-data-monitoring/*-data-monitoring.md"
    "07-closure-review/*-closure-review.md"
)

# 检查每个预期文件
for pattern in "${EXPECTED_FILES[@]}"; do
    # 分离阶段目录和文件模式
    stage_dir=$(echo "$pattern" | cut -d/ -f1)
    file_pattern=$(echo "$pattern" | cut -d/ -f2)

    # 检查是否有匹配的文件
    matching_files=$(ls -la "$WORKFLOW_DIR/$stage_dir/$file_pattern" 2>/dev/null | grep -v "^total" | wc -l)

    if [ $matching_files -gt 0 ]; then
        echo "✅ $stage_dir: 找到 $matching_files 个匹配文件"
        # 显示具体文件名
        ls -la "$WORKFLOW_DIR/$stage_dir/$file_pattern" 2>/dev/null | grep -v "^total" | awk '{print "   - " $9}'
    else
        echo "❌ $stage_dir: 未找到匹配文件 ($file_pattern)"
    fi
done

echo "=================================="
echo "📊 活动运营工作流输出文件验证完成！"
