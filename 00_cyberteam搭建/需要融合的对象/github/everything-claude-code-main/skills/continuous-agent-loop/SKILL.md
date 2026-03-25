# 连续代理循环

这是 v1.8+ 规范循环技能名称。它取代了“自主循环”，同时保持了一个版本的兼容性。

## 循环选择流程```text
Start
  |
  +-- Need strict CI/PR control? -- yes --> continuous-pr
  |                                    
  +-- Need RFC decomposition? -- yes --> rfc-dag
  |
  +-- Need exploratory parallel generation? -- yes --> infinite
  |
  +-- default --> sequential
```## 组合模式

推荐的生产堆栈：
1. RFC分解（`ralphinho-rfc-pipeline`）
2. 质量门（`plankton-code-quality` + `/quality-gate`）
3. 评估循环（`eval-harness`）
4. 会话持久化（`nanoclaw-repl`）

## 故障模式

- 循环流失而没有可衡量的进展
- 具有相同根本原因的重复重试
- 合并队列停顿
- 无限制升级带来的成本漂移

## 恢复

- 冻结循环
- 运行“/harness-audit”
- 缩小失败单位的范围
- 具有明确接受标准的重播