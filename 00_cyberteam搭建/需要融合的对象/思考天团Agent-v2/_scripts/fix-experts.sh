#!/bin/bash
#==============================================================================
# 思考天团 Expert Agent 批量修复脚本
# 功能: 为 experts/15-25 创建 assess/evals/refs 目录并生成标准文件
# 作者: 思考天团开发组
# 版本: v1.0
# 最后更新: 2026-03-21
#==============================================================================

set -e  # 遇到错误立即退出

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
AGENTS_DIR="$PROJECT_DIR/agents"
TEMPLATE_FILE="$SCRIPT_DIR/../_templates/expert-expansion-template.md"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

#-------------------------------------------------------------------------------
# 生成 CLI 命令、元数据Schema、Handoff协议 追加内容
#-------------------------------------------------------------------------------
generate_appendix() {
    local agent_num="$1"
    local agent_name="$2"
    local agent_model="$3"

    cat << 'APPENDIX'

---

## CLI命令定义

### 触发命令
| 命令 | 功能 | 用法 |
|------|------|------|
| /思考天团-[编号]-[英文名] | 启动专家分析 | /思考天团-15-opportunity-cost |

### 命令执行流程
```
用户输入 → 触发词识别 → Agent调度 → 专家分析 → 结果输出 → 交接下一个专家
```

### 错误处理
- 未知命令 → 返回可用命令列表
- 执行超时 → 返回部分结果 + 警告
- 置信度不足 → 请求用户补充信息

---

## 元数据Schema

```yaml
expert_id: "[编号]-[英文名]"
display_name: "[中文名]"
model: "[思维模型]"
capabilities:
  - [能力1]
  - [能力2]
triggers:
  primary:
    - "[触发词1]"
  secondary:
    - "[触发词2]"
integration:
  handoff_to: ["相邻专家列表"]
  can_collaborate: ["协作专家"]
version: "1.0"
```

### 实例
```yaml
expert_id: "15-opportunity-cost"
display_name: "机会成本决策专家"
model: "Opportunity Cost Theory"
capabilities:
  - 量化权衡决策利弊
  - 识别隐性机会成本
  - 沉没成本识别
triggers:
  primary:
    - "选择权衡"
    - "资源分配"
  secondary:
    - "犹豫不决"
    - "放弃评估"
integration:
  handoff_to:
    - "16-sunk-cost"
    - "22-pareto"
  can_collaborate:
    - "01-kahneman"
    - "04-swot-tows"
version: "1.0"
```

---

## 交接协议（Handoff）

### 输入Schema
```json
{
  "task": "分析任务",
  "context": {
    "decision_problem": "决策问题描述",
    "options": ["选项列表"],
    "constraints": ["约束条件"]
  },
  "previous_experts": ["已咨询的专家"],
  "user_id": "用户标识"
}
```

### 输出Schema
```json
{
  "expert_id": "[编号]-[英文名]",
  "insights": [
    "洞察1: ...",
    "洞察2: ...",
    "洞察3: ..."
  ],
  "confidence": 0.85,
  "key_findings": {
    "primary": "主要发现",
    "secondary": "次要发现"
  },
  "handoff": {
    "next_expert": "建议下一个专家",
    "reason": "交接原因",
    "urgency": "low|medium|high"
  }
}
```

### Handoff质量标准
- 所有洞察必须有时间戳
- 置信度必须附带理由
- next_expert 必须说明原因

---

## DevQA循环

### 自我检验清单
- [ ] **假设明确**: 每个结论的前提假设是否列出？
- [ ] **证据充分**: 关键断言是否有数据/案例支撑？
- [ ] **逻辑严密**: 推理链是否无跳跃？
- [ ] **遗漏检查**: 是否有反例被忽略？

### 置信度评估
| 置信度 | 等级 | 行动 |
|--------|------|------|
| < 0.6 | 低 | 返回用户补充信息 |
| 0.6-0.8 | 中 | 标注不确定领域 |
| > 0.8 | 高 | 正常输出 |

### 迭代优化
1. 初始输出 → 自我审查 → 发现不足 → 补充修正 → 最终输出
2. 每次迭代记录置信度变化

---

## 五级质量门禁

| 级别 | 触发条件 | 检查项 | 通过标准 |
|------|----------|--------|----------|
| L1 | 格式检查 | 触发词/输入/输出是否完整 | 3项全有 |
| L2 | 逻辑检查 | 推理链是否完整 | 前提→结论 清晰 |
| L3 | 证据检查 | 关键断言是否有依据 | 有来源/数据 |
| L4 | 交叉验证 | 是否与其他专家一致 | 无冲突或已标注 |
| L5 | 用户验证 | 用户满意度 | >80% 或 标记待验 |

### 质量门禁检查点
```
[ ] L1: 输出包含 触发词识别结果
[ ] L1: 输出包含 标准化输入确认
[ ] L1: 输出包含 结构化输出格式
[ ] L2: 每个结论有清晰前提
[ ] L2: 推理步骤无跳跃
[ ] L3: 关键数字有来源
[ ] L3: 案例有出处
[ ] L4: 与相邻专家无直接冲突
[ ] L4: 冲突已标注原因
[ ] L5: 用户反馈已收集
```

APPENDIX
}

