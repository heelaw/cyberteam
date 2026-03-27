/**
 * TODO 应用 - 客户端逻辑
 * 支持本地存储和 API 集成
 */

class TodoApp {
    constructor() {
        // API 配置
        this.apiBase = 'http://localhost:8080/api';
        this.useApi = false; // 设置为 true 启用 API 模式

        // 状态管理
        this.todos = [];
        this.currentFilter = 'all';
        this.currentSort = 'created';

        // DOM 元素
        this.elements = {
            form: document.getElementById('todoForm'),
            input: document.getElementById('todoInput'),
            priority: document.getElementById('prioritySelect'),
            list: document.getElementById('todoList'),
            emptyState: document.getElementById('emptyState'),
            filterBtns: document.querySelectorAll('.filter-btn'),
            sortSelect: document.getElementById('sortSelect'),
            totalCount: document.getElementById('totalCount'),
            pendingCount: document.getElementById('pendingCount'),
            completedCount: document.getElementById('completedCount')
        };

        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.bindEvents();
        this.loadTodos();
    }

    /**
     * 绑定事件监听
     */
    bindEvents() {
        // 表单提交
        this.elements.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTodo();
        });

        // 筛选按钮
        this.elements.filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.elements.filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFilter = btn.dataset.filter;
                this.render();
            });
        });

        // 排序选择
        this.elements.sortSelect.addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.render();
        });

        // 任务列表事件委托
        this.elements.list.addEventListener('click', (e) => {
            const todoItem = e.target.closest('.todo-item');
            if (!todoItem) return;

            const id = todoItem.dataset.id;

            if (e.target.classList.contains('todo-checkbox')) {
                this.toggleTodo(id);
            } else if (e.target.classList.contains('btn-delete')) {
                this.deleteTodo(id);
            } else if (e.target.classList.contains('btn-edit')) {
                this.editTodo(id);
            }
        });
    }

    /**
     * 加载待办事项
     */
    async loadTodos() {
        if (this.useApi) {
            try {
                const response = await fetch(`${this.apiBase}/todos`);
                this.todos = await response.json();
            } catch (error) {
                console.error('加载失败，使用本地存储:', error);
                this.todos = this.getLocalTodos();
            }
        } else {
            this.todos = this.getLocalTodos();
        }

        this.render();
    }

    /**
     * 从本地存储获取
     */
    getLocalTodos() {
        const stored = localStorage.getItem('todos');
        return stored ? JSON.parse(stored) : [];
    }

    /**
     * 保存到本地存储
     */
    saveLocalTodos() {
        localStorage.setItem('todos', JSON.stringify(this.todos));
    }

    /**
     * 添加待办事项
     */
    async addTodo() {
        const text = this.elements.input.value.trim();
        const priority = this.elements.priority.value;

        if (!text) return;

        const todo = {
            id: this.generateId(),
            text,
            priority,
            completed: false,
            createdAt: new Date().toISOString()
        };

        if (this.useApi) {
            try {
                const response = await fetch(`${this.apiBase}/todos`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(todo)
                });
                const created = await response.json();
                this.todos.push(created);
            } catch (error) {
                console.error('创建失败，保存到本地:', error);
                this.todos.push(todo);
                this.saveLocalTodos();
            }
        } else {
            this.todos.push(todo);
            this.saveLocalTodos();
        }

        this.elements.input.value = '';
        this.render();
    }

    /**
     * 切换完成状态
     */
    async toggleTodo(id) {
        const todo = this.todos.find(t => t.id === id);
        if (!todo) return;

        todo.completed = !todo.completed;

        if (this.useApi) {
            try {
                await fetch(`${this.apiBase}/todos/${id}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ completed: todo.completed })
                });
            } catch (error) {
                console.error('更新失败，保存到本地:', error);
                this.saveLocalTodos();
            }
        } else {
            this.saveLocalTodos();
        }

        this.render();
    }

    /**
     * 删除待办事项
     */
    async deleteTodo(id) {
        if (!confirm('确定要删除这个待办事项吗？')) return;

        this.todos = this.todos.filter(t => t.id !== id);

        if (this.useApi) {
            try {
                await fetch(`${this.apiBase}/todos/${id}`, {
                    method: 'DELETE'
                });
            } catch (error) {
                console.error('删除失败，更新本地存储:', error);
                this.saveLocalTodos();
            }
        } else {
            this.saveLocalTodos();
        }

        this.render();
    }

    /**
     * 编辑待办事项
     */
    editTodo(id) {
        const todo = this.todos.find(t => t.id === id);
        if (!todo) return;

        const newText = prompt('编辑待办事项:', todo.text);
        if (newText === null || newText.trim() === '') return;

        todo.text = newText.trim();

        if (this.useApi) {
            fetch(`${this.apiBase}/todos/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: todo.text })
            }).catch(error => {
                console.error('更新失败，保存到本地:', error);
                this.saveLocalTodos();
            });
        } else {
            this.saveLocalTodos();
        }

        this.render();
    }

    /**
     * 渲染 UI
     */
    render() {
        // 筛选
        let filtered = this.todos;
        if (this.currentFilter === 'pending') {
            filtered = this.todos.filter(t => !t.completed);
        } else if (this.currentFilter === 'completed') {
            filtered = this.todos.filter(t => t.completed);
        }

        // 排序
        filtered = this.sortTodos(filtered);

        // 更新统计
        this.updateStats();

        // 渲染列表
        if (filtered.length === 0) {
            this.elements.list.style.display = 'none';
            this.elements.emptyState.style.display = 'block';
        } else {
            this.elements.list.style.display = 'block';
            this.elements.emptyState.style.display = 'none';
            this.elements.list.innerHTML = filtered.map(todo => this.renderTodoItem(todo)).join('');
        }
    }

    /**
     * 排序待办事项
     */
    sortTodos(todos) {
        const sorted = [...todos];

        switch (this.currentSort) {
            case 'priority':
                const priorityOrder = { high: 0, medium: 1, low: 2 };
                sorted.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
                break;
            case 'title':
                sorted.sort((a, b) => a.text.localeCompare(b.text));
                break;
            case 'created':
            default:
                sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
                break;
        }

        return sorted;
    }

    /**
     * 渲染单个待办事项
     */
    renderTodoItem(todo) {
        const priorityClass = `priority-${todo.priority}`;
        const priorityLabel = {
            high: '高',
            medium: '中',
            low: '低'
        }[todo.priority];

        const date = new Date(todo.createdAt).toLocaleDateString('zh-CN');

        return `
            <li class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo.id}">
                <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''}>
                <div class="todo-content">
                    <div class="todo-text">${this.escapeHtml(todo.text)}</div>
                    <div class="todo-meta">
                        <span class="todo-priority ${priorityClass}">${priorityLabel}优先级</span>
                        <span class="todo-date">${date}</span>
                    </div>
                </div>
                <div class="todo-actions">
                    <button class="btn-action btn-edit" title="编辑">编辑</button>
                    <button class="btn-action btn-delete" title="删除">删除</button>
                </div>
            </li>
        `;
    }

    /**
     * 更新统计数据
     */
    updateStats() {
        const total = this.todos.length;
        const completed = this.todos.filter(t => t.completed).length;
        const pending = total - completed;

        this.elements.totalCount.textContent = total;
        this.elements.pendingCount.textContent = pending;
        this.elements.completedCount.textContent = completed;
    }

    /**
     * 生成唯一 ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * HTML 转义
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new TodoApp();
});
