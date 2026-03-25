# 架构

本文档解释 **为什么** gstack是按照现在这种方式构建的。有关设置和命令,请参阅CLAUDE.md。有关贡献,请参阅CONTRIBUTING.md。

## 核心思想

gstack为Claude Code提供了一个持久的浏览器和一套固执己见的工作流技能。浏览器是困难的部分——其他一切都是Markdown。

关键洞察:与浏览器交互的AI代理需要 **亚秒级延迟** 和 **持久状态**。如果每个命令都冷启动一个浏览器,你每个工具调用要等待3-5秒。如果浏览器在命令之间死掉,你会丢失cookie、标签页和登录会话。所以gstack运行一个长期运行的Chromium守护进程,CLI通过localhost HTTP与之对话。

```
Claude Code                     gstack
─────────                      ──────
                               ┌──────────────────────┐
  Tool call: $B snapshot -i    │  CLI (compiled binary)│
  ─────────────────────────→   │  • reads state file   │
                               │  • POST /command      │
                               │    to localhost:PORT   │
                               └──────────┬───────────┘
                                          │ HTTP
                               ┌──────────▼───────────┐
                               │  Server (Bun.serve)   │
                               │  • dispatches command  │
                               │  • talks to Chromium   │
                               │  • returns plain text  │
                               └──────────┬───────────┘
                                          │ CDP
                               ┌──────────▼───────────┐
                               │  Chromium (headless)   │
                               │  • persistent tabs     │
                               │  • cookies carry over  │
                               │  • 30min idle timeout  │
                               └───────────────────────┘
```

首次调用启动一切(~3秒)。之后的每次调用:~100-200毫秒。

## 为什么用Bun

Node.js也可以。Bun在这里更好,原因有三个:

1. **编译后的二进制文件。** `bun build --compile` 生成一个单一的约58MB可执行文件。运行时没有 `node_modules`,没有 `npx`,没有PATH配置。二进制文件直接运行。这很重要,因为gstack安装到 `~/.claude/skills/`,用户不希望在那里管理Node.js项目。

2. **原生SQLite。** Cookie解密直接读取Chromium的SQLite cookie数据库。Bun有内置的 `new Database()` —— 没有 `better-sqlite3`,没有原生插件编译,没有gyp。少了一个在不同机器上会坏掉的东西。

3. **原生TypeScript。** 服务器在开发时以 `bun run server.ts` 运行。没有编译步骤,没有 `ts-node`,没有要调试的源映射。编译后的二进制文件用于部署;源文件用于开发。

4. **内置HTTP服务器。** `Bun.serve()` 快速、简单,不需要Express或Fastify。服务器处理约10条路由。框架会是开销。

瓶颈永远是Chromium,而不是CLI或服务器。Bun的启动速度(编译二进制文件约1ms vs Node约100ms)很好,但不是我们选择它的原因。编译后的二进制文件和原生SQLite才是。

## 守护进程模型

### 为什么不每个命令启动一个浏览器?

Playwright可以在约2-3秒内启动Chromium。对于单个截图,这很好。对于有20+命令的QA会话,那是40+秒的浏览器启动开销。更糟的是:你在命令之间丢失所有状态。Cookie、localStorage、登录会话、打开的标签页——全部丢失。

守护进程模型意味着:

- **持久状态。** 登录一次,保持登录。打开一个标签页,它保持打开。localStorage在命令之间保持。
- **亚秒级命令。** 首次调用后,每个命令只是一个HTTP POST。包括Chromium的工作在内约100-200ms往返。
- **自动生命周期。** 服务器在首次使用时自动启动,空闲30分钟后自动关闭。不需要进程管理。

### 状态文件

服务器写入 `.gstack/browse.json`(通过tmp + rename原子写入,模式0o600):

```json
{ "pid": 12345, "port": 34567, "token": "uuid-v4", "startedAt": "...", "binaryVersion": "abc123" }
```

CLI读取这个文件来找到服务器。如果文件丢失、过时,或PID死亡,CLI生成一个新服务器。

### 端口选择

