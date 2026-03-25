# 第一阶段发行包 — 2026 年 3 月 12 日

## 状态

这些问题草案是根据 3 月 11 日的大型计划和 3 月 12 日的计划准备的
切换。我尝试直接在 GitHub 中打开它们，但问题创建是
由于 MCP 会话中缺少 GitHub 身份验证而被阻止。

## GitHub 状态

这些草稿后来通过“gh”发布：

- `#423` 为 ECC 实施清单驱动的选择性安装配置文件
- `#421` 添加 ECC 安装状态以及卸载/医生/修复生命周期
- `#424` 为 ECC 2.0 控制平面定义规范会话适配器合约
- `#422` 定义生成的技能放置和来源政策
- `#425` 定义工具调用之后的治理和可见性

下面的主体被保留为用于创建的本地源包
问题。

## 第 1 期

### 标题

为 ECC 实施清单驱动的选择性安装配置文件

### 标签

- `增强`

### 身体```md
## Problem

ECC still installs primarily by target and language. The repo now has first-pass
selective-install manifests and a non-mutating plan resolver, but the installer
itself does not yet consume those profiles.

Current groundwork already landed in-repo:

- `manifests/install-modules.json`
- `manifests/install-profiles.json`
- `scripts/ci/validate-install-manifests.js`
- `scripts/lib/install-manifests.js`
- `scripts/install-plan.js`

That means the missing step is no longer design discovery. The missing step is
execution: wire profile/module resolution into the actual install flow while
preserving backward compatibility.

## Scope

Implement manifest-driven install execution for current ECC targets:

- `claude`
- `cursor`
- `antigravity`

Add first-pass support for:

- `ecc-install --profile <name>`
- `ecc-install --modules <id,id,...>`
- target-aware filtering based on module target support
- backward-compatible legacy language installs during rollout

## Non-Goals

- Full uninstall/doctor/repair lifecycle in the same issue
- Codex/OpenCode install targets in the first pass if that blocks rollout
- Reorganizing the repository into separate published packages

## Acceptance Criteria

- `install.sh` can resolve and install a named profile
- `install.sh` can resolve explicit module IDs
- Unsupported modules for a target are skipped or rejected deterministically
- Legacy language-based install mode still works
- Tests cover profile resolution and installer behavior
- Docs explain the new preferred profile/module install path
```## 第 2 期

### 标题

添加 ECC 安装状态以及卸载/医生/修复生命周期

### 标签

- `增强`

### 身体```md
## Problem

ECC has no canonical installed-state record. That makes uninstall, repair, and
post-install inspection nondeterministic.

Today the repo can classify installable content, but it still cannot reliably
answer:

- what profile/modules were installed
- what target they were installed into
- what paths ECC owns
- how to remove or repair only ECC-managed files

Without install-state, lifecycle commands are guesswork.

## Scope

Introduce a durable install-state contract and the first lifecycle commands:

- `ecc list-installed`
- `ecc uninstall`
- `ecc doctor`
- `ecc repair`

Suggested state locations:

- Claude: `~/.claude/ecc/install-state.json`
- Cursor: `./.cursor/ecc-install-state.json`
- Antigravity: `./.agent/ecc-install-state.json`

The state file should capture at minimum:

- installed version
- timestamp
- target
- profile
- resolved modules
- copied/managed paths
- source repo version or package version

## Non-Goals

- Rebuilding the installer architecture from scratch
- Full remote/cloud control-plane functionality
- Target support expansion beyond the current local installers unless it falls
  out naturally

## Acceptance Criteria

- Successful installs write install-state deterministically
- `list-installed` reports target/profile/modules/version cleanly
- `doctor` reports missing or drifted managed paths
- `repair` restores missing managed files from recorded install-state
- `uninstall` removes only ECC-managed files and leaves unrelated local files
  alone
- Tests cover install-state creation and lifecycle behavior
```## 第 3 期

### 标题

为 ECC 2.0 控制平面定义规范会话适配器合约

### 标签

- `增强`

### 身体```md
## Problem

ECC now has real orchestration/session substrate, but it is still
implementation-specific.

Current state:

- tmux/worktree orchestration exists
- machine-readable session snapshots exist
- Claude local session-history commands exist

What does not exist yet is a harness-neutral adapter boundary that can normalize
session/task state across:

- tmux-orchestrated workers
- plain Claude sessions
- Codex worktrees
- OpenCode sessions
- later remote or GitHub-integrated operator surfaces

Without that adapter contract, any future ECC 2.0 operator shell will be forced
to read tmux-specific and markdown-coordination details directly.

## Scope

Define and implement the first-pass canonical session adapter layer.

Suggested deliverables:

- adapter registry
- canonical session snapshot schema
- `dmux-tmux` adapter backed by current orchestration code
- `claude-history` adapter backed by current session history utilities
- read-only inspection CLI for canonical session snapshots

## Non-Goals

- Full ECC 2.0 UI in the same issue
- Monetization/GitHub App implementation
- Remote multi-user control plane

## Acceptance Criteria

- There is a documented canonical snapshot contract
- Current tmux orchestration snapshot code is wrapped as an adapter rather than
  the top-level product contract
- A second non-tmux adapter exists to prove the abstraction is real
- Tests cover adapter selection and normalized snapshot output
- The design clearly separates adapter concerns from orchestration and UI
  concerns
```## 第 4 期

### 标题

定义生成的技能放置和来源政策

### 标签

- `增强`

### 身体```md
## Problem

ECC now has a large and growing skill surface, but generated/imported/learned
skills do not yet have a clear long-term placement and provenance policy.

This creates several problems:

- unclear separation between curated skills and generated/learned skills
- validator noise around directories that may or may not exist locally
- weak provenance for imported or machine-generated skill content
- uncertainty about where future automated learning outputs should live

As ECC grows, the repo needs explicit rules for where generated skill artifacts
belong and how they are identified.

## Scope

Define a repo-wide policy for:

- curated vs generated vs imported skill placement
- provenance metadata requirements
- validator behavior for optional/generated skill directories
- whether generated skills are shipped, ignored, or materialized during
  install/build steps

## Non-Goals

- Building a full external skill marketplace
- Rewriting all existing skill content in one pass
- Solving every content-quality issue in the same issue

## Acceptance Criteria

- A documented placement policy exists for generated/imported skills
- Provenance requirements are explicit
- Validators no longer produce ambiguous behavior around optional/generated
  skill locations
- The policy clearly states what is publishable vs local-only
- Follow-on implementation work is split into concrete, bounded PR-sized steps
```