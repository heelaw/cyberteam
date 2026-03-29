#!/bin/bash

# 检查工作流状态
WORKFLOW_DIR="../workflow"

echo "🔍 正在检查工作流状态..."
echo "工作流目录：$WORKFLOW_DIR"
echo "=================================="

# 定义阶段信息
STAGES=(
    "00-init: 工作流初始化"
    "01-user-research: 用户需求挖掘"
    "02-selling-points: 产品卖点挖掘"
    "03-pain-points: 痛点定位"
    "04-strategy: 需求类型判断"
    "05-channel-strategy: 场景与渠道分析"
    "06-draft: 文案撰写"
    "07-final: 文案优化"
    "08-tracking: 效果追踪与迭代"
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
        else
            echo "⏸️ $stage_name: 未完成 (目录已创建，无文件)"
        fi
    else
        echo "❌ $stage_name: 未开始 (目录不存在)"
    fi
done

echo "=================================="
echo "📊 工作流状态检查完成！"
