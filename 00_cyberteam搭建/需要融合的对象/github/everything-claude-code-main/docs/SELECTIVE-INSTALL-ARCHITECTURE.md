# ECC 2.0 Selective Install Discovery

## Purpose

This document turns the March 11 mega-plan selective-install requirement into a
concrete ECC 2.0 discovery design.

The goal is not just "fewer files copied during install." The actual target is
an install system that can answer, deterministically:

- what was requested
- what was resolved
- what was copied or generated
- what target-specific transforms were applied
- what ECC owns and may safely remove or repair later

That is the missing contract between ECC 1.x installation and an ECC 2.0
control plane.

## Current Implemented Foundation

The first selective-install substrate already exists in-repo:

- `manifests/install-modules.json`
- `manifests/install-profiles.json`
- `schemas/install-modules.schema.json`
- `schemas/install-profiles.schema.json`
- `schemas/install-state.schema.json`
- `scripts/ci/validate-install-manifests.js`
- `scripts/lib/install-manifests.js`
- `scripts/lib/install/request.js`
- `scripts/lib/install/runtime.js`
- `scripts/lib/install/apply.js`
- `scripts/lib/install-targets/`
- `scripts/lib/install-state.js`
- `scripts/lib/install-executor.js`
- `scripts/lib/install-lifecycle.js`
- `scripts/ecc.js`
- `scripts/install-apply.js`
- `scripts/install-plan.js`
- `scripts/list-installed.js`
- `scripts/doctor.js`

Current capabilities:

- machine-readable module and profile catalogs
- CI validation that manifest entries point at real repo paths
- dependency expansion and target filtering
- adapter-aware operation planning
- canonical request normalization for legacy and manifest install modes
- explicit runtime dispatch from normalized requests into plan creation
- legacy and manifest installs both write durable install-state
- read-only inspection of install plans before any mutation
- unified `ecc` CLI routing install, planning, and lifecycle commands
- lifecycle inspection and mutation via `list-installed`, `doctor`, `repair`,
  and `uninstall`

Current limitation:

- target-specific merge/remove semantics are still scaffold-level for some modules
- legacy `ecc-install` compatibility still points at `install.sh`
- publish surface is still broad in `package.json`

## Current Code Review

The current installer stack is already much healthier than the original
language-first shell installer, but it still concentrates too much
responsibility in a few files.

### Current Runtime Path

The runtime flow today is:

1. `install.sh`
   thin shell wrapper that resolves the real package root
2. `scripts/install-apply.js`
   user-facing installer CLI for legacy and manifest modes
3. `scripts/lib/install/request.js`
   CLI parsing plus canonical request normalization
4. `scripts/lib/install/runtime.js`
   runtime dispatch from normalized requests into install plans
5. `scripts/lib/install-executor.js`
   argument translation, legacy compatibility, operation materialization,
   filesystem mutation, and install-state write
6. `scripts/lib/install-manifests.js`
   module/profile catalog loading plus dependency expansion
7. `scripts/lib/install-targets/`
   target root and destination-path scaffolding
8. `scripts/lib/install-state.js`
   schema-backed install-state read/write
9. `scripts/lib/install-lifecycle.js`
   doctor/repair/uninstall behavior derived from stored operations

That is enough to prove the selective-install substrate, but not enough to make
the installer architecture feel settled.

### Current Strengths

- install intent is now explicit through `--profile` and `--modules`
- request parsing and request normalization are now split from the CLI shell
- target root resolution is already adapterized
- lifecycle commands now use durable install-state instead of guessing
- the repo already has a unified Node entrypoint through `ecc` and
  `install-apply.js`

### Current Coupling Still Present

1. `install-executor.js` is smaller than before, but still carrying too many
   planning and materialization layers at once.
   The request boundary is now extracted, but legacy request translation,
   manifest-plan expansion, and operation materialization still live together.
2. target adapters are still too thin.
   Today they mostly resolve roots and scaffold destination paths. The real
   install semantics still live in executor branches and path heuristics.
3. the planner/executor boundary is not clean enough yet.
   `install-manifests.js` resolves modules, but the final install operation set
   is still partly constructed in executor-specific logic.
