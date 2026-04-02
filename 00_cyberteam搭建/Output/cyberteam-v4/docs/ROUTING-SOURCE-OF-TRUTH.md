# 路由统一性分析报告

> 分析日期: 2026-04-01
> 分析范围: engine/ceo/ceo.py, engine/thinking/router.py, engine/thinking/injector.py

---

## 一、重复点清单

### 1.1 Intent (意图) 分类重复

| 来源 | 定义方式 | Intent数量 | 差异 |
|------|----------|------------|------|
| `CEO Router` | `Intent` Enum | 8个 | 有 `UNKNOWN` |
| `Thinking Router` | `INTENT_TRIGGER_RULES` dict | 8个 | 有 `财务投资` |
| `Thinking Injector` | `intent_rules` dict | 8个 | 有 `财务投资` |

**CEO Router Intent 定义** (`engine/ceo/ceo.py:64-72`):
```python
class Intent(Enum):
    DATA_ANALYSIS = "数据分析"
    CONTENT_OPS = "内容运营"
    TECH_ENGINEERING = "技术研发"
    SECURITY = "安全合规"
    STRATEGY = "战略规划"
    HR = "人力资源"
    OPERATIONS = "运营支持"
    UNKNOWN = "未知"
```

**Thinking Router INTENT_TRIGGER_RULES** (`engine/thinking/router.py:17-72`):
```python
INTENT_TRIGGER_RULES: dict[str, list[tuple[str, float]]] = {
    "数据分析": [...],
    "内容运营": [...],
    "技术研发": [...],
    "安全合规": [...],
    "战略规划": [...],
    "人力资源": [...],
    "运营支持": [...],
    "财务投资": [...],  # CEO没有，CEO归入"数据分析"
}
```

**冲突**: `财务投资` 在 Thinking Router/Injector 中是独立 intent，但在 CEO Router 中被归入 `DATA_ANALYSIS`。

---

### 1.2 Complexity (复杂度) 定义重复

| 来源 | 定义方式 | 值 |
|------|----------|-----|
| `CEO Router` | `Complexity` Enum | `HIGH`, `MEDIUM`, `LOW` |
| `Thinking Router` | `COMPLEXITY_MODEL_COUNT` dict | `"高"`, `"中"`, `"低"` |
| `Thinking Injector` | `_infer_complexity()` 返回 | `"高"`, `"中"`, `"低"` |

**冲突**: CEO 使用英文 Enum，Thinking 使用中文字符串。需要显式转换。

---

### 1.3 Intent → Category 映射重复

| 来源 | 映射定义位置 |
|------|--------------|
| `Thinking Router` | `ThinkingRouter._get_models_by_category()` (router.py:193-207) |
| `Thinking Injector` | `ThinkingInjector._infer_intent()` (injector.py:251-270) |

两者都有独立推断逻辑，逻辑略有不同。

---

### 1.4 部门映射重复

| 来源 | 部门映射 |
|------|----------|
| `CEO Router` | `_map_intent_to_dept()` (ceo.py:525-536) |
| `Thinking Router` | 无直接映射 |
| `Thinking Injector` | `_infer_domain()` (injector.py:290-310) |

CEO 的部门映射与 Injector 的 domain 推断有部分重叠但不一致。

---

## 二、单一事实源选择

### 2.1 推荐的事实源划分

| 维度 | 保留位置 | 理由 |
|------|----------|------|
| **Intent 定义** | `CEO Router` (`Intent` Enum) | CEO 是入口点，所有路由都应基于同一意图分类 |
| **Intent 关键词** | `CEO Router` (`INTENT_KEYWORDS`) | CEO 的关键词更完整，包含更明确的触发规则 |
| **Complexity 定义** | `CEO Router` (`Complexity` Enum) | CEO 评估复杂度，其他组件应引用 |
| **Routing Target** | `CEO Router` (`RoutingTarget` Enum) | CEO 决定路由目标，Thinking 只是执行注入 |
| **模型数量映射** | `Thinking Router` (`COMPLEXITY_MODEL_COUNT`) | Thinking 的职责，保留在此 |
| **互斥规则** | `Thinking Router` (`MUTUALLY_EXCLUSIVE`) | Thinking 的职责，保留在此 |

### 2.2 需要消除的重复

| 重复项 | 当前状态 | 建议 |
|--------|----------|------|
| `INTENT_TRIGGER_RULES` | Thinking Router 独有 | **删除**，改用 CEO 的 `INTENT_KEYWORDS` |
| `Thinking Injector._infer_intent()` | Injector 独有 | **改为接收参数**，不自己推断 |
| `Thinking Injector._infer_complexity()` | Injector 独有 | **改为接收参数**，不自己推断 |
| `Thinking Router._get_models_by_category()` | Router 独有 | **删除**，Intent→Category 映射应统一在 CEO |

---

## 三、引用位置（改造成引用）

### 3.1 Thinking Router 应引用 CEO 的 Intent

