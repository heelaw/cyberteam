#!/usr/bin/env python3
# CyberTeam v2 - 思维专家批量加载器

"""
自动加载 /Users/cyberwiz/Documents/01_Project/02_Skill研发/思考天团Agent/agents/ 下的所有思维专家
解析 AGENT.md 并转换为 thinking_injector 可用的格式
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# 专家库路径
EXPERTS_DIR = Path("/Users/cyberwiz/Documents/01_Project/02_Skill研发/思考天团Agent/agents")


@dataclass
class ExpertInfo:
    """思维专家信息"""
    id: str
    name: str
    name_cn: str
    category: str
    description: str
    triggers: List[str]
    capabilities: List[str]
    input_format: str = ""
    output_format: str = ""
    critical_rules: List[str] = field(default_factory=list)
    analysis_flow: str = ""
    agent_md_path: str = ""


def parse_agent_md(file_path: Path) -> Optional[ExpertInfo]:
    """解析 AGENT.md 文件"""

    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")

    # 提取基本信息
    info = {}

    # 从元数据Schema提取
    schema_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if schema_match:
        try:
            schema = json.loads(schema_match.group(1))
            info["id"] = schema.get("id", "")
            info["name_cn"] = schema.get("name", "")
            info["triggers"] = schema.get("triggers", [])
            info["capabilities"] = schema.get("capabilities", [])
        except json.JSONDecodeError:
            pass

    # 如果没有从Schema提取到，从标题提取
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match and not info.get("name_cn"):
        info["name_cn"] = title_match.group(1).strip()

    # 从表格提取触发词（备用）
    if not info.get("triggers"):
        trigger_match = re.search(r'\|.*?触发.*?\|\n\|[-|]+\|\n((?:\|.*?\n)+)', content)
        if trigger_match:
            triggers = []
            for line in trigger_match.group(1).split("\n"):
                cells = line.strip("|").split("|")
                if len(cells) >= 2 and cells[1].strip():
                    triggers.append(cells[1].strip())
            info["triggers"] = triggers

    # 提取输入格式
    input_match = re.search(r'## 输入格式\s*\n```\s*\n([\s\S]+?)```', content)
    if input_match:
        info["input_format"] = input_match.group(1).strip()

    # 提取输出格式
    output_match = re.search(r'## 输出格式\s*\n```[\s\S]*?\n([\s\S]+?)```', content)
    if output_match:
        info["output_format"] = output_match.group(1).strip()

    # 提取关键规则
    rules = []
    rules_match = re.search(r'### 必须遵守\s*\n((?:\d+\..+\n)+)', content)
    if rules_match:
        for line in rules_match.group(1).split("\n"):
            if line.strip():
                rules.append(line.strip())
    info["critical_rules"] = rules

    # 推断分类
    info["category"] = infer_category(info.get("name_cn", ""), info.get("capabilities", []))

    # 提取描述（从核心定位）
    desc_match = re.search(r'## 核心定位\s*\n+([^\n#]+)', content)
    if desc_match:
        info["description"] = desc_match.group(1).strip()[:200]
    else:
        info["description"] = info.get("name_cn", "")

    # 生成ID（从文件夹名）
    folder_name = file_path.parent.name
    # 去掉前缀数字
    info["id"] = re.sub(r'^\d+-', '', folder_name)
    info["name"] = info["name_cn"]

    return ExpertInfo(
        id=info.get("id", ""),
        name=info.get("name", ""),
        name_cn=info.get("name_cn", ""),
        category=info.get("category", "general"),
        description=info.get("description", ""),
        triggers=info.get("triggers", []),
        capabilities=info.get("capabilities", []),
        input_format=info.get("input_format", ""),
        output_format=info.get("output_format", ""),
        critical_rules=info.get("critical_rules", []),
        analysis_flow="",
        agent_md_path=str(file_path)
    )


def infer_category(name: str, capabilities: List[str]) -> str:
    """推断专家分类"""

    name_lower = name.lower()
    caps_text = " ".join(capabilities).lower()

    # 决策类
    decision_keywords = ["决策", "选择", "风险", "偏差", "卡尼曼", "博弈", "贝叶斯", "概率"]
    if any(kw in name_lower or kw in caps_text for kw in decision_keywords):
        return "decision"

    # 战略类
    strategy_keywords = ["战略", "swot", "波特", "竞争", "五力", "bcg"]
    if any(kw in name_lower or kw in caps_text for kw in strategy_keywords):
        return "strategy"

    # 增长类
    growth_keywords = ["增长", "用户", "获客", "变现", "aarrr", "海盗"]
    if any(kw in name_lower or kw in caps_text for kw in growth_keywords):
        return "growth"

    # 执行类
    execution_keywords = ["执行", "grow", "wbs", "okr", "pdca", "计划", "行动", "目标"]
    if any(kw in name_lower or kw in caps_text for kw in execution_keywords):
        return "execution"

    # 创意类
    creative_keywords = ["创意", "设计思维", "六顶", "横向", "发散"]
    if any(kw in name_lower or kw in caps_text for kw in creative_keywords):
        return "creative"

    # 分析类
    analysis_keywords = ["分析", "思维", "批判", "系统", "why", "根本"]
    if any(kw in name_lower or kw in caps_text for kw in analysis_keywords):
        return "analysis"

    # 管理类
    mgmt_keywords = ["管理", "领导", "团队", "组织", "变革", "人力"]
    if any(kw in name_lower or kw in caps_text for kw in mgmt_keywords):
        return "management"

    # 心理类
    psych_keywords = ["心理", "情绪", "认知", "偏见", "效应"]
    if any(kw in name_lower or kw in caps_text for kw in psych_keywords):
        return "psychology"

    return "general"


def load_all_experts() -> List[ExpertInfo]:
    """加载所有思维专家"""

    experts = []

    if not EXPERTS_DIR.exists():
        print(f"⚠️ 专家目录不存在: {EXPERTS_DIR}")
        return experts

    # 遍历所有子目录
    for folder in sorted(EXPERTS_DIR.iterdir()):
        if not folder.is_dir():
            continue

        agent_md = folder / "AGENT.md"
        if agent_md.exists():
            expert = parse_agent_md(agent_md)
            if expert and expert.id:
                experts.append(expert)
                print(f"  ✓ {expert.id}: {expert.name_cn} ({expert.category})")

    return experts


def generate_expert_catalog(experts: List[ExpertInfo]) -> Dict[str, Any]:
    """生成专家目录"""

    catalog = {
        "total": len(experts),
        "categories": {},
        "experts": []
    }

    # 按分类统计
    for expert in experts:
        if expert.category not in catalog["categories"]:
            catalog["categories"][expert.category] = []
        catalog["categories"][expert.category].append(expert.id)

        catalog["experts"].append({
            "id": expert.id,
            "name": expert.name,
            "name_cn": expert.name_cn,
            "category": expert.category,
            "description": expert.description,
            "triggers": expert.triggers,
            "capabilities": expert.capabilities
        })

    return catalog


def generate_thinking_injector_code(experts: List[ExpertInfo]) -> str:
    """生成 thinking_injector.py 的专家加载代码"""

    lines = [
        "# 自动生成的专家加载代码",
        "# 生成时间: 2026-03-24",
        "# 总共: {} 个思维专家\n".format(len(experts)),
    ]

    lines.append("def _load_expert_library(self):")
    lines.append('    """加载所有思维专家 - 自动生成"""')

    # 按分类组织
    by_category = {}
    for expert in experts:
        if expert.category not in by_category:
            by_category[expert.category] = []
        by_category[expert.category].append(expert)

    for category, category_experts in sorted(by_category.items()):
        lines.append(f"\n    # ===== {category.upper()} ({len(category_experts)}) =====")

        for expert in category_experts:
            triggers = repr(expert.triggers[:5])  # 只取前5个触发词

            lines.append(f"""
        self._add_expert(Expert(
            id="{expert.id}",
            name="{expert.name}",
            name_cn="{expert.name_cn}",
            category="{expert.category}",
            description="{expert.description[:100]}",
            trigger_keywords={triggers},
            injection_template=""" + '"""')
            lines.append(f"{expert.description}")
            lines.append('"""')
            lines.append("        ))")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("CyberTeam v2 - 思维专家批量加载器")
    print("=" * 60)
    print(f"\n📂 专家目录: {EXPERTS_DIR}\n")

    # 加载所有专家
    experts = load_all_experts()

    print(f"\n✅ 成功加载 {len(experts)} 个思维专家")

    # 生成目录
    catalog = generate_expert_catalog(experts)

    # 打印分类统计
    print("\n📊 分类统计:")
    for category, ids in sorted(catalog["categories"].items()):
        print(f"  [{category}] {len(ids)} 个")

    # 保存目录
    output_dir = Path(__file__).parent.parent / "config"
    output_dir.mkdir(exist_ok=True)

    catalog_path = output_dir / "expert_catalog.json"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"\n💾 目录已保存: {catalog_path}")

    # 生成代码
    code = generate_thinking_injector_code(experts)
    code_path = output_dir / "expert_library_auto.py"
    code_path.write_text(code, encoding="utf-8")
    print(f"💾 代码已保存: {code_path}")

    # 保存专家列表
    experts_path = output_dir / "experts_list.md"
    with open(experts_path, "w", encoding="utf-8") as f:
        f.write("# 思维专家目录\n\n")
        f.write(f"总计: {len(experts)} 个专家\n\n")

        by_category = {}
        for expert in experts:
            if expert.category not in by_category:
                by_category[expert.category] = []
            by_category[expert.category].append(expert)

        for category, category_experts in sorted(by_category.items()):
            f.write(f"\n## {category.upper()}\n\n")
            for expert in category_experts:
                f.write(f"- **{expert.name_cn}** (`{expert.id}`): {expert.description[:80]}...\n")

    print(f"💾 专家列表已保存: {experts_path}")

    return experts, catalog


if __name__ == "__main__":
    experts, catalog = main()
