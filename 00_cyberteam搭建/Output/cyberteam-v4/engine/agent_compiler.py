#!/usr/bin/env python3
"""
CyberTeam V4 - Agent 编译器

把 agent.yaml + SOUL.md + prompts/ 编译成运行时 AgentProfile。

参考 Magic 的 Agent 编译器概念，保留 CyberTeam 的现代公司治理特色。

功能:
- compile(): 编译单个 Agent 目录
- compile_all(): 编译 AGENTS/ 下所有 Agent
- generate_agent_yaml(): 为缺少 agent.yaml 的 Agent 生成配置
- generate_prompts(): 为缺少 prompts/ 的 Agent 生成模块化 Prompt

Usage:
    python engine/agent_compiler.py AGENTS/
    python engine/agent_compiler.py AGENTS/ --init  # 初始化所有缺失文件
"""

import yaml
import re
import sys
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentProfile:
    """编译后的 Agent 配置"""
    name: str
    department: str
    layer: str  # decision | coordination | execution
    model: str = "main_llm"
    daily_budget: float = 10.0
    tools: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    subordinates: list[str] = field(default_factory=list)
    triggers: dict = field(default_factory=dict)
    approval_required: list[str] = field(default_factory=list)
    system_prompt: str = ""
    soul_path: str = ""
    prompts: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Agent 元数据映射 - 基于 rbac.py 中的角色定义和 AGENTS 目录结构
# ---------------------------------------------------------------------------

