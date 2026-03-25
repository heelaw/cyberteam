# baoyu-skills 集成指南

> **版本**: v3.1 | **创建日期**: 2026-03-24 | **更新日期**: 2026-03-24 | **定位**: 内容运营技能调用手册
>
> 本文档定义了 baoyu-skills (17个内容运营技能) 的集成方式、调用协议、使用场景。
>
> **v3.1 更新**: 整合到 L3A 内容运营部，明确调用边界。

---

## 目录

1. [baoyu-skills 概述](#一baoyu-skills概述)
2. [技能分类与清单](#二技能分类与清单)
3. [调用机制](#三调用机制)
4. [使用场景](#四使用场景)
5. [集成协议](#五集成协议)
6. [最佳实践](#六最佳实践)

---

## 一、baoyu-skills 概述

> **重要说明**: baoyu-skills 是 CyberTeam v3 架构中定义的概念性技能集合。
>
> 这些技能由内容运营部通过 7 专家系统调用，执行具体的内容运营任务。
>
> 调用方式: 用户请求 → CEO 路由到内容运营部 → 7 专家决策 → 调用对应技能 → 返回结果

### 1.1 什么是 baoyu-skills

```yaml
定义:
  baoyu-skills 是一套内容运营技能集合，
  包含 17 个实用技能，覆盖内容创作、
  图像生成、多平台发布、格式转换等场景。

核心价值:
  - 全流程覆盖: 从创作到发布
  - 多平台支持: 小红书、公众号、微博、X等
  - 自动化处理: 格式转换、图像生成
  - 专业质量: 符合平台规范

提供者:
  baoyu (第三方技能集合)
```

### 1.2 架构定位

```
┌─────────────────────────────────────────────────────────────┐
│                    CyberTeam v3 架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  内容运营部 (主要使用者)                                      │
│    ↓                                                        │
│  7位专家协作                                                 │
│    ├── 用户画像专家                                          │
│    ├── 文案撰写专家                                          │
│    └── 内容审核专家                                          │
│    ↓                                                        │
│  baoyu-skills (17个技能)                                    │
│    ├── 图像生成 (6个)                                       │
│    ├── 多平台发布 (4个)                                     │
│    ├── 格式转换 (3个)                                       │
│    └── 内容获取 (2个)                                       │
│    ↓                                                        │
│  产出物交付                                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 技能清单

| 类别 | 技能数 | 技能列表 |
|------|--------|----------|
| **图像生成** | 6 | cover-image, image-gen, xhs-images, comic, article-illustrator, infographic |
| **多平台发布** | 4 | post-to-wechat, post-to-weibo, post-to-x, xhs-images --publish |
| **格式转换** | 3 | format-markdown, markdown-to-html, translate |
| **内容获取** | 2 | url-to-markdown, youtube-transcript |
| **运营技能** | 2 | 活动运营标准八步, 新媒体运营基础 |

---

## 二、技能分类与清单

### 2.1 图像生成类 (6个)

#### baoyu-cover-image

```yaml
功能: 生成封面图
支持比例:
  - 2.35:1 (横版，公众号)
  - 16:9 (横版，通用)
  - 1:1 (方形，通用)

调用格式:
  baoyu-cover-image "标题" --type [landscape|square|portrait]

参数:
  - text: 封面文字 (必需)
  - type: 比例类型 (可选，默认 landscape)

输出:
  - 封面图文件
  - 文件路径

示例:
  baoyu-cover-image "AI写作工具推荐" --type landscape
  → 生成 2.35:1 横版封面图
```

#### baoyu-image-gen

```yaml
功能: 通用图像生成

调用格式:
  baoyu-image-gen "图像描述"

参数:
  - prompt: 图像描述 (必需)

输出:
  - 生成图像
  - 文件路径

示例:
  baoyu-image-gen "一个现代风格的办公场景，有人在用电脑"
  → 生成对应图像
```

#### baoyu-xhs-images

```yaml
功能: 小红书系列图生成 (1-9张，3:4)

调用格式:
  baoyu-xhs-images "主题" --count [1-9]

参数:
  - topic: 图片主题 (必需)
  - count: 图片数量 (可选，默认3)
  - publish: 是否发布 (可选)

输出:
  - 系列图片 (3:4)
  - 文件路径

示例:
  baoyu-xhs-images "AI写作工具推荐" --count 5
  → 生成 5 张小红书图片
```

#### baoyu-comic

```yaml
功能: 品牌故事漫画生成

调用格式:
  baoyu-comic "故事描述"

参数:
  - story: 故事描述 (必需)

输出:
  - 漫画图像
  - 文件路径

示例:
  baoyu-comic "小明使用AI写作工具后，效率提升10倍的故事"
  → 生成品牌故事漫画
```

#### baoyu-article-illustrator

```yaml
功能: 文章配图生成

调用格式:
  baoyu-article-illustrator "文章内容" --count [1-5]

参数:
  - content: 文章内容 (必需)
  - count: 配图数量 (可选，默认1)

输出:
  - 配图
  - 文件路径

示例:
  baoyu-article-illustrator "AI写作工具介绍文章..." --count 3
  → 生成 3 张配图
```

#### baoyu-infographic

```yaml
功能: 信息图生成 (多种布局)

调用格式:
  baoyu-infographic "数据信息" --layout [timeline|comparison|list|chart]

参数:
  - data: 数据信息 (必需)
  - layout: 布局类型 (可选)

布局类型:
  - timeline: 时间线布局
  - comparison: 对比布局
  - list: 列表布局
  - chart: 图表布局

输出:
  - 信息图
  - 文件路径

示例:
  baoyu-infographic "AI写作工具的发展历程..." --layout timeline
  → 生成时间线信息图
```

### 2.2 多平台发布类 (4个)

#### baoyu-post-to-wechat

```yaml
功能: 发布到公众号

调用格式:
  baoyu-post-to-wechat --title "标题" --content "HTML内容"

参数:
  - title: 文章标题 (必需)
  - content: HTML内容 (必需)
  - cover: 封面图 (可选)

输出:
  - 发布状态
  - 文章链接

示例:
  baoyu-post-to-wechat --title "AI写作工具推荐" --content article.html
  → 发布到公众号
```

#### baoyu-post-to-weibo

```yaml
功能: 发布到微博

调用格式:
  baoyu-post-to-weibo --content "微博内容" --images "图片路径"

参数:
  - content: 微博内容 (必需)
  - images: 图片 (可选，逗号分隔)

输出:
  - 发布状态
  - 微博链接

示例:
  baoyu-post-to-weibo --content "推荐一个超好用的AI写作工具！" --images cover.jpg
  → 发布到微博
```

#### baoyu-post-to-x

```yaml
功能: 发布到 X (Twitter)

调用格式:
  baoyu-post-to-x --content "推文内容" --media "媒体路径"

参数:
  - content: 推文内容 (必需)
  - media: 媒体文件 (可选)

输出:
  - 发布状态
  - 推文链接

示例:
  baoyu-post-to-x --content "Check out this AI writing tool!" --media cover.jpg
  → 发布到 X
```

#### baoyu-xhs-images --publish

```yaml
功能: 发布到小红书

调用格式:
  baoyu-xhs-images "主题" --publish

参数:
  - topic: 笔记主题 (必需)
  - publish: 发布标志 (必需)

输出:
  - 发布状态
  - 笔记链接

示例:
  baoyu-xhs-images "AI写作工具推荐" --count 5 --publish
  → 生成并发布小红书笔记
```

### 2.3 格式转换类 (3个)

#### baoyu-format-markdown

```yaml
功能: Markdown 美化

调用格式:
  baoyu-format-markdown article.md

参数:
  - file: Markdown文件 (必需)

输出:
  - 美化后的 Markdown
  - 保存到原文件

示例:
  baoyu-format-markdown draft.md
  → 美化 draft.md
```

#### baoyu-markdown-to-html

```yaml
功能: Markdown 转 HTML (支持微信主题)

调用格式:
  baoyu-markdown-to-html article.md --theme [wechat|default]

参数:
  - file: Markdown文件 (必需)
  - theme: 主题 (可选，默认 wechat)

输出:
  - HTML文件
  - 文件路径

示例:
  baoyu-markdown-to-html article.md --theme wechat
  → 转换为微信主题 HTML
```

#### baoyu-translate

```yaml
功能: 多语言翻译

调用格式:
  baoyu-translate article.md --to [en|ja|ko|...]

参数:
  - file: 文件 (必需)
  - to: 目标语言 (必需)

支持语言:
  - en: 英语
  - ja: 日语
  - ko: 韩语
  - ... (更多)

输出:
  - 翻译后的文件
  - 文件路径

示例:
  baoyu-translate article.md --to en
  → 翻译为英语
```

### 2.4 内容获取类 (2个)

#### baoyu-url-to-markdown

```yaml
功能: 网页转 Markdown

调用格式:
  baoyu-url-to-markdown https://example.com/article

参数:
  - url: 网页URL (必需)

输出:
  - Markdown文件
  - 文件路径

示例:
  baoyu-url-to-markdown https://example.com/article
  → 保存为 Markdown
```

#### baoyu-youtube-transcript

```yaml
功能: YouTube 字幕提取

调用格式:
  baoyu-youtube-transcript https://youtube.com/watch?v=xxx

参数:
  - url: YouTube URL (必需)

输出:
  - 字幕文本
  - 文件路径

示例:
  baoyu-youtube-transcript https://youtube.com/watch?v=xxx
  → 提取字幕
```

### 2.5 运营技能类 (2个)

#### 活动运营标准八步

```yaml
功能: 活动策划全流程

步骤:
  1. 目标设定
  2. 用户洞察
  3. 创意策划
  4. 方案设计
  5. 资源准备
  6. 执行监控
  7. 复盘总结
  8. 持续优化

调用方式:
  作为思维框架注入到内容运营部
```

#### 新媒体运营基础

```yaml
功能: 平台认知/内容规划/用户运营

内容:
  - 平台认知: 各平台特性
  - 内容规划: 内容策略
  - 用户运营: 用户增长

调用方式:
  作为思维框架注入到内容运营部
```

---

## 三、调用机制

### 3.1 调用方式

#### 方式1: 直接调用

```yaml
调用格式:
  baoyu-{skill-name} [参数]

示例:
  baoyu-cover-image "标题" --type landscape
  baoyu-xhs-images "主题" --count 5 --publish
  baoyu-post-to-wechat --title "标题" --content content.html

执行流程:
  1. 内容运营部决策调用
  2. 执行技能调用
  3. 获取执行结果
  4. 返回给 PM
```

#### 方式2: 通过专家决策调用

```yaml
调用流程:
  1. 7位专家协作
  2. 专家决策需要调用技能
  3. 专家生成调用序列
  4. PM 执行调用序列
  5. 返回结果给专家
  6. 专家整合结果

示例:
  专家决策:
    - 需要生成封面图
    - 需要生成配图
    - 需要发布到公众号

  调用序列:
    baoyu-cover-image "标题" --type landscape
    baoyu-article-illustrator "内容" --count 3
    baoyu-markdown-to-html article.md --theme wechat
    baoyu-post-to-wechat --title "标题" --content article.html
```

#### 方式3: 批量调用

```yaml
批量场景:
  - 多平台同时发布
  - 批量生成图像
  - 批量格式转换

调用方式:
  并行执行多个技能

示例:
  并行:
    - baoyu-post-to-wechat ...
    - baoyu-post-to-weibo ...
    - baoyu-xhs-images --publish ...

  输出: 多平台发布状态
```

### 3.2 调用协议

```yaml
输入格式:
  {
    "skill": "baoyu-cover-image",
    "params": {
      "text": "标题",
      "type": "landscape"
    }
  }

输出格式:
  {
    "skill": "baoyu-cover-image",
    "status": "success",
    "result": {
      "file": "/path/to/image.jpg",
      "url": "https://..."
    },
    "error": null
  }

错误处理:
  if 调用失败:
    - 记录错误日志
    - 返回错误信息
    - 降级到备用方案
    - 通知 PM
```

### 3.3 参数传递规范

```yaml
图像生成:
  - 文字参数: UTF-8 编码
  - 比例参数: landscape|square|portrait
  - 数量参数: 1-9 (小红书)

多平台发布:
  - 标题: 简洁明了
  - 内容: HTML格式 (公众号)
  - 图片: 支持多图 (逗号分隔)

格式转换:
  - 文件路径: 绝对路径或相对路径
  - 目标语言: ISO 639-1 代码
  - 主题: wechat|default
```

---

## 四、使用场景

### 4.1 公众号文章创作与发布

```yaml
场景: 创作并发布公众号文章

流程:
  Step 1: 用户画像分析 (expert-user-persona)
  Step 2: 文案撰写 (expert-copywriter)
  Step 3: 内容审核 (expert-reviewer)
  Step 4: 格式美化 (baoyu-format-markdown)
  Step 5: HTML转换 (baoyu-markdown-to-html --theme wechat)
  Step 6: 封面图生成 (baoyu-cover-image --type landscape)
  Step 7: 配图生成 (baoyu-article-illustrator --count 3)
  Step 8: 发布 (baoyu-post-to-wechat)

调用序列:
  baoyu-format-markdown article.md
  baoyu-markdown-to-html article.md --theme wechat
  baoyu-cover-image "标题" --type landscape
  baoyu-article-illustrator "内容" --count 3
  baoyu-post-to-wechat --title "标题" --content article.html --cover cover.jpg

预期产出:
  - 美化的 Markdown
  - 微信主题 HTML
  - 横版封面图
  - 3张配图
  - 发布状态
```

### 4.2 小红书笔记创作与发布

```yaml
场景: 创作并发布小红书笔记

流程:
  Step 1: 用户画像分析
  Step 2: 文案撰写
  Step 3: 内容审核
  Step 4: 系列图生成 (baoyu-xhs-images --count 5)
  Step 5: 发布 (baoyu-xhs-images --publish)

调用序列:
  baoyu-xhs-images "主题" --count 5 --publish

预期产出:
  - 5张小红书图片 (3:4)
  - 发布状态
  - 笔记链接
```

### 4.3 多平台同时发布

```yaml
场景: 一篇内容多平台发布

流程:
  Step 1: 通用文案创作
  Step 2: 平台适配
  Step 3: 并行发布

调用序列 (并行):
  # 公众号
  baoyu-markdown-to-html article.md --theme wechat
  baoyu-cover-image "标题" --type landscape
  baoyu-post-to-wechat --title "标题" --content article.html

  # 小红书
  baoyu-xhs-images "主题" --count 5 --publish

  # 微博
  baoyu-post-to-weibo --content "微博内容" --images cover.jpg

  # X
  baoyu-post-to-x --content "Tweet content" --media cover.jpg

预期产出:
  - 公众号发布状态
  - 小红书发布状态
  - 微博发布状态
  - X发布状态
```

### 4.4 内容获取与再创作

```yaml
场景: 获取网页内容并再创作

流程:
  Step 1: 网页转 Markdown (baoyu-url-to-markdown)
  Step 2: 内容再创作
  Step 3: 翻译 (baoyu-translate)
  Step 4: 发布

调用序列:
  baoyu-url-to-markdown https://example.com/article
  → 获取 content.md
  → 再创作
  → baoyu-translate content.md --to en
  → 发布

预期产出:
  - 原文 Markdown
  - 翻译后 Markdown
  - 发布内容
```

---

## 五、集成协议

### 5.1 与内容运营部集成

```yaml
集成方式:
  baoyu-skills 作为内容运营部的标准工具集

调用流程:
  1. 用户需求 → CEO
  2. CEO 路由到内容运营部
  3. PM 触发 7 位专家协作
  4. 专家决策调用 baoyu-skills
  5. PM 执行调用序列
  6. 返回结果给专家
  7. 专家整合结果
  8. QA 审核
  9. 返回最终产出

调用权限:
  - 内容运营部: 所有技能
  - 其他部门: 只读调用 (如需要)
```

### 5.2 与专家系统集成

```yaml
expert-user-persona (用户画像专家):
  不直接调用 baoyu-skills
  提供用户画像输入

expert-copywriter (文案撰写专家):
  决策调用:
    - 需要封面图 → baoyu-cover-image
    - 需要配图 → baoyu-article-illustrator
    - 需要信息图 → baoyu-infographic

expert-reviewer (内容审核专家):
  不直接调用 baoyu-skills
  审核内容产出

未来专家:
  expert-visual-design (视觉设计专家)
    - 决策调用所有图像生成技能

  expert-distribution (分发策略专家)
    - 决策调用所有发布技能
```

### 5.3 错误处理

```yaml
错误类型:
  1. 参数错误
  2. 文件不存在
  3. 网络错误
  4. API 限制
  5. 平台错误

处理策略:
  1. 参数错误
     - 返回参数说明
     - 提供正确示例
     - 重新调用

  2. 文件不存在
     - 检查文件路径
     - 尝试生成默认文件
     - 降级处理

  3. 网络错误
     - 重试 3 次
     - 记录错误日志
     - 通知用户

  4. API 限制
     - 等待重试
     - 降级到手动
     - 通知用户

  5. 平台错误
     - 检查平台状态
     - 稍后重试
     - 保存草稿
```

---

## 六、最佳实践

### 6.1 图像生成

```yaml
最佳实践:
  1. 封面图
     - 使用 baoyu-cover-image
     - 公众号用 landscape (2.35:1)
     - 小红书用 portrait (3:4)
     - 微博用 square (1:1)

  2. 配图
     - 使用 baoyu-article-illustrator
     - 数量: 3-5 张
     - 风格: 保持一致

  3. 信息图
     - 使用 baoyu-infographic
     - 选择合适布局
     - 数据清晰易读
```

### 6.2 多平台发布

```yaml
最佳实践:
  1. 平台适配
     - 公众号: 专业深度，长文
     - 小红书: 种草分享，图片为主
     - 微博: 短平快，热点
     - X: 观点讨论，短内容

  2. 发布顺序
     - 先发布主要平台
     - 再发布其他平台
     - 或并行发布

  3. 内容复用
     - 核心内容一致
     - 形式适配平台
     - 避免完全重复
```

### 6.3 格式转换

```yaml
最佳实践:
  1. Markdown 美化
     - 发布前执行
     - 检查格式规范
     - 统一排版风格

  2. HTML 转换
     - 选择正确主题
     - 公众号用 wechat 主题
     - 检查转换效果

  3. 翻译
     - 明确目标语言
     - 检查翻译质量
     - 人工校对关键术语
```

### 6.4 批量操作

```yaml
最佳实践:
  1. 图像生成
     - 批量生成相似图像
     - 统一风格和参数

  2. 多平台发布
     - 准备好所有素材
     - 并行执行发布
     - 监控发布状态

  3. 格式转换
     - 批量转换文件
     - 统一输出目录
```

---

## 七、附录

### 7.1 技能速查表

| 技能 | 功能 | 常用参数 |
|------|------|----------|
| cover-image | 封面图 | --type landscape\|square\|portrait |
| image-gen | 通用图像 | prompt |
| xhs-images | 小红书图 | --count 1-9, --publish |
| comic | 漫画 | story |
| article-illustrator | 配图 | --count 1-5 |
| infographic | 信息图 | --layout timeline\|comparison\|list\|chart |
| post-to-wechat | 公众号 | --title, --content, --cover |
| post-to-weibo | 微博 | --content, --images |
| post-to-x | X | --content, --media |
| format-markdown | 美化 | file |
| markdown-to-html | HTML | --theme wechat\|default |
| translate | 翻译 | --to en\|ja\|ko\|... |
| url-to-markdown | 网页转MD | url |
| youtube-transcript | 字幕 | url |

### 7.2 安装指南

```yaml
前提条件:
  - Claude Code CLI 已安装
  - 具有内容运营需求
  - 已配置相关平台 API 密钥（可选）

安装方式:

方式1: 作为概念性技能使用 (推荐)
  说明:
    baoyu-skills 是 CyberTeam v3 架构中定义的
    内容运营技能集合，由内容运营部通过 7 专家
    系统调用。

  使用方式:
    用户: "创作一篇关于 AI 写作工具的文章并发布"
    → CEO 路由到内容运营部
    → 7 专家协作决策需要哪些技能
    → 调用对应技能（概念性调用）
    → 返回执行结果

方式2: 实现为独立 Skills (未来)

  Step 1: 创建技能目录
    mkdir -p ~/.claude/skills/baoyu-skills

  Step 2: 创建技能文件
    每个 skill 对应一个独立文件:
      - cover-image.md
      - image-gen.md
      - xhs-images.md
      - ...

  Step 3: 配置 SKILL.md
    定义技能元数据、参数、输出格式

  Step 4: 配置 API 密钥 (如需要)
    - OpenAI DALL-E API (图像生成)
    - 微信公众号 API
    - 微博 API
    - X (Twitter) API
    - 小红书 API (通过第三方)

验证安装:
  # 检查技能是否可用
  ls ~/.claude/skills/baoyu-skills/

  # 测试调用
  /baoyu-cover-image "测试标题" --type landscape
```

### 7.3 平台规范

| 平台 | 封面比例 | 内容风格 | 发布技能 |
|------|----------|----------|----------|
| 公众号 | 2.35:1 | 专业/深度 | post-to-wechat |
| 小红书 | 3:4 | 种草/生活方式 | xhs-images --publish |
| 微博 | 16:9 / 1:1 | 短平快/热点 | post-to-weibo |
| X | 16:9 | 观点/讨论 | post-to-x |

### 7.3 相关文档

- [00-分层集成架构设计.md](./00-分层集成架构设计.md)
- [01-公司架构与人员配置.md](./01-公司架构与人员配置.md)
- [07-用户执行指南.md](./07-用户执行指南.md)
- [08-思考天团集成指南.md](./08-思考天团集成指南.md)

---

**文档版本**: v3.1
**创建日期**: 2026-03-24
**最后更新**: 2026-03-24

---

*本文档定义了 baoyu-skills (17个内容运营技能) 的集成方式、调用协议、使用场景。*
