# 迭代检索模式

解决多代理工作流程中的“上下文问题”，子代理在开始工作之前不知道他们需要什么上下文。

## 何时激活

- 产生需要代码库上下文的子代理，它们无法预先预测
- 构建多代理工作流程，其中上下文逐渐细化
- 在代理任务中遇到“上下文太大”或“缺少上下文”失败
- 设计类似 RAG 的检索管道以进行代码探索
- 优化代理编排中的令牌使用

## 问题

子代理是在有限的上下文中产生的。他们不知道：
- 哪些文件包含相关代码
- 代码库中存在哪些模式
- 项目使用什么术语

标准方法失败：
- **发送所有内容**：超出上下文限制
- **不发送任何内容**：代理缺少关键信息
- **猜猜需要什么**：经常错误

## 解决方案：迭代检索

逐步完善上下文的 4 阶段循环：```
┌─────────────────────────────────────────────┐
│                                             │
│   ┌──────────┐      ┌──────────┐            │
│   │ DISPATCH │─────▶│ EVALUATE │            │
│   └──────────┘      └──────────┘            │
│        ▲                  │                 │
│        │                  ▼                 │
│   ┌──────────┐      ┌──────────┐            │
│   │   LOOP   │◀─────│  REFINE  │            │
│   └──────────┘      └──────────┘            │
│                                             │
│        Max 3 cycles, then proceed           │
└─────────────────────────────────────────────┘
```### 第 1 阶段：调度

收集候选文件的初始广泛查询：```javascript
// Start with high-level intent
const initialQuery = {
  patterns: ['src/**/*.ts', 'lib/**/*.ts'],
  keywords: ['authentication', 'user', 'session'],
  excludes: ['*.test.ts', '*.spec.ts']
};

// Dispatch to retrieval agent
const candidates = await retrieveFiles(initialQuery);
```### 第 2 阶段：评估

评估检索到的内容的相关性：```javascript
function evaluateRelevance(files, task) {
  return files.map(file => ({
    path: file.path,
    relevance: scoreRelevance(file.content, task),
    reason: explainRelevance(file.content, task),
    missingContext: identifyGaps(file.content, task)
  }));
}
```评分标准：
- **高 (0.8-1.0)**：直接实现目标功能
- **中 (0.5-0.7)**：包含相关模式或类型
- **低 (0.2-0.4)**：切向相关
- **无 (0-0.2)**：不相关，排除

### 第三阶段：完善

根据评估更新搜索条件：```javascript
function refineQuery(evaluation, previousQuery) {
  return {
    // Add new patterns discovered in high-relevance files
    patterns: [...previousQuery.patterns, ...extractPatterns(evaluation)],

    // Add terminology found in codebase
    keywords: [...previousQuery.keywords, ...extractKeywords(evaluation)],

    // Exclude confirmed irrelevant paths
    excludes: [...previousQuery.excludes, ...evaluation
      .filter(e => e.relevance < 0.2)
      .map(e => e.path)
    ],

    // Target specific gaps
    focusAreas: evaluation
      .flatMap(e => e.missingContext)
      .filter(unique)
  };
}
```### 第 4 阶段：循环

使用细化标准重复（最多 3 个周期）：```javascript
async function iterativeRetrieve(task, maxCycles = 3) {
  let query = createInitialQuery(task);
  let bestContext = [];

  for (let cycle = 0; cycle < maxCycles; cycle++) {
    const candidates = await retrieveFiles(query);
    const evaluation = evaluateRelevance(candidates, task);

    // Check if we have sufficient context
    const highRelevance = evaluation.filter(e => e.relevance >= 0.7);
    if (highRelevance.length >= 3 && !hasCriticalGaps(evaluation)) {
      return highRelevance;
    }

    // Refine and continue
    query = refineQuery(evaluation, query);
    bestContext = mergeContext(bestContext, highRelevance);
  }

  return bestContext;
}
```## 实际例子

### 示例 1：错误修复上下文```
Task: "Fix the authentication token expiry bug"

Cycle 1:
  DISPATCH: Search for "token", "auth", "expiry" in src/**
  EVALUATE: Found auth.ts (0.9), tokens.ts (0.8), user.ts (0.3)
  REFINE: Add "refresh", "jwt" keywords; exclude user.ts

Cycle 2:
  DISPATCH: Search refined terms
  EVALUATE: Found session-manager.ts (0.95), jwt-utils.ts (0.85)
  REFINE: Sufficient context (2 high-relevance files)

Result: auth.ts, tokens.ts, session-manager.ts, jwt-utils.ts
```### 示例 2：功能实现```
Task: "Add rate limiting to API endpoints"

Cycle 1:
  DISPATCH: Search "rate", "limit", "api" in routes/**
  EVALUATE: No matches - codebase uses "throttle" terminology
  REFINE: Add "throttle", "middleware" keywords

Cycle 2:
  DISPATCH: Search refined terms
  EVALUATE: Found throttle.ts (0.9), middleware/index.ts (0.7)
  REFINE: Need router patterns

Cycle 3:
  DISPATCH: Search "router", "express" patterns
  EVALUATE: Found router-setup.ts (0.8)
  REFINE: Sufficient context

Result: throttle.ts, middleware/index.ts, router-setup.ts
```## 与代理集成

在代理提示中使用：```markdown
When retrieving context for this task:
1. Start with broad keyword search
2. Evaluate each file's relevance (0-1 scale)
3. Identify what context is still missing
4. Refine search criteria and repeat (max 3 cycles)
5. Return files with relevance >= 0.7
```## 最佳实践

1. **从广泛开始，逐渐缩小** - 不要过度指定初始查询
2. **学习代码库术语** - 第一个周期通常会揭示命名约定
3. **跟踪缺失的内容** - 明确的差距识别推动改进
4. **止于“足够好”** - 3 个高相关性文件胜过 10 个平庸文件
5. **自信地排除** - 低相关性文件不会变得相关

## 相关

- [长格式指南](https://x.com/affaanmustafa/status/2014040193557471352) - 子代理编排部分
- “持续学习”技能 - 随着时间的推移而改进的模式
- 与 ECC 捆绑在一起的代理定义（手动安装路径：`agents/`）