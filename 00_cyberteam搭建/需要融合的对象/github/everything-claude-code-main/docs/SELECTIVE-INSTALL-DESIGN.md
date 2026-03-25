# ECC 选择性安装设计

## 目的

本文档定义了面向用户的 ECC 选择性安装设计。

它补充了
`docs/SELECTIVE-INSTALL-ARCHITECTURE.md`，重点关注内部运行时
架构和代码边界。

本文档首先回答了产品和运营商的问题：

- 用户如何选择ECC组件
- CLI 应该是什么样的
- 应该存在什么配置文件
- 安装应如何跨线束目标进行
- 设计如何映射到当前 ECC 代码库而不需要重写

## 问题

今天，ECC 仍然感觉像是一个大型有效负载安装程序，尽管现在有存储库
具有首次通过清单和生命周期支持。

用户需要一个更简单的心理模型：

- 安装基线
- 添加他们实际使用的语言包
- 添加他们真正想要的框架配置
- 添加可选功能包，例如安全、研究或编排

选择性安装系统应该让 ECC 感觉可组合，而不是
全有或全无。

在当前的基板中，面向用户的组件仍然是一个别名层
较粗糙的内部安装模块。这意味着包含/排除已经有用
在模块选择级别，但某些文件级别边界仍然不完善
直到底层模块图被更细地分割。

## 目标

1. 让用户快速安装较小的默认 ECC 占用空间。
2. 让用户从可重用的组件系列中组合安装：
   - 核心规则
   - 语言包
   - 框架包
   - 能力包
   - 目标/平台配置
3. 在 Claude、Cursor、Antigravity、Codex 和
   开放代码。
4. 保持安装可检查、可修复和可卸载。
5. 保留与当前 `ecc-install typescript` 的向后兼容性
   推出期间的样式。

## 非目标

- 第一阶段将ECC打包成多个npm包
- 建立远程市场
- 同一阶段的完整控制平面用户界面
- 在选择性安装船舶之前解决每个技能分类问题

## 用户体验原则

### 1.从小事做起

用户应该能够通过一个命令获得有用的 ECC 安装：```bash
ecc install --target claude --profile core
```默认体验不应假设用户需要每个技能系列和
每个框架。

### 2. 按意图构建

用户应该考虑：

- “我想要开发者基线”
- “我需要 TypeScript 和 Python”
- “我想要 Next.js 和 Django”
- “我想要安全包”

用户不必知道原始的内部存储库路径。

### 3. 突变前预览

每个安装路径都应支持试运行规划：```bash
ecc install --target cursor --profile developer --with lang:typescript --with framework:nextjs --dry-run
```该计划应清楚地表明：

- 选定的组件
- 跳过的组件
- 目标根
- 管理路径
- 预期安装状态位置

### 4.本地配置应该是一流的

团队应该能够提交项目级安装配置并使用：```bash
ecc install --config ecc-install.json
```这允许跨贡献者和 CI 进行确定性安装。

## 组件模型

当前清单已使用安装模块和配置文件。面向用户的
设计应保留内部结构，但将其呈现为四个主要
组件系列。

近期实施说明：一些面向用户的组件 ID 仍解析为
共享内部模块，特别是在语言/框架层。的
目录立即改善用户体验，同时保留通向更精细的干净路径
后期阶段的模块粒度。

### 1. 基线

这些是默认的 ECC 构建块：

- 核心规则
- 基线代理
- 核心命令
- 运行时挂钩
- 平台配置
- 工作流程质量原语

当前内部模块的示例：

- `规则核心`
- `代理核心`
- `命令核心`
- `钩子运行时`
- `平台配置`
- `工作流程质量`

### 2. 语言包

语言包为语言生态系统提供了组规则、指南和工作流程。

示例：

- `lang:打字稿`
- `lang:python`
- `郎：去`
- `语言：java`
- `lang:rust`

每个语言包应解析为一个或多个内部模块以及
目标特定资产。

### 3. 框架包

框架包位于语言包之上并引入特定于框架的规则，
技能和可选设置。

示例：

- `框架：反应`
- `框架：nextjs`
- `框架：django`
-`框架：springboot`
- `框架：laravel`

框架包应依赖于正确的语言包或基线
在适当的地方使用原语。

### 4. 功能包

功能包是跨领域的 ECC 功能包。

示例：

- `能力：安全`
- `能力：研究`
- `能力：编排`
- `能力：媒体`
- `能力：内容`

这些应该映射到当前已经引入的模块系列
清单。

## 个人资料

配置文件仍然是最快的入口匝道。

推荐的面向用户的配置文件：

- `核心`
  最小基线，对于大多数尝试 ECC 的用户来说是安全默认值
- `开发人员`
  活跃软件工程工作的最佳默认设置
- `安全`
  基线加上高度安全的指导
-`研究`
  基线加上研究/内容/调查工具
- `满`
  所有已分类且当前支持的内容

配置文件应该可以与附加的“--with”和“--without”标志组合。

例子：```bash
ecc install --target claude --profile developer --with lang:typescript --with framework:nextjs --without capability:orchestration
```## 提议的 CLI 设计