AGENT_REGISTRY: dict[str, dict] = {
    # ---- 增长部 (growth) ----
    "增长营销": {
        "department": "growth",
        "layer": "execution",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file", "call_subagent"],
        "skills": ["增长逻辑梳理法", "漏斗分析法", "A/B测试设计"],
        "subordinates": [],
        "triggers": {
            "keywords": ["增长", "拉新", "获客", "增长黑客", "增长策略"],
            "task_types": ["growth_strategy", "user_acquisition"],
        },
        "approval_required": ["publish_content", "budget_exceed_5usd"],
    },
    "内容运营": {
        "department": "growth",
        "layer": "execution",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file"],
        "skills": ["内容选题八方向", "内容调性定位法", "爆款笔记写作"],
        "subordinates": [],
        "triggers": {
            "keywords": ["内容", "文案", "选题", "爆款", "内容策划"],
            "task_types": ["content_creation", "content_strategy"],
        },
        "approval_required": ["publish_content"],
    },
    "效果营销": {
        "department": "growth",
        "layer": "execution",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file"],
        "skills": ["投放策略", "ROI优化", "渠道效果分析"],
        "subordinates": [],
        "triggers": {
            "keywords": ["投放", "ROI", "效果", "广告", "竞价", "信息流"],
            "task_types": ["performance_marketing", "ad_campaign"],
        },
        "approval_required": ["budget_exceed_5usd", "publish_content"],
    },
    "活动运营": {
        "department": "growth",
        "layer": "execution",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file"],
        "skills": ["活动九大驱动力", "活动目标发痛点确定", "活动运营标准八步"],
        "subordinates": [],
        "triggers": {
            "keywords": ["活动", "促销", "大促", "节日活动", "营销活动"],
            "task_types": ["event_planning", "campaign_management"],
        },
        "approval_required": ["publish_content", "budget_exceed_5usd"],
    },
    "用户运营": {
        "department": "growth",
        "layer": "execution",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file"],
        "skills": ["用户留存诊断", "用户生命周期管理", "用户分层运营"],
        "subordinates": [],
        "triggers": {
            "keywords": ["用户", "留存", "活跃", "生命周期", "用户画像"],
            "task_types": ["user_retention", "user_engagement"],
        },
        "approval_required": [],
    },
    "商业分析": {
        "department": "growth",
        "layer": "coordination",
        "model": "main_llm",
        "daily_budget": 10.0,
        "tools": ["web_search", "write_file", "read_file", "call_subagent"],
        "skills": ["价值落地诊断", "业务价值评估法", "抽象问题具体化"],
        "subordinates": ["增长营销", "效果营销"],
        "triggers": {
            "keywords": ["分析", "商业", "市场", "竞争", "竞品", "数据"],
            "task_types": ["market_analysis", "competitive_analysis"],
        },
        "approval_required": [],
    },
    "团队管理": {
        "department": "growth",
        "layer": "coordination",
        "model": "main_llm",
        "daily_budget": 10.0,
        "tools": ["web_search", "write_file", "read_file", "call_subagent"],
        "skills": ["团队管理基本方法", "8大常见管理工具", "激励体系设计"],
        "subordinates": ["用户运营", "内容运营"],
        "triggers": {
            "keywords": ["团队", "管理", "带人", "领导", "组织", "1on1"],
            "task_types": ["team_management", "leadership"],
        },
        "approval_required": [],
    },
    "工作管理": {
        "department": "growth",
        "layer": "coordination",
        "model": "main_llm",
        "daily_budget": 10.0,
        "tools": ["web_search", "write_file", "read_file", "call_subagent"],
        "skills": ["SOP建立四步法", "指标拆解三逻辑", "精益运营思维"],
        "subordinates": ["活动运营"],
        "triggers": {
            "keywords": ["SOP", "流程", "效率", "工作管理", "进度"],
            "task_types": ["process_optimization", "sop_creation"],
        },
        "approval_required": [],
    },
    "策略规划": {
        "department": "growth",
        "layer": "coordination",
        "model": "main_llm",
        "daily_budget": 12.0,
        "tools": ["web_search", "write_file", "read_file", "call_subagent"],
        "skills": ["制定局部业务目标", "横向交叉模型", "成功三要素分析"],
        "subordinates": ["商业分析", "增长营销"],
        "triggers": {
            "keywords": ["策略", "规划", "战略", "方向", "目标", "北极星"],
            "task_types": ["strategy_planning", "goal_setting"],
        },
        "approval_required": ["budget_exceed_10usd"],
    },
    "高级运营": {
        "department": "growth",
        "layer": "coordination",
        "model": "main_llm",
        "daily_budget": 10.0,
        "tools": ["web_search", "write_file", "read_file", "call_subagent"],
        "skills": ["数据分析进阶", "用户分层运营", "增长实验设计", "转化优化"],
        "subordinates": ["用户运营", "内容运营", "活动运营"],
        "triggers": {
            "keywords": ["进阶", "提升", "深度运营", "精细化"],
            "task_types": ["ops_advancement", "skill_improvement"],
        },
        "approval_required": [],
    },
    # ---- 产品部 (product) ----
    "产品运营": {
        "department": "product",
        "layer": "execution",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file"],
        "skills": ["产品需求分析", "PRD编写", "用户故事地图"],
        "subordinates": [],
        "triggers": {
            "keywords": ["产品", "功能", "需求", "迭代", "PRD"],
            "task_types": ["product_management", "feature_planning"],
        },
        "approval_required": [],
    },
    "用户研究": {
        "department": "product",
        "layer": "execution",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file"],
        "skills": ["用户访谈", "问卷调查", "可用性测试", "数据分析"],
        "subordinates": [],
        "triggers": {
            "keywords": ["用户研究", "用户调研", "访谈", "可用性", "用户体验"],
            "task_types": ["user_research", "usability_testing"],
        },
        "approval_required": [],
    },
    # ---- 财务部 (finance) ----
    "财务管理": {
        "department": "finance",
        "layer": "coordination",
        "model": "main_llm",
        "daily_budget": 8.0,
        "tools": ["web_search", "write_file", "read_file"],
        "skills": ["财务尽职调查法", "定价策略", "收入预测模型"],
        "subordinates": [],
        "triggers": {
            "keywords": ["财务", "预算", "成本", "定价", "ROI", "利润"],
            "task_types": ["finance_analysis", "budget_planning"],
        },
        "approval_required": ["budget_exceed_10usd"],
    },
    # ---- 质疑者 (socratic-questioner) ----
    "质疑者": {
        "department": "socratic-questioner",
        "layer": "decision",
        "model": "main_llm",
        "daily_budget": 5.0,
        "tools": ["web_search", "read_file"],
        "skills": ["苏格拉底追问法", "三层追问法", "数据来源验证"],
        "subordinates": [],
        "triggers": {
            "keywords": ["质疑", "验证", "审查", "讨论", "辩论"],
            "task_types": ["quality_review", "debate", "discussion"],
        },
        "approval_required": [],
    },
}