10000-60000之间的随机端口(冲突时重试最多5次)。这意味着10个Conductor工作空间可以各自运行自己的browse守护进程,零配置和零端口冲突。旧方法(扫描9400-9409)在多工作空间设置中经常坏掉。

### 版本自动重启

构建将 `git rev-parse HEAD` 写入 `browse/dist/.version`。每次CLI调用时,如果二进制文件的版本与运行中服务器的 `binaryVersion` 不匹配,CLI杀死旧服务器并启动一个新服务器。这完全防止了"过时二进制文件"这类bug——重建二进制文件,下一个命令自动获取它。

## 安全模型

### 仅localhost

HTTP服务器绑定到 `localhost`,而不是 `0.0.0.0`。网络无法访问它。

### Bearer token认证

每个服务器会话生成一个随机UUID token,写入状态文件,模式0o600(仅所有者可读)。每个HTTP请求必须包含 `Authorization: Bearer <token>`。如果token不匹配,服务器返回401。

这防止同一机器上的其他进程与你的browse服务器对话。Cookie选择器UI(`/cookie-picker`)和健康检查(`/health`)豁免——它们仅限localhost,不执行命令。

### Cookie安全

Cookie是gstack处理的最敏感数据。设计:

1. **Keychain访问需要用户批准。** 每个浏览器首次cookie导入触发macOS Keychain对话框。用户必须点击"允许"或"始终允许"。gstack永远不会静默访问凭证。

2. **解密在进程内发生。** Cookie值在内存中解密(PBKDF2 + AES-128-CBC),加载到Playwright上下文中,永远不以明文写入磁盘。Cookie选择器UI从不显示cookie值——只有域名和计数。

3. **数据库是只读的。** gstack复制Chromium cookie DB到临时文件(以避免与运行中浏览器的SQLite锁冲突)并以只读方式打开。它永远不会修改你真实浏览器的cookie数据库。

4. **Key缓存是按会话的。** Keychain密码和派生AES密钥缓存在服务器生命周期内的内存中。当服务器关闭时(空闲超时或显式停止),缓存消失。

5. **日志中没有cookie值。** 控制台、网络和对话框日志从不包含cookie值。`cookies` 命令输出cookie元数据(域名、名称、过期),但值被截断。

### Shell注入预防

浏览器注册表(Comet、Chrome、Arc、Brave、Edge)是硬编码的。数据库路径从已知常量构建,永远不从用户输入构造。Keychain访问使用 `Bun.spawn()` 和显式参数数组,而不是shell字符串插值。

## Ref系统

Refs(`@e1`、`@e2`、`@c1`)是代理如何 addressing 页面元素而不写CSS选择器或XPath的方式。

### 它如何工作

```
1. Agent运行: $B snapshot -i
2. Server调用Playwright的page.accessibility.snapshot()
3. Parser遍历ARIA树,分配顺序refs: @e1, @e2, @e3...
4. 对于每个ref,构建Playwright Locator: getByRole(role, { name }).nth(index)
5. 在BrowserManager实例上存储Map<string, RefEntry>(role + name + Locator)
6. 将注释树作为纯文本返回

之后:
7. Agent运行: $B click @e3
8. Server解析@e3 → Locator → locator.click()
```

### 为什么用Locator,而不是DOM mutation

显而易见的方法是向DOM注入 `data-ref="@e1"` 属性。这会在以下情况下坏掉:

- **CSP(内容安全策略)。** 许多生产站点阻止来自脚本的DOM修改。
- **React/Vue/Svelte水合。** 框架调和可以剥离注入的属性。
- **Shadow DOM。** 从外部无法到达shadow根。

Playwright Locator在DOM外部。它们使用ARIA树(Chromium内部维护)和 `getByRole()` 查询。没有DOM mutation,没有CSP问题,没有框架冲突。

### Ref生命周期

Ref在导航时清除(主框架上的 `framenavigated` 事件)。这是正确的——导航后,所有locator都过时了。代理必须再次运行 `snapshot` 以获取新的refs。这是设计使然:过时的refs应该大声失败,而不是点击错误的元素。