4. lifecycle behavior depends on low-level recorded operations more than on
   stable module semantics.
   That works for plain file copy, but becomes brittle for merge/generate/remove
   behaviors.
5. compatibility mode is mixed directly into the main installer runtime.
   Legacy language installs should behave like a request adapter, not as a
   parallel installer architecture.

## Proposed Modular Architecture Changes

The next architectural step is to separate the installer into explicit layers,
with each layer returning stable data instead of immediately mutating files.

### Target State

The desired install pipeline is:

1. CLI surface
2. request normalization
3. module resolution
4. target planning
5. operation planning
6. execution
7. install-state persistence
8. lifecycle services built on the same operation contract

The main idea is simple:

- manifests describe content
- adapters describe target-specific landing semantics
- planners describe what should happen
- executors apply those plans
- lifecycle commands reuse the same plan/state model instead of reinventing it

### Proposed Runtime Layers

#### 1. CLI Surface

Responsibility:

- parse user intent only
- route to install, plan, doctor, repair, uninstall
- render human or JSON output

Should not own:

- legacy language translation
- target-specific install rules
- operation construction

Suggested files:```text
scripts/ecc.js
scripts/install-apply.js
scripts/install-plan.js
scripts/doctor.js
scripts/repair.js
scripts/uninstall.js
```它们仍然作为入口点，但成为库模块的薄包装。

#### 2. 请求规范器

责任：

- 将原始 CLI 标志转换为规范的安装请求
- 将旧语言安装转换为兼容性请求形式
- 尽早拒绝混合或不明确的输入

建议的规范请求：```json
{
  "mode": "manifest",
  "target": "cursor",
  "profile": "developer",
  "modules": [],
  "legacyLanguages": [],
  "dryRun": false
}
```或者，在兼容模式下：```json
{
  "mode": "legacy-compat",
  "target": "claude",
  "profile": null,
  "modules": [],
  "legacyLanguages": ["typescript", "python"],
  "dryRun": false
}
```这让管道的其余部分忽略请求是否来自旧的或
新的 CLI 语法。

#### 3. 模块解析器

责任：

- 加载清单目录
- 扩展依赖关系
- 拒绝冲突
- 过滤每个目标不支持的模块
- 返回一个规范的解析对象

该层应保持纯净且只读。

它不应该知道：

- 目标文件系统路径
- 合并语义
- 复制策略

当前最近的文件：

- `scripts/lib/install-manifests.js`

建议分割：```text
scripts/lib/install/catalog.js
scripts/lib/install/resolve-request.js
scripts/lib/install/resolve-modules.js
```#### 4. 目标规划器

责任：

- 选择安装目标适配器
- 解析目标根
- 解析安装状态路径
- 扩展模块到目标的映射规则
- 发出目标感知的操作意图

这就是目标特定含义应该存在的地方。

示例：

- 克劳德可以在`~/.claude`下保留本机层次结构
- 光标可能会以与规则不同的方式同步捆绑的“.cursor”根子项
- 生成的配置可能需要合并或替换语义，具体取决于目标

当前最近的文件：

- `scripts/lib/install-targets/helpers.js`
- `scripts/lib/install-targets/registry.js`

建议的演变：```text
scripts/lib/install/targets/registry.js
scripts/lib/install/targets/claude-home.js
scripts/lib/install/targets/cursor-project.js
scripts/lib/install/targets/antigravity-project.js
```每个适配器最终应该公开多个“resolveRoot”。
它应该拥有针对其目标家庭的路径和战略规划。

#### 5. 运营规划师

责任：

- 将模块解析加上适配器规则转换为类型化操作图
- 发出一流的操作，例如：
  - `复制文件`
  - `复制树`
  - `合并 json`
  - `渲染模板`
  - `删除`
- 附加所有权和验证元数据

这是当前安装程序中缺少的架构接缝。

如今，操作部分是脚手架级别的，部分是特定于执行者的。
ECC 2.0 应该使操作规划成为一个独立的阶段，以便：

- “计划”成为执行的真正预览
- `doctor` 可以验证预期行为，而不仅仅是当前文件
- “修复”可以安全地重建确切缺失的工作
- `uninstall` 只能反转托管操作

#### 6. 执行引擎

责任：

