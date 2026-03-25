# Python 安全性

> 此文件使用 Python 特定内容扩展了通用安全规则。

## 秘密管理```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]  # Raises KeyError if missing
```## 安全扫描

- 使用 **bandit** 进行静态安全分析：```bash
  bandit -r src/
  ```## 参考

请参阅技能：“django-security”，了解 Django 特定的安全指南（如果适用）。