class AgentCompiler:
    """Agent 编译器"""

    def compile(self, agent_dir: Path) -> Optional[AgentProfile]:
        """
        编译单个 Agent 目录

        Args:
            agent_dir: Agent 目录路径

        Returns:
            AgentProfile 或 None (如果目录不包含 SOUL.md)
        """
        if not (agent_dir / "SOUL.md").exists():
            logger.warning(f"跳过 {agent_dir.name}: 缺少 SOUL.md")
            return None

        # 读取 YAML 配置
        config = {}
        yaml_path = agent_dir / "agent.yaml"
        if yaml_path.exists():
            raw = yaml_path.read_text(encoding="utf-8")
            config = yaml.safe_load(raw) or {}

        # 如果 YAML 里没有 name，从目录名推导
        if not config.get("name"):
            config["name"] = agent_dir.name

        # 读取 SOUL.md
        soul = (agent_dir / "SOUL.md").read_text(encoding="utf-8")

        # 读取模块化 Prompts
        prompts = {}
        prompts_dir = agent_dir / "prompts"
        if prompts_dir.exists():
            for p in prompts_dir.glob("*.prompt"):
                prompts[p.stem] = p.read_text(encoding="utf-8")

        # 组合 system_prompt
        system_prompt = self._compose(soul, prompts)

        return AgentProfile(
            name=config.get("name", agent_dir.name),
            department=config.get("department", "unknown"),
            layer=config.get("layer", "execution"),
            model=config.get("model", "main_llm"),
            daily_budget=config.get("daily_budget", 10.0),
            tools=config.get("tools", ["read_file", "write_file"]),
            skills=config.get("skills", []),
            subordinates=config.get("subordinates", []),
            triggers=config.get("triggers", {}),
            approval_required=config.get("approval_required", []),
            system_prompt=system_prompt,
            soul_path=str(agent_dir / "SOUL.md"),
            prompts=prompts,
        )

    def compile_all(self, agents_root: Path) -> dict[str, AgentProfile]:
        """
        编译所有 Agent

        Args:
            agents_root: AGENTS/ 根目录

        Returns:
            Dict[name, AgentProfile]
        """
        profiles: dict[str, AgentProfile] = {}
        for dept_dir in agents_root.iterdir():
            if not dept_dir.is_dir() or dept_dir.name.startswith("_"):
                continue
            for agent_dir in dept_dir.iterdir():
                if agent_dir.is_dir() and (agent_dir / "SOUL.md").exists():
                    profile = self.compile(agent_dir)
                    if profile:
                        profiles[profile.name] = profile
        return profiles

    def _compose(self, soul: str, prompts: dict[str, str]) -> str:
        """
        组合 system_prompt: SOUL.md + prompts 按优先级拼接

        Args:
            soul: SOUL.md 内容
            prompts: prompts/*.prompt 内容字典

        Returns:
            组合后的 system_prompt 字符串
        """
        parts = [soul]
        for key in ["base", "debate", "quality"]:
            if key in prompts:
                parts.append(f"\n## {key.upper()}\n{prompts[key]}")
        return "\n\n---\n\n".join(p for p in parts if p.strip())


# ---------------------------------------------------------------------------
# 初始化工具方法 - 用于批量生成 agent.yaml 和 prompts/
# ---------------------------------------------------------------------------