### Ref过期检测

SPA可以在不触发 `framenavigated` 的情况下改变DOM(例如React路由转换、标签切换、模态打开)。这使得refs过时,即使页面URL没有改变。为了捕捉这个,`resolveRef()` 在使用任何ref之前执行异步 `count()` 检查:

```
resolveRef(@e3) → entry = refMap.get("e3")
                → count = await entry.locator.count()
                → if count === 0: throw "Ref @e3已过期——元素不再存在。运行'snapshot'获取新的refs。"
                → if count > 0: return { locator }
```

这快速失败(~5ms开销)而不是让Playwright的30秒动作超时在缺失元素上到期。`RefEntry` 存储 `role` 和 `name` 元数据以及Locator,以便错误消息可以告诉代理元素是什么。

### 游标交互式refs(@c)

`-C` 标志找到可点击但不在ARIA树中的元素——使用 `cursor: pointer` 样式化的东西、具有 `onclick` 属性的元素或自定义 `tabindex`。这些在单独的命名空间中获取 `@c1`、`@c2` refs。这捕捉框架呈现为 `<div>` 但实际上是按钮的自定义组件。

## 日志架构

三个环形缓冲区(每个50,000条目,O(1)推送):

```
浏览器事件 → CircularBuffer(内存) → 异步刷新到.gstack/*.log
```

控制台消息、网络请求和对话框事件各有自己的缓冲区。每1秒刷新一次——服务器仅追加自上次刷新以来的新条目。这意味着:

- HTTP请求处理永远不会被磁盘I/O阻塞
- 日志在服务器崩溃中存活(最多1秒数据丢失)
- 内存有界限(50K条目 × 3个缓冲区)
- 磁盘文件是仅追加的,可由外部工具读取

`console`、`network` 和 `dialog` 命令从内存缓冲区读取,而不是磁盘。磁盘文件用于事后调试。

## SKILL.md模板系统

### 问题

SKILL.md文件告诉Claude如何使用browse命令。如果文档列出一个不存在的标志,或错过了添加的命令,代理会出错。手动维护的文档总是与代码漂移。

### 解决方案

```
SKILL.md.tmpl          (人工编写的散文 + 占位符)
       ↓
gen-skill-docs.ts      (读取源代码元数据)
       ↓
SKILL.md               (提交,自动生成的部分)
```

模板包含需要人工判断的工作流、提示和示例。占位符在构建时从源代码填充:

| 占位符 | 来源 | 它生成什么 |
|--------|------|------------|
| `{{COMMAND_REFERENCE}}` | `commands.ts` | 分类命令表 |
| `{{SNAPSHOT_FLAGS}}` | `snapshot.ts` | 带示例的标志参考 |
| `{{PREAMBLE}}` | `gen-skill-docs.ts` | 启动块:更新检查、会话跟踪、贡献者模式、AskUserQuestion格式 |
| `{{BROWSE_SETUP}}` | `gen-skill-docs.ts` | 二进制发现 + 设置说明 |
| `{{BASE_BRANCH_DETECT}}` | `gen-skill-docs.ts` | PR定位技能的动态基础分支检测(ship、review、qa、plan-ceo-review) |
| `{{QA_METHODOLOGY}}` | `gen-skill-docs.ts` | /qa和/qa-only的共享QA方法块 |
| `{{DESIGN_METHODOLOGY}}` | `gen-skill-docs.ts` | /plan-design-review和/design-review的共享设计审计方法 |
| `{{REVIEW_DASHBOARD}}` | `gen-skill-docs.ts` | /ship预飞的审查准备仪表板 |
| `{{TEST_BOOTSTRAP}}` | `gen-skill-docs.ts` | /qa、/ship、/design-review的测试框架检测、引导、CI/CD设置 |

这是结构合理的——如果代码中存在命令,它就会出现在文档中。如果不存在,就不能出现。

### 前导码

每个技能以 `{{PREAMBLE}}` 块开始,在技能的逻辑之前运行。它在一个bash命令中处理四件事:

