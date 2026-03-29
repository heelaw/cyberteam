# 内容运营专家 Agent 集成方案

**版本**: v1.0
**日期**: 2026-03-24
**作者**: P8 (基于 baoyu-skills v1.79.2)
**状态**: 已完成
**文件位置**: `Output/CyberTeam-v2.1/agents/experts/content-ops.md`

---

## 一、Agent 定义

```yaml
content-ops-agent:
  name: "内容运营专家 (ContentOps)"
  version: "v1.0"
  color: "#FF6B9D"
  icon: "🎨"

  identity:
    role: "内容创作与多平台发布专家"
    mission: "用 baoyu-skills 生成专业内容，一键发布到全平台"

  location: "Output/CyberTeam-v2.1/agents/experts/content-ops.md"

  skill_backends:
    - baoyu-image-gen        # AI图像生成 (多API)
    - baoyu-article-illustrator  # 文章配图
    - baoyu-cover-image      # 封面图
    - baoyu-infographic      # 信息图
    - baoyu-comic            # 知识漫画
    - baoyu-slide-deck       # PPT幻灯片
    - baoyu-xhs-images       # 小红书图片
    - baoyu-post-to-weibo    # 微博发布
    - baoyu-post-to-wechat   # 公众号发布
    - baoyu-post-to-x        # X发布
    - baoyu-translate        # 多语言翻译
    - baoyu-url-to-markdown  # 网页转Markdown
    - baoyu-youtube-transcript # YouTube字幕
    - baoyu-markdown-to-html  # Markdown转HTML
    - baoyu-format-markdown   # Markdown美化
    - baoyu-compress-image    # 图片压缩
    - baoyu-danger-gemini-web # Gemini后端
```

---

## 二、触发条件

### 精确触发关键词

| 类型 | 关键词 |
|------|--------|
| **图像生成** | 生成图片 / create image / 生成封面 / 生成配图 / 为文章配图 |
| **信息图** | 信息图 / infographic / 可视化 / 高密度信息大图 |
| **PPT** | PPT / 幻灯片 / slide deck / 生成演示文稿 |
| **漫画** | 知识漫画 / 教育漫画 / 漫画化 / comic |
| **小红书** | 小红书 / xhs / RedNote / 种草 / 小红书图片 |
| **发布** | 发布微博 / 发布公众号 / 发布到X / 分享到微博 |
| **翻译** | 翻译 / translate / 精翻 / 快速翻译 / 本地化 |
| **素材获取** | 网页转markdown / YouTube字幕 / 视频字幕 / 抓取内容 |
| **格式转换** | markdown转html / 微信外链 / 美化文章 / format markdown |
| **图片处理** | 压缩图片 / 优化图片 / 转webp |

### CEO 调度规则

```
用户输入 → CEO意图解析 → 任务类型判断
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ↓                          ↓                          ↓
    内容创作类                    发布类                      素材类
         │                          │                          │
    → 内容运营专家             → 内容运营专家             → 内容运营专家
    (生成配图/封面/信息图)     (发布到多平台)            (抓取/翻译/整理)
```

---

## 三、工作流设计

### 工作流 A: 内容创作 → 配图 → 多平台发布

```
用户: "帮我把这篇竞品分析报告发布到公众号和微博，需要配图"

   ┌──────────────────────────────────────────────────────────────┐
   │  Step 1: 内容理解                                           │
   │  - 类型: 竞品分析报告                                       │
   │  - 目标: 公众号 + 微博                                      │
   │  - 需求: 配图 + 格式化                                      │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 2: 内容预处理                                          │
   │  /baoyu-format-markdown 竞品分析.md                         │
   │  /baoyu-markdown-to-html 竞品分析-formatted.md --theme wechat │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 3: 配图生成                                           │
   │  /baoyu-cover-image 竞品分析.md --aspect 2.35:1          │
   │  /baoyu-article-illustrator 竞品分析.md --type infographic │
   │  /baoyu-infographic 竞品数据.md --layout comparison       │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 4: 多平台发布                                         │
   │  /baoyu-post-to-wechat --title "竞品分析" --content xxx.html │
   │  /baoyu-post-to-weibo --article 竞品分析-formatted.md       │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 5: 汇报交付                                            │
   │  - 公众号: 已发布 [链接]                                     │
   │  - 微博: 已发布 [链接]                                       │
   │  - 配图: 3张 [路径]                                          │
   └──────────────────────────────────────────────────────────────┘
```

