#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运营案例拆解文档分析脚本
分析案例文档的结构和内容，提取通用方法论
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

# 案例文件夹路径
CASE_FOLDER = "/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/02 领域（Area)/2.0_运营领域/6.0_运营skill/【运营案例拆解】"

def get_all_cases() -> List[Dict]:
    """获取所有案例文档信息"""
    cases = []
    folder_path = Path(CASE_FOLDER)

    for file in folder_path.glob("*.pdf"):
        cases.append({
            "name": file.name,
            "path": str(file),
            "type": "pdf",
            "number": file.name.split()[0] if file.name.split()[0].isdigit() else None
        })

    for file in folder_path.glob("*.docx"):
        cases.append({
            "name": file.name,
            "path": str(file),
            "type": "docx",
            "number": file.name.split()[0] if file.name.split()[0].isdigit() else None
        })

    # 按编号排序
    cases.sort(key=lambda x: int(x["number"]) if x["number"] else 999)
    return cases

def categorize_cases(cases: List[Dict]) -> Dict[str, List[Dict]]:
    """按类型分类案例"""
    categories = {
        "私域运营": [],
        "用户增长": [],
        "用户活跃": [],
        "活动策划": [],
        "内容营销": [],
        "品牌营销": [],
        "产品运营": [],
        "社群运营": [],
        "联名营销": [],
        "其他": []
    }

    keywords_map = {
        "私域运营": ["私域", "社群", "会员", "精细化运营"],
        "用户增长": ["增长", "拉新", "用户增长", "获客"],
        "用户活跃": ["用户活跃", "活跃", "留存"],
        "活动策划": ["活动", "营销活动", "运营活动"],
        "内容营销": ["内容", "文案", "短视频", "直播"],
        "品牌营销": ["品牌", "营销", "宣发", "口碑"],
        "产品运营": ["产品", "APP", "运营"],
        "社群运营": ["社群", "社区", "群"],
        "联名营销": ["联名", "合作"]
    }

    for case in cases:
        name = case["name"].lower()
        categorized = False

        for category, keywords in keywords_map.items():
            if any(keyword in name for keyword in keywords):
                categories[category].append(case)
                categorized = True
                break

        if not categorized:
            categories["其他"].append(case)

    return categories

def extract_structure_from_filename(filename: str) -> Dict:
    """从文件名提取结构信息"""
    # 移除扩展名
    name = filename.rsplit('.', 1)[0]

    # 提取编号
    number_match = re.match(r'^(\d+)', name)
    number = number_match.group(1) if number_match else None

    # 提取日期
    date_match = re.search(r'(\d{4}\.\d+\.\d+)', name)
    date = date_match.group(1) if date_match else None

    # 提取品牌/产品名称
    brands = [
        "瑞幸", "奈雪", "喜茶", "蜜雪冰城", "霸王茶姬", "肯德基",
        "美团", "抖音", "微信", "网易", "得物", "蔚来",
        "丁香医生", "樊登读书", "考虫", "baby care", "醉鹅娘",
        "孩子王", "乐刻", "交个朋友", "拼多多", "淘宝",
        "Lululemon", "Kimi", "黑神话", "封神", "流浪地球",
        "妙鸭相机", "TikTok", "多邻国", "瑞幸x茅台"
    ]

    brand = None
    for b in brands:
        if b.lower() in name.lower():
            brand = b
            break

    return {
        "number": number,
        "date": date,
        "brand": brand,
        "title": name
    }

def main():
    """主函数"""
    print("=" * 80)
    print("运营案例拆解文档分析")
    print("=" * 80)

    # 获取所有案例
    cases = get_all_cases()
    print(f"\n📊 总计发现 {len(cases)} 个案例文档")

    # 统计文档类型
    pdf_count = sum(1 for c in cases if c["type"] == "pdf")
    docx_count = sum(1 for c in cases if c["type"] == "docx")
    print(f"   - PDF文档: {pdf_count} 个")
    print(f"   - DOCX文档: {docx_count} 个")

    # 分类统计
    categories = categorize_cases(cases)
    print("\n📋 案例分类统计:")
    for category, case_list in categories.items():
        if case_list:
            print(f"   - {category}: {len(case_list)} 个")

    # 显示代表性案例
    print("\n🎯 代表性案例列表:")
    print("=" * 80)

    for category, case_list in categories.items():
        if case_list:
            print(f"\n【{category}】({len(case_list)}个)")
            for case in case_List[:5]:  # 只显示前5个
                info = extract_structure_from_filename(case["name"])
                print(f"   {info['number'] or 'N/A'}. {info['brand'] or '未知品牌'} - {case['name'][:50]}...")

    # 保存分析结果
    result = {
        "total_cases": len(cases),
        "pdf_count": pdf_count,
        "docx_count": docx_count,
        "categories": {k: len(v) for k, v in categories.items()},
        "cases": [
            {
                **case,
                **extract_structure_from_filename(case["name"])
            }
            for case in cases
        ]
    }

    output_file = "/Users/cyberwiz/Documents/trae_projects/Claude code/operation-case-analyzer/cases_overview.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分析结果已保存至: {output_file}")

if __name__ == "__main__":
    main()
