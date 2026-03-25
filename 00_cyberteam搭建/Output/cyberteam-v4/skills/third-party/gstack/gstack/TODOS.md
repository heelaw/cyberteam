# 待办事项

## 浏览

### 将server.ts打包到编译的二进制文件中

**什么:** 完全消除 `resolveServerScript()` 回退链 —— 将server.ts打包到编译的browse二进制文件中。

**为什么:** 当前的回退链(检查cli.ts旁边、检查全局安装)很脆弱,在v0.3.2中导致了bug。单个编译二进制文件更简单、更可靠。

**背景:** Bun的 `--compile` 标志可以打包多个入口点。服务器当前通过文件路径查找在运行时解析。打包它完全移除了解析步骤。

**工作量:** M
**优先级:** P2
**依赖:** 无

### 会话(隔离的浏览器实例)

**什么:** 带独立cookie/存储/历史的隔离浏览器实例,可按名称寻址。

**为什么:** 支持不同用户角色的并行测试、A/B测试验证和干净的认证状态管理。

**背景:** 需要Playwright浏览器上下文隔离。每个会话获得自己的上下文,带有独立cookie/localStorage。需要视频录制(干净的上下文生命周期)和认证vault。

**工作量:** L
**优先级:** P3

### 视频录制

**什么:** 将浏览器交互录制为视频(开始/停止控制)。

**为什么:** QA报告和PR正文中的视频证据。当前延迟,因为 `recreateContext()` 破坏页面状态。

**背景:** 需要会话以获得干净的上下文生命周期。Playwright支持每个上下文视频录制。还需要WebM → GIF转换以嵌入PR。

**工作量:** M
**优先级:** P3
**依赖:** 会话

### v20加密格式支持

**什么:** 未来Chromium cookie DB版本的AES-256-GCM支持(当前v10)。

**为什么:** 未来Chromium版本可能更改加密格式。主动支持防止坏掉。

**工作量:** S
**优先级:** P3

### 状态持久化

**什么:** 将cookie + localStorage保存/加载到JSON文件以实现可重现的测试会话。

**为什么:** 支持"从我上次停下的地方继续"的QA会话和可重复的认证状态。

**背景:** 来自handoff功能的 `saveState()`/`restoreState()` helpers(browser-manager.ts)已经捕获cookie + localStorage + sessionStorage + URL。在此基础上添加文件I/O约20行。

**工作量:** S
**优先级:** P3
**依赖:** 会话

### 认证vault

**什么:** 加密凭证存储,按名称引用。LLM永远看不到密码。

**为什么:** 安全 —— 当前认证凭证流经LLM上下文。Vault将密钥排除在AI视野之外。

**工作量:** L
**优先级:** P3
**依赖:** 会话、状态持久化

### iframe支持

**什么:** 用于跨帧交互的 `frame <sel>` 和 `frame main` 命令。

**为什么:** 许多web应用使用iframe(嵌入、支付表单、广告)。当前对browse不可见。

**工作量:** M
**优先级:** P4

### 语义定位器

**什么:** 带附加操作的 `find role/label/text/placeholder/testid`。

**为什么:** 比CSS选择器或ref编号更 resilient 的元素选择。

**工作量:** M
**优先级:** P4

### 设备仿真预设

**什么:** 用于移动/平板测试的 `set device "iPhone 16 Pro"`。

**为什么:** 无需手动视口调整即可进行响应式布局测试。

**工作量:** S
**优先级:** P4

### 网络模拟/路由

**什么:** 拦截、阻止和模拟网络请求。

**为什么:** 测试错误状态、加载状态和离线行为。

**工作量:** M
**优先级:** P4

### 下载处理

**什么:** 带路径控制的点击下载。

**为什么:** 端到端测试文件下载流程。

**工作量:** S
**优先级:** P4

### 内容安全

**什么:** `--max-output` 截断、`--allowed-domains` 过滤。

**为什么:** 防止上下文窗口溢出并限制导航到安全域。