#-------------------------------------------------------------------------------
# 为单个专家创建 assess/evals/refs 目录和文件
#-------------------------------------------------------------------------------
fix_single_expert() {
    local agent_path="$1"
    local agent_name=$(basename "$agent_path")

    log_info "处理专家: $agent_name"

    # 创建目录
    mkdir -p "$agent_path/assess"
    mkdir -p "$agent_path/evals"
    mkdir -p "$agent_path/references"

    # 创建 assess/README.md
    cat > "$agent_path/assess/README.md" << 'ASSESS_EOF'
# 评估标准

## 评估维度

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 完整性 | 20% | 章节是否齐全（触发词/输入/输出/质量门禁） |
| 准确性 | 30% | 理论是否正确，逻辑是否严密 |
| 可执行性 | 30% | 输出是否可操作，用户能否直接使用 |
| 独特性 | 20% | 是否有差异化，区别于其他专家 |

## 评分等级

| 等级 | 分数 | 说明 |
|------|------|------|
| 优秀 | 95-100 | 全部维度超出预期 |
| 良好 | 85-94 | 全部维度达标，部分优秀 |
| 及格 | 75-84 | 主要维度达标 |
| 不及格 | <75 | 存在P0问题 |

## 及格线

- **标准模式**: 总分 >= 85分
- **Momus严格模式**: 总分 >= 95分

## 快速检查清单

- [ ] 触发词覆盖主要场景
- [ ] 输入格式标准化
- [ ] 输出格式结构化
- [ ] 包含CLI命令定义
- [ ] 包含元数据Schema
- [ ] 包含Handoff协议
- [ ] 包含DevQA循环
- [ ] 包含五级质量门禁
ASSESS_EOF

    # 创建 evals/README.md
    cat > "$agent_path/evals/README.md" << 'EVALS_EOF'
# 测试用例

## 正面测试用例

### 测试用例 1: 标准流程
```json
{
  "id": "positive-01",
  "input": "【标准输入示例】",
  "expected_output": "【期望输出】",
  "validation": [
    "输出包含完整结构",
    "置信度在合理范围",
    "包含交接建议"
  ]
}
```

## 负面测试用例

### 测试用例 1: 边界输入
```json
{
  "id": "negative-01",
  "input": "【空输入/极端输入】",
  "expected_behavior": "优雅降级",
  "fallback": "返回格式化的空结果，要求用户补充"
}
```

### 测试用例 2: 置信度不足
```json
{
  "id": "negative-02",
  "input": "【信息不足的输入】",
  "expected_behavior": "置信度 < 0.6",
  "fallback": "返回补充信息请求"
}
```

## 边界条件

| 条件 | 预期行为 |
|------|----------|
| 空输入 | 返回输入模板 |
| 超长输入 | 截断+警告 |
| 格式错误 | 尝试解析+标注问题 |
| 并发请求 | 队列处理 |
EVALS_EOF

    # 创建 references/README.md
    cat > "$agent_path/references/README.md" << 'REFS_EOF'
# 参考资料

## 必读文献

1. [经典著作/论文]

## 案例库

### 成功案例
1. [案例1]
2. [案例2]

### 失败案例
1. [案例1]
2. [案例2]

## 延伸阅读

1. [相关模型/框架]
2. [进阶读物]
REFS_EOF

    log_success "$agent_name: assess/evals/references 目录和文件已创建"
}

#-------------------------------------------------------------------------------
# 为主 AGENT.md 追加 CLI/元数据/Handoff 内容
#-------------------------------------------------------------------------------
append_to_agent() {
    local agent_path="$1"
    local agent_name=$(basename "$agent_path")
    local agent_md="$agent_path/AGENT.md"

    if [[ ! -f "$agent_md" ]]; then
        log_warn "$agent_name: AGENT.md 不存在，跳过"
        return
    fi

    # 检查是否已追加（防止重复）
    if grep -q "## CLI命令定义" "$agent_md" 2>/dev/null; then
        log_warn "$agent_name: 已包含 CLI命令定义，跳过"
        return
    fi

    # 追加内容
    generate_appendix >> "$agent_md"
    log_success "$agent_name: AGENT.md 已追加 CLI/元数据/Handoff"
}

#-------------------------------------------------------------------------------
# 主流程
#-------------------------------------------------------------------------------
main() {
    log_info "=========================================="
    log_info "  思考天团 Expert Agent 批量修复脚本"
    log_info "=========================================="
    log_info "项目目录: $PROJECT_DIR"
    log_info "代理目录: $AGENTS_DIR"
    log_info ""

    # 检查模板文件
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_warn "模板文件不存在: $TEMPLATE_FILE"
        log_info "将使用内置模板"
    fi

    # 处理专家 15-25
    local experts=(
        "15-opportunity-cost"
        "16-sunk-cost"
        "17-confirmation-bias"
        "18-critical-thinking"
        "19-systems-thinking"
        "20-anti-fragile"
        "21-game-theory"
        "22-pareto"
        "23-compound-effect"
        "24-porters-five-forces"
        "25-long-tail"
    )

    local count=0
    for expert in "${experts[@]}"; do
        local expert_path="$AGENTS_DIR/$expert"
        if [[ -d "$expert_path" ]]; then
            fix_single_expert "$expert_path"
            append_to_agent "$expert_path"
            ((count++))
        else
            log_warn "专家目录不存在: $expert"
        fi
    done

    log_info ""
    log_success "=========================================="
    log_success "  处理完成: $count 个专家"
    log_success "=========================================="
    log_info ""
    log_info "下一步操作:"
    log_info "  1. 检查生成的 assess/evals/references 文件"
    log_info "  2. 根据模板填充具体内容"
    log_info "  3. 运行测试验证"
}

# 执行
main "$@"
