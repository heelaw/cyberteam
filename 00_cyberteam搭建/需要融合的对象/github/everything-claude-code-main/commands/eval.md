# 评估命令

管理评估驱动的开发工作流程。

## 用法

`/eval [定义|检查|报告|列表] [功能名称]`

## 定义评估

`/eval 定义功能名称`

创建一个新的 eval 定义：

1. 使用模板创建 `.claude/evals/feature-name.md`：```markdown
## EVAL: feature-name
Created: $(date)

### Capability Evals
- [ ] [Description of capability 1]
- [ ] [Description of capability 2]

### Regression Evals
- [ ] [Existing behavior 1 still works]
- [ ] [Existing behavior 2 still works]

### Success Criteria
- pass@3 > 90% for capability evals
- pass^3 = 100% for regression evals
```2. 提示用户填写特定条件

## 检查评估

`/eval 检查功能名称`

对某个功能运行评估：

1. 从 `.claude/evals/feature-name.md` 读取 eval 定义
2. 对于每个能力评估：
   - 尝试验证标准
   - 记录通过/失败
   - 在`.claude/evals/feature-name.log`中记录尝试
3. 对于每个回归评估：
   - 运行相关测试
   - 与基线比较
   - 记录通过/失败
4. 报告当前状态：```
EVAL CHECK: feature-name
========================
Capability: X/Y passing
Regression: X/Y passing
Status: IN PROGRESS / READY
```## 报告评估

`/eval 报告功能名称`

生成综合评估报告：```
EVAL REPORT: feature-name
=========================
Generated: $(date)

CAPABILITY EVALS
----------------
[eval-1]: PASS (pass@1)
[eval-2]: PASS (pass@2) - required retry
[eval-3]: FAIL - see notes

REGRESSION EVALS
----------------
[test-1]: PASS
[test-2]: PASS
[test-3]: PASS

METRICS
-------
Capability pass@1: 67%
Capability pass@3: 100%
Regression pass^3: 100%

NOTES
-----
[Any issues, edge cases, or observations]

RECOMMENDATION
--------------
[SHIP / NEEDS WORK / BLOCKED]
```## 列出评估

`/评估列表`

显示所有 eval 定义：```
EVAL DEFINITIONS
================
feature-auth      [3/5 passing] IN PROGRESS
feature-search    [5/5 passing] READY
feature-export    [0/4 passing] NOT STARTED
```## 参数

$参数：
- `define <name>` - 创建新的 eval 定义
- `check <name>` - 运行并检查评估
- `report <name>` - 生成完整报告
- `list` - 显示所有评估
- `clean` - 删除旧的评估日志（保留最后 10 次运行）