**工作量:** S
**优先级:** P4

### 流式传输(WebSocket实时预览)

**什么:** 用于配对浏览会话的基于WebSocket的实时预览。

**为什么:** 支持实时协作 —— 人类观看AI浏览。

**工作量:** L
**优先级:** P4

### CDP模式

**什么:** 通过Chrome DevTools Protocol连接到已运行的Chrome/Electron应用。

**为什么:** 测试生产应用、Electron应用和现有浏览器会话,无需启动新实例。

**工作量:** M
**优先级:** P4

### Linux/Windows cookie解密

**什么:** 非macOS cookie导入的GNOME Keyring / kwallet / DPAPI支持。

**为什么:** 跨平台cookie导入。当前仅macOS(Keychain)。

**工作量:** L
**优先级:** P4

## 发布

### Ship日志 —— /ship运行的持久记录

**什么:** 在每次/ship运行结束时向 `.gstack/ship-log.json` 追加结构化JSON条目(版本、日期、分支、PR URL、审查发现、Greptile统计、完成待办事项、测试结果)。

**为什么:** /retro没有关于发布速度的结构化数据。Ship日志支持:每周PR趋势、审查发现率、Greptile随时间信号、测试套件增长。

**背景:** /retro已经读取greptile-history.md —— 相同模式。Eval持久化(eval-store.ts)显示JSON追加模式存在于代码库中。ship模板中约15行。

**工作量:** S
**优先级:** P2
**依赖:** 无

### 部署后验证(ship + browse)

**什么:** 推送后,浏览暂存/预览URL,截取关键页面截图,检查控制台JS错误,通过快照diff比较暂存vs生产。在PR正文中包含验证截图。如果发现关键错误则停止。

**为什么:** 在合并前捕捉部署时回归(JS错误、破碎布局)。

**背景:** 需要S3上传基础设� 用于PR截图。与可视化PR注释配对。

**工作量:** L
**优先级:** P2
**依赖:** /setup-gstack-upload、可视化PR注释

### 带截图的PR正文可视化验证

**什么:** /ship步骤7.5:推送后截取关键页面截图,嵌入PR正文。

**为什么:** PR中的可视化证据。审查者无需本地部署即可看到更改。

**背景:** 第3.6阶段的一部分。需要S3上传用于图片托管。

**工作量:** M
**优先级:** P2
**依赖:** /setup-gstack-upload

## 审查

### 内联PR注释

**什么:** /ship和/review在特定file:line位置发布内联审查评论,使用 `gh api` 创建pull request review comments。

**为什么:** 行级注释比顶级评论更可操作。PR线程成为Greptile、Claude和人类审查者之间的逐行对话。

**背景:** GitHub通过 `gh api repos/$REPO/pulls/$PR/reviews` 支持内联review comments。与第3.6阶段可视化注释自然配对。

**工作量:** S
**优先级:** P2
**依赖:** 无

### Greptile训练反馈导出

**什么:** 将greptile-history.md聚合为机器可读的JSON摘要,了解假阳性模式,可导出给Greptile团队以改进模型。

**为什么:** 关闭反馈循环 —— Greptile可以使用FP数据停止在其代码库上犯同样的错误。

**背景:** 曾是P3未来想法。升级到P2,因为greptile-history.md数据基础设施已经存在。信号数据已经被收集;这只是使其可导出。约40行。

**工作量:** S
**优先级:** P2
**依赖:** 累积足够FP数据(10+条目)

### 带注释截图的可视化审查

**什么:** /review步骤4.5:浏览PR的预览部署,更改页面的注释截图,与生产环境比较,检查响应式布局,验证可访问性树。

**为什么:** 可视化diff捕捉代码审查遗漏的布局回归。

**背景:** 第3.6阶段的一部分。需要S3上传用于图片托管。

**工作量:** M
**优先级:** P2
**依赖:** /setup-gstack-upload

## QA

### QA趋势跟踪

