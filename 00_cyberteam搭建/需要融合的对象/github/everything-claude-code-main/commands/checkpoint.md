# 检查点命令

在工作流程中创建或验证检查点。

## 用法

`/checkpoint [创建|验证|列表] [名称]`

## 创建检查点

创建检查点时：

1. 运行“/verify fast”以确保当前状态是干净的
2. 使用检查点名称创建 git stash 或提交
3. 将检查点记录到`.claude/checkpoints.log`：```bash
echo "$(date +%Y-%m-%d-%H:%M) | $CHECKPOINT_NAME | $(git rev-parse --short HEAD)" >> .claude/checkpoints.log
```4. 创建报告检查点

## 验证检查点

根据检查点进行验证时：

1.从日志中读取检查点
2. 将当前状态与检查点进行比较：
   - 自检查点以来添加的文件
   - 自检查点以来修改的文件
   - 现在与当时的测试通过率
   - 现在的覆盖范围与当时的覆盖范围

3. 报告：```
CHECKPOINT COMPARISON: $NAME
============================
Files changed: X
Tests: +Y passed / -Z failed
Coverage: +X% / -Y%
Build: [PASS/FAIL]
```## 列出检查点

显示所有检查点：
- 姓名
- 时间戳
-Git SHA
- 状态（当前、落后、领先）

## 工作流程

典型的检查点流程：```
[Start] --> /checkpoint create "feature-start"
   |
[Implement] --> /checkpoint create "core-done"
   |
[Test] --> /checkpoint verify "core-done"
   |
[Refactor] --> /checkpoint create "refactor-done"
   |
[PR] --> /checkpoint verify "feature-start"
```## 参数

$参数：
- `create <name>` - 创建命名检查点
- `verify <name>` - 根据命名检查点进行验证
- `list` - 显示所有检查点
- `clear` - 删除旧的检查点（保留最后 5 个）