1. **更新检查** —— 调用 `gstack-update-check`,报告是否有升级可用。
2. **会话跟踪** —— 接触 `~/.gstack/sessions/$PPID` 并计算活动会话(过去2小时内修改的文件)。当3+会话运行时,所有技能进入"ELI16模式"——每个问题都会重新为用户接地上下文,因为他们在同时处理多个窗口。
3. **贡献者模式** —— 从配置读取 `gstack_contributor`。当为true时,代理在gstack本身行为不当时向 `~/.gstack/contributor-logs/` 提交随意现场报告。
4. **AskUserQuestion格式** —— 通用格式:上下文、问题、`建议:选择X因为___`、字母选项。在所有技能中保持一致。

### 为什么提交,而不是运行时生成?

三个原因:

1. **Claude在技能加载时读取SKILL.md。** 当用户调用 `/browse` 时没有构建步骤。文件必须已经存在且正确。
2. **CI可以验证新鲜度。** `gen:skill-docs --dry-run` + `git diff --exit-code` 在合并前捕捉过时的文档。
3. **Git blame工作。** 你可以看到命令何时添加以及在哪个提交中。

### 模板测试层

| 层 | 什么 | 成本 | 速度 |
|----|------|------|------|
| 1 — 静态验证 | 解析SKILL.md中的每个 `$B` 命令,对照注册表验证 | 免费 | <2s |
| 2 — 通过 `claude -p` 的E2E | 生成真实Claude会话,运行每个技能,检查错误 | ~$3.85 | ~20分钟 |
| 3 — LLM-as-judge | Sonnet对清晰度/完整性/可操作性评分 | ~$0.15 | ~30秒 |

第1层在每次 `bun test` 时运行。第2+3层在 `EVALS=1` 后门控。理念:免费捕捉95%的问题,只在需要判断时使用LLM。

## 命令分发

命令按副作用分类:

- **READ**(text、html、links、console、cookies、...): 无变异。可以安全重试。返回页面状态。
- **WRITE**(goto、click、fill、press、...): 改变页面状态。不是幂等的。
- **META**(snapshot、screenshot、tabs、chain、...): 不完全适合读/写的服务器级操作。

这不仅仅是组织性的。服务器用它来进行分发:

```typescript
if (READ_COMMANDS.has(cmd))  → handleReadCommand(cmd, args, bm)
if (WRITE_COMMANDS.has(cmd)) → handleWriteCommand(cmd, args, bm)
if (META_COMMANDS.has(cmd))  → handleMetaCommand(cmd, args, bm, shutdown)
```

`help` 命令返回所有三组,以便代理可以自我发现可用命令。

## 错误哲学

错误是为AI代理准备的,不是人类。每个错误消息必须是可操作的:

- "Element not found" → "元素未找到或不可交互。运行 `snapshot -i` 查看可用元素。"
- "Selector matched multiple elements" → "选择器匹配了多个元素。使用 `snapshot` 的@refs代替。"
- Timeout → "30秒后导航超时。页面可能很慢或URL可能错误。"

Playwright的原生错误通过 `wrapError()` 重写,以剥离内部堆栈跟踪并添加指导。代理应该能够阅读错误并知道下一步做什么,无需人工干预。

### 崩溃恢复

服务器不尝试自我修复。如果Chromium崩溃(`browser.on('disconnected')`),服务器立即退出。CLI在下一个命令上检测到死服务器并自动重启。这比尝试重新连接到一个半死不活的浏览器进程更简单和更可靠。

## E2E测试基础设施

### 会话运行器(`test/helpers/session-runner.ts`)

E2E测试生成 `claude -p` 作为完全独立的子进程——不是通过Agent SDK,因为它不能在Claude Code会话内嵌套。运行器:

1. 将提示写入临时文件(避免shell转义问题)
2. 生成 `sh -c 'cat prompt | claude -p --output-format stream-json --verbose'`
3. 从stdout流式传输NDJSON以获取实时进度
4. 与可配置超时竞争
5. 将完整NDJSON转录解析为结构化结果

`parseNDJSON()` 函数是纯的——没有I/O,没有副作用——使其可以独立测试。

