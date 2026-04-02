# /skill-create - 本地技能生成

分析存储库的 git 历史记录以提取编码模式并生成 SKILL.md 文件，向 Claude 传授您团队的实践。

＃＃ 用法```bash
/skill-create                    # Analyze current repo
/skill-create --commits 100      # Analyze last 100 commits
/skill-create --output ./skills  # Custom output directory
/skill-create --instincts        # Also generate instincts for continuous-learning-v2
```## 它的作用

1. **解析 Git 历史记录** - 分析提交、文件更改和模式
2. **检测模式** - 识别重复出现的工作流程和约定
3. **生成 SKILL.md** - 创建有效的克劳德代码技能文件
4. **选择性地创建本能** - 对于持续学习 v2 系统

## 分析步骤

### 第 1 步：收集 Git 数据```bash
# Get recent commits with file changes
git log --oneline -n ${COMMITS:-200} --name-only --pretty=format:"%H|%s|%ad" --date=short

# Get commit frequency by file
git log --oneline -n 200 --name-only | grep -v "^$" | grep -v "^[a-f0-9]" | sort | uniq -c | sort -rn | head -20

# Get commit message patterns
git log --oneline -n 200 | cut -d' ' -f2- | head -50
```### 第 2 步：检测模式

寻找这些模式类型：

|图案|检测方法|
|------|------------------|
| **提交约定** |提交消息的正则表达式 (feat:、fix:、chore:) |
| **文件共同更改** |总是一起变化的文件 |
| **工作流程顺序** |重复文件更改模式|
| **架构** |文件夹结构和命名约定|
| **测试模​​式** |测试文件位置、命名、覆盖范围 |

### 步骤3：生成SKILL.md

输出格式：```markdown
---
name: {repo-name}-patterns
description: Coding patterns extracted from {repo-name}
version: 1.0.0
source: local-git-analysis
analyzed_commits: {count}
---

# {Repo Name} Patterns

## Commit Conventions
{detected commit message patterns}

## Code Architecture
{detected folder structure and organization}

## Workflows
{detected repeating file change patterns}

## Testing Patterns
{detected test conventions}
```### 步骤 4：生成本能（if --instincts）

对于持续学习 v2 集成：```yaml
---
id: {repo}-commit-convention
trigger: "when writing a commit message"
confidence: 0.8
domain: git
source: local-repo-analysis
---

# Use Conventional Commits

## Action
Prefix commits with: feat:, fix:, chore:, docs:, test:, refactor:

## Evidence
- Analyzed {n} commits
- {percentage}% follow conventional commit format
```## 输出示例

在 TypeScript 项目上运行 `/skill-create` 可能会产生：```markdown
---
name: my-app-patterns
description: Coding patterns from my-app repository
version: 1.0.0
source: local-git-analysis
analyzed_commits: 150
---

# My App Patterns

## Commit Conventions

This project uses **conventional commits**:
- `feat:` - New features
- `fix:` - Bug fixes
- `chore:` - Maintenance tasks
- `docs:` - Documentation updates

## Code Architecture

```源代码/
├── Components/ # React 组件 (PascalCase.tsx)
├── hooks/ # 自定义钩子（使用*.ts）
├── utils/ # 实用函数
├── types/ # TypeScript 类型定义
└── services/ # API 和外部服务```

## Workflows

### Adding a New Component
1. Create `src/components/ComponentName.tsx`
2. Add tests in `src/components/__tests__/ComponentName.test.tsx`
3. Export from `src/components/index.ts`

### Database Migration
1. Modify `src/db/schema.ts`
2. Run `pnpm db:generate`
3. Run `pnpm db:migrate`

## Testing Patterns

- Test files: `__tests__/` directories or `.test.ts` suffix
- Coverage target: 80%+
- Framework: Vitest
```## GitHub 应用程序集成

对于高级功能（10k+ 提交、团队共享、自动 PR），请使用 [Skill Creator GitHub 应用程序](https://github.com/apps/skill-creator)：

- 安装：[github.com/apps/skill-creator](https://github.com/apps/skill-creator)
- 对任何问题发表评论“/skill-creatoranalyze”
- 通过生成的技能获得 PR

## 相关命令

- `/instinct-import` - 导入生成的本能
- `/instinct-status` - 查看学到的本能
- `/evolve` - 将本能聚集到技能/代理中

---

*[Everything Claude 代码](https://github.com/affaan-m/everything-claude-code) 的一部分*