# 索引

## 读取顺序

1. 先看 `route-map.md`，确认当前问题属于哪一段 SOP。
2. 再看对应 Skill 的 `references/reference.md`，只读这一步需要的最小框架。
3. 再看 `assessments/assessment.md`，确认输出是否够用。

## 文件作用

- `route-map.md`：文案 Agent 的路由总图。
- `assessment.md`：根 Agent 的验收标准。
- `skills/*/references/reference.md`：各最小 SOP 的判断框架。
- `skills/*/assessments/assessment.md`：各 Skill 的验收标准。
- `skills/*/scripts/run.py`：脚本入口，默认由父 Agent 调用。

## 约定

- 只把必要信息往下读，不把整套材料一次性塞进上下文。
- canonical Skill 只负责一个最小 SOP 单元。
- 根文档只做路由，不做知识堆砌。
