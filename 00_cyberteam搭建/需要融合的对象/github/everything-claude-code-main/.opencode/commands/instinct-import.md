# 本能导入命令

从文件或 URL 导入本能：$ARGUMENTS

## 你的任务

将本能导入持续学习 v2 系统中。

## 导入源

### 文件导入```
/instinct-import path/to/instincts.json
```### 网址导入```
/instinct-import https://example.com/instincts.json
```### 团队共享导入```
/instinct-import @teammate/instincts
```## 导入格式

预期的 JSON 结构：```json
{
  "instincts": [
    {
      "trigger": "[situation description]",
      "action": "[recommended action]",
      "confidence": 0.7,
      "category": "coding",
      "source": "imported"
    }
  ],
  "metadata": {
    "version": "1.0",
    "exported": "2025-01-15T10:00:00Z",
    "author": "username"
  }
}
```## 导入流程

1. **验证格式** - 检查 JSON 结构
2. **重复数据删除** - 跳过现有的本能
3. **调整信心** - 降低进口信心（×0.8）
4. **合并** - 添加到本地本能存储
5. **报告** - 显示导入摘要

## 导入报告```
Import Summary
==============
Source: [path or URL]
Total in file: X
Imported: Y
Skipped (duplicates): Z
Errors: W

Imported Instincts:
- [trigger] (confidence: 0.XX)
- [trigger] (confidence: 0.XX)
...
```## 冲突解决

导入重复项时：
- 保留更高可信度的版本
- 合并应用程序计数
- 更新时间戳

---

**提示**：导入后使用“/instinct-status”查看导入的本能。