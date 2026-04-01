# Python 测试

> 此文件使用 Python 特定内容扩展了通用测试规则。

## 框架

使用 **pytest** 作为测试框架。

## 覆盖范围```bash
pytest --cov=src --cov-report=term-missing
```## 测试组织

使用 pytest.mark 进行测试分类：```python
import pytest

@pytest.mark.unit
def test_calculate_total():
    ...

@pytest.mark.integration
def test_database_connection():
    ...
```## 参考

有关详细的 pytest 模式和装置，请参阅技能：“python-testing”。