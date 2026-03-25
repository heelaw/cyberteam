# 交叉帖子

通过平台原生适配在多个社交平台上分发内容。

## 何时激活

- 用户想要将内容发布到多个平台
- 在社交媒体上发布公告、发布或更新
- 将帖子从一个平台重新调整到其他平台
- 用户说“交叉发布”、“到处发布”、“在所有平台上共享”或“分发此内容”

## 核心规则

1. **切勿跨平台发布相同的内容。** 每个平台都会进行本机适配。
2. **先主平台。**发布到主平台，然后适应其他平台。
3. **尊重平台约定。** 长度限制、格式、链接处理都不同。
4. **每个帖子一个想法。** 如果源内容有多个想法，请拆分到多个帖子中。
5. **归属很重要。** 如果交叉发布其他人的内容，请注明来源。

## 平台规格

|平台|最大长度|链接处理 |标签 |媒体|
|----------|------------|----------------|----------|--------|
| X | 280 个字符（高级版 4000 个）|按长度计算 |最小（最多 1-2）|图片、视频、GIF |
|领英 | 3000 个字符 |不计长度| 3-5 相关 |图像、视频、文档、轮播 |
|主题 | 500 个字符 |单独的链接附件|无典型 |图片、视频 |
|蓝天| 300 个字符 |通过构面（富文本）|无（使用提要）|图片 |

## 工作流程

### 第 1 步：创建源内容

从核心思想开始。使用“内容引擎”技能获得高质量草稿：
- 识别单一核心消息
- 确定主要平台（受众最多的平台）
- 首先起草主要平台版本

### 第 2 步：确定目标平台

询问用户或根据上下文确定：
- 针对哪些平台
- 优先顺序（主要获得最好的版本）
- 任何特定于平台的要求（例如，LinkedIn 需要专业语气）

### 第 3 步：根据平台进行调整

对于每个目标平台，转换内容：

**X 适配：**
- 以钩子打开，而不是摘要
- 快速切入核心洞察
- 尽可能将链接保留在正文之外
- 使用线程格式来显示较长的内容

**LinkedIn 改编：**
- 强有力的第一行（在“查看更多”之前可见）
- 带换行符的短段落
- 围绕课程、结果或专业要点进行框架
- 比 X 更明确的上下文（LinkedIn 受众需要框架）

**线程适配：**
- 对话、随意的语气
- 比 LinkedIn 短，比 X 压缩程度低
- 如果可能的话，视觉优先

**蓝天适应：**
- 直接、简洁（限制 300 个字符）
- 以社区为导向的基调
- 使用提要/列表代替主题标签进行主题定位

### 第 4 步：发布主要平台

先发布到主平台：
- 对 X 使用 `x-api` 技能
- 为其他人使用特定于平台的 API 或工具
- 捕获帖子 URL 以供交叉引用

### 步骤 5：发布到二级平台

将改编后的版本发布到其余平台：
- 错开时间（不是同时进行——间隔 30-60 分钟）
- 在适当的情况下包括跨平台参考（“X 上的更长线程”等）

## 内容适配示例

### 来源：产品发布会

**X 版本：**```
We just shipped [feature].

[One specific thing it does that's impressive]

[Link]
```**领英版本：**```
Excited to share: we just launched [feature] at [Company].

Here's why it matters:

[2-3 short paragraphs with context]

[Takeaway for the audience]

[Link]
```**线程版本：**```
just shipped something cool — [feature]

[casual explanation of what it does]

link in bio
```### 来源：技术洞察

**X 版本：**```
TIL: [specific technical insight]

[Why it matters in one sentence]
```**领英版本：**```
A pattern I've been using that's made a real difference:

[Technical insight with professional framing]

[How it applies to teams/orgs]

#relevantHashtag
```## API 集成

### 批量交叉发布服务（示例模式）
如果使用交叉发布服务（例如 Postbridge、Buffer 或自定义 API），该模式如下所示：```python
import os
import requests

resp = requests.post(
    "https://your-crosspost-service.example/api/posts",
    headers={"Authorization": f"Bearer {os.environ['POSTBRIDGE_API_KEY']}"},
    json={
        "platforms": ["twitter", "linkedin", "threads"],
        "content": {
            "twitter": {"text": x_version},
            "linkedin": {"text": linkedin_version},
            "threads": {"text": threads_version}
        }
    },
    timeout=30,
)
resp.raise_for_status()
```### 手动发帖
如果没有 Postbridge，则使用其本机 API 发布到每个平台：
- X：使用`x-api`技能模式
- LinkedIn：带有 OAuth 2.0 的 LinkedIn API v2
- 线程：线程 API（元）
- Bluesky：AT协议API

## 质量门

发帖前：
- [ ] 每个平台版本自然读取该平台
- [ ] 跨平台没有相同的内容
- [ ] 遵守长度限制
- [ ] 链接有效且位置适当
- [ ] 语气符合平台惯例
- [ ] 媒体大小适合每个平台

## 相关技能

- `content-engine` — 生成平台原生内容
- `x-api` — X/Twitter API 集成