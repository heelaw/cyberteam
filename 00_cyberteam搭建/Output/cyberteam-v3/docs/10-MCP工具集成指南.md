# MCP 工具集成指南

> **版本**: v3.1 | **创建日期**: 2026-03-24 | **更新日期**: 2026-03-24 | **定位**: MCP 工具调用手册
>
> 本文档定义了 MiniMax、Filesystem、WebReader 等 MCP 工具的集成方式、调用协议、使用场景。
>
> **v3.1 更新**: 整合到基础设施层，明确调用优先级。

---

## 目录

1. [MCP 工具概述](#一mcp-工具概述)
2. [工具分类与清单](#二工具分类与清单)
3. [调用机制](#三调用机制)
4. [使用场景](#四使用场景)
5. [集成协议](#五集成协议)
6. [最佳实践](#六最佳实践)

---

## 一、MCP 工具概述

### 1.1 什么是 MCP

```yaml
定义:
  MCP (Model Context Protocol) 是一个工具协议，
  允许 LLM 访问外部工具和数据源。

核心价值:
  - 扩展能力: LLM 可以调用外部工具
  - 实时数据: 访问最新信息
  - 文件操作: 读写本地文件
  - 图像分析: 理解图片内容

已集成工具:
  - MiniMax MCP: 网络搜索、图像分析
  - Filesystem MCP: 文件系统操作
  - WebReader MCP: 网页内容读取
```

### 1.2 架构定位

```
┌─────────────────────────────────────────────────────────────┐
│                    CyberTeam v3 架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  所有部门 (使用者)                                           │
│    ↓                                                        │
│  MCP 工具层                                                 │
│    ├── MiniMax MCP                                         │
│    │   ├── web_search: 网络搜索                            │
│    │   └── understand_image: 图像分析                      │
│    ├── Filesystem MCP                                      │
│    │   ├── read_text_file: 读文件                          │
│    │   ├── write_file: 写文件                              │
│    │   ├── directory_tree: 目录树                          │
│    │   └── ... (更多)                                      │
│    └── WebReader MCP                                       │
│        └── webReader: 网页内容读取                         │
│    ↓                                                        │
│  返回结果给部门                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 工具清单

| 工具 | 功能 | 主要用途 |
|------|------|----------|
| **MiniMax web_search** | 网络搜索 | 搜索最新信息、实时数据 |
| **MiniMax understand_image** | 图像分析 | 分析图片内容、提取信息 |
| **Filesystem read_text_file** | 读文件 | 读取文本文件内容 |
| **Filesystem write_file** | 写文件 | 写入文件内容 |
| **Filesystem directory_tree** | 目录树 | 获取目录结构 |
| **Filesystem list_directory** | 列目录 | 列出目录内容 |
| **WebReader webReader** | 网页读取 | 读取网页内容并转换 |

---

## 二、工具分类与清单

### 2.1 MiniMax MCP

#### mcp__MiniMax__web_search

```yaml
功能: 网络搜索

调用格式:
  mcp__MiniMax__web_search(query="搜索关键词")

参数:
  - query: 搜索关键词 (必需)

返回格式:
  {
    "organic": [
      {
        "title": "结果标题",
        "link": "结果链接",
        "snippet": "结果摘要",
        "date": "日期"
      }
    ],
    "related_searches": [
      {
        "query": "相关搜索"
      }
    ]
  }

使用场景:
  - 搜索最新信息
  - 查询实时数据
  - 研究市场趋势
  - 竞品分析

注意事项:
  - 搜索关键词要简洁明确
  - 使用3-5个关键词效果最佳
  - 可以指定年份获取最新信息

示例:
  # 搜索 2026 年 AI 发展趋势
  mcp__MiniMax__web_search(query="2026年 AI 发展趋势")

  # 搜索小红书运营技巧
  mcp__MiniMax__web_search(query="小红书运营技巧 2026")
```

#### mcp__MiniMax__understand_image

```yaml
功能: 图像分析

调用格式:
  mcp__MiniMax__understand_image(
    prompt="分析提示",
    image_source="图片路径或URL"
  )

参数:
  - prompt: 分析提示 (必需)
  - image_source: 图片路径 (必需)
    - 支持本地路径: "/path/to/image.png"
    - 支持 HTTP URL: "https://example.com/image.jpg"

返回格式:
  {
    "description": "图片描述",
    "analysis": "详细分析",
    "key_elements": ["关键元素1", "关键元素2"]
  }

使用场景:
  - 分析封面图
  - 提取图片信息
  - 审核图片内容
  - 生成图片描述

注意事项:
  - 支持格式: JPEG, PNG, WebP
  - 文件路径需要是绝对路径
  - URL 需要是完整的 HTTP/HTTPS 地址

示例:
  # 分析封面图
  mcp__MiniMax__understand_image(
    prompt="分析这张封面图的设计风格和主要内容",
    image_source="/path/to/cover.jpg"
  )

  # 分析产品图
  mcp__MiniMax__understand_image(
    prompt="描述这个产品的外观和特点",
    image_source="https://example.com/product.jpg"
  )
```

### 2.2 Filesystem MCP

#### mcp__filesystem__read_text_file

```yaml
功能: 读取文本文件

调用格式:
  mcp__filesystem__read_text_file(path="/path/to/file.md")

参数:
  - path: 文件路径 (必需)
  - head: 返回前N行 (可选)
  - tail: 返回后N行 (可选)

返回格式:
  {
    "content": "文件内容",
    "line_count": 行数,
    "encoding": "编码"
  }

使用场景:
  - 读取配置文件
  - 读取文档内容
  - 读取代码文件
  - 读取数据文件

注意事项:
  - 路径可以是相对路径或绝对路径
  - 大文件建议使用 head/tail 参数
  - 二进制文件请用 read_file

示例:
  # 读取整个文件
  mcp__filesystem__read_text_file(path="README.md")

  # 读取前50行
  mcp__filesystem__read_text_file(path="README.md", head=50)
```

#### mcp__filesystem__write_file

```yaml
功能: 写入文件

调用格式:
  mcp__filesystem__write_file(
    path="/path/to/file.md",
    content="文件内容"
  )

参数:
  - path: 文件路径 (必需)
  - content: 文件内容 (必需)

返回格式:
  {
    "success": true,
    "path": "/path/to/file.md",
    "bytes_written": 字节数
  }

使用场景:
  - 创建文档
  - 保存配置
  - 导出数据
  - 生成报告

注意事项:
  - 如果文件存在会被覆盖
  - 目录不存在会自动创建
  - 内容必须是文本格式

示例:
  # 创建 Markdown 文档
  mcp__filesystem__write_file(
    path="output/report.md",
    content="# 报告\n\n内容..."
  )
```

#### mcp__filesystem__directory_tree

```yaml
功能: 获取目录树

调用格式:
  mcp__filesystem__directory_tree(path="/path/to/dir")

参数:
  - path: 目录路径 (必需)
  - excludePatterns: 排除模式 (可选)

返回格式:
  {
    "name": "目录名",
    "type": "directory",
    "children": [
      {
        "name": "文件名",
        "type": "file"
      }
    ]
  }

使用场景:
  - 了解项目结构
  - 查找文件
  - 分析目录组织
  - 生成文档索引

注意事项:
  - 大目录可能返回较多数据
  - 可以使用 excludePatterns 过滤

示例:
  # 查看项目结构
  mcp__filesystem__directory_tree(path=".")

  # 排除 node_modules
  mcp__filesystem__directory_tree(
    path=".",
    excludePatterns=["node_modules", ".git"]
  )
```

#### mcp__filesystem__list_directory

```yaml
功能: 列出目录内容

调用格式:
  mcp__filesystem__list_directory(path="/path/to/dir")

参数:
  - path: 目录路径 (必需)

返回格式:
  {
    "items": [
      {
        "name": "文件名",
        "type": "file|directory"
      }
    ]
  }

使用场景:
  - 查看目录内容
  - 列出文件清单
  - 检查文件是否存在

示例:
  # 列出当前目录
  mcp__filesystem__list_directory(path=".")
```

### 2.3 WebReader MCP

#### mcp__web_reader__webReader

```yaml
功能: 读取网页内容并转换为 Markdown

调用格式:
  mcp__web_reader__webReader(url="https://example.com")

参数:
  - url: 网页URL (必需)
  - return_format: 返回格式 (可选，markdown|text)
  - retain_images: 保留图片 (可选，true|false)

返回格式:
  {
    "title": "网页标题",
    "content": "Markdown内容",
    "images": ["图片URL列表"],
    "links": ["链接列表"]
  }

使用场景:
  - 获取文章内容
  - 爬取网页数据
  - 提取网页信息
  - 生成文档

注意事项:
  - 需要完整的 URL
  - 某些网站可能禁止爬取
  - 建议设置合理的超时时间

示例:
  # 读取文章
  mcp__web_reader__webReader(
    url="https://example.com/article"
  )

  # 不保留图片
  mcp__web_reader__webReader(
    url="https://example.com/article",
    retain_images=false
  )
```

---

## 三、调用机制

### 3.1 调用方式

#### 方式1: 直接调用

```yaml
调用格式:
  mcp__{tool_name}__{function_name}(参数)

示例:
  mcp__MiniMax__web_search(query="搜索关键词")
  mcp__filesystem__read_text_file(path="file.md")
  mcp__web_reader__webReader(url="https://example.com")

执行流程:
  1. Agent 决策调用工具
  2. 执行工具调用
  3. 获取返回结果
  4. 处理结果
  5. 返回给用户
```

#### 方式2: 通过 Agent 调用

```yaml
调用流程:
  1. 用户请求
  2. CEO 路由到部门
  3. 部门 Agent 决策调用 MCP 工具
  4. 执行工具调用
  5. 处理结果
  6. 返回给用户

示例:
  用户: "搜索最新的 AI 写作工具"
  → CEO 路由到数据分析部
  → 数据分析部调用 mcp__MiniMax__web_search
  → 处理搜索结果
  → 返回分析报告
```

#### 方式3: 批量调用

```yaml
批量场景:
  - 搜索多个关键词
  - 读取多个文件
  - 分析多个图片

调用方式:
  并行执行多个工具调用

示例:
  并行:
    - mcp__MiniMax__web_search(query="AI写作工具")
    - mcp__MiniMax__web_search(query="AI内容生成")
    - mcp__MiniMax__web_search(query="AI文案工具")

  输出: 综合搜索结果
```

### 3.2 调用协议

```yaml
输入格式:
  {
    "tool": "mcp__MiniMax__web_search",
    "function": "web_search",
    "params": {
      "query": "搜索关键词"
    }
  }

输出格式:
  {
    "tool": "mcp__MiniMax__web_search",
    "status": "success",
    "result": {...},
    "error": null
  }

错误处理:
  if 调用失败:
    - 记录错误日志
    - 返回错误信息
    - 降级到备用方案
    - 通知用户
```

### 3.3 优先级配置

```yaml
优先级规则 (来自 CLAUDE.md):

网络搜索:
  任务: 搜索网络信息
  工具: MiniMax MCP web_search ✅
  禁用: WebSearch 工具 ❌

图像分析:
  任务: 分析图片内容
  工具: MiniMax MCP understand_image ✅
  禁用: 其他图像分析工具 ❌

原因:
  - MiniMax 提供更好的中文支持
  - MiniMax 结果更准确
  - 统一使用 MiniMax 便于管理
```

---

## 四、使用场景

### 4.1 数据分析场景

```yaml
场景: 市场调研

流程:
  Step 1: 使用 web_search 搜索市场信息
  Step 2: 使用 webReader 读取相关文章
  Step 3: 使用 read_text_file 读取历史数据
  Step 4: 分析整合数据
  Step 5: 生成调研报告

调用序列:
  mcp__MiniMax__web_search(query="2026年 AI 写作工具市场")
  mcp__web_reader__webReader(url="https://example.com/article")
  mcp__filesystem__read_text_file(path="data/历史数据.csv")

预期产出:
  - 市场调研报告
  - 竞品分析
  - 趋势预测
```

### 4.2 内容创作场景

```yaml
场景: 创作基于研究的内容

流程:
  Step 1: 使用 web_search 研究主题
  Step 2: 使用 webReader 读取参考资料
  Step 3: 提取关键信息
  Step 4: 创作内容
  Step 5: 使用 write_file 保存内容

调用序列:
  mcp__MiniMax__web_search(query="AI写作工具应用场景")
  mcp__web_reader__webReader(url="https://example.com/guide")
  → 创作内容
  mcp__filesystem__write_file(path="output/article.md")

预期产出:
  - 研究笔记
  - 创作内容
  - 参考资料
```

### 4.3 图片处理场景

```yaml
场景: 分析并处理图片

流程:
  Step 1: 使用 understand_image 分析图片
  Step 2: 提取图片信息
  Step 3: 根据分析结果处理
  Step 4: 生成处理报告

调用序列:
  mcp__MiniMax__understand_image(
    prompt="分析这张封面图的设计风格、色彩、布局",
    image_source="/path/to/cover.jpg"
  )

预期产出:
  - 图片分析报告
  - 设计建议
  - 优化方向
```

### 4.4 文档管理场景

```yaml
场景: 文档整理与归档

流程:
  Step 1: 使用 directory_tree 查看目录结构
  Step 2: 使用 list_directory 列出文件
  Step 3: 使用 read_text_file 读取文件
  Step 4: 整理分类
  Step 5: 使用 write_file 保存索引

调用序列:
  mcp__filesystem__directory_tree(path="docs/")
  mcp__filesystem__list_directory(path="docs/")
  mcp__filesystem__read_text_file(path="docs/article.md")
  → 整理
  mcp__filesystem__write_file(path="docs/index.md")

预期产出:
  - 目录结构图
  - 文件清单
  - 分类索引
```

---

## 五、集成协议

### 5.1 与各部门集成

```yaml
数据分析部:
  主要使用:
    - web_search: 搜索市场信息
    - webReader: 读取研究报告
    - read_text_file: 读取数据文件

内容运营部:
  主要使用:
    - web_search: 搜索热点话题
    - understand_image: 分析图片
    - write_file: 保存内容

技术研发部:
  主要使用:
    - read_text_file: 读取代码
    - write_file: 写入代码
    - directory_tree: 查看项目结构

安全合规部:
  主要使用:
    - read_text_file: 读取配置
    - directory_tree: 扫描文件
    - web_search: 查询安全信息
```

### 5.2 调用权限

```yaml
权限级别:
  L1 (CEO):
    - 所有工具只读权限

  L2 (PM/Strategy):
    - web_search: 完全权限
    - webReader: 完全权限
    - read_text_file: 完全权限
    - write_file: 受限权限 (只能写输出目录)

  L3 (部门):
    - web_search: 完全权限
    - webReader: 完全权限
    - read_text_file: 完全权限
    - write_file: 完全权限 (部门目录)
    - directory_tree: 完全权限
```

### 5.3 错误处理

```yaml
错误类型:
  1. 参数错误
  2. 文件不存在
  3. 网络错误
  4. 权限错误
  5. 超时错误

处理策略:
  1. 参数错误
     - 返回参数说明
     - 提供正确示例
     - 重新调用

  2. 文件不存在
     - 检查文件路径
     - 尝试备用路径
     - 返回错误信息

  3. 网络错误
     - 重试 3 次
     - 记录错误日志
     - 降级到缓存

  4. 权限错误
     - 检查权限配置
     - 请求权限升级
     - 通知用户

  5. 超时错误
     - 增加超时时间
     - 重试调用
     - 降级处理
```

---

## 六、最佳实践

### 6.1 搜索技巧

```yaml
最佳实践:
  1. 关键词选择
     - 使用3-5个关键词
     - 包含时间限定 (如 2026)
     - 使用具体术语

  2. 结果筛选
     - 查看标题和摘要
     - 优先选择权威来源
     - 注意发布时间

  3. 信息验证
     - 多源对比
     - 交叉验证
     - 更新信息
```

### 6.2 文件操作

```yaml
最佳实践:
  1. 路径规范
     - 使用绝对路径
     - 规范文件命名
     - 统一目录结构

  2. 大文件处理
     - 使用 head/tail 参数
     - 分段读取
     - 流式处理

  3. 安全写入
     - 先备份再写入
     - 使用临时文件
     - 原子操作
```

### 6.3 图片处理

```yaml
最佳实践:
  1. 图片分析
     - 提供清晰的提示
     - 指定分析维度
     - 关注关键信息

  2. 图片路径
     - 使用绝对路径
     - 检查文件存在
     - 验证格式支持

  3. 结果验证
     - 检查分析准确性
     - 补充遗漏信息
     - 人工审核关键点
```

### 6.4 网页读取

```yaml
最佳实践:
  1. URL 规范
     - 使用完整 URL
     - 包含协议 (http/https)
     - 验证 URL 有效性

  2. 内容处理
     - 选择合适格式
     - 处理图片链接
     - 清理无用信息

  3. 遵守规则
     - 遵守 robots.txt
     - 设置合理频率
     - 尊重版权
```

---

## 七、附录

### 7.1 工具速查表

| 工具 | 功能 | 主要参数 |
|------|------|----------|
| MiniMax web_search | 网络搜索 | query |
| MiniMax understand_image | 图像分析 | prompt, image_source |
| Filesystem read_text_file | 读文件 | path, head, tail |
| Filesystem write_file | 写文件 | path, content |
| Filesystem directory_tree | 目录树 | path, excludePatterns |
| Filesystem list_directory | 列目录 | path |
| WebReader webReader | 网页读取 | url, return_format, retain_images |

### 7.2 相关文档

- [00-分层集成架构设计.md](./00-分层集成架构设计.md)
- [01-公司架构与人员配置.md](./01-公司架构与人员配置.md)
- [07-用户执行指南.md](./07-用户执行指南.md)

---

**文档版本**: v3.1
**创建日期**: 2026-03-24
**最后更新**: 2026-03-24

---

*本文档定义了 MiniMax、Filesystem、WebReader 等 MCP 工具的集成方式、调用协议、使用场景。*