- 应用类型化操作图
- 强制执行覆盖和所有权规则
- 阶段安全写入
- 收集最终应用操作结果

这一层不应该决定“做什么”。
它应该只决定*如何*安全地应用提供的操作类型。

当前最近的文件：

- `scripts/lib/install-executor.js`

推荐重构：```text
scripts/lib/install/executor/apply-plan.js
scripts/lib/install/executor/apply-copy.js
scripts/lib/install/executor/apply-merge-json.js
scripts/lib/install/executor/apply-remove.js
```这将执行器逻辑从一个大型分支运行时转变为一组小型分支运行时
操作处理程序。

#### 7. 安装状态存储

责任：

- 验证并保留安装状态
- 记录规范的请求、解决方案和应用的操作
- 支持生命周期命令，而无需强制它们对安装进行逆向工程

当前最近的文件：

- `scripts/lib/install-state.js`

该层已经接近正确的形状。剩下的主要变化是
一旦合并/生成语义成为现实，就可以存储更丰富的操作元数据。

#### 8. 生命周期服务

责任：

- `list-installed`：仅检查状态
- `doctor`：将所需/安装状态视图与当前文件系统进行比较
-“修复”：从状态重新生成计划并重新应用安全操作
- `uninstall`：仅删除 ECC 拥有的输出

当前最近的文件：

- `scripts/lib/install-lifecycle.js`

该层最终应该对操作类型和所有权策略进行操作，
不仅仅是原始的“复制文件”记录。

## 建议的文件布局

干净的模块化最终状态应该大致如下所示：```text
scripts/lib/install/
  catalog.js
  request.js
  resolve-modules.js
  plan-operations.js
  state-store.js
  targets/
    registry.js
    claude-home.js
    cursor-project.js
    antigravity-project.js
    codex-home.js
    opencode-home.js
  executor/
    apply-plan.js
    apply-copy.js
    apply-merge-json.js
    apply-render-template.js
    apply-remove.js
  lifecycle/
    discover.js
    doctor.js
    repair.js
    uninstall.js
```这不是包装拆分。
它是当前存储库内的代码所有权分割，因此每一层都有一个工作。

## 当前文件的迁移图

风险最低的迁移路径是渐进式的，而不是重写式的。

### 保留

- `install.sh` 作为公共兼容性垫片
- `scripts/ecc.js` 作为统一的 CLI
- `scripts/lib/install-state.js` 作为状态存储的起点
- 当前目标适配器 ID 和状态位置

### 提取

- 请求解析和兼容性翻译出来
  `scripts/lib/install-executor.js`
- 从执行分支到目标的目标感知操作规划
  适配器和规划器模块
- 将共享生命周期整体分析为更小的生命周期特定分析
  服务

### 逐渐替换

- 具有类型化操作的广泛路径复制启发式
- 具有适配器拥有语义的仅脚手架适配器规划
- 遗留语言安装分支与遗留请求翻译成相同的
  计划者/执行者管道

## 接下来要立即进行的架构更改

如果目标是 ECC 2.0 而不仅仅是“足够工作”，那么下一个模块化
步骤应该是：

1. 将`install-executor.js`拆分为请求规范化、操作规划、
   和执行模块
2. 将特定目标的策略决策转移到适配器拥有的规划方法中
3. 使 `repair` 和 `uninstall` 在类型化操作处理程序上运行，而不是
   只有普通的“复制文件”记录
4. 教导有关安装策略和所有权的清单，以便规划者不会
   不再依赖于路径启发法
5. 仅在内部模块边界确定后才缩小 npm 发布面
   稳定

## 为什么当前模型还不够

如今，ECC 的行为仍然像一个广泛的有效负载复制器：

- `install.sh` 是语言优先和目标分支重的
- 目标部分隐含在目录布局中
- 卸载、修复和修复现已存在，但仍属于早期生命周期命令
- 存储库无法证明先前安装实际写入的内容
- `package.json` 中的发布面仍然很广泛

这就产生了大型计划中已经指出的问题：

- 用户提取的内容超出了他们的利用或工作流程需求
- 支持和升级更加困难，因为安装没有记录
- 目标行为发生漂移，因为安装逻辑在 shell 分支中重复
- Codex 或 OpenCode 等未来目标需要更多特殊情况逻辑
  重用稳定安装合同