**什么:** 随着时间比较baseline.json,检测跨QA运行的回归。

**为什么:** 发现质量趋势 —— 应用在变好还是变坏?

**背景:** QA已经编写结构化报告。这添加了跨运行比较。

**工作量:** S
**优先级:** P2

### CI/CD QA集成

**什么:** `/qa` 作为GitHub Action步骤,如果健康分数下降则失败PR。

**为什么:** CI中的自动化质量门。在合并前捕捉回归。

**工作量:** M
**优先级:** P2

### 智能默认QA层

**什么:** 几次运行后,检查index.md中用户通常选择的层,跳过AskUserQuestion。

**为什么:** 减少重复用户的摩擦。

**工作量:** S
**优先级:** P2

### 无障碍审计模式

**什么:** 用于专注无障碍测试的 `--a11y` 标志。

**为什么:** 除了一般QA清单之外的专用无障碍测试。

**工作量:** S
**优先级:** P3

### 非GitHub提供商的CI/CD生成

**什么:** 扩展CI/CD引导以生成GitLab CI(`.gitlab-ci.yml`)、CircleCI(`.circleci/config.yml`)和Bitrise管道。

**为什么:** 并非所有项目都使用GitHub Actions。通用CI/CD引导将使测试引导适用于每个人。

**背景:** v1仅随GitHub Actions一起提供。检测逻辑已经检查 `.gitlab-ci.yml`、`.circleci/`、`bitrise.yml` 并跳过并显示信息性注释。每个提供商需要在 `generateTestBootstrap()` 的模板文本中约20行。

**工作量:** M
**优先级:** P3
**依赖:** 测试引导(已发布)

### 自动升级弱测试(★)为强测试(★★★)

**什么:** 当步骤3.4覆盖率审计识别出现有的★级测试(冒烟/平凡断言)时,生成改进版本,测试边缘情况和错误路径。

**为什么:** 许多代码库的测试技术上存在但不能捕捉真实bug —— `expect(component).toBeDefined()` 不是测试行为。升级这些弥合了"有测试"和"有好测试"之间的差距。

**背景:** 需要测试覆盖率审计的质量评分规则。修改现有测试文件比创建新文件风险更大 —— 需要仔细diff以确保升级的测试仍然通过。考虑创建伴随测试文件而不是修改原始文件。

**工作量:** M
**优先级:** P3
**依赖:** 测试质量评分(已发布)

## 回顾

### 部署健康跟踪(retro + browse)

**什么:** 截图生产状态,检查性能指标(页面加载时间),统计关键页面的控制台错误,跟踪回顾窗口的趋势。

**为什么:** 回顾应该包括生产健康以及代码指标。

**背景:** 需要browse集成。截图 + 指标输入回顾输出。

**工作量:** L
**优先级:** P3
**依赖:** 浏览会话

## 基础设施

### /setup-gstack-upload技能(S3桶)

**什么:** 配置S3桶用于图片托管。可视化PR注释的一次性设置。

**为什么:** /ship和/review中可视化PR注释的先决条件。

**工作量:** M
**优先级:** P2

### gstack-upload helper

**什么:** `browse/bin/gstack-upload` —— 上传文件到S3,返回公共URL。

**为什么:** 所有需要将图片嵌入PR的技能的共享工具。

**工作量:** S
**优先级:** P2
**依赖:** /setup-gstack-upload

### WebM到GIF转换

**什么:** 基于ffmpeg的WebM → GIF转换,用于PR中的视频证据。

**为什么:** GitHub PR正文渲染GIF但不渲染WebM。需要视频录制证据。

**工作量:** S
**优先级:** P3
**依赖:** 视频录制

### 部署验证技能

**什么:** 轻量级部署后冒烟测试:点击关键URL,验证200,截图关键页面,控制台错误检查,与基线快照比较。通过/失败带证据。

**为什么:** 快速部署后置信度检查,与完整QA分开。

**工作量:** M
**优先级:** P2

