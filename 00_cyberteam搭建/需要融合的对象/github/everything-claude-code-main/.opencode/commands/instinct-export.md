# 本能导出命令

导出与他人分享的本能：$ARGUMENTS

## 你的任务

从 Continuous-learning-v2 系统中导出本能。

## 导出选项

### 全部导出```
/instinct-export
```### 仅导出高置信度```
/instinct-export --min-confidence 0.8
```### 按类别导出```
/instinct-export --category coding
```### 导出到特定路径```
/instinct-export --output ./my-instincts.json
```## 导出格式```json
{
  "instincts": [
    {
      "id": "instinct-123",
      "trigger": "[situation description]",
      "action": "[recommended action]",
      "confidence": 0.85,
      "category": "coding",
      "applications": 10,
      "successes": 9,
      "source": "session-observation"
    }
  ],
  "metadata": {
    "version": "1.0",
    "exported": "2025-01-15T10:00:00Z",
    "author": "username",
    "total": 25,
    "filter": "confidence >= 0.8"
  }
}
```## 导出报告```
Export Summary
==============
Output: ./instincts-export.json
Total instincts: X
Filtered: Y
Exported: Z

Categories:
- coding: N
- testing: N
- security: N
- git: N

Top Instincts (by confidence):
1. [trigger] (0.XX)
2. [trigger] (0.XX)
3. [trigger] (0.XX)
```## 分享

导出后：
- 直接分享JSON文件
- 上传到团队存储库
- 发布到本能注册表

---

**提示**：导出高置信度本能 (>0.8)，以获得更高质量的股票。