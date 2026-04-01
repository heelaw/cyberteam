# 优先级排序Skill - 上游依赖

## 依赖的Skills

| 上游Skill | 依赖类型 | 描述 |
|-----------|----------|------|
| 解决方案生成 | 强依赖 | 需要解决方案列表作为输入 |
| 根因挖掘 | 弱依赖 | 问题诊断结果作为参考 |
| 瓶颈分析 | 弱依赖 | 瓶颈识别结果作为参考 |

## 数据依赖

| 数据源 | 类型 | 描述 |
|--------|------|------|
| 解决方案列表 | Array | 待排序的解决方案 |
| 问题分析报告 | Object | 问题的根因和瓶颈信息 |
| 资源约束 | Object | 可用资源限制 |

## 依赖配置

```yaml
upstream_dependencies:
  required:
    - skill: solution-generation
      input: solutions
      output: solution_list
  optional:
    - skill: root-cause-analysis
      input: problem_diagnosis
      output: cause_report
    - skill: bottleneck-analysis
      input: process_data
      output: bottleneck_report
```