### 工作流 B: 竞品调研 → 素材获取 → 本地化 → 发布

```
用户: "帮我调研竞品A的营销策略，发布到小红书"

   ┌──────────────────────────────────────────────────────────────┐
   │  Step 1: 素材抓取                                          │
   │  /baoyu-url-to-markdown https://竞品A官网/marketing          │
   │  /baoyu-post-to-x --url 竞品A最新推文  (如适用)            │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 2: 内容翻译/改写                                      │
   │  /baoyu-translate 竞品A策略.md --mode refined --to zh      │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 3: 小红书内容生成                                      │
   │  /baoyu-xhs-images 竞品A分析.md --style cute --layout balanced │
   │  /baoyu-xhs-images 竞品A分析.md --style fresh --layout flow │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 4: 发布                                               │
   │  发布小红书系列图片 (1-10张)                                │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   交付: 小红书竞品分析系列 ✅
```

### 工作流 C: 视频内容 → 字幕提取 → 文章 → 多平台发布

```
用户: "这个YouTube视频讲了什么？整理成文章发公众号"

   ┌──────────────────────────────────────────────────────────────┐
   │  Step 1: 字幕提取                                          │
   │  /baoyu-youtube-transcript "youtube.com/watch?v=xxx"        │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 2: 文章撰写 + 翻译 (如外语视频)                       │
   │  /baoyu-translate 字幕文件.md --mode refined --to zh       │
   │  /baoyu-format-markdown 整理后的字幕.md                     │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 3: 配图 + 封面                                       │
   │  /baoyu-cover-image 文章.md                                 │
   │  /baoyu-article-illustrator 文章.md --type scene            │
   └────────────────────────────┬───────────────────────────────┘
                                 ↓
   ┌──────────────────────────────────────────────────────────────┐
   │  Step 4: 发布公众号                                         │
   │  /baoyu-markdown-to-html 文章-formatted.md --theme wechat   │
   │  /baoyu-post-to-wechat --title "视频解读" --content xxx.html │
   └──────────────────────────────────────────────────────────────┘
```

---

## 四、完整调用指令库

### 4.1 图像生成 (6个)

```bash
# 通用图像生成 (多API自动选择)
/baoyu-image-gen "prompt" [--aspect 1:1|16:9|2.35:1] [--style artistic|photo] [--provider openai|google|dashscope|jimeng|seedream]
# 示例
/baoyu-image-gen "科技感未来城市，霓虹灯光，赛博朋克风格"
/baoyu-image-gen "产品截图手机展示，简洁白色背景" --aspect 1:1

# 文章配图 (自动分析文章结构)
/baoyu-article-illustrator article.md
/baoyu-article-illustrator article.md --type infographic|scene|flowchart|comparison|framework|timeline
/baoyu-article-illustrator article.md --style notion|warm|minimal|blueprint|watercolor|elegant
/baoyu-article-illustrator article.md --preset tech-explainer  # 预设组合
# Type选项: infographic | scene | flowchart | comparison | framework | timeline
# Style选项: notion | warm | minimal | blueprint | watercolor | elegant | ... (20+)

# 封面图
/baoyu-cover-image article.md [--aspect 2.35:1|16:9|1:1]
/baoyu-cover-image article.md --style blueprint --mood mysterious
/baoyu-cover-image article.md --palette vibrant --rendering cinematic

# 信息图
/baoyu-infographic content.md [--layout mind-map|venn|funnel|pipeline|hierarchical-layers]
/baoyu-infographic content.md --style corporate-memphis|technical-schematic|ikea-manual|chalkboard
/baoyu-infographic content.md --lang zh|en --aspect 3:4|16:9
# 21种布局 × 20种视觉风格，可自由组合

# 知识漫画
/baoyu-comic "知识主题" --style classic|dramatic|realistic|sepia|shoujo|warm|wuxia|vibrant
/baoyu-comic "知识主题" --tone serious|humorous|inspirational
# 风格选项: classic | dramatic | realistic | sepia | shoujo | warm | wuxia | vibrant
# 基调选项: serious | humorous | inspirational

# 小红书连环图
/baoyu-xhs-images content.md [--style cute|fresh|minimal|notion|pop|retro|warm|bold|chalkboard]
/baoyu-xhs-images content.md [--layout balanced|comparison|dense|flow|list|sparse]
/baoyu-xhs-images content.md --count 6  # 生成6张
/baoyu-xhs-images content.md --publish   # 生成后直接发布
# 11种风格 × 8种版式，组合丰富
```