### GitHub Actions评估上传

**什么:** 在CI中运行评估套件,将结果JSON作为artifact上传,在PR上发布摘要评论。

**为什么:** CI集成在合并前捕捉质量回归,并为每个PR提供持久评估记录。

**背景:** 需要CI secrets中的 `ANTHROPIC_API_KEY`。成本约$4/次。Eval持久化系统(v0.3.6)将JSON写入 `~/.gstack-dev/evals/` —— CI将作为GitHub Actions artifacts上传,并使用 `eval:compare` 发布delta评论。

**工作量:** M
**优先级:** P2
**依赖:** Eval持久化(v0.3.6中已发布)

### E2E模型固定

**什么:** 将E2E测试固定到claude-sonnet-4-6以提高成本效率,为不稳定LLM响应添加retry:2。

**为什么:** 降低E2E测试成本和不稳定性。

**工作量:** XS
**优先级:** P2

### Eval Web仪表板

**什么:** `bun run eval:dashboard` 提供本地HTML与图表:成本趋势、检测率、通过/失败历史。

**为什么:** 视觉图表比CLI工具更好地发现趋势。

**背景:** 读取 `~/.gstack-dev/evals/*.json`。约200行HTML + chart.js通过Bun HTTP服务器。

**工作量:** M
**优先级:** P3
**依赖:** Eval持久化(v0.3.6中已发布)

### CI/CD QA质量门

**什么:** 将 `/qa` 作为GitHub Action步骤运行,如果健康分数低于阈值则失败PR。

**为什么:** 自动化质量门在合并前捕捉回归。当前QA是手动的 —— CI集成使其成为标准工作流的一部分。

**背景:** 需要CI中提供headless browse二进制文件。`/qa` 技能已经产生带有健康分数的 `baseline.json` —— CI步骤将比较主分支基线,如果分数下降则失败。需要 `ANTHROPIC_API_KEY`,因为 `/qa` 使用Claude。

**工作量:** M
**优先级:** P2
**依赖:** 无

### 跨平台URL打开helper

**什么:** `gstack-open-url` helper脚本 —— 检测平台,使用 `open`(macOS)或 `xdg-open`(Linux)。

**为什么:** 首次完整性原则介绍使用macOS `open` 来启动文章。如果gstack支持Linux,这会静默失败。

**工作量:** S(人工:约30分钟 / CC:约2分钟)
**优先级:** P4
**依赖:** 无

### 基于CDP的DOM突变检测用于ref过期

**什么:** 使用Chrome DevTools Protocol `DOM.documentUpdated` / MutationObserver事件在DOM更改时主动使过时的refs无效,无需 require explicit `snapshot` 调用。

**为什么:** 当前ref过期检测(async count()检查)仅在操作时捕捉过时refs。CDP突变检测会在refs变 过时 时主动警告,完全防止SPA重新渲染的5秒超时。

**背景:** ref过期修复的第1+2部分(RefEntry元数据 + 通过count()的急切验证)已发布。这是第3部分 —— 最雄心勃勃的部分。需要CDP会话以及Playwright、MutationObserver bridge和仔细的性能调优以避免每次DOM更改的开销。

**工作量:** L
**优先级:** P3
**依赖:** Ref过期第1+2部分(已发布)

## 办公时间/设计

### 设计文档 → Supabase团队存储同步

**什么:** 将设计文档(`*-design-*.md`)添加到Supabase同步管道,以及测试计划、回顾快照和QA报告。

**为什么:** 跨团队设计规模化发现。本地 `~/.gstack/projects/$SLUG/` 关键字grep发现适用于同机器用户现在,但Supabase同步使其适用于整个团队。重复想法浮出水面,每个人都能看到已经探索了什么。

**背景:** /office-hours将设计文档写入 `~/.gstack/projects/$SLUG/`。团队存储已经同步测试计划、回顾快照、QA报告。设计文档遵循相同模式 —— 只需添加同步适配器。