### 可观测性数据流

```
  skill-e2e.test.ts
        │
        │ generates runId, passes testName + runId to each call
        │
  ┌─────┼──────────────────────────────┐
  │     │                              │
  │  runSkillTest()              evalCollector
  │  (session-runner.ts)         (eval-store.ts)
  │     │                              │
  │  per tool call:              per addTest():
  │  ┌──┼──────────┐              savePartial()
  │  │  │          │                   │
  │  ▼  ▼          ▼                   ▼
  │ [HB] [PL]    [NJ]          _partial-e2e.json
  │  │    │        │             (atomic overwrite)
  │  │    │        │
  │  ▼    ▼        ▼
  │ e2e-  prog-  {name}
  │ live  ress   .ndjson
  │ .json .log
  │
  │  on failure:
  │  {name}-failure.json
  │
  │  ALL files in ~/.gstack-dev/
  │  Run dir: e2e-runs/{runId}/
  │
  │         eval-watch.ts
  │              │
  │        ┌─────┴─────┐
  │     read HB     read partial
  │        └─────┬─────┘
  │              ▼
  │        render dashboard
  │        (stale >10min? warn)
```

**Split ownership:** session-runner拥有heartbeat(当前测试状态),eval-store拥有partial results(完成的测试状态)。观察者读取两者。没有任何组件知道另一个——它们只通过文件系统共享数据。

**Non-fatal everything:** 所有可观测性I/O都包装在try/catch中。写入失败永远不会导致测试失败。测试本身是真相来源;可观测性是尽力而为。

**机器可读诊断:** 每个测试结果包括 `exit_reason`(success、timeout、error_max_turns、error_api、exit_code_N)、`timeout_at_turn` 和 `last_tool_call`。这支持如下 `jq` 查询:
```bash
jq '.tests[] | select(.exit_reason == "timeout") | .last_tool_call' ~/.gstack-dev/evals/_partial-e2e.json
```

### Eval持久化(`test/helpers/eval-store.ts`)

`EvalCollector` 累积测试结果并以两种方式写入:

1. **增量:** `savePartial()` 在每个测试后写入 `_partial-e2e.json`(原子:写入 `.tmp`,`fs.renameSync`)。
   生存kills。
2. **最终:** `finalize()` 写入带时间戳的eval文件(例如 `e2e-20260314-143022.json`)。partial文件永远不清理——它在eval文件旁边持久化用于可观测性。

`eval:compare` 对比两个eval运行。`eval:summary` 聚合 `~/.gstack-dev/evals/` 中所有运行的数据。

### 测试层

| 层 | 什么 | 成本 | 速度 |
|----|------|------|------|
| 1 — 静态验证 | 解析 `$B` 命令,对照注册表验证,观察性单元测试 | 免费 | <5s |
| 2 — 通过 `claude -p` 的E2E | 生成真实Claude会话,运行每个技能,扫描错误 | ~$3.85 | ~20分钟 |
| 3 — LLM-as-judge | Sonnet对清晰度/完整性/可操作性评分 | ~$0.15 | ~30秒 |

第1层在每次 `bun test` 时运行。第2+3层在 `EVALS=1` 后门禁。理念:免费捕捉95%的问题,只在需要判断调用和集成测试时使用LLM。

## 故意不在这里的东西

- **没有WebSocket流。** HTTP请求/响应更简单,可以curl调试,速度足够。流会为边际收益增加复杂性。
- **没有MCP协议。** MCP为每个请求添加JSON模式开销并需要持久连接。普通HTTP + 普通文本输出对token更轻,更容易调试。
- **没有多用户支持。** 每个工作空间一个服务器,一个用户。token认证是纵深防御,不是多租户。
- **没有Windows/Linux cookie解密。** macOS Keychain是唯一支持的凭证存储。Linux(GNOME Keyring/kwallet)和Windows(DPAPI)在架构上可行但未实现。
- **没有iframe支持。** Playwright可以处理iframe但ref系统尚未跨帧边界。这是请求最多的缺失功能。
