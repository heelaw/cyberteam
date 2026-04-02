# Python 编码风格

> 此文件使用 Python 特定内容扩展了通用编码风格规则。

## 标准

- 遵循 **PEP 8** 约定
- 在所有函数签名上使用**类型注释**

## 不变性

更喜欢不可变的数据结构：```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    name: str
    email: str

from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float
```## 格式化

- **黑色**用于代码格式化
- **isort** 用于进口分拣
- **褶边**用于掉毛

## 参考

请参阅技能：“python-patterns”，了解全面的 Python 习惯用法和模式。