def _extract_zh_from_soul(soul_text: str) -> str:
    """
    从 SOUL.md 提取核心职责描述

    提取策略:
    1. 从"语气风格"章节下提取描述
    2. 如果没有，从文件头部的非标题内容提取
    3. 兜底使用通用描述
    """
    lines = soul_text.strip().split("\n")

    # 策略1: 从"语气风格"章节提取
    in_tone = False
    tone_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped in ("## 语气风格", "## 语气风格"):
            in_tone = True
            continue
        if in_tone:
            if stripped.startswith("## "):
                break
            if not stripped:
                continue
            # 去掉 markdown 加粗标记
            cleaned = stripped.replace("**", "").strip()
            if cleaned and not cleaned.startswith("-"):
                tone_lines.append(cleaned)
            elif cleaned.startswith("- "):
                tone_lines.append(cleaned[2:])

    if tone_lines:
        return " ".join(tone_lines)[:200]

    # 策略2: 从"灵魂本质"章节提取 (针对质疑者等)
    in_soul = False
    soul_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped in ("## 灵魂本质", "## 灵魂"):
            in_soul = True
            continue
        if in_soul:
            if stripped.startswith("## "):
                break
            if not stripped:
                continue
            if stripped.startswith(">"):
                cleaned = stripped[1:].strip()
                if cleaned:
                    soul_lines.append(cleaned)
            elif stripped.startswith("**") and stripped.endswith("**"):
                soul_lines.append(stripped.replace("**", ""))
            elif not stripped.startswith("```") and not stripped.startswith("---"):
                soul_lines.append(stripped)

    if soul_lines:
        return " ".join(soul_lines)[:200]

    # 策略3: 从文件头部提取
    desc_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith(">"):
            cleaned = stripped[1:].strip()
            if cleaned:
                desc_lines.append(cleaned)
            continue
        if stripped.startswith("---") or stripped.startswith("```"):
            continue
        desc_lines.append(stripped)

    return " ".join(desc_lines)[:200] if desc_lines else "执行分配的任务"


def _extract_forbidden_words(soul_text: str) -> list[str]:
    """从 SOUL.md 提取禁止词"""
    words = []
    in_forbidden = False
    for line in soul_text.split("\n"):
        if "禁止词" in line:
            in_forbidden = True
            continue
        if in_forbidden and line.startswith("## "):
            break
        if in_forbidden and line.strip().startswith("- "):
            # 去掉引号
            w = line.strip()[2:].strip().strip('"').strip("'")
            words.append(w)
    return words


def generate_agent_yaml(agent_dir: Path) -> bool:
    """为 Agent 目录生成 agent.yaml"""
    yaml_path = agent_dir / "agent.yaml"
    if yaml_path.exists():
        return False  # 已存在不覆盖

    name = agent_dir.name
    dept = agent_dir.parent.name

    # 从注册表查找预定义配置
    reg = AGENT_REGISTRY.get(name, {})

    config = {
        "name": name,
        "department": reg.get("department", dept),
        "layer": reg.get("layer", "execution"),
        "model": reg.get("model", "main_llm"),
        "daily_budget": reg.get("daily_budget", 10.0),
        "tools": reg.get("tools", ["read_file", "write_file"]),
        "skills": reg.get("skills", []),
        "subordinates": reg.get("subordinates", []),
        "triggers": reg.get("triggers", {"keywords": [], "task_types": []}),
        "approval_required": reg.get("approval_required", []),
    }

    yaml_content = yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False)
    yaml_path.write_text(yaml_content, encoding="utf-8")
    return True


