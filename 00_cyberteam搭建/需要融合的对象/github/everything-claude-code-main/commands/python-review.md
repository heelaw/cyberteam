# Python 代码审查

此命令调用 **python-reviewer** 代理来进行全面的 Python 特定代码审查。

## 该命令的作用

1. **识别Python更改**：通过`git diff`查找修改的`.py`文件
2. **运行静态分析**：执行 `ruff`, `mypy`, `pylint`, `black --check`
3. **安全扫描**：检查SQL注入、命令注入、不安全反序列化
4. **类型安全审查**：分析类型提示和 mypy 错误
5. **Pythonic Code Check**：验证代码遵循 PEP 8 和 Python 最佳实践
6. **生成报告**：按严重程度对问题进行分类

## 何时使用

在以下情况下使用“/python-review”：
- 编写或修改Python代码后
- 在提交 Python 更改之前
- 使用 Python 代码审查拉取请求
- 加入新的 Python 代码库
- 学习Pythonic模式和习语

## 评论类别

### 严重（必须修复）
- SQL/命令注入漏洞
- 不安全的 eval/exec 使用
- Pickle 不安全的反序列化
- 硬编码凭证
- YAML 不安全加载
- 裸露的 except 子句隐藏错误

### 高（应该修复）
- 缺少公共函数的类型提示
- 可变的默认参数
- 默默地吞掉异常
- 不使用资源上下文管理器
- C 风格的循环而不是推导式
- 使用 type() 代替 isinstance()
- 无锁的竞争条件

### 中（考虑）
- PEP 8 格式违规
- 缺少公共函数的文档字符串
- 打印语句而不是记录
- 低效的字符串操作
- 没有命名常量的幻数
- 不使用 f 字符串进行格式化
- 创建不必要的列表

## 自动检查运行```bash
# Type checking
mypy .

# Linting and formatting
ruff check .
black --check .
isort --check-only .

# Security scanning
bandit -r .

# Dependency audit
pip-audit
safety check

# Testing
pytest --cov=app --cov-report=term-missing
```## 用法示例```text
User: /python-review

Agent:
# Python Code Review Report

## Files Reviewed
- app/routes/user.py (modified)
- app/services/auth.py (modified)

## Static Analysis Results
✓ ruff: No issues
✓ mypy: No errors
⚠️ black: 2 files need reformatting
✓ bandit: No security issues

## Issues Found

[CRITICAL] SQL Injection vulnerability
File: app/routes/user.py:42
Issue: User input directly interpolated into SQL query
```蟒蛇
query = f"SELECT * FROM users WHERE id = {user_id}" # 不好```
Fix: Use parameterized query
```蟒蛇
query = "SELECT * FROM users WHERE id = %s" # 好
光标.执行（查询，（user_id，））```

[HIGH] Mutable default argument
File: app/services/auth.py:18
Issue: Mutable default argument causes shared state
```蟒蛇
def process_items(items=[]): # 不好
    items.append("新")
    退货```
Fix: Use None as default
```蟒蛇
def process_items(items=None): # 好
    如果项目为无：
        项目=[]
    items.append("新")
    退货```

[MEDIUM] Missing type hints
File: app/services/auth.py:25
Issue: Public function without type annotations
```蟒蛇
def get_user(user_id): # 不好
    返回 db.find(user_id)```
Fix: Add type hints
```蟒蛇
def get_user(user_id: str) -> 可选[用户]: # 好
    返回 db.find(user_id)```

[MEDIUM] Not using context manager
File: app/routes/user.py:55
Issue: File not closed on exception
```蟒蛇
f = open("config.json") # 不好
数据 = f.read()
f.close()```
Fix: Use context manager
```蟒蛇
with open("config.json") as f: # 好
    数据 = f.read()```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 2

Recommendation: ❌ Block merge until CRITICAL issue is fixed

## Formatting Required
Run: `black app/routes/user.py app/services/auth.py`
```## 批准标准

|状态 |状况 |
|--------|------------|
| ✅ 批准 |没有严重或严重问题 |
| ⚠️警告|仅中等问题（谨慎合并）|
| ❌ 块 |发现严重或严重问题 |

## 与其他命令集成

- 首先使用 `/tdd` 确保测试通过
- 使用“/code-review”解决非 Python 特定问题
- 在提交之前使用`/python-review`
- 如果静态分析工具失败，请使用“/build-fix”

## 特定于框架的评论

### Django 项目
审稿人检查：
- N+1查询问题（使用`select_lated`和`prefetch_lated`）
- 缺少模型更改的迁移
- ORM 可以工作时的原始 SQL 使用
- 缺少用于多步骤操作的“transaction.atomic()”

### FastAPI 项目
审稿人检查：
- CORS配置错误
- 用于请求验证的 Pydantic 模型
- 响应模型的正确性
- 正确的异步/等待使用
- 依赖注入模式

### 烧瓶项目
审稿人检查：
- 上下文管理（应用程序上下文、请求上下文）
- 正确的错误处理
- 蓝图组织
- 配置管理

## 相关

- 代理：`agents/python-reviewer.md`
- 技能：`技能/python-patterns/`、`技能/python-testing/`

## 常见修复

### 添加类型提示```python
# Before
def calculate(x, y):
    return x + y

# After
from typing import Union

def calculate(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
    return x + y
```### 使用上下文管理器```python
# Before
f = open("file.txt")
data = f.read()
f.close()

# After
with open("file.txt") as f:
    data = f.read()
```### 使用列表推导式```python
# Before
result = []
for item in items:
    if item.active:
        result.append(item.name)

# After
result = [item.name for item in items if item.active]
```### 修复可变默认值```python
# Before
def append(value, items=[]):
    items.append(value)
    return items

# After
def append(value, items=None):
    if items is None:
        items = []
    items.append(value)
    return items
```### 使用 f 字符串 (Python 3.6+)```python
# Before
name = "Alice"
greeting = "Hello, " + name + "!"
greeting2 = "Hello, {}".format(name)

# After
greeting = f"Hello, {name}!"
```### 修复循环中的字符串连接```python
# Before
result = ""
for item in items:
    result += str(item)

# After
result = "".join(str(item) for item in items)
```## Python 版本兼容性

当代码使用较新 Python 版本的功能时，审阅者会注意到：

|特色 |最低Python |
|---------|----------------|
|类型提示 | 3.5+ |
| f 弦 | 3.6+ |
|海象运算符 (`:=`) | 3.8+ |
|仅位置参数 | 3.8+ |
|匹配语句 | 3.10+ |
|类型联合 (&#96;x &#124; None&#96;) | 3.10+ |

确保项目的“pyproject.toml”或“setup.py”指定正确的最低 Python 版本。