### 主要命令```bash
ecc install
ecc plan
ecc list-installed
ecc doctor
ecc repair
ecc uninstall
ecc catalog
```### 安装 CLI

推荐形状：```bash
ecc install [--target <target>] [--profile <name>] [--with <component>]... [--without <component>]... [--config <path>] [--dry-run] [--json]
```示例：```bash
ecc install --target claude --profile core
ecc install --target cursor --profile developer --with lang:typescript --with framework:nextjs
ecc install --target antigravity --with capability:security --with lang:python
ecc install --config ecc-install.json
```### 计划 CLI

推荐形状：```bash
ecc plan [same selection flags as install]
```目的：

- 生成没有突变的预览
- 作为选择性安装的规范调试界面

### 目录 CLI

推荐形状：```bash
ecc catalog profiles
ecc catalog components
ecc catalog components --family language
ecc catalog show framework:nextjs
```目的：

- 让用户无需阅读文档即可发现有效的组件名称
- 保持配置创作平易近人

### 兼容性 CLI

这些遗留流程在迁移过程中应该仍然有效：```bash
ecc-install typescript
ecc-install --target cursor typescript
ecc typescript
```在内部，这些应该标准化为新的请求模型并写入
安装状态与现代安装相同。

## 建议的配置文件

### 文件名

推荐默认值：

- `ecc-install.json`

可选的未来支持：

- `.ecc/install.json`

### 配置形状```json
{
  "$schema": "./schemas/ecc-install-config.schema.json",
  "version": 1,
  "target": "cursor",
  "profile": "developer",
  "include": [
    "lang:typescript",
    "lang:python",
    "framework:nextjs",
    "capability:security"
  ],
  "exclude": [
    "capability:media"
  ],
  "options": {
    "hooksProfile": "standard",
    "mcpCatalog": "baseline",
    "includeExamples": false
  }
}
```### 字段语义

- `目标`
  选定的线束目标，例如“claude”、“cursor”或“antigravity”
- `个人资料`
  基线配置文件开始
- `包括`
  要添加的附加组件
- `排除`
  从配置文件结果中减去的分量
- `选项`
  不改变组件标识的目标/运行时调整标志

### 优先规则

1. CLI 参数覆盖配置文件值。
2. 配置文件覆盖配置文件默认值。
3. 配置文件默认值覆盖内部模块默认值。

这使得行为可预测且易于解释。

## 模块化安装流程

面向用户的流程应该是：

1.加载配置文件（如果提供或自动检测到）
2. 将 CLI 意图合并到配置意图之上
3. 将请求规范化为规范选择
4. 将配置文件扩展到基线组件
5.添加`include`组件
6. 减去“排除”组件
7.解决依赖关系和目标兼容性
8. 制定计划
9. 如果未处于空运行模式，则应用操作
10. 写入安装状态

重要的用户体验属性是完全相同的流程能力：

- `安装`
-`计划`
- `修复`
- `卸载`

这些命令的不同之处在于操作，而不在于 ECC 如何理解所选安装。

## 目标行为

选择性安装应在所有组件中保留相同的概念组件图
目标，同时让目标适配器决定内容如何落地。

### 克劳德

最适合：

- 家庭范围的 ECC 基线
- 命令、代理、规则、挂钩、平台配置、编排

### 光标

最适合：

- 项目范围内的安装
- 规则加上项目本地自动化和配置

### 反重力

最适合：

- 项目范围的代理/规则/工作流程安装

### 法典/开放代码

应保留附加目标而不是安装程序的特殊叉子。

选择性安装设计应该使这些只是新的适配器加上新的
特定于目标的映射规则，而不是新的安装程序架构。

## 技术可行性

这个设计是可行的，因为 repo 已经有：

- 安装模块和配置文件清单
- 具有安装状态路径的目标适配器
- 计划检查
- 安装状态记录
- 生命周期命令
- 统一的“ecc”CLI 界面

缺失的工作不是概念发明。缺失的工作是产品化
将当前的基底转换为更干净的面向用户的组件模型。

### 第一阶段可行

- 配置文件+包括/排除选择
- `ecc-install.json` 配置文件解析
- 目录/发现命令
- 从面向用户的组件 ID 到内部模块集的别名映射
- 试运行和 JSON 规划

### 第二阶段可行

- 更丰富的目标适配器语义
- 类似配置资产的合并感知操作
- 更强的非复制操作修复/卸载行为

### 稍后

- 减少发布表面
- 生成细长的捆绑包
- 远程组件获取

## 映射到当前 ECC 清单

当前的清单尚未公开真正面向用户的 `lang:*` /
`框架：*` / `功能：*` 分类。这应该被介绍为
现有模块之上的表示层，而不是作为第二个安装程序
发动机。

推荐方法：

- 保留“install-modules.json”作为内部解析目录
- 添加面向用户的组件目录，将友好的组件 ID 映射到一个或多个
  更多内部模块
- 让配置文件引用内部模块或面向用户的组件 ID
  在迁移窗口期间

这可以避免破坏当前的选择性安装基础，同时改善用户体验。

## 建议推出

### 第一阶段：设计和发现

- 最终确定面向用户的组件分类
- 添加配置架构
- 添加 CLI 设计和优先规则

### 第 2 阶段：面向用户的解析层

- 实现组件别名
- 实现配置文件解析
- 实施“包含”/“排除”
- 实施“目录”

### 第 3 阶段：更强的目标语义

- 将更多逻辑纳入目标拥有的规划中
- 干净地支持合并/生成操作
- 提高修复/卸载保真度

### 第 4 阶段：包装优化

- 狭窄的出版表面
- 评估生成的包

## 推荐

下一个实施举措不应该是“重写安装程序”。

应该是：

1. 保留当前的清单/运行时底层
2.添加面向用户的组件目录和配置文件
3.添加 `include` / `exclude` 选择和目录发现
4. 让现有的规划器和生命周期堆栈使用该模型

这是从当前 ECC 代码库到真正选择性的最短路径
安装体验感觉就像 ECC 2.0，而不是大型旧版安装程序。