#!/usr/bin/env python3
"""
CyberTeam v2 - 简化版专家加载器
直接从 AGENT.md 文件加载专家元数据
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

EXPERTS_DIR = Path("/Users/cyberwiz/Documents/01_Project/02_Skill研发/思考天团Agent/agents")


def parse_agent_md(file_path: Path) -> Optional[Dict]:
    """解析单个 AGENT.md"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return None

    result = {
        "folder": file_path.parent.name,
        "path": str(file_path)
    }

    # 从元数据Schema提取
    schema_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content)
    if schema_match:
        try:
            schema = json.loads(schema_match.group(1))
            result["id"] = schema.get("id", "")
            result["name"] = schema.get("name", "")
            result["triggers"] = schema.get("triggers", [])
            result["capabilities"] = schema.get("capabilities", [])
        except json.JSONDecodeError:
            pass

    # 从标题提取名称
    if not result.get("name"):
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            result["name"] = title_match.group(1).strip()

    # 生成ID
    folder_name = file_path.parent.name
    result["id"] = re.sub(r'^\d+-', '', folder_name)

    return result


def load_all_experts() -> List[Dict]:
    """加载所有专家"""
    experts = []
    for folder in sorted(EXPERTS_DIR.iterdir()):
        if folder.is_dir():
            agent_md = folder / "AGENT.md"
            if agent_md.exists():
                expert = parse_agent_md(agent_md)
                if expert:
                    experts.append(expert)
    return experts


def main():
    print("加载思维专家...")
    experts = load_all_experts()
    print(f"加载了 {len(experts)} 个专家")

    # 按分类组织
    by_category = {}
    for e in experts:
        cat = infer_category(e)
        e["category"] = cat
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(e["id"])

    # 输出
    print("\n分类统计:")
    for cat, ids in sorted(by_category.items()):
        print(f"  {cat}: {len(ids)}")

    # 保存
    catalog = {
        "total": len(experts),
        "categories": by_category,
        "experts": experts
    }

    out_path = Path(__file__).parent.parent / "config" / "expert_catalog.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\n保存到: {out_path}")

    return catalog


def infer_category(e: Dict) -> str:
    """推断分类"""
    name = (e.get("name") or "").lower()
    triggers = " ".join(e.get("triggers", [])).lower()
    caps = " ".join(e.get("capabilities", [])).lower()
    text = f"{name} {triggers} {caps}"

    keywords_map = {
        "decision": ["决策", "选择", "风险", "偏差", "卡尼曼", "博弈", "贝叶斯", "概率"],
        "strategy": ["战略", "swot", "波特", "竞争", "五力", "bcg", "tows"],
        "growth": ["增长", "用户", "获客", "变现", "海盗"],
        "execution": ["执行", "grow", "wbs", "okr", "pdca", "计划", "行动", "目标"],
        "creative": ["创意", "设计思维", "六顶", "横向", "发散", "design thinking"],
        "analysis": ["分析", "思维", "批判", "系统", "why", "根本", "five why"],
        "management": ["管理", "领导", "团队", "组织", "变革", "人力", "经理"],
        "psychology": ["心理", "情绪", "认知", "偏见", "效应"],
    }

    for cat, keywords in keywords_map.items():
        if any(kw in text for kw in keywords):
            return cat

    return "general"


if __name__ == "__main__":
    main()
