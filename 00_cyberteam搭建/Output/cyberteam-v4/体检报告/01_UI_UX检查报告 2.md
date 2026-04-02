# CyberTeam-v4 UI/UX 检查报告

**检查日期**: 2026-03-28
**检查范围**: webui/、frontend/、projects/*/05_Playground/、cyberteam/board/
**版本**: CyberTeam-v4

---

## 执行摘要

| 维度 | 评分 | 问题数 | 严重 | 中等 | 轻微 |
|------|------|--------|------|------|------|
| 代码质量 | 6/10 | 18 | 4 | 8 | 6 |
| 响应式设计 | 5/10 | 12 | 3 | 5 | 4 |
| 颜色一致性 | 4/10 | 8 | 2 | 4 | 2 |
| 可访问性 | 3/10 | 15 | 5 | 7 | 3 |
| 性能 | 6/10 | 10 | 2 | 4 | 4 |
| 安全性 | 4/10 | 6 | 2 | 2 | 2 |
| **综合评分** | **4.7/10** | **69** | **18** | **30** | **21** |

---

## 一、严重问题（必须修复）

### 1.1 [严重] XSS 安全漏洞
**文件**: `projects/*/05_Playground/活动看板_*.html`
**位置**: `showDoc()` 函数 (约第480行)

```javascript
function showDoc(id) {
    const d = docs[id];
    document.getElementById('modalBody').innerHTML = `
        <p>${d.summary}</p>  // XSS漏洞！
    `;
}
```

**问题**: 直接将 `d.summary` 和 `d.key` 插入 innerHTML，未做转义。如果文档内容包含 `<script>` 标签或事件处理器（如 `<img onerror=...>`），将被执行。

**修复建议**:
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('modalBody').innerHTML = `
    <p>${escapeHtml(d.summary)}</p>
    <div>${escapeHtml(d.key)}</div>
`;
```

### 1.2 [严重] 硬编码 API URL 无容错
**文件**: `frontend/index.html`, `frontend/todo-app/js/app.js`, `webui/src/pages/*.tsx`
**问题**: API URL 硬编码为 `http://localhost:8080` 或 `http://localhost:8000`，服务不可用时 UI 直接崩溃。

**当前代码**:
```javascript
const API_BASE = 'http://localhost:8080';
// 失败时只显示 "?"
document.getElementById('totalTasks').textContent = '?';
```

**修复建议**:
1. 添加连接状态检测
2. 显示友好的离线提示
3. 实现请求超时（5秒）
4. 使用 `navigator.onLine` 检测

### 1.3 [严重] 缺少错误边界
**文件**: `webui/src/*.tsx`
**问题**: React 应用无错误边界，任何组件崩溃都会导致白屏。

**修复建议**:
```typescript
class ErrorBoundary extends React.Component {
    state = { hasError: false };
    static getDerivedStateFromError() { return { hasError: true }; }
    render() {
        if (this.state.hasError) {
            return <div className="p-4 text-red-500">组件出错，请刷新页面</div>;
        }
        return this.props.children;
    }
}
```

### 1.4 [严重] 内存泄漏风险
**文件**: `projects/*/05_Playground/活动看板_*.html`
**问题**: 滑块 `oninput` 事件不断触发 `updateSim()`，未节流（throttle）。

**影响**: 快速拖动时导致大量重排和重绘，CPU占用高。

**修复建议**:
```javascript
function throttle(fn, delay) {
    let last = 0;
    return function(...args) {
        const now = Date.now();
        if (now - last >= delay) {
            last = now;
            fn.apply(this, args);
        }
    };
}

document.getElementById('bfPassby').oninput = throttle(updateSim, 100);
```

---

## 二、中等问题

### 2.1 [中等] 响应式布局失效
**文件**: `frontend/index.html`, `projects/*/05_Playground/*.html`
**问题**:
1. `stats-grid` 使用 `grid-template-columns: repeat(4, 1fr)`，平板和手机端无法适配
2. Playground 的 `main-content` 使用 `display: grid; grid-template-columns: 1fr 400px` 固定右面板400px，小屏溢出

**修复建议**:
```css
/* 移动端 */
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .main-content {
        grid-template-columns: 1fr !important;
    }
}
@media (max-width: 480px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
}
```

### 2.2 [中等] 颜色系统不统一
**文件**: 全局

| 位置 | 主色 | 次色 | 强调色 |
|------|------|------|--------|
| frontend/index.html | `#1a1a2e` | `#16213e` | `#00d4ff` |
| frontend/todo-app | `#4f46e5` | `#10b981` | `#f59e0b` |
| webui (Tailwind) | `slate-900` | `blue-600` | `green-600` |
| Playground | `#1a1a2e` | `#16213e` | `#e94560` |
| cyberteam/board/ | `#050505` | `rgba(20,20,20,0.6)` | `#3b82f6` |

**修复建议**: 建立统一的设计令牌（Design Tokens）

