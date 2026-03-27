# CyberTeam Agent 前导码模板

## 标准前导码 (所有Agent必须使用)

```bash
# === 前导码 ===
# 1. 更新检查
_UPD=$(~/.claude/skills/gstack/bin/gstack-update-check 2>/dev/null || \
      ~/.claude/skills/gstack/bin/gstack-update-check 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || true

# 2. 会话跟踪
mkdir -p ~/.gstack/sessions
touch ~/.gstack/sessions/"$PPID"
_SESSIONS=$(find ~/.gstack/sessions -mmin -120 -type f 2>/dev/null | wc -l | tr -d ' ')
find ~/.gstack/sessions -mmin +120 -type f -delete 2>/dev/null || true

# 3. Repo信息
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "BRANCH: $_BRANCH"

# 4. 完整性原则
# AI时代完整性的边际成本接近零——永远选择完整实现
```

## AskUserQuestion格式规范

### 标准格式
```
1. Re-ground: 陈述项目、当前分支、当前计划/任务 (1-2句话)
2. Simplify: 用16岁能理解的语言解释问题，不用术语
3. Recommend: 推荐方案 + Completeness评分 (10分=完整实现)
4. Options: 选项列表 (A/B/C...)
```

### Completeness评分标准
- 10 = 完整实现(全部边缘用例、100%覆盖)
- 7 = 覆盖happy path但跳过一些边缘
- 3 = 捷径，延期重要工作
- ≤5 = 旗帜标识，说明不完整

### 选项要求
当一个选项是完整实现而另一个是捷径时:
- 必须推荐完整选项
- 即使需要更多代码/时间
- 说明为什么完整性更重要

## 完成状态协议

### 标准结束语
```
| 完成状态 |
|----------|
| ✅ DONE — 所有步骤成功完成，每个声明都有证据 |
| ⚠️ DONE_WITH_CONCERNS — 完成但有问题需要用户知晓 |
| 🔴 BLOCKED — 无法继续，列出阻塞原因和尝试过的方案 |
| ❓ NEEDS_CONTEXT — 缺少继续所需信息，明确说明需要什么 |
```

---

**版本**: v1.0 | **来源**: gstack前导码系统 + CyberTeam整合 | **日期**: 2026-03-23
