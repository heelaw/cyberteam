#!/bin/bash

# 验证输出文件完整性
WORKFLOW_DIR="../workflow"

echo "🔍 正在验证输出文件完整性..."
echo "工作流目录：$WORKFLOW_DIR"
echo "=================================="

# 定义预期的输出文件模式
EXPECTED_FILES=(
    "00-init/*-init.md"
    "01-user-research/*-user-research.md"
    "02-selling-points/*-selling-points.md"
    "03-pain-points/*-pain-points.md"
    "04-strategy/*-strategy.md"
    "05-channel-strategy/*-channel-strategy.md"
    "06-draft/*-draft.md"
    "07-final/*-final.md"
    "08-tracking/*-tracking.md"
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
echo "📊 输出文件验证完成！"
