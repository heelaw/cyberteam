# 结构化文本解析的正则表达式与法学硕士

用于解析结构化文本（测验、表格、发票、文档）的实用决策框架。关键见解：正则表达式可以廉价且确定地处理 95-98% 的情况。为剩余的边缘情况保留昂贵的法学硕士学位。

## 何时激活

- 解析具有重复模式的结构化文本（问题、表格、表格）
- 在正则表达式和LLM之间做出文本提取的决定
- 构建结合两种方法的混合管道
- 优化文本处理中的成本/准确性权衡

## 决策框架```
Is the text format consistent and repeating?
├── Yes (>90% follows a pattern) → Start with Regex
│   ├── Regex handles 95%+ → Done, no LLM needed
│   └── Regex handles <95% → Add LLM for edge cases only
└── No (free-form, highly variable) → Use LLM directly
```## 架构模式```
Source Text
    │
    ▼
[Regex Parser] ─── Extracts structure (95-98% accuracy)
    │
    ▼
[Text Cleaner] ─── Removes noise (markers, page numbers, artifacts)
    │
    ▼
[Confidence Scorer] ─── Flags low-confidence extractions
    │
    ├── High confidence (≥0.95) → Direct output
    │
    └── Low confidence (<0.95) → [LLM Validator] → Output
```## 实施

### 1. 正则表达式解析器（处理大多数）```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedItem:
    id: str
    text: str
    choices: tuple[str, ...]
    answer: str
    confidence: float = 1.0

def parse_structured_text(content: str) -> list[ParsedItem]:
    """Parse structured text using regex patterns."""
    pattern = re.compile(
        r"(?P<id>\d+)\.\s*(?P<text>.+?)\n"
        r"(?P<choices>(?:[A-D]\..+?\n)+)"
        r"Answer:\s*(?P<answer>[A-D])",
        re.MULTILINE | re.DOTALL,
    )
    items = []
    for match in pattern.finditer(content):
        choices = tuple(
            c.strip() for c in re.findall(r"[A-D]\.\s*(.+)", match.group("choices"))
        )
        items.append(ParsedItem(
            id=match.group("id"),
            text=match.group("text").strip(),
            choices=choices,
            answer=match.group("answer"),
        ))
    return items
```### 2. 置信度评分

标记可能需要 LLM 审查的项目：```python
@dataclass(frozen=True)
class ConfidenceFlag:
    item_id: str
    score: float
    reasons: tuple[str, ...]

def score_confidence(item: ParsedItem) -> ConfidenceFlag:
    """Score extraction confidence and flag issues."""
    reasons = []
    score = 1.0

    if len(item.choices) < 3:
        reasons.append("few_choices")
        score -= 0.3

    if not item.answer:
        reasons.append("missing_answer")
        score -= 0.5

    if len(item.text) < 10:
        reasons.append("short_text")
        score -= 0.2

    return ConfidenceFlag(
        item_id=item.id,
        score=max(0.0, score),
        reasons=tuple(reasons),
    )

def identify_low_confidence(
    items: list[ParsedItem],
    threshold: float = 0.95,
) -> list[ConfidenceFlag]:
    """Return items below confidence threshold."""
    flags = [score_confidence(item) for item in items]
    return [f for f in flags if f.score < threshold]
```### 3. LLM 验证器（仅限边缘情况）```python
def validate_with_llm(
    item: ParsedItem,
    original_text: str,
    client,
) -> ParsedItem:
    """Use LLM to fix low-confidence extractions."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Cheapest model for validation
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                f"Extract the question, choices, and answer from this text.\n\n"
                f"Text: {original_text}\n\n"
                f"Current extraction: {item}\n\n"
                f"Return corrected JSON if needed, or 'CORRECT' if accurate."
            ),
        }],
    )
    # Parse LLM response and return corrected item...
    return corrected_item
```### 4. 混合管道```python
def process_document(
    content: str,
    *,
    llm_client=None,
    confidence_threshold: float = 0.95,
) -> list[ParsedItem]:
    """Full pipeline: regex -> confidence check -> LLM for edge cases."""
    # Step 1: Regex extraction (handles 95-98%)
    items = parse_structured_text(content)

    # Step 2: Confidence scoring
    low_confidence = identify_low_confidence(items, confidence_threshold)

    if not low_confidence or llm_client is None:
        return items

    # Step 3: LLM validation (only for flagged items)
    low_conf_ids = {f.item_id for f in low_confidence}
    result = []
    for item in items:
        if item.id in low_conf_ids:
            result.append(validate_with_llm(item, content, llm_client))
        else:
            result.append(item)

    return result
```## 真实世界指标

来自生产测验解析管道（410 项）：

|公制|价值|
|--------|--------|
|正则表达式成功率 | 98.0% |
|低可信度项目 | 8 (2.0%) |
|需要LLM电话| 〜5 |
|与全LLM相比节省成本| 〜95% |
|测试覆盖率| 93% |

## 最佳实践

- **从正则表达式开始** - 即使不完美的正则表达式也可以为您提供改进的基准
- **使用置信度评分**以编程方式确定需要 LLM 帮助的内容
- **使用最便宜的LLM**进行验证（俳句级模型就足够了）
- **从不改变**解析的项目 - 从清理/验证步骤返回新实例
- **TDD 对于解析器来说效果很好**——首先为已知模式编写测试，然后是边缘情况
- **记录指标**（正则表达式成功率、LLM 调用计数）以跟踪管道运行状况

## 要避免的反模式

- 当正则表达式处理 95% 以上的情况时，将所有文本发送到 LLM（昂贵且缓慢）
- 使用正则表达式来处理自由格式、高度可变的文本（LLM 在这里更好）
- 跳过置信度评分并希望正则表达式“正常工作”
- 在清理/验证步骤期间改变解析的对象
- 不测试边缘情况（格式错误的输入、缺失字段、编码问题）

## 何时使用

- 测验/考试问题解析
- 表单数据提取
- 发票/收据处理
- 文档结构解析（标题、部分、表格）
- 任何具有重复模式且成本很重要的结构化文本