def generate_prompts(agent_dir: Path) -> bool:
    """为 Agent 目录生成 prompts/ 目录和三个 prompt 文件"""
    prompts_dir = agent_dir / "prompts"
    if prompts_dir.exists():
        return False  # 已存在不覆盖

    name = agent_dir.name
    soul_path = agent_dir / "SOUL.md"

    # 读取 SOUL.md 用于提取内容
    soul_text = soul_path.read_text(encoding="utf-8") if soul_path.exists() else ""
    desc = _extract_zh_from_soul(soul_text)
    forbidden = _extract_forbidden_words(soul_text)

    prompts_dir.mkdir(parents=True, exist_ok=True)

    # 翻译辅助
    dept_en = {
        "growth": "Growth", "product": "Product", "finance": "Finance",
        "socratic-questioner": "Socratic Questioner", "tech": "Engineering",
    }.get(agent_dir.parent.name, agent_dir.parent.name)

    # base.prompt - 基础指令
    base_prompt = f"""<!--zh
你是{name}（{dept_en}部门），负责{desc}。你需要遵守团队协作规范，确保产出的专业性和可落地性。
{f"绝对禁止使用以下表述：{', '.join(forbidden)}" if forbidden else ""}
-->
You are the {name} Agent ({dept_en} Department), responsible for {desc[:150]}.
You must follow team collaboration standards and ensure professional, actionable output.
{f"NEVER use these phrases: {', '.join(forbidden)}" if forbidden else ""}
"""
    (prompts_dir / "base.prompt").write_text(base_prompt, encoding="utf-8")

    # debate.prompt - 辩论模式指令
    debate_prompt = f"""<!--zh
在辩论模式下，你作为{name}（{dept_en}部门）需要：
1. 用数据和事实支撑你的论点，不凭感觉发言
2. 认真倾听其他 Agent 的观点，找到共识和分歧
3. 如果发现自己观点有误，主动承认并调整
4. 最终目标是找到最优方案，而非赢得辩论
-->
In debate mode, as the {name} Agent ({dept_en} Department), you must:
1. Support your arguments with data and facts, never speculate
2. Listen to other Agents' perspectives, identify consensus and disagreement
3. Acknowledge and adjust if your viewpoint is found to be incorrect
4. The ultimate goal is to find the optimal solution, not to win the debate
"""
    (prompts_dir / "debate.prompt").write_text(debate_prompt, encoding="utf-8")

    # quality.prompt - 质量检查指令
    quality_prompt = f"""<!--zh
在质量检查模式下，你需要审视产出是否符合以下标准：
1. 数据来源是否明确标注（估算/调研/搜索/用户提供）
2. 逻辑推理链条是否完整，没有跳跃
3. 是否考虑了反面观点和风险因素
4. 产出是否可落地执行，有具体步骤
5. 是否符合 CyberTeam 质量规范
-->
In quality check mode, review the output against these standards:
1. Data sources are clearly labeled (estimate/research/search/user-provided)
2. Logical reasoning chain is complete with no gaps
3. Counter-arguments and risk factors have been considered
4. Output is actionable with specific steps
5. Complies with CyberTeam quality standards
"""
    (prompts_dir / "quality.prompt").write_text(quality_prompt, encoding="utf-8")

    return True


def init_all_agents(agents_root: Path):
    """
    初始化所有 Agent: 生成缺失的 agent.yaml 和 prompts/

    Args:
        agents_root: AGENTS/ 根目录
    """
    yaml_count = 0
    prompt_count = 0

    for dept_dir in agents_root.iterdir():
        if not dept_dir.is_dir() or dept_dir.name.startswith("_"):
            continue
        for agent_dir in dept_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            if not (agent_dir / "SOUL.md").exists():
                continue

            if generate_agent_yaml(agent_dir):
                yaml_count += 1
                logger.info(f"  生成 agent.yaml: {agent_dir.name}")

            if generate_prompts(agent_dir):
                prompt_count += 1
                logger.info(f"  生成 prompts/: {agent_dir.name}")

    return yaml_count, prompt_count


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="CyberTeam Agent 编译器")
    parser.add_argument("agents_root", nargs="?", default="AGENTS", help="AGENTS 目录路径")
    parser.add_argument("--init", action="store_true", help="初始化缺失的 agent.yaml 和 prompts/")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    agents_root = Path(args.agents_root)
    if not agents_root.exists():
        print(f"ERROR: 目录不存在: {agents_root}")
        sys.exit(1)

    if args.init:
        print(f"=== 初始化 Agent 配置: {agents_root} ===")
        yaml_count, prompt_count = init_all_agents(agents_root)
        print(f"\n生成 agent.yaml: {yaml_count} 个")
        print(f"生成 prompts/:   {prompt_count} 个")

    print(f"\n=== 编译 Agent: {agents_root} ===")
    compiler = AgentCompiler()
    profiles = compiler.compile_all(agents_root)

    for name, p in sorted(profiles.items()):
        print(f"  {name}: dept={p.department}, layer={p.layer}, "
              f"tools={len(p.tools)}, skills={len(p.skills)}, "
              f"prompts={len(p.prompts)}")

    print(f"\n总计编译 {len(profiles)} 个 Agent")

    # 统计信息
    layers = {"decision": 0, "coordination": 0, "execution": 0}
    depts: dict[str, int] = {}
    for p in profiles.values():
        layers[p.layer] = layers.get(p.layer, 0) + 1
        depts[p.department] = depts.get(p.department, 0) + 1

    print(f"\n--- 层级分布 ---")
    for layer, count in layers.items():
        print(f"  {layer}: {count} 个")

    print(f"\n--- 部门分布 ---")
    for dept, count in sorted(depts.items()):
        print(f"  {dept}: {count} 个")

    return profiles


if __name__ == "__main__":
    main()