**工作量:** S
**优先级:** P2
**依赖:** `garrytan/team-supabase-store` 分支登陆main

### /yc-prep技能

**什么:** 在/office-hours识别强信号后帮助创始人准备YC申请的技能。从设计文档中提取,为YC申请问题构建答案,进行模拟面试。

**为什么:** 关闭循环。/office-hours识别创始人,/yc-prep帮助他们好好申请。设计文档已经包含YC申请的大部分原材料。

**工作量:** M(人工:约2周 / CC:约2小时)
**优先级:** P2
**依赖:** office-hours创始人发现引擎先发布

## 设计审查

### /plan-design-review + /qa-design-review + /design-consultation —— 已发布

作为v0.5.0在main上发布。包括 `/plan-design-review`(仅报告设计审计)、`/qa-design-review`(审计 + 修复循环)和 `/design-consultation`(交互式DESIGN.md创建)。`{{DESIGN_METHODOLOGY}}`解析器提供共享80项设计审计清单。

## 文档发布

### 从/ship自动调用/document-release —— 已发布

在v0.8.3中发布。向 `/ship` 添加步骤8.5 —— 创建PR后,`/ship` 自动读取 `document-release/SKILL.md` 并执行文档更新工作流。零摩擦文档更新。

### `{{DOC_VOICE}}`共享解析器

**什么:** 在gen-skill-docs.ts中创建占位符解析器,编码gstack voice指南(友好、以用户为中心、以好处为先)。注入到/ship步骤5、/document-release步骤5,并从CLAUDE.md引用。

**为什么:** DRY —— voice规则当前生活在3个地方的内联(CLAUDE.md CHANGELOG风格部分、/ship步骤5、/document-release步骤5)。当voice发展时,所有三个都会漂移。

**背景:** 与 `{{QA_METHODOLOGY}}` 相同的模式 —— 共享块注入多个模板以防止漂移。gen-skill-docs.ts中约20行。

**工作量:** S
**优先级:** P2
**依赖:** 无

## Ship置信度仪表板

### 智能审查相关性检测 —— 部分发布

~~**什么:** 根据分支更改自动检测4个审查中哪些相关(如果无CSS/视图更改则跳过设计审查,如果仅计划则跳过代码审查)。~~

`bin/gstack-diff-scope` 已发布 —— 将diff分类为SCOPE_FRONTEND、SCOPE_BACKEND、SCOPE_PROMPTS、SCOPE_TESTS、SCOPE_DOCS、SCOPE_CONFIG。design-review-lite使用它来跳过当无前端文件更改时。仪表板集成用于条件行显示是后续跟进。

**剩余:** 仪表板条件行显示(当SCOPE_FRONTEND=false时隐藏"设计审查:尚未运行")。扩展到工程审查(仅配置时跳过文档)和CEO审查(仅配置时跳过)。

**工作量:** S
**优先级:** P3
**依赖:** gstack-diff-scope(已发布)

### /merge技能 —— 审查门控PR合并

**什么:** 创建 `/merge` 技能,合并已批准的PR,但首先检查审查准备仪表板,如果未进行代码审查则运行 `/review`(优先修复)。将"ship"(创建PR)与"merge"(landing it)分开。

**为什么:** 当前 `/review` 在 `/ship` 步骤3.5中运行,但不作为门跟踪。`/merge` 技能确保代码审查总是在landing之前发生,并支持其他人先审查PR的工作流。

**背景:** `/ship` 创建PR。`/merge` 将:检查仪表板 → 如果需要则运行 `/review` → `gh pr merge`。这是代码审查跟踪应该属于的地方 —— 在merge时,而不是计划时。

**工作量:** M
**优先级:** P2
**依赖:** Ship置信度仪表板(已发布)

## 完整性

### 完整性指标仪表板

**什么:** 跟踪Claude在gstack会话中选择完整选项vs快捷方式的频率。聚合到显示完整性趋势随时间的仪表板。