```css
:root {
    --color-bg-primary: #0f172a;
    --color-bg-secondary: #1e293b;
    --color-accent: #3b82f6;
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-danger: #ef4444;
    --color-text-primary: #f1f5f9;
    --color-text-secondary: #94a3b8;
}
```

### 2.3 [中等] 可访问性缺失
**问题清单**:
1. 无 ARIA landmarks（main, nav, aside）
2. 无 skip link（跳转主要内容）
3. 对话框无 `role="dialog"` 和 `aria-modal`
4. 表单无关联 `<label>`（`frontend/todo-app` 有，其他缺失）
5. 图标按钮无 `aria-label`
6. 颜色对比度不足（部分灰色文字在深色背景上WCAG AA失败）

**修复建议**:
```html
<!-- 对话框 -->
<div role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <h2 id="modalTitle">文档标题</h2>
</div>

<!-- skip link -->
<a href="#main-content" class="sr-only focus:not-sr-only">跳到主要内容</a>

<!-- 图标按钮 -->
<button aria-label="关闭对话框">×</button>
```

### 2.4 [中等] Tailwind 与原生 CSS 混用
**文件**: `webui/src/` (React + Tailwind) vs `frontend/` (原生HTML + CSS)

**问题**: 项目中存在两套样式系统，增加维护成本。

**建议**: 统一使用 Tailwind CSS 或建立清晰的分层。

### 2.5 [中等] API 请求无清理机制
**文件**: `webui/src/pages/*.tsx`
**问题**: `useEffect` 中的 fetch 未实现 abort，组件卸载后可能更新已卸载状态。

```typescript
useEffect(() => {
    fetch(`${API}/data`).then(setData); // 无 cleanup
}, []);
```

**修复建议**:
```typescript
useEffect(() => {
    const controller = new AbortController();
    fetch(`${API}/data`, { signal: controller.signal })
        .then(res => res.json())
        .then(setData)
        .catch(err => { if (err.name !== 'AbortError') console.error(err); });
    return () => controller.abort();
}, []);
```

### 2.6 [中等] 表单验证缺失
**文件**: `frontend/index.html` (任务输入框)
**问题**: 任务输入框无长度限制、无必填校验，提交空任务后端会返回错误但前端无反馈。

**修复建议**:
```html
<input type="text" class="task-input" id="taskInput"
    placeholder="输入任务描述... (例如: 帮我分析用户增长策略)"
    required minlength="5" maxlength="500"
    oninvalid="this.setCustomValidity('请输入至少5个字符的任务描述')">
<button class="btn" onclick="createTask()">提交任务</button>
```

### 2.7 [中等] 缺少加载状态
**文件**: `frontend/index.html`
**问题**: 按钮点击后无 loading 状态，用户可能重复提交。

**修复建议**:
```javascript
async function createTask() {
    const btn = document.querySelector('.btn');
    btn.disabled = true;
    btn.textContent = '提交中...';
    try {
        await fetch(...);
    } finally {
        btn.disabled = false;
        btn.textContent = '提交任务';
    }
}
```

### 2.8 [中等] localStorage 无容错
**文件**: `frontend/todo-app/js/app.js`
**问题**: 隐私模式或存储满时 localStorage 会抛异常。

```javascript
getLocalTodos() {
    const stored = localStorage.getItem('todos'); // 可能抛异常
    return stored ? JSON.parse(stored) : [];
}
```

**修复建议**:
```javascript
getLocalTodos() {
    try {
        const stored = localStorage.getItem('todos');
        return stored ? JSON.parse(stored) : [];
    } catch (e) {
        console.warn('localStorage 不可用:', e);
        return [];
    }
}
```

---

## 三、轻微问题

### 3.1 [轻微] 无 Favicon
**文件**: `webui/index.html`, `frontend/index.html`
**问题**: 所有 HTML 均无 `<link rel="icon">`

### 3.2 [轻微] 字体回退不完整
**文件**: `frontend/index.html`, `frontend/todo-app/css/style.css`
**问题**: `font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` 缺少中文字体回退。

**修复**: 添加 `'PingFang SC', 'Microsoft YaHei', sans-serif`

### 3.3 [轻微] 触摸目标过小
**文件**: Playground HTML
**问题**: `.tab` 元素 `padding: 10px 16px` 可能在移动端不够大（建议 ≥44px）。

### 3.4 [轻微] CSS 未压缩
**文件**: `frontend/todo-app/css/style.css`
**问题**: 生产环境 CSS 应压缩。

### 3.5 [轻微] Modal 定位问题
**文件**: Playground HTML
**问题**: `.modal-close` 使用 `position: absolute` 但父元素 `.modal-content` 未设置 `position: relative`。

### 3.6 [轻微] 无打印样式
**文件**: Playground HTML
**问题**: 商业报告应支持打印，建议添加 `@media print` 样式表。

---

## 四、新增文件检查结果