## ECC 2.0设计论文

选择性安装应建模为：

1. 将请求的意图解析为规范模块图
2. 通过目标适配器转换该图
3.执行确定性安装操作集
4. 将 install-state 写入持久的事实来源

这意味着 ECC 2.0 需要两份合约，而不是一份：

- 内容合同
  存在哪些模块以及它们如何相互依赖
- 目标合同
  这些模块如何登陆 Claude、Cursor、Antigravity、Codex 或 OpenCode

当前的存储库仅包含早期形式的前半部分。
当前的仓库现在拥有第一个完整的垂直切片，但不是完整的
特定于目标的语义。

## 设计限制

1. 保留 `everything-claude-code` 作为规范源代码库。
2. 在迁移期间保留现有的“install.sh”流。
3. 支持同一规划者的家庭范围和项目范围目标。
4.使卸载/修复/医生成为可能，无需猜测。
5. 避免每个目标的复制逻辑泄漏回模块定义中。
6. 保持未来 Codex 和 OpenCode 支持的附加性，而不是重写。

## 规范工件

### 1. 模块目录

模块目录是规范的内容图。

当前已实施的字段：

- `id`
-`善良`
- `描述`
- `路径`
- `目标`
- `依赖关系`
- `默认安装`
- `成本`
- `稳定性`

ECC 2.0 仍需要的字段：

- `安装策略`
  例如“复制”、“展平规则”、“生成”、“合并配置”
- `所有权`
  ECC 是否完全拥有目标路径或仅在其下生成的文件
- `路径模式`
  例如“保留”、“展平”、“目标模板”
-`冲突`
  不能在一个目标上共存的模块或路径族
- `发布`
  该模块是默认打包、可选还是安装后生成

建议的未来形状：```json
{
  "id": "hooks-runtime",
  "kind": "hooks",
  "paths": ["hooks", "scripts/hooks"],
  "targets": ["claude", "cursor", "opencode"],
  "dependencies": [],
  "installStrategy": "copy",
  "pathMode": "preserve",
  "ownership": "managed",
  "defaultInstall": true,
  "cost": "medium",
  "stability": "stable"
}
```### 2. 型材目录

轮廓保持薄。

它们应该表达用户意图，而不是重复的目标逻辑。

当前已实施的示例：

- `核心`
- `开发人员`
- `安全`
-`研究`
- `满`

还需要字段：

- `默认目标`
- `推荐`
- `排除`
- `需要确认`

这让 ECC 2.0 可以说：

- “developer”是 Claude 和 Cursor 的推荐默认值
- 对于狭窄的本地安装来说，“研究”可能很繁重
- 允许“full”，但不是默认值

### 3. 目标适配器

这是主要缺失的层。

模块图不应该知道：

- 克劳德家住的地方
- 光标如何展平或重新映射内容
- 哪些配置文件需要合并语义而不是盲目复制

那属于目标适配器。

建议接口：```ts
type InstallTargetAdapter = {
  id: string;
  kind: "home" | "project";
  supports(target: string): boolean;
  resolveRoot(input?: string): Promise<string>;
  planOperations(input: InstallOperationInput): Promise<InstallOperation[]>;
  validate?(input: InstallOperationInput): Promise<ValidationIssue[]>;
};
```建议的第一个适配器：

1.`克劳德之家`
   写入`~/.claude/...`
2. `光标项目`
   写入`./.cursor/...`
3.“反重力项目”
   写入`./.agent/...`
4.`法典之家`
   后来
5.`opencode-home`
   后来

这与会话适配器发现中已经提出的相同模式匹配
文档：首先是规范合同，其次是特定于线束的适配器。

## 安装规划模型

当前的 `scripts/install-plan.js` CLI 证明该存储库可以解析请求
模块到过滤后的模块集中。

ECC 2.0需要下一层：操作规划。

建议的阶段：

1. 输入标准化
   - 解析`--target`
   - 解析`--profile`
   - 解析`--modules`
   - 可选择翻译旧语言参数
2.模块分辨率
   - 扩展依赖关系
   - 拒绝冲突
   - 按支持的目标过滤
3.适配器规划
   - 解析目标根
   - 导出精确的复制或生成操作
   - 识别配置合并和目标重新映射
