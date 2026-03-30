# Gstack Skills Workflow

> **版本**: v3.1
> **更新日期**: 2026-03-24

---

## 目录结构

```
workflow/
├── 01-feature-development/  # 功能开发案例
├── 02-code-review/          # 代码审查案例
├── 03-qa-testing/           # QA 测试案例
└── 04-deployment/          # 部署发布案例
```

---

## 案例格式

每个案例应包含以下文件:

```
{case-name}/
├── input.md              # 需求描述
├── code/                 # 代码文件
│   ├── before/          # 修改前
│   └── after/           # 修改后
├── review.md            # 审查报告
├── test-results.md      # 测试结果
└── deployment.md       # 部署记录
```

---

## 贡献指南

### 添加新案例

1. 创建案例目录:
   ```bash
   mkdir -p workflow/{category}/{case-name}
   mkdir -p workflow/{category}/{case-name}/code/{before,after}
   ```

2. 创建案例文件:
   - input.md: 描述开发需求
   - code/before/: 修改前的代码
   - code/after/: 修改后的代码
   - review.md: 代码审查报告
   - test-results.md: 测试结果
   - deployment.md: 部署记录

3. 更新索引

---

## 案例索引

### 01-feature-development (功能开发)

| 案例 | 使用的技能 | 日期 |
|------|-----------|------|
| 待添加 | - | - |

### 02-code-review (代码审查)

| 案例 | 审查维度 | 日期 |
|------|---------|------|
| 待添加 | - | - |

### 03-qa-testing (QA 测试)

| 案例 | 测试类型 | 日期 |
|------|---------|------|
| 待添加 | - | - |

### 04-deployment (部署发布)

| 案例 | 部署平台 | 日期 |
|------|---------|------|
| 待添加 | - | - |