### 4.2 PPT / 幻灯片

```bash
/baoyu-slide-deck topic.md
/baoyu-slide-deck topic.md --slides 10
/baoyu-slide-deck topic.md --style minimal|blueprint|editorial|watercolor
# 自动生成大纲 → 逐张生成 → 输出完整幻灯片系列
```

### 4.3 内容发布 (4个)

```bash
# 微信公众号
/baoyu-post-to-wechat --title "标题" --content article.html
/baoyu-post-to-wechat --markdown article.md    # 自动转HTML
/baoyu-post-to-wechat --image-text --images img1.jpg,img2.jpg,img3.jpg
# 首次需要: 浏览器登录微信公众号后台 (Chrome CDP)

# 微博
/baoyu-post-to-weibo --text "微博正文（最多2000字）" --images img1.jpg,img2.jpg
/baoyu-post-to-weibo --article article.md  # 头条文章（长文）
# 首次需要: 浏览器登录微博

# X / Twitter
/baoyu-post-to-x --text "推文内容（最多280字）" --images img.jpg
/baoyu-post-to-x --article article.md  # X Articles 长文
# 首次需要: 浏览器登录 X

# 小红书 (生成+发布)
/baoyu-xhs-images content.md --style cute --layout balanced --publish
```

### 4.4 内容处理 (7个)

```bash
# 翻译
/baoyu-translate article.md --to zh|en|ja|ko|fr|es  # 快速翻译
/baoyu-translate article.md --mode refined  # 精细翻译(分析→翻译→审校→润色)
/baoyu-translate article.md --glossary terms.txt  # 带术语表翻译

# 网页转Markdown
/baoyu-url-to-markdown https://example.com/article
/baoyu-url-to-markdown https://example.com --wait-for-login  # 登录态页面

# YouTube字幕提取
/baoyu-youtube-transcript "youtube.com/watch?v=xxx"
/baoyu-youtube-transcript "xxx" --lang zh --translate-to en
/baoyu-youtube-transcript "xxx" --chapters  # 保留章节信息

# X推文转Markdown
/baoyu-danger-x-to-markdown https://x.com/user/status/123

# Markdown转HTML
/baoyu-markdown-to-html article.md
/baoyu-markdown-to-html article.md --theme wechat|github|minimal
/baoyu-markdown-to-html article.md --citations  # 外链转底部引用(微信友好)

# Markdown美化
/baoyu-format-markdown raw.md
# 输出: raw-formatted.md (添加frontmatter/标题/摘要/粗体/列表)

# 图片压缩
/baoyu-compress-image image.jpg
/baoyu-compress-image image.jpg --format webp|png --quality 80
```

---

## 五、与现有 Agent 的协作

### 5.1 协作矩阵

| 任务类型 | 主责 Agent | 协同 Agent | 协作内容 |
|---------|----------|-----------|---------|
| 竞品分析报告 | 运营顾问 | **内容运营专家** | 生成信息图 + 发布公众号/小红书 |
| 品牌升级方案 | 品牌顾问 | **内容运营专家** | 生成漫画 + 封面图 + 多平台发布 |
| 产品发布 | 产品顾问 | **内容运营专家** | 生成配图 + PPT + 公众号发布 |
| 技术分享 | 技术顾问 | **内容运营专家** | 提取视频字幕 + 整理文章 + 公众号发布 |
| 增长数据汇报 | 增长顾问 | **内容运营专家** | 生成数据可视化 + PPT + 微博发布 |

