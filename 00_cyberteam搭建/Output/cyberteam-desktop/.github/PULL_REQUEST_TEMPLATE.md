## Pull Request 模板

---

## 描述
<!-- 简要描述这个 PR 的内容 -->

## 类型
- [ ] 新功能 (`feat`)
- [ ] Bug 修复 (`fix`)
- [ ] 重构 (`refactor`)
- [ ] 文档 (`docs`)
- [ ] CI/CD (`ci`)
- [ ] 其他 (`chore`)

## 影响的范围
<!-- 这个 PR 影响到哪些模块 -->
- [ ] 聊天/消息功能 (`chat`)
- [ ] API Provider 配置 (`provider`)
- [ ] 部门/组织架构 (`department`)
- [ ] Agent 管理 (`agent`)
- [ ] Skill 管理 (`skill`)
- [ ] Agent 市场 (`market`)
- [ ] Playground 看板 (`playground`)
- [ ] UI 组件 (`ui`)
- [ ] Electron 主进程 (`electron`)
- [ ] 文档 (`docs`)

## 测试
- [ ] 单元测试通过 (`pnpm test`)
- [ ] E2E 测试通过 (`pnpm test:e2e`)
- [ ] 手动测试通过

## 截图（UI 变更）
<!-- 如果有 UI 变更，添加截图 -->

## Checklist
- [ ] 代码符合 TypeScript strict mode
- [ ] 没有 ESLint 错误 (`pnpm lint`)
- [ ] 类型检查通过 (`pnpm typecheck`)
- [ ] 提交信息符合规范（参考 CONTRIBUTING.md）
- [ ] 新功能包含测试
- [ ] Bug 修复包含回归测试

---

## 如何填写

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 示例

```
feat(chat): add @mention support with agent picker

- Implement TipTap Mention extension with 1200ms activation window
- Add agent picker dropdown with avatar and role display
- Support @agent, @department, @skill mention types

Closes #123
```

### Type 类别

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式 |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 测试 |
| `chore` | 构建/工具 |
| `ci` | CI/CD |