4. 空运行输出
   - 显示选定的模块
   - 显示跳过的模块
   - 显示确切的文件操作
5.突变
   - 执行运营计划
6. 状态写入
   - 仅在成功完成后保留安装状态

建议操作形状：```json
{
  "kind": "copy",
  "moduleId": "rules-core",
  "source": "rules/common/coding-style.md",
  "destination": "/Users/example/.claude/rules/common/coding-style.md",
  "ownership": "managed",
  "overwritePolicy": "replace"
}
```其他操作种类：

- `复制`
- `复制树`
- `平复复制`
- `渲染模板`
- `合并 json`
- `合并 jsonc`
- `mkdir`
- `删除`

## 安装状态合约

安装状态是 ECC 1.x 所缺少的持久合同。

建议的路径约定：

- 克劳德目标：
  `~/.claude/ecc/install-state.json`
- Cursor target:
  `./.cursor/ecc-install-state.json`
- 反重力目标：
  `./.agent/ecc-install-state.json`
- 未来法典目标：
  `~/.codex/ecc-install-state.json`

建议有效负载：```json
{
  "schemaVersion": "ecc.install.v1",
  "installedAt": "2026-03-13T00:00:00Z",
  "lastValidatedAt": "2026-03-13T00:00:00Z",
  "target": {
    "id": "claude-home",
    "root": "/Users/example/.claude"
  },
  "request": {
    "profile": "developer",
    "modules": ["orchestration"],
    "legacyLanguages": ["typescript", "python"]
  },
  "resolution": {
    "selectedModules": [
      "rules-core",
      "agents-core",
      "commands-core",
      "hooks-runtime",
      "platform-configs",
      "workflow-quality",
      "framework-language",
      "database",
      "orchestration"
    ],
    "skippedModules": []
  },
  "source": {
    "repoVersion": "1.9.0",
    "repoCommit": "git-sha",
    "manifestVersion": 1
  },
  "operations": [
    {
      "kind": "copy",
      "moduleId": "rules-core",
      "destination": "/Users/example/.claude/rules/common/coding-style.md",
      "digest": "sha256:..."
    }
  ]
}
```国家要求：

- 足够的卸载详细信息以仅删除 ECC 管理的输出
- 足够的修复细节，以比较所需文件与实际安装的文件
- 足够的细节让医生解释漂移而不是猜测

## 生命周期命令

以下命令是安装状态的生命周期表面：

1. `ecc 列表已安装`
2.`ecc卸载`
3.`ecc医生`
4.`ecc修复`

目前实施情况：

- `ecc list-installed` 路由到 `node script/list-installed.js`
- `ecc uninstall` 路由到 `node script/uninstall.js`
- `ecc doctor` 路由到 `node script/doctor.js`
- `ecc Repair` 路由到 `node script/repair.js`
- 迁移期间遗留脚本入口点仍然可用

### `列表安装`

职责：

- 显示目标 ID 和根
- 显示请求的配置文件/模块
- 显示已解析的模块
- 显示源版本和安装时间

### `卸载`

职责：

- 加载安装状态
- 仅删除状态中记录的 ECC 管理的目的地
- 保持用户创作的不相关文件不变
- 仅在成功清理后删除安装状态

### `医生`

职责：

- 检测丢失的托管文件
- 检测意外的配置漂移
- 检测不再存在的目标根
- 检测清单/版本不匹配

### `修复`

职责：

- 从安装状态重建所需的操作计划
- 重新复制丢失或漂移的托管文件
- 如果当前清单中不再存在请求的模块，则拒绝修复
  除非存在兼容性映射

## 旧版兼容层

当前 `install.sh` 接受：

- `--target <claude|光标|反重力>`
- 语言名称列表

这种行为不可能一下子消失，因为用户已经依赖它了。

ECC 2.0 应该将遗留语言参数转换为兼容性请求。

建议的方法：

1. 保留传统模式的现有 CLI 形状
2. 将语言名称映射到模块请求，例如：
   - `规则核心`
   - 目标兼容的规则子集
3. 即使对于旧版安装也要写入安装状态
4. 将请求标记为 `legacyMode: true`

