# 瓶颈分析Skill - 接口协议

## 输入接口

| 接口名称 | 类型 | 描述 | 必需 |
|----------|------|------|------|
| business_process | Object | 业务流程描述 | 是 |
| performance_data | Object | 性能数据 | 是 |

## 输出接口

| 接口名称 | 类型 | 描述 |
|----------|------|------|
| bottleneck_report | Object | 瓶颈分析报告 |
| optimization_suggestions | Array | 优化建议 |
