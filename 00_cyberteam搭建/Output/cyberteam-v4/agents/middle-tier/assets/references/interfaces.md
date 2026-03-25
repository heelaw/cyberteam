# interfaces - 资产库中台

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `task` | Task | 任务描述 |
| `task_type` | enum | 任务类型（工程开发/创意设计/运营策略/安全审查/营销执行） |
| `scenarios` | string[] | 场景标签列表 |
| `urgency` | enum | 紧急程度（可选） |
| `complexity` | enum | 复杂度（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `dispatch_result` | DispatchResult | 调度结果 |
| `selected_assets` | Asset[] | 选中的资产列表 |
| `fallback_assets` | Asset[] | 备选资产列表 |
| `estimated_wait` | int | 预计等待时间（秒） |

## Asset 结构

```yaml
Asset:
  id: string              # 资产唯一ID
  name: string            # 资产名称
  type: enum              # gstack/agency/baoyu
  category: string        # 细分类别
  skills: string[]        # 技能清单
  scenarios: string[]    # 适用场景
  quality_score: float    # 质量评分 (0-1)
  usage_count: int        # 使用次数
  success_rate: float    # 成功率
  avg_duration: float    # 平均耗时(秒)
  current_load: int       # 当前负载
  max_load: int          # 最大负载
```

## DispatchResult 结构

```yaml
DispatchResult:
  success: boolean        # 调度是否成功
  selected_asset: Asset  # 选中的资产
  fallback_assets: Asset[] # 备选资产
  dispatch_strategy: string # 调度策略说明
  estimated_wait: int    # 预计等待秒数
  confidence: float      # 调度置信度
```

## 资产分类

### A类: gstack工程能力 (40+)

| 类别 | Agent数量 | 核心能力 |
|------|-----------|----------|
| 规划类 | 5 | roadmapper, planner |
| 执行类 | 8 | executor, frontend-dev |
| 验证类 | 4 | verifier, ui-checker |
| 审查类 | 6 | code-reviewer, security-reviewer |
| 调试类 | 3 | debugger, build-error-resolver |
| 设计类 | 7 | ui-designer, ux-architect |
| DevOps类 | 5 | devops-automator, sre |
| 移动类 | 3 | mobile-app-builder |

### B类: agency专业能力 (15类/100+)

| 类别 | Agent数量 | 核心能力 |
|------|-----------|----------|
| 运营类 | 20+ | 操盘手、增长、内容、用户 |
| 营销类 | 15+ | 品牌、投放、SEO、KOL |
| 战略类 | 10+ | 战略规划、竞争分析 |
| 产品类 | 12+ | 需求分析、用户体验 |
| 技术类 | 15+ | 架构、安全、性能 |

### C类: baoyu创意能力 (18)

| Skill | 核心能力 | 输出 |
|-------|----------|------|
| baoyu-image-gen | AI图片生成 | 图片 |
| baoyu-post-to-x | X/Twitter发布 | 帖子 |
| baoyu-slide-deck | PPT生成 | PPT |
| baoyu-translate | 翻译 | 译文 |
| baoyu-comic | 漫画生成 | 漫画 |
| baoyu-infographic | 信息图生成 | 信息图 |

## 调度策略矩阵

| 任务类型 | 首选资产类型 | 备选资产类型 | 并发数 |
|----------|--------------|--------------|--------|
| 工程开发 | gstack | agency | 3-5 |
| 创意设计 | baoyu | gstack-design | 2-4 |
| 运营策略 | agency | gstack-planner | 1-3 |
| 安全审查 | gstack-security | agency-security | 1-2 |
| 营销执行 | baoyu | agency-marketing | 5-10 |

## 调用示例

```python
from agents.middle-tier.assets import AssetHub

assets = AssetHub()

result = assets.dispatch(task={
    "type": "工程开发",
    "description": "开发用户登录功能",
    "scenarios": ["前端", "React", "响应式"]
})

# 返回示例
{
    "success": True,
    "selected_asset": {
        "id": "gs-006",
        "name": "engineering-frontend-developer",
        "type": "gstack",
        "category": "前端开发",
        "quality_score": 0.92,
        "current_load": 2,
        "max_load": 5
    },
    "fallback_assets": [
        {"id": "gs-011", "name": "design-ui-designer", "quality_score": 0.88},
        {"id": "ag-001", "name": "业务操盘手咨询", "quality_score": 0.85}
    ],
    "estimated_wait": 0,
    "confidence": 0.92
}
```