### 5.2 协作示例

```
CEO 分配: "分析竞品A的营销策略，输出报告并发布到小红书"

   运营顾问 (主责)
   │
   ├── 竞品数据收集
   ├── 竞品策略分析
   └── 输出: 竞品分析报告.md
              │
              ▼
        内容运营专家 (协同)
              │
   ┌──────────┼──────────┐
   ↓          ↓          ↓
信息图生成  小红书图   公众号配图
   │          │          │
   ↓          ↓          ↓
 发布小红书  发布小红书  发布公众号
```

---

## 六、前置配置清单

### 6.1 依赖安装

```bash
# 1. Bun 运行时
brew install oven-sh/bun/bun
# 或: /bin/bash -c "$(curl -fsSL https://bun.sh/install)"

# 2. Chrome (CDP技能需要)
/Applications/Google\ Chrome.app  # 确认已安装

# 3. 配置 BAOYU_SKILLS 环境变量
# baoyu-skills 需已安装 (通过 /plugin install baoyu-skills@baoyu-skills)

# 4. AI API Keys (至少一个)
# 方式A: OpenAI (推荐)
export OPENAI_API_KEY="sk-ant-..."

# 方式B: 阿里通义万象 (国内，推荐，便宜)
/export DASHSCOPE_API_KEY="sk-..."

# 方式C: 即梦AI (国内)
# /export JIMENG_API_KEY="sk-..."
```

### 6.2 平台登录配置

```bash
# 创建 Chrome Profile 目录
mkdir -p ~/.baoyu-chrome
export BAOYU_CHROME_PROFILE_DIR=~/.baoyu-chrome

# 首次使用各平台时:
# 1. baoyu-post-to-wechat → 打开Chrome扫码登录微信公众号后台
# 2. baoyu-post-to-weibo  → 打开Chrome扫码登录微博
# 3. baoyu-post-to-x      → 打开Chrome登录X/Twitter

# Chrome Profile 路径 (各平台共用):
# macOS: ~/Library/Application Support/Google/Chrome/
# Linux: ~/.config/google-chrome/
# Windows: %LOCALAPPDATA%\Google\Chrome\User Data\
```

---

## 七、Agent 文件结构

```
Output/CyberTeam-v2.1/
└── agents/
    └── experts/
        └── content-ops.md    ← 本Agent定义 (新建)

Plan/
└── 21-内容运营专家Agent集成方案.md  ← 本文档

baoyu-skills (外部依赖)
└── skills/
    ├── baoyu-image-gen/
    ├── baoyu-article-illustrator/
    ├── baoyu-cover-image/
    ├── baoyu-infographic/
    ├── baoyu-comic/
    ├── baoyu-slide-deck/
    ├── baoyu-xhs-images/
    ├── baoyu-post-to-weibo/
    ├── baoyu-post-to-wechat/
    ├── baoyu-post-to-x/
    ├── baoyu-translate/
    ├── baoyu-url-to-markdown/
    ├── baoyu-youtube-transcript/
    ├── baoyu-markdown-to-html/
    ├── baoyu-format-markdown/
    ├── baoyu-compress-image/
    └── baoyu-danger-gemini-web/
```

---

## 八、交付物清单

| 交付物 | 路径 | 状态 |
|--------|------|------|
| Agent定义文件 | `Output/CyberTeam-v2.1/agents/experts/content-ops.md` | ✅ 已完成 |
| 集成方案文档 | `Plan/21-内容运营专家Agent集成方案.md` | ✅ 已完成 |
| baoyu-skills集成方案 | `Plan/20-baoyu-skills集成方案.md` | ✅ 已完成 |
| Agent Prompt (嵌入CEO) | 已在Plan/04 CEO-Agent中增加专家调度规则 | ✅ 已完成 |
| 协作流程配置 | 已在Plan/11运营专家集成方案中更新路由 | ✅ 已完成 |