**当前**: `Thinking Router` 有独立的 `INTENT_TRIGGER_RULES`

**改为**: 直接使用 CEO 的 `INTENT_KEYWORDS` 或创建共享常量

```python
# 建议: 创建共享常量文件 engine/constants.py
INTENT_KEYWORDS = {
    Intent.DATA_ANALYSIS: ["增长", "数据", "分析", ...],
    Intent.CONTENT_OPS: ["内容", "文案", ...],
    ...
}
```

### 3.2 Thinking Injector 应接收 Intent/Complexity 参数

**当前**:
```python
def inject_auto(self, context: InjectionContext) -> "InjectionResult":
    # 内部自己推断 intent 和 complexity
    task_context = TaskContext(
        intent=self._infer_intent(context),  # 自己推断
        complexity=self._infer_complexity(context),  # 自己推断
    )
```

**改为**:
```python
def inject_auto(
    self,
    context: InjectionContext,
    intent: str = None,  # CEO 传入
    complexity: str = None  # CEO 传入
) -> "InjectionResult":
    # 如果没传入才推断（保持向后兼容）
    inferred_intent = intent or self._infer_intent(context)
    inferred_complexity = complexity or self._infer_complexity(context)
```

---

## 四、维护风险

### 4.1 当前风险

| 风险 | 描述 | 影响 |
|------|------|------|
| **意图不一致** | 同一个任务在不同层被归入不同 intent | 模型选择错误 |
| **复杂度不一致** | "高" vs `HIGH` 字符串不匹配 | 模型数量错误 |
| **部门映射丢失** | Injector 的 domain 推断与 CEO 的 dept 映射不同 | 路由目标偏差 |
| **维护困难** | 修改 intent 需要改3个地方 | 增加出错概率 |

### 4.2 风险缓解

| 风险 | 缓解措施 |
|------|----------|
| 意图不一致 | 统一到 `Intent` Enum，Thinking 只引用不定义 |
| 复杂度不一致 | 创建 `Complexity.to_thinking_string()` 转换方法 |
| 部门映射丢失 | `ThinkingInjector` 增加 `domain` 参数，由 CEO 传入 |
| 维护困难 | 将共享常量集中在 `engine/constants.py` |

---

## 五、最小改动方案

### 5.1 创建共享常量

```python
# engine/constants.py
from engine.ceo.ceo import Intent, Complexity

# Intent → 触发关键词 (来自 CEO)
INTENT_KEYWORDS = {
    Intent.DATA_ANALYSIS: ["增长", "数据", "分析", "财务", "投资", "ROI", ...],
    Intent.CONTENT_OPS: ["内容", "文案", "创作", ...],
    ...
}

# Intent → ModelCategory (新增强制映射)
INTENT_TO_CATEGORY = {
    Intent.DATA_ANALYSIS: "ANALYSIS",
    Intent.CONTENT_OPS: "CREATIVE",
    Intent.TECH_ENGINEERING: "SYSTEM",
    Intent.SECURITY: "EVALUATION",
    Intent.STRATEGY: "DECISION",
    Intent.HR: "DECISION",
    Intent.OPERATIONS: "SYSTEM",
    Intent.UNKNOWN: "ANALYSIS",
}

# Complexity → 模型数量
COMPLEXITY_MODEL_COUNT = {
    "高": 3,
    "中": 2,
    "低": 1,
}
```

### 5.2 修改 Thinking Router

```python
# engine/thinking/router.py
# 删除 INTENT_TRIGGER_RULES，改为引用常量
from engine.constants import INTENT_KEYWORDS, INTENT_TO_CATEGORY, COMPLEXITY_MODEL_COUNT
```

### 5.3 修改 Thinking Injector

```python
# engine/thinking/injector.py
# inject_auto 增加可选参数
def inject_auto(
    self,
    context: InjectionContext,
    intent: str = None,
    complexity: str = None,
    domain: str = None,
) -> "InjectionResult":
    # 优先使用传入参数
    inferred_intent = intent or self._infer_intent(context)
    inferred_complexity = complexity or self._infer_complexity(context)
    inferred_domain = domain or self._infer_domain(context)
```

### 5.4 修改 CEO Router

```python
# engine/ceo/ceo.py
# 在调用 ThinkingInjector 时传入完整上下文
thinking_result = self._inject_thinking(
    user_input,
    intent.value,  # 传入 string intent
    complexity.value,  # 传入 string complexity
    domain_map.get(intent.value),  # 传入 domain
)
```

---

## 六、验证无歧义检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Intent 定义唯一 | ✅ | 统一在 `Intent` Enum |
| Complexity 定义唯一 | ⚠️ | 需添加转换方法 |
| 部门/Domain 映射一致 | ❌ | 需统一 |
| Thinking 组件不自己推断 | ❌ | 需重构为接收参数 |
| 无循环引用 | ✅ | CEO → Thinking，Thinking 不回写 CEO |

---

*报告生成: router-arch agent*
