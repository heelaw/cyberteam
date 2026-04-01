# 活动案例库使用指南

## 案例库结构

```
activity-operations/
├── references/
│   └── cases/                          # 案例文档（会被Claude读取）
│       ├── case_template.md            # 案例模板
│       ├── coffee_shop_luxi_202501.md  # 具体案例（Markdown）
│       └── ...
└── assets/
    └── cases/                          # 案例素材（供输出时引用）
        ├── coffee_shop_luxi_202501/    # 按案例组织
        │   ├── poster.png              # 海报
        │   ├── report.pdf              # PDF报告
        │   ├── data.xlsx               # 数据表格
        │   └── photos/                 # 活动照片
        └── case_assets_guide.md        # 本文档
```

## 案例文件存放规则

### 1. references/cases/ - 案例文档

**用途**：存放Markdown格式的案例核心内容，会被Claude读取到context中

**文件类型**：仅限 `.md` 文件

**命名规范**：
```
[业务类型]_[地点/特征]_[YYYYMMDD].md

示例：
- coffee_shop_luxi_20250109.md    (洛溪咖啡厅案例)
- ecommerce_double11_20241111.md  (双11电商案例)
- community_newyear_20250101.md   (社群新年案例)
```

**内容要求**：
- 使用 `case_template.md` 作为模板
- 提取案例核心信息和洞察
- 避免大段复制粘贴原始文档

### 2. assets/cases/ - 案例素材

**用途**：存放PDF、图片、设计稿等素材文件

**文件类型**：支持任意格式（PDF、PNG、JPG、DOCX、XLSX等）

**组织方式**：
```
assets/cases/
├── [案例文件夹]/
│   ├── 📄 report.pdf              # 活动报告
│   ├── 🖼️ poster.png              # 海报设计
│   ├── 📊 data.xlsx               # 原始数据
│   ├── 📸 photos/                 # 活动照片
│   │   ├── img001.jpg
│   │   └── img002.jpg
│   └── 📝 sop.pdf                 # 执行SOP
```

## PDF文档处理方案

### 推荐做法：双轨制

```
原始PDF → assets/cases/[案例名]/report.pdf
    ↓
提取核心内容 → references/cases/[案例名].md
```

### 处理流程

**Step 1: 存放原始PDF**

将完整的PDF报告存放到 `assets/cases/`：

```
assets/cases/coffee_shop_luxi_202501/
├── original_report.pdf      # 原始PDF报告
└── poster.pdf              # 海报PDF
```

**Step 2: 提取关键信息到Markdown**

创建对应的Markdown文件在 `references/cases/`：

```markdown
# 活动案例：洛溪咖啡厅咖啡日记活动

## 一、背景与目标
[从PDF中提取关键信息]

## 二、活动方案设计
[从PDF中提取关键信息]

...

## 七、附件索引
| 附件名称 | 类型 | 路径 |
|---------|------|------|
| 活动报告 | PDF | assets/cases/coffee_shop_luxi_202501/original_report.pdf |
| 海报设计 | PDF | assets/cases/coffee_shop_luxi_202501/poster.pdf |
```

**Step 3: Claude如何使用**

- **Markdown文件**：会被自动读取，Claude可以了解案例内容
- **PDF文件**：当Claude需要引用时，会读取PDF内容

### PDF处理示例

假设你有一份PDF活动报告：

```bash
# 原始PDF位置
assets/cases/coffee_shop_luxi_202501/activity_report.pdf

# 对应的Markdown文件
references/cases/coffee_shop_luxi_202501.md
```

在Markdown中引用PDF：

```markdown
## 七、附件索引

| 附件名称 | 类型 | 路径 | 说明 |
|---------|------|------|------|
| 完整活动报告 | PDF | assets/cases/coffee_shop_luxi_202501/activity_report.pdf | 包含详细数据分析和复盘 |
| 海报设计稿 | PDF | assets/cases/coffee_shop_luxi_202501/poster.pdf | 活动海报源文件 |
```

## 新增案例流程

### 方法1: 从零创建案例

```bash
# 1. 复制模板
cp references/cases/case_template.md references/cases/[新案例名].md

# 2. 创建素材文件夹
mkdir -p assets/cases/[新案例名]/

# 3. 填写案例内容
# 编辑 references/cases/[新案例名].md

# 4. 整理素材文件
# 将PDF、图片等放入 assets/cases/[新案例名]/
```

### 方法2: 从现有PDF创建案例

```bash
# 1. 存放PDF
cp [原始PDF路径] assets/cases/[案例名]/report.pdf

# 2. 创建Markdown摘要
cp references/cases/case_template.md references/cases/[案例名].md

# 3. 从PDF提取关键信息填入Markdown
# （可使用PDF阅读工具或手动提取）

# 4. 在Markdown的"附件索引"部分引用PDF路径
```

## PDF内容提取建议

### 需要提取到Markdown的内容

✅ **必须提取**：
- 活动目标和实际结果
- 核心玩法和机制
- 数据和转化率
- 成功经验和失败教训
- 可复用的洞察

❌ **无需提取**（保留在PDF中）：
- 大段原始数据表格
- 设计稿细节描述
- 详细的执行日志
- 大量截图和图片

### Claude如何处理PDF

当Claude需要查看PDF时：
1. 会先读取Markdown了解案例概况
2. 需要详细信息时，会读取对应的PDF文件
3. 可以下载PDF文件作为参考或输出

## 案例检索

### 按标签检索

在Markdown案例文件中添加标签：

```markdown
## 案例标签

**行业**：餐饮/电商/SaaS/教育/社群
**类型**：拉新/促活/转化/复购/品牌
**场景**：线上/线下/OMO
**渠道**：微信/抖音/小红书/社群
**结果**：成功案例/失败案例/混合案例

**业务标签**：#咖啡厅 #社区营销 #小红书种草 #免单活动
```

### 案例关联

在案例中添加相关案例链接：

```markdown
## 八、相关案例

- [咖啡厅春节活动](references/cases/coffee_spring_202502.md) - 同一店铺的后续活动
- [小红书种草案例合集](references/cases/xiaohongshu_cases.md) - 小红书营销案例
```

## 案例质量控制

### 案例完整性检查清单

- [ ] 活动目标清晰，有具体数值
- [ ] 玩法机制描述完整
- [ ] 有真实数据（目标vs实际）
- [ ] 有复盘和经验总结
- [ ] 有核心洞察提炼
- [ ] 附件路径正确可访问
- [ ] 案例标签完整

### 案例更新

当活动有后续进展或新数据时：

```bash
# 1. 更新Markdown文件
vim references/cases/[案例名].md

# 2. 添加新版PDF（如有）
cp [新报告] assets/cases/[案例名]/report_v2.pdf

# 3. 在Markdown中添加版本说明
## 更新记录
- v1.0 (2025-01-09): 初始版本
- v2.0 (2025-02-01): 增加1月后续数据
```

## 常见问题

### Q: PDF太大怎么办？

A: 建议：
1. 压缩PDF（使用 Adobe Acrobat 或在线工具）
2. 拆分PDF（主报告+附件）
3. 提取关键内容到Markdown，PDF仅作为存档

### Q: 如何从图片中提取文字？

A: 使用OCR工具：
- 在线：[OCR工具推荐]
- 本地：Tesseract、Adobe Acrobat
- 提取后整理到Markdown

### Q: 案例多久更新一次？

A: 建议：
- 活动进行中：每周更新数据
- 活动结束后：1周内完成复盘
- 长期跟踪：每月更新后续数据
