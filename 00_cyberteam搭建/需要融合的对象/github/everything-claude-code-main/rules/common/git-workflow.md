# Git 工作流程

## 提交消息格式```
<type>: <description>

<optional body>
```类型：feat、fix、refactor、docs、test、chore、perf、ci

注意：通过 ~/.claude/settings.json 全局禁用归因。

## 拉取请求工作流程

创建 PR 时：
1.分析完整的提交历史记录（不仅仅是最新的提交）
2. 使用 `git diff [base-branch]...HEAD` 查看所有更改
3. 草拟全面的公关摘要
4. 将测试计划包含在 TODO 中
5. 如果有新分支，则使用“-u”标志推送

> 对于git操作之前的完整开发流程（规划、TDD、代码审查），
> 参见 [development-workflow.md](./development-workflow.md)。