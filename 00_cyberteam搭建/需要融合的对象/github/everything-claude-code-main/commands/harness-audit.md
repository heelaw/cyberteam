# 利用审核命令

运行确定性存储库利用审核并返回优先记分卡。

## 用法

`/harness-audit [范围] [--format text|json]`

- `scope`（可选）：`repo`（默认）、`hooks`、`skills`、`commands`、`agents`
- `--format`：输出样式（默认为`text`，用于自动化的`json`）

## 确定性引擎

始终运行：```bash
node scripts/harness-audit.js <scope> --format <text|json>
```该脚本是评分和检查的真实来源。不要发明额外的维度或临时点。

标题版本：“2026-03-16”。

该脚本计算 7 个固定类别（每个类别均经过“0-10”标准化）：

1. 工具覆盖范围
2. 上下文效率
3. 质量门
4. 内存持久化
5. 评估范围
6. 安全护栏
7. 成本效益

分数源自显式文件/规则检查，并且对于同一提交是可重现的。

## 输出合约

返回：

1.“overall_score”超出“max_score”（“repo”为 70；范围审计较小）
2. 类别分数和具体结果
3. 精确文件路径检查失败
4. 确定性输出中的前 3 个操作 (`top_actions`)
5. 建议下一步应用的 ECC 技能

## 清单

- 直接使用脚本输出；不要手动重新评分。
- 如果请求 `--format json`，则返回脚本 JSON 不变。
- 如果需要文本，请总结失败的检查和主要操作。
- 包括“checks[]”和“top_actions[]”中的确切文件路径。

## 结果示例```text
Harness Audit (repo): 66/70
- Tool Coverage: 10/10 (10/10 pts)
- Context Efficiency: 9/10 (9/10 pts)
- Quality Gates: 10/10 (10/10 pts)

Top 3 Actions:
1) [Security Guardrails] Add prompt/tool preflight security guards in hooks/hooks.json. (hooks/hooks.json)
2) [Tool Coverage] Sync commands/harness-audit.md and .opencode/commands/harness-audit.md. (.opencode/commands/harness-audit.md)
3) [Eval Coverage] Increase automated test coverage across scripts/hooks/lib. (tests/)
```## 参数

$参数：
- `repo|hooks|skills|commands|agents`（可选范围）
- `--format text|json` （可选输出格式）