示例：```json
{
  "request": {
    "legacyMode": true,
    "legacyLanguages": ["typescript", "python"]
  }
}
```这使旧行为保持可用，同时将所有安装移动到相同状态
合同。

## 发布边界

当前的 npm 包仍然通过“package.json”发布广泛的有效负载。

ECC 2.0 应该仔细改进这一点。

推荐顺序：

1. 首先保留一个规范的npm包
2. 在更改发布形式之前使用清单来驱动安装时选择
3. 稍后才考虑在安全的情况下减少包装表面

为什么：

- 选择性安装可以在激进的打包手术之前发货
- 卸载和修复更多地依赖于安装状态而不是发布更改
- 如果包源保持统一，Codex/OpenCode 支持会更容易

以后可能的方向：

- 每个配置文件生成细长的捆绑包
- 生成特定于目标的 tarball
- 可选的重型模块远程获取

这些是第 3 阶段或更高版本，不是配置文件感知安装的先决条件。

## 文件布局推荐

建议的下一个文件：```text
scripts/lib/install-targets/
  claude-home.js
  cursor-project.js
  antigravity-project.js
  registry.js
scripts/lib/install-state.js
scripts/ecc.js
scripts/install-apply.js
scripts/list-installed.js
scripts/uninstall.js
scripts/doctor.js
scripts/repair.js
tests/lib/install-targets.test.js
tests/lib/install-state.test.js
tests/lib/install-lifecycle.test.js
````install.sh` 可以在迁移过程中保留面向用户的入口点，但它
应该成为围绕基于节点的规划器和执行器的薄壳，而不是
继续增长每个目标的 shell 分支。

## 执行顺序

### 第 1 阶段：规划者到合同

1. 保留当前的清单模式和解析器
2.在已解析模块之上添加运营计划
3.定义`ecc.install.v1`状态模式
4. 安装成功时写入安装状态

### 第 2 阶段：目标适配器

1. 将 Claude 安装行为提取到 `claude-home` 适配器中
2. 将 Cursor 安装行为提取到 `cursor-project` 适配器中
3. 将Antigravity安装行为提取到“antigravity-project”适配器中
4. 将`install.sh`简化为参数解析加适配器调用

### 第 3 阶段：生命周期

1. 添加更强大的特定于目标的合并/删除语义
2. 扩大非复制操作的修复/卸载范围
3. 将包裹运输表面减少到模块图而不是广泛的文件夹
4. 决定何时 `ecc-install` 应该成为 `ecc install` 的精简别名

### 第 4 阶段：发布和未来目标

1.评估“package.json”发布表面的安全减少
2.添加`codex-home`
3.添加`opencode-home`
4. 如果包装压力仍然很高，请考虑生成型材束

## 立即回购本地后续步骤

此存储库中信号最强的下一步实施举措是：

1.为类似配置的模块添加特定于目标的合并/删除语义
2. 将修复和卸载扩展到简单的复制文件操作之外
3. 将包裹运输表面减少到模块图而不是广泛的文件夹
4. 决定`ecc-install`是保持独立还是成为`ecc install`
5.添加锁定测试：
   - 特定于目标的合并/删除行为
   - 修复和卸载非复制操作的安全性
   - 统一的`ecc` CLI路由和兼容性保证

## 开放问题

1. 规则是否应该永远在遗留模式下保持语言可寻址，或者仅在
   迁移窗口？
2. `platform-configs` 应该始终与 `core` 一起安装，还是分成
   更小的特定目标模块？
3. 我们希望配置合并语义记录在操作级别还是仅记录在
   适配器逻辑？
4. 高技能家庭最终是否应该转向按需取货而不是
   打包时间包含在内？
5. Codex 和 OpenCode 目标适配器是否应仅在 Claude/Cursor 之后发货
   生命周期命令稳定吗？

## 推荐

将当前清单解析器视为安装适配器“0”：

1. 保留当前安装表面
2. 将真实复制行为移至目标适配器后面
3.为每次成功安装写入安装状态
4.使卸载、修复和修复仅依赖于安装状态
5.然后才收缩包装或添加更多目标

这是从 ECC 1.x 安装程序蔓延到 ECC 2.0 的最短路径
安装/控制合同是确定性的、可支持的和可扩展的。