### 4.1 cyberteam/board/index.html (ClawTeam Nexus)

| 维度 | 评分 | 问题 |
|------|------|------|
| UI设计 | 8/10 | 视觉层次清晰，Glassmorphism风格统一 |
| 代码质量 | 7/10 | JS内联，无外部依赖管理 |
| 响应式 | 5/10 | 固定280px侧边栏，小屏需滚动 |
| 可访问性 | 4/10 | 缺少ARIA标签、skip link |

**优点**:
- 动画效果流畅（orb动画、slideIn动画）
- 颜色系统相对统一（使用CSS变量）
- 状态管理清晰（pending/progress/completed/blocked）

**问题**:
- `kanban-board` 在小于1300px屏幕使用 `grid-template-columns: 1fr`，但没有移动端适配
- select 元素自定义样式在某些浏览器可能不兼容
- EventSource 连接无自动重连机制

### 4.2 frontend/team-builder.html

| 维度 | 评分 | 问题 |
|------|------|------|
| UI设计 | 7/10 | 科技感强，粒子背景效果好 |
| 代码质量 | 5/10 | CSS/JS全内联，难以维护 |
| 响应式 | 4/10 | 大量固定像素值，无媒体查询 |
| 可访问性 | 3/10 | 几乎无ARIA支持 |

**问题**:
- 文件过大（60KB+），全部内联
- CSS变量命名与行业惯例不符（如 `--glow-cyan` 应为 `--color-glow-cyan`）
- 无构建流程，修改困难

### 4.3 webui/dist/ (构建产物)

| 维度 | 评分 | 问题 |
|------|------|------|
| 文件结构 | 8/10 | 正确的构建产物分离 |
| 性能 | 8/10 | Tailwind已压缩，资源分离 |
| 可维护性 | 6/10 | 源码目录结构不完整 |

**问题**:
- `frontend/src/` 目录缺失，源码可能已丢失
- `webui/src/` 存在但结构不明确

---

## 五、文件清单

| 文件 | 严重 | 中等 | 轻微 | 主要问题 |
|------|------|------|------|----------|
| `webui/index.html` | 0 | 1 | 2 | 缺少 favicon |
| `webui/src/App.tsx` | 0 | 1 | 0 | 无错误边界 |
| `webui/src/pages/Dashboard.tsx` | 0 | 2 | 0 | API无abort、无加载骨架 |
| `frontend/index.html` | 1 | 3 | 2 | API无容错、表单无验证 |
| `frontend/todo-app/index.html` | 0 | 2 | 1 | 缺少 aria-label |
| `frontend/todo-app/css/style.css` | 0 | 1 | 2 | 字体回退、无打印样式 |
| `frontend/todo-app/js/app.js` | 0 | 3 | 1 | localStorage无容错、无throttle |
| `cyberteam/board/index.html` | 0 | 2 | 2 | 响应式不足、无自动重连 |
| `frontend/team-builder.html` | 0 | 3 | 3 | 内联代码过多、响应式缺失 |
| `projects/*/05_Playground/*.html` | 3 | 4 | 2 | XSS、内存泄漏、响应式失效 |

---

## 六、修复优先级

### P0 - 立即修复（安全/崩溃）
1. XSS 漏洞修复
2. API 无容错导致的白屏
3. 错误边界缺失

### P1 - 本周修复
4. 响应式布局适配
5. 可访问性基本达标（ARIA）
6. 内存泄漏（throttle）
7. API 请求 abort

### P2 - 下周修复
8. 统一设计令牌
9. 表单验证
10. 加载状态优化
11. localStorage 容错

### P3 - 长期优化
12. Tailwind/CSS 统一
13. 打印样式
14. 性能优化（code splitting）
15. 单元测试覆盖率

---

## 七、测试建议

1. **功能测试**: 在 API 服务关闭状态下打开前端，验证错误提示
2. **响应式测试**: 使用 Chrome DevTools 测试 320px-1920px 断点
3. **安全测试**: 在文档摘要中注入 `<script>alert(1)</script>` 验证转义
4. **性能测试**: Lighthouse 评分应达到 80+
5. **可访问性测试**: 使用 axe-core 扫描，应达到 WCAG AA

---

## 八、总结

CyberTeam-v4 的前端UI整体具有科技感和视觉冲击力，特别是 ClawTeam Nexus 的Glassmorphism设计和动画效果较为出色。但存在以下核心问题：

1. **架构问题**: 多处源码目录不完整，frontend/src/ 缺失
2. **安全问题**: Playground HTML存在XSS漏洞
3. **一致性问题**: 颜色系统、样式方案不统一
4. **可访问性问题**: 缺少ARIA、无skip link、对比度不足
5. **响应式问题**: 多个页面缺少移动端适配

建议优先修复P0级别问题，然后逐步完善P1-P3的优化项。

---

**检查人**: UI/UX 审查专家 Agent
**下次检查**: 修复 P0/P1 问题后一周内