**为什么:** 没有测量,我们无法知道完整性原则是否有效。可能发现模式(例如,某些技能仍然偏向快捷方式)。

**背景:** 需要日志记录选择(例如,当AskUserQuestion解决时追加到JSONL文件)、解析它们,并显示趋势。类似于eval持久化的模式。

**工作量:** M(人工) / S(CC)
**优先级:** P3
**依赖:** 煮沸湖发布(v0.6.1)

## 安全与可观测性

### 按需Hook技能(/careful、/freeze、/guard) —— 已发布

~~**什么:** 三个新技能,使用Claude Code的会话范围PreToolUse hooks来按需添加安全护栏。~~

在v0.6.5中作为 `/careful`、`/freeze`、`/guard` 和 `/unfreeze` 发布。包括hook触发率遥测(仅模式名称,无命令内容)和内联技能激活遥测。

### 技能使用遥测 —— 已发布

~~**什么:** 跟踪调用了哪些技能、多频繁、从哪个仓库。~~

在v0.6.5中发布。gen-skill-docs.ts中的TemplateContext将技能名称烘焙到前导码遥测线中。分析CLI(`bun run analytics`)用于查询。/retro集成显示本周使用的技能。

### /investigate scoped调试增强(在遥测上 gated)

**什么:** 对/investigate auto-freeze的六个增强,取决于遥测显示freeze hook在实际调试会话中是否真正触发。

**为什么:** /investigate v0.7.1 auto-freezes编辑到被调试的模块。如果遥测显示hook经常触发,这些增强使体验更智能。如果它从不触发,问题就不是真实的,这些就不值得构建。

**背景:** 所有项目都是对 `investigate/SKILL.md.tmpl` 的散文添加。没有新脚本。

**项目:**
1. 堆栈跟踪自动检测freeze目录(解析最深应用帧)
2. Freeze边界扩大(到达边界时请求扩大而不是硬块)
3. 修复后自动unfreeze + 完整测试套件运行
4. 调试仪器清理(用DEBUG-TEMP标记,提交前移除)
5. 调试会话持久化(~/.gstack/investigate-sessions/ —— 保存调查以重用)
6. 调试报告中的调查时间线(带时间戳的假设日志)

**工作量:** M(全部6个组合)
**优先级:** P3
**依赖:** 遥测数据显示freeze hook在实际/investigate会话中触发

## 已完成

### 阶段1:基础(v0.2.0)
- 重命名为gstack
- 重构为monorepo布局
- 技能symlinks的设置脚本
- 带ref的快照命令基于元素选择
- 快照测试
**完成:** v0.2.0

### 阶段2:增强浏览器(v0.2.0)
- 带注释截图、快照diff、对话框处理、文件上传
- 光标交互式元素、元素状态检查
- CircularBuffer、async缓冲区刷新、健康检查
- Playwright错误包装、useragent修复
- 148个集成测试
**完成:** v0.2.0

### 阶段3:QA测试代理(v0.3.0)
- 带6阶段工作流、3种模式(完整/快速/回归)的/qa SKILL.md
- 问题分类、严重性分类、探索清单
- 报告模板、健康评分规则、框架检测
- wait/console/cookie-import命令、find-browse二进制文件
**完成:** v0.3.0

### 阶段3.5:浏览器Cookie导入(v0.3.x)
- cookie-import-browser命令(Chromium cookie DB解密)
- Cookie选择器Web UI、/setup-browser-cookies技能
- 18个单元测试、浏览器注册表(Comet、Chrome、Arc、Brave、Edge)
**完成:** v0.3.1

### E2E测试成本跟踪
- 跟踪累积API支出,如果超过阈值则警告
**完成:** v0.3.6

### 自动升级模式 + 智能更新检查
- 配置CLI(`bin/gstack-config`)、通过 `~/.gstack/config.yaml` 自动升级、12h缓存TTL、指数snooze退避(24h→48h→1周)、"不要再问"选项、升级时同步vendored副本
**完成:** v0.3.8
