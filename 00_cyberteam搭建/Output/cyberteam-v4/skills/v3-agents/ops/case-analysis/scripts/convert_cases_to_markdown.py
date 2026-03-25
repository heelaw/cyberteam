#!/usr/bin/env python3
"""
运营案例批量转换脚本
将PDF和DOCX格式的案例转换为markdown，并按类型分类存储
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 案例分类映射（基于之前的分析）
CASE_CATEGORIES = {
    # 私域运营类
    '007': 'private_domain', '008': 'private_domain', '009': 'private_domain',
    '010': 'private_domain', '013': 'private_domain', '014': 'private_domain',
    '015': 'private_domain', '016': 'private_domain', '022': 'private_domain',
    '026': 'private_domain', '028': 'private_domain', '030': 'private_domain',
    '034': 'private_domain', '055': 'private_domain', '069': 'private_domain',

    # 用户增长类
    '011': 'user_growth', '012': 'user_growth', '044': 'user_growth',

    # 品牌营销类
    '035': 'brand_marketing', '048': 'brand_marketing', '053': 'brand_marketing',
    '056': 'brand_marketing', '063': 'brand_marketing', '065': 'brand_marketing',
    '071': 'brand_marketing', '072': 'brand_marketing', '077': 'brand_marketing',
    '078': 'brand_marketing',

    # 联名营销类
    '050': 'collaboration',

    # 产品运营类
    '024': 'product', '025': 'product', '027': 'product', '038': 'product',
    '043': 'product', '046': 'product',

    # 内容营销类
    '032': 'content', '052': 'content',

    # 活动策划类
    '058': 'activity',

    # 其他
    '073': 'other', '074': 'other', '075': 'other', '076': 'other'
}

# 中文名称映射
CATEGORY_NAMES = {
    'private_domain': '私域运营',
    'user_growth': '用户增长',
    'brand_marketing': '品牌营销',
    'collaboration': '联名营销',
    'product': '产品运营',
    'content': '内容营销',
    'activity': '活动策划',
    'other': '其他'
}

# 源文件夹
SOURCE_DIR = "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/02 领域（Area)/2.0_运营领域/6.0_运营skill/【运营案例拆解】"

# 目标文件夹
TARGET_DIR = "/Users/cyberwiz/Documents/trae_projects/Claude code/operation-case-analyzer/cases"


def extract_case_number(filename):
    """从文件名中提取案例编号"""
    for prefix in filename.split()[:3]:  # 检查前几个词
        if prefix.isdigit():
            return prefix
    return None


def categorize_case(filename):
    """根据文件名判断案例类型"""
    case_num = extract_case_number(filename)
    if case_num and case_num in CASE_CATEGORIES:
        return CASE_CATEGORIES[case_num]

    # 如果编号不在映射中，尝试根据关键词判断
    name_lower = filename.lower()
    if '私域' in name_lower or '社群' in name_lower:
        return 'private_domain'
    elif '增长' in name_lower or '拉新' in name_lower:
        return 'user_growth'
    elif '营销' in name_lower or '品牌' in name_lower or '爆火' in name_lower:
        return 'brand_marketing'
    elif '联名' in name_lower:
        return 'collaboration'
    elif '活动' in name_lower:
        return 'activity'
    elif '内容' in name_lower:
        return 'content'
    else:
        return 'product'  # 默认归为产品运营


def convert_pdf_to_text(pdf_path):
    """转换PDF为文本"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text
    except Exception as e:
        print(f"PDF转换错误 {pdf_path}: {e}")
        return None


