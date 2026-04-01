# Bun 运行时

Bun 是一个快速的一体化 JavaScript 运行时和工具包：运行时、包管理器、捆绑器和测试运行器。

## 何时使用

- **首选 Bun** 用于：新的 JS/TS 项目、安装/运行速度很重要的脚本、使用 Bun 运行时的 Vercel 部署，以及当您需要单个工具链（运行 + 安装 + 测试 + 构建）时。
- **首选 Node** 用于：最大的生态系统兼容性、采用 Node 的遗留工具，或者当依赖项存在已知的 Bun 问题时。

使用时机：采用 Bun、从 Node 迁移、编写或调试 Bun 脚本/测试、或在 Vercel 或其他平台上配置 Bun。

## 它是如何工作的

- **运行时**：嵌入式节点兼容运行时（基于 JavaScriptCore 构建，在 Zig 中实现）。
- **包管理器**：`bun install` 明显比 npm/yarn 快。当前Bun中的Lockfile默认为“bun.lock”（文本）；旧版本使用“bun.lockb”（二进制）。
- **捆绑器**：适用于应用程序和库的内置捆绑器和转译器。
- **测试运行器**：内置 `bun test` 和类似 Jest 的 API。

**从 Node 迁移**：将 `node script.js` 替换为 `bun run script.js` 或 `bun script.js`。运行“bun install”代替“npm install”；大多数软件包都可以工作。对 npm 脚本使用 `bun run`； `bun x` 用于 npx 式的一次性运行。支持节点内置；更喜欢 Bun API，因为它们存在以获得更好的性能。

**Vercel**：在项目设置中将运行时设置为 Bun。构建：“bun run build”或“bun build ./src/index.ts --outdir=dist”。安装：`bun install --frozen-lockfile` 用于可重复部署。

## 示例

### 运行并安装```bash
# Install dependencies (creates/updates bun.lock or bun.lockb)
bun install

# Run a script or file
bun run dev
bun run src/index.ts
bun src/index.ts
```### 脚本和环境```bash
bun run --env-file=.env dev
FOO=bar bun run script.ts
```### 测试```bash
bun test
bun test --watch
``````typescript
// test/example.test.ts
import { expect, test } from "bun:test";

test("add", () => {
  expect(1 + 2).toBe(3);
});
```### 运行时 API```typescript
const file = Bun.file("package.json");
const json = await file.json();

Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello");
  },
});
```## 最佳实践

- 提交锁定文件（`bun.lock` 或 `bun.lockb`）以进行可重复安装。
- 更喜欢“bun run”脚本。对于 TypeScript，Bun 原生运行“.ts”。
- 使依赖项保持最新； Bun 和生态系统发展迅速。