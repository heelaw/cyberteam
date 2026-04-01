# 重构 Clean 命令

分析并清理代码库：$ARGUMENTS

## 你的任务

1. **使用分析工具检测死代码**
2. **识别重复**和整合机会
3. **通过文档安全删除**未使用的代码
4. **验证**没有功能损坏

## 检测阶段

### 运行分析工具```bash
# Find unused exports
npx knip

# Find unused dependencies
npx depcheck

# Find unused TypeScript exports
npx ts-prune
```### 手动检查

- 未使用的函数（无调用者）
- 未使用的变量
- 未使用的进口
- 注释掉的代码
- 无法访问的代码
- 未使用的 CSS 类

## 移除阶段

### 删除之前

1. **搜索用法** - grep，查找引用
2. **检查导出** - 可能在外部使用
3. **验证测试** - 没有测试依赖于它
4. **文档删除** - git提交消息

### 安全驱逐令

1.首先删除未使用的导入
2.删除未使用的私有函数
3.删除未使用的导出函数
4. 删除未使用的类型/接口
5.删除未使用的文件

## 巩固阶段

### 识别重复项

- 类似的功能，但有细微的差别
- 复制粘贴代码块
- 重复图案

### 整合策略

1. **提取效用函数** - 用于重复逻辑
2. **创建基类** - 类似的类
3. **使用高阶函数** - 对于重复模式
4. **创建共享常量** - 用于魔法值

## 验证

清理后：

1. `npm run build` - 构建成功
2. `npm test` - 所有测试都通过
3. `npm run lint` - 没有新的 lint 错误
4. 手动冒烟测试 - 功能正常

## 报告格式```
Dead Code Analysis
==================

Removed:
- file.ts: functionName (unused export)
- utils.ts: helperFunction (no callers)

Consolidated:
- formatDate() and formatDateTime() → dateUtils.format()

Remaining (manual review needed):
- oldComponent.tsx: potentially unused, verify with team
```---

**注意**：拆卸前务必进行验证。如有疑问，请询问或添加“// TODO：验证用法”注释。