def convert_docx_to_text(docx_path):
    """转换DOCX为文本"""
    try:
        from docx import Document
        doc = Document(docx_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n\n"
        return text
    except ImportError:
        print("需要安装 python-docx: pip install python-docx")
        return None
    except Exception as e:
        print(f"DOCX转换错误 {docx_path}: {e}")
        return None


def text_to_markdown(text, filename):
    """将文本转换为结构化的markdown"""
    lines = text.split('\n')
    markdown_lines = []
    markdown_lines.append(f"# {filename}\n\n")
    markdown_lines.append(f"> 转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    markdown_lines.append("---\n\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测标题（数字开头或全大写）
        if line[0].isdigit() and ('、' in line or '.' in line):
            # 是一个标题
            level = 0
            for char in line:
                if char.isdigit():
                    level += 1
                else:
                    break

            # 提取标题内容
            content = line.split('、')[-1].split('.')[-1].strip()
            if level == 1:
                markdown_lines.append(f"\n## {content}\n\n")
            elif level == 2:
                markdown_lines.append(f"\n### {content}\n\n")
            else:
                markdown_lines.append(f"\n#### {content}\n\n")
        elif len(line) < 50 and line.isupper():
            # 可能是小节标题
            markdown_lines.append(f"\n### {line}\n\n")
        else:
            markdown_lines.append(line + "\n")

    return ''.join(markdown_lines)


def create_directory_structure():
    """创建目录结构"""
    categories = set(CASE_CATEGORIES.values()) | {'other'}

    for cat in categories:
        cat_dir = os.path.join(TARGET_DIR, cat)
        os.makedirs(cat_dir, exist_ok=True)
        print(f"✅ 创建目录: {cat} ({CATEGORY_NAMES.get(cat, cat)})")


def create_readme():
    """创建案例库README"""
    readme_content = """# 运营案例库

本目录包含85+运营案例的markdown版本，按类型分类存储。

## 目录结构

"""

    for cat_key, cat_name in CATEGORY_NAMES.items():
        cat_dir = os.path.join(TARGET_DIR, cat_key)
        if os.path.exists(cat_dir):
            files = [f for f in os.listdir(cat_dir) if f.endswith('.md')]
            readme_content += f"### {cat_name} ({len(files)}个案例)\n\n"
            readme_content += f"路径: `./{cat_key}/`\n\n"

    readme_content += """
## 使用说明

1. 按类型浏览：进入对应的分类文件夹
2. 按编号查找：案例文件名包含原始编号
3. 详细索引：查看 `../references/case_index.md`

## 转换信息

- 转换时间：{}
- 案例总数：85+
- 文档格式：Markdown
""".format(datetime.now().strftime('%Y-%m-%d %H:%M'))

    with open(os.path.join(TARGET_DIR, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("✅ 创建README.md")


def main():
    """主函数"""
    print("="*60)
    print("运营案例批量转换脚本")
    print("="*60)

    # 创建目录结构
    print("\n步骤1: 创建目录结构...")
    create_directory_structure()

    # 扫描源文件夹
    print(f"\n步骤2: 扫描源文件夹 {SOURCE_DIR}...")
    all_files = os.listdir(SOURCE_DIR)
    pdf_files = [f for f in all_files if f.endswith('.pdf')]
    docx_files = [f for f in all_files if f.endswith('.docx')]

    print(f"  发现 {len(pdf_files)} 个PDF文件")
    print(f"  发现 {len(docx_files)} 个DOCX文件")
    print(f"  总计 {len(pdf_files) + len(docx_files)} 个文件")

    # 转换PDF文件
    print("\n步骤3: 转换PDF文件...")
    pdf_converted = 0
    for i, filename in enumerate(pdf_files, 1):
        print(f"  [{i}/{len(pdf_files)}] 处理: {filename}")

        source_path = os.path.join(SOURCE_DIR, filename)
        category = categorize_case(filename)

        # 转换为文本
        text = convert_pdf_to_text(source_path)
        if text:
            # 转换为markdown
            md_filename = filename.replace('.pdf', '.md')
            markdown_content = text_to_markdown(text, filename)

            # 保存到对应分类目录
            target_path = os.path.join(TARGET_DIR, category, md_filename)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            pdf_converted += 1
            print(f"           → {category}/")
        else:
            print(f"           ✗ 转换失败")

    print(f"\n  PDF转换完成: {pdf_converted}/{len(pdf_files)}")

    # 转换DOCX文件
    print("\n步骤4: 转换DOCX文件...")
    docx_converted = 0
    for i, filename in enumerate(docx_files, 1):
        print(f"  [{i}/{len(docx_files)}] 处理: {filename}")

        source_path = os.path.join(SOURCE_DIR, filename)
        category = categorize_case(filename)

        # 转换为文本
        text = convert_docx_to_text(source_path)
        if text:
            # 转换为markdown
            md_filename = filename.replace('.docx', '.md')
            markdown_content = text_to_markdown(text, filename)

            # 保存到对应分类目录
            target_path = os.path.join(TARGET_DIR, category, md_filename)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            docx_converted += 1
            print(f"           → {category}/")
        else:
            print(f"           ✗ 转换失败")

    print(f"\n  DOCX转换完成: {docx_converted}/{len(docx_files)}")

    # 创建README
    print("\n步骤5: 创建案例库README...")
    create_readme()

    # 总结
    print("\n" + "="*60)
    print("转换完成！")
    print("="*60)
    print(f"PDF转换: {pdf_converted} 个")
    print(f"DOCX转换: {docx_converted} 个")
    print(f"总计: {pdf_converted + docx_converted} 个案例")
    print(f"\n输出目录: {TARGET_DIR}")


if __name__ == "__main__":
    main()
