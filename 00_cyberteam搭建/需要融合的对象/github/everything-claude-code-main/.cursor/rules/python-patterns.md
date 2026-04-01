# Python 模式

> 此文件使用 Python 特定内容扩展了常见模式规则。

## 协议（鸭子打字）```python
from typing import Protocol

class Repository(Protocol):
    def find_by_id(self, id: str) -> dict | None: ...
    def save(self, entity: dict) -> dict: ...
```## 作为 DTO 的数据类```python
from dataclasses import dataclass

@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: int | None = None
```## 上下文管理器和生成器

- 使用上下文管理器（`with`语句）进行资源管理
- 使用生成器进行惰性求值和内存高效迭代

## 参考

请参阅技能：`python-patterns` 了解全面的模式，包括装饰器、并发和包组织。