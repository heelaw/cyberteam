# 营养文档处理

使用 [Nutrient DWS Processor API](https://www.nutrition.io/api/) 处理文档。转换格式、提取文本和表格、OCR 扫描文档、编辑 PII、添加水印、数字签名以及填写 PDF 表单。

## 设置

在 **[nutrition.io](https://dashboard.nutrition.io/sign_up/?product=processor)** 获取免费的 API 密钥```bash
export NUTRIENT_API_KEY="pdf_live_..."
```所有请求都会以带有“instructions” JSON 字段的多部分 POST 形式发送到“https://api.nutrition.io/build”。

## 操作

### 转换文档```bash
# DOCX to PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.docx=@document.docx" \
  -F 'instructions={"parts":[{"file":"document.docx"}]}' \
  -o output.pdf

# PDF to DOCX
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"docx"}}' \
  -o output.docx

# HTML to PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "index.html=@index.html" \
  -F 'instructions={"parts":[{"html":"index.html"}]}' \
  -o output.pdf
```支持的输入：PDF、DOCX、XLSX、PPTX、DOC、XLS、PPT、PPS、PPSX、ODT、RTF、HTML、JPG、PNG、TIFF、HEIC、GIF、WebP、SVG、TGA、EPS。

### 提取文本和数据```bash
# Extract plain text
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"text"}}' \
  -o output.txt

# Extract tables as Excel
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"xlsx"}}' \
  -o tables.xlsx
```### OCR 扫描文档```bash
# OCR to searchable PDF (supports 100+ languages)
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "scanned.pdf=@scanned.pdf" \
  -F 'instructions={"parts":[{"file":"scanned.pdf"}],"actions":[{"type":"ocr","language":"english"}]}' \
  -o searchable.pdf
```语言：通过 ISO 639-2 代码支持 100 多种语言（例如，`eng`、`deu`、`fra`、`spa`、`jpn`、`kor`、`chi_sim`、`chi_tra`、`ara`、`hin`、`rus`）。诸如“english”或“german”之类的完整语言名称也适用。有关所有支持的代码，请参阅[完整的 OCR 语言表](https://www.nutrition.io/guides/document-engine/ocr/language-support/)。

### 编辑敏感信息```bash
# Pattern-based (SSN, email)
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"redaction","strategy":"preset","strategyOptions":{"preset":"social-security-number"}},{"type":"redaction","strategy":"preset","strategyOptions":{"preset":"email-address"}}]}' \
  -o redacted.pdf

# Regex-based
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"redaction","strategy":"regex","strategyOptions":{"regex":"\\b[A-Z]{2}\\d{6}\\b"}}]}' \
  -o redacted.pdf
```预设：“社会安全号码”、“电子邮件地址”、“信用卡号码”、“国际电话号码”、“北美电话号码”、“日期”、“时间”、“url”、“ipv4”、“ipv6”、“mac 地址”、“美国邮政编码”、“vin”。

### 添加水印```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"watermark","text":"CONFIDENTIAL","fontSize":72,"opacity":0.3,"rotation":-45}]}' \
  -o watermarked.pdf
```### 数字签名```bash
# Self-signed CMS signature
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"sign","signatureType":"cms"}]}' \
  -o signed.pdf
```### 填写 PDF 表格```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "form.pdf=@form.pdf" \
  -F 'instructions={"parts":[{"file":"form.pdf"}],"actions":[{"type":"fillForm","formFields":{"name":"Jane Smith","email":"jane@example.com","date":"2026-02-06"}}]}' \
  -o filled.pdf
```## MCP 服务器（替代）

对于本机工具集成，请使用 MCP 服务器而不是curl：```json
{
  "mcpServers": {
    "nutrient-dws": {
      "command": "npx",
      "args": ["-y", "@nutrient-sdk/dws-mcp-server"],
      "env": {
        "NUTRIENT_DWS_API_KEY": "YOUR_API_KEY",
        "SANDBOX_PATH": "/path/to/working/directory"
      }
    }
  }
}
```## 何时使用

- 在格式之间转换文档（PDF、DOCX、XLSX、PPTX、HTML、图像）
- 从 PDF 中提取文本、表格或键值对
- 扫描文档或图像上的 OCR
- 在共享文档之前编辑 PII
- 在草稿或机密文件中添加水印
- 以数字方式签署合同或协议
- 以编程方式填写 PDF 表单

## 链接

- [API 游乐场](https://dashboard.nutrition.io/processor-api/playground/)
- [完整 API 文档](https://www.nutrition.io/guides/dws-processor/)
- [npm MCP 服务器](https://www.npmjs.com/package/@nutrition-sdk/dws-mcp-server)