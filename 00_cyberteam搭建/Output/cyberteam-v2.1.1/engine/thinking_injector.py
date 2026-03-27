# CyberTeam v2 - 思维注入引擎 v2

"""
思维注入引擎 - 从 expert_catalog.json 加载 100+ 思维专家
核心机制：根据上下文自动选择相关思维专家，生成增强提示词
"""

import json
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Expert:
    """思维专家"""
    id: str
    name: str
    name_cn: str
    category: str
    description: str
    trigger_keywords: List[str]
    injection_template: str
    capabilities: List[str] = field(default_factory=list)
    weight: float = 1.0


@dataclass
class ThinkingContext:
    """思维上下文"""
    user_input: str
    selected_experts: List[Expert]
    thinking_prompt: str
    injection_points: List[str]
    confidence: float = 0.0
    reasoning_chain: List[str] = field(default_factory=list)


class IntentClassifier:
    """意图分类器 - 基于 expert_catalog.json 的触发词"""

    INTENT_PATTERNS = {
        # 决策类
        "decision": {
            "keywords": ["选择", "决策", "纠结", "风险", "判断", "评估", "权衡", "决定", "取舍"],
            "weight": 1.3
        },
        # 分析类
        "analysis": {
            "keywords": ["分析", "原因", "诊断", "为什么", "问题", "评估", "研究", "考察"],
            "weight": 1.0
        },
        # 执行类 - 核心关键词扩展，覆盖"做XX"型输入
        "execution": {
            "keywords": ["做", "怎么做", "执行", "实施", "落地", "实现", "计划", "任务", "构建", "开发", "创建", "搭建"],
            "weight": 1.2
        },
        # 战略类
        "strategy": {
            "keywords": ["战略", "竞争", "规划", "目标", "愿景", "定位", "策略", "方向", "商业模式"],
            "weight": 1.2
        },
        # 创意思维
        "creative": {
            "keywords": ["创新", "突破", "颠覆", "创意", "新思路", "想法", "方案"],
            "weight": 1.4
        },
        # 管理类
        "management": {
            "keywords": ["组织", "团队", "管理", "变革", "领导", "晋升", "招聘", "人力"],
            "weight": 1.1
        },
        # 增长类
        "growth": {
            "keywords": ["增长", "获客", "用户", "转化", "留存", "变现", "DAU", "MAU", "付费", "日活", "月活", "获益"],
            "weight": 1.2
        },
        # 产品类 - 新增，覆盖"平台"、"教育"等
        "product": {
            "keywords": ["产品", "功能", "需求", "迭代", "平台", "APP", "网站", "教育", "课程", "体验", "设计"],
            "weight": 1.1
        },
        # 技术类 - 新增
        "technology": {
            "keywords": ["技术", "架构", "开发", "代码", "系统", "性能", "安全", "部署"],
            "weight": 1.0
        },
        # 心理类
        "psychology": {
            "keywords": ["心理", "偏见", "偏差", "认知", "情绪", "自信", "心态"],
            "weight": 1.1
        },
        # 一般类 - 扩展
        "general": {
            "keywords": ["怎么", "如何", "是什么", "为什么", "帮我", "我想", "建议"],
            "weight": 0.3
        }
    }

    def classify(self, text: str) -> Dict[str, float]:
        """对输入文本进行意图分类"""
        text_lower = text.lower()
        scores = {}

        for intent, config in self.INTENT_PATTERNS.items():
            score = 0.0
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += 1.0

            if score > 0:
                scores[intent] = score * config["weight"]

        # 归一化
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}

        return scores


class ThinkingLibrary:
    """思维专家库 - 从 JSON 加载 100+ 专家"""

    def __init__(self, catalog_path: str = None):
        self.experts: Dict[str, Expert] = {}
        self.catalog_path = catalog_path or str(
            Path(__file__).parent.parent / "config" / "expert_catalog.json"
        )
        self._load_from_json()

    def _load_from_json(self):
        """从 JSON 加载专家库"""
        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)

            # 加载专家列表 - catalog 可以是列表或字典
            experts_list = catalog if isinstance(catalog, list) else catalog.get("experts", [])
            for expert_data in experts_list:
                expert_id = expert_data.get("id", "")
                if not expert_id:
                    continue
                # 优先从 JSON 读取真实数据，降级到函数生成
                name_cn = expert_data.get("name") or self._id_to_name(expert_id)
                category = expert_data.get("category") or self._get_category(expert_id)
                triggers = expert_data.get("triggers") or self._get_triggers(expert_id)
                capabilities = expert_data.get("capabilities") or [name_cn]
                expert = Expert(
                    id=expert_id,
                    name=name_cn,
                    name_cn=name_cn,
                    category=category,
                    description=expert_data.get("description", f"{name_cn}思维模型"),
                    trigger_keywords=triggers,
                    injection_template=self._generate_template(expert_data, name_cn),
                    capabilities=capabilities
                )
                self.experts[expert.id] = expert

            # 加载意图触发映射 - catalog 可以是列表或字典
            self.intent_triggers = {}
            if isinstance(catalog, dict):
                self.intent_triggers = catalog.get("intent_triggers", {})

            logger.info(f"Loaded {len(self.experts)} experts from {self.catalog_path}")

        except FileNotFoundError:
            logger.warning(f"Expert catalog not found: {self.catalog_path}")
            self._load_builtin()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse expert catalog: {e}")
            self._load_builtin()

    def _id_to_name(self, expert_id: str) -> str:
        """将 id 转换为中文名称"""
        # 简单的 id 到名称映射
        mappings = {
            "kahneman": "卡尼曼双系统", "first-principle": "第一性原理",
            "six-hats": "六顶思考帽", "swot-tows": "SWOT分析",
            "fivewhy": "5Why追问", "goldlin": "黄金圈法则",
            "grow": "GROW模型", "kiss": "KISS原则",
            "mckinsey": "麦肯锡7S", "ai-board": "AI董事会",
            "abc-emotion": "情绪ABC", "algoheuristic": "算法启发",
            "pest": "PEST分析", "porters-five": "波特五力",
            "bcg-matrix": "BCG矩阵", "ansoff": "安索夫矩阵",
            "business-model-canvas": "商业模式画布", "value-chain": "价值链",
            "crowd": "群体智慧", "decision-tree": "决策树",
            "second-order": "二阶思维", "inversion": "逆向思维",
            "premortem": "事前尸检", "occur": "5Why分析"
        }
        return mappings.get(expert_id, expert_id.replace("-", " ").title())

    def _get_category(self, expert_id: str) -> str:
        """获取专家类别"""
        categories = {
            "decision": ["kahneman", "decision-tree", "bayes", "game_theory"],
            "analysis": ["fivewhy", "swot-tows", "pest", "porters-five"],
            "creative": ["six-hats", "lateral-thinking", "brainstorm"],
            "execution": ["grow", "wbs", "pdca"],
            "strategy": ["bcg-matrix", "ansoff", "business-model-canvas"],
            "product": ["product", "ux", "design", "business-model-canvas", "value-chain"],
            "technology": ["tech", "architecture", "system", "infrastructure"],
            "growth": ["growth", "pirate", "aarrr", "pmaf", "ltv"],
            "management": ["hr", "team", "org", "leadership"]
        }
        for cat, ids in categories.items():
            if expert_id in ids:
                return cat
        return "general"

    def _get_triggers(self, expert_id: str) -> List[str]:
        """获取触发关键词"""
        triggers = {
            "kahneman": ["直觉", "判断", "偏差"],
            "first-principle": ["本质", "基础", "拆解"],
            "swot-tows": ["战略", "竞争", "优势"],
            "grow": ["目标", "现状", "方案"]
        }
        return triggers.get(expert_id, ["分析"])

    def _generate_template(self, expert_data: Dict, name: str = "") -> str:
        """生成注入模板"""
        name = name or expert_data.get("name", expert_data.get("id", ""))

        template = f"## {name}\n\n"
        triggers = expert_data.get("triggers", self._get_triggers(expert_data.get("id", "")))
        if triggers:
            template += f"**适用场景**: {', '.join(triggers[:3])}\n\n"
        template += "请运用此思维模型进行分析。"

        return template

    def _load_builtin(self):
        """加载内置专家（备用）"""
        self.experts = {}
        self.intent_triggers = {}
        logger.warning("Using empty expert library")

    def search_by_triggers(self, keywords: List[str]) -> List[Expert]:
        """根据关键词搜索专家"""
        results = []
        for expert in self.experts.values():
            for kw in keywords:
                for trigger in expert.trigger_keywords:
                    if kw.lower() in trigger.lower():
                        results.append(expert)
                        break
                    if kw.lower() in expert.description.lower():
                        if expert not in results:
                            results.append(expert)
                        break
        return results

    def get_by_category(self, category: str) -> List[Expert]:
        """按类别获取专家"""
        return [e for e in self.experts.values() if e.category == category]

    def get_by_ids(self, ids: List[str]) -> List[Expert]:
        """按ID列表获取专家"""
        return [self.experts[i] for i in ids if i in self.experts]

    def get_by_intent(self, text: str) -> List[Expert]:
        """根据文本内容匹配意图，返回相关专家"""
        text_lower = text.lower()
        results = []

        # 检查 intent_triggers
        for pattern, expert_ids in self.intent_triggers.items():
            # 解析模式中的关键词
            keywords = pattern.replace("|", " ").split()
            if any(kw in text_lower for kw in keywords):
                for eid in expert_ids:
                    if eid in self.experts:
                        results.append(self.experts[eid])

        return results


class ThinkingInjector:
    """思维注入引擎 - 核心类"""

    def __init__(self, catalog_path: str = None):
        self.library = ThinkingLibrary(catalog_path)
        self.intent_classifier = IntentClassifier()
        self.max_active_experts = 5

    def process(self, user_input: str, agent_context: Dict[str, Any] = None) -> ThinkingContext:
        """处理用户输入，生成思维注入上下文"""

        context = agent_context or {}
        reasoning_chain = []

        # 1. 意图分类
        reasoning_chain.append("步骤1：意图分类")
        intents = self.intent_classifier.classify(user_input)
        reasoning_chain.append(f"识别意图：{intents}")

        # 2. 选择思维专家
        reasoning_chain.append("步骤2：选择思维专家")
        selected_experts = self._select_experts(user_input, intents, context)
        reasoning_chain.append(f"选中专家：{[e.name_cn for e in selected_experts]}")

        # 3. 生成思维提示
        reasoning_chain.append("步骤3：生成思维提示")
        thinking_prompt = self._generate_prompt(selected_experts, user_input)

        # 4. 查找注入点
        injection_points = self._find_injection_points(context)

        # 5. 计算置信度
        confidence = self._calculate_confidence(selected_experts, intents)

        return ThinkingContext(
            user_input=user_input,
            selected_experts=selected_experts,
            thinking_prompt=thinking_prompt,
            injection_points=injection_points,
            confidence=confidence,
            reasoning_chain=reasoning_chain
        )

    def _select_experts(
        self,
        text: str,
        intents: Dict[str, float],
        context: Dict[str, Any]
    ) -> List[Expert]:
        """根据意图和文本选择最相关的思维专家"""

        candidates = {}

        # 方法1: 从 intent_triggers 匹配
        intent_experts = self.library.get_by_intent(text)
        for expert in intent_experts:
            candidates[expert.id] = expert

        # 方法2: 从意图分类的 keywords 匹配
        for intent, score in intents.items():
            if score >= 0.3:
                # 获取该类别的前几个专家
                category_experts = self.library.get_by_category(intent)
                for expert in category_experts[:3]:
                    if expert.id not in candidates:
                        candidates[expert.id] = expert

        # 方法3: 强制指定专家
        if context.get("forced_experts"):
            for eid in context["forced_experts"]:
                if eid in self.library.experts:
                    candidates[eid] = self.library.experts[eid]

        # 方法4: 文本关键词直接匹配
        text_keywords = self._extract_keywords(text)
        matched = self.library.search_by_triggers(text_keywords)
        for expert in matched:
            if expert.id not in candidates:
                candidates[expert.id] = expert

        # 排序并选择
        selected = list(candidates.values())[:self.max_active_experts]

        logger.info(f"Selected {len(selected)} experts: {[e.id for e in selected]}")

        return selected

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单分词
        words = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', text.lower())
        return words

    def _generate_prompt(self, experts: List[Expert], question: str) -> str:
        """生成包含思维专家的增强提示词"""

        if not experts:
            return question

        prompt_parts = [
            "## 思维增强\n",
            f"当前问题：{question}\n\n",
            "请运用以下思维模型进行分析：\n"
        ]

        for expert in experts:
            prompt_parts.append(f"\n### {expert.name_cn}\n")
            prompt_parts.append(f"{expert.description}\n")
            prompt_parts.append(f"{expert.injection_template}\n")

        prompt_parts.append("\n---\n")
        prompt_parts.append("请结合上述思维模型，给出全面深入的分析。\n")

        return "".join(prompt_parts)

    def _find_injection_points(self, context: Dict[str, Any]) -> List[str]:
        """找到合适的注入点"""
        points = ["system_prompt", "analysis_phase", "output_generation"]
        if context.get("include_review"):
            points.append("output_review")
        return points

    def _calculate_confidence(
        self,
        experts: List[Expert],
        intents: Dict[str, float]
    ) -> float:
        """计算置信度"""
        if not experts or not intents:
            return 0.0

        avg_intent = sum(intents.values()) / len(intents) if intents else 0.5
        expert_coverage = len(experts) / self.max_active_experts

        return min((avg_intent * 0.6 + expert_coverage * 0.4), 1.0)


class CEOThinkingEngine:
    """CEO 专用思维引擎 - 5W1H1Y + MECE 分解"""

    def __init__(self, thinking_injector: ThinkingInjector = None):
        self.injector = thinking_injector or ThinkingInjector()

    def decompose(self, user_input: str) -> Dict[str, Any]:
        """5W1H1Y 拆解 + MECE 分类"""

        decomposition = {
            "What": self._extract_what(user_input),
            "Why": self._extract_why(user_input),
            "Who": self._extract_who(user_input),
            "When": self._extract_when(user_input),
            "Where": self._extract_where(user_input),
            "How": self._extract_how(user_input),
            "Yield": self._extract_yield(user_input)
        }

        mece = self._apply_mece(user_input, decomposition)
        thinking_context = self.injector.process(user_input)

        return {
            "decomposition": decomposition,
            "mece": mece,
            "thinking_context": thinking_context,
            "management_team_suggestion": self._suggest_management_team(decomposition, mece),
            "execution_plan": self._generate_execution_plan(decomposition, mece)
        }

    def _extract_what(self, text: str) -> Dict[str, Any]:
        return {
            "status": "extracted",
            "content": text,
            "questions": ["具体要做什么？", "范围边界在哪里？"]
        }

    def _extract_why(self, text: str) -> Dict[str, Any]:
        return {
            "status": "needs_clarification",
            "content": "",
            "questions": ["为什么要做这件事？", "背后的动机是什么？"]
        }

    def _extract_who(self, text: str) -> Dict[str, Any]:
        return {
            "status": "needs_clarification",
            "content": "",
            "questions": ["团队规模和能力如何？", "谁是决策者？"]
        }

    def _extract_when(self, text: str) -> Dict[str, Any]:
        time_patterns = [r'\d+年', r'\d+月', r'\d+天', r'\d+周', r'\d+季度', r'1年']
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                return {"status": "extracted", "content": match.group(), "questions": []}
        return {"status": "needs_clarification", "content": "", "questions": ["时间限制是什么？"]}

    def _extract_where(self, text: str) -> Dict[str, Any]:
        return {"status": "extracted", "content": "待定（需明确）", "questions": ["线上还是线下？"]}

    def _extract_how(self, text: str) -> Dict[str, Any]:
        return {"status": "needs_clarification", "content": "", "questions": ["具体方法论？", "资源限制？"]}

    def _extract_yield(self, text: str) -> Dict[str, Any]:
        return {"status": "needs_clarification", "content": "", "questions": ["KPI是什么？", "成功标准？"]}

    def _apply_mece(self, user_input: str, decomposition: Dict) -> Dict[str, Any]:
        """MECE 分类"""
        text_lower = user_input.lower()
        categories = []

        if any(kw in text_lower for kw in ["增长", "用户", "获客", "dau", "growth"]):
            categories = [
                {"name": "用户获取", "items": ["渠道策略", "内容营销", "口碑传播"]},
                {"name": "用户激活", "items": ["首次体验", "新手引导"]},
                {"name": "用户留存", "items": ["内容质量", "会员体系"]},
                {"name": "商业变现", "items": ["定价策略", "付费转化"]}
            ]
        elif any(kw in text_lower for kw in ["产品", "功能", "设计"]):
            categories = [
                {"name": "需求分析", "items": ["用户调研", "竞品分析"]},
                {"name": "产品设计", "items": ["交互设计", "视觉设计"]},
                {"name": "技术实现", "items": ["架构设计", "开发实现"]},
                {"name": "发布运营", "items": ["灰度发布", "数据监控"]}
            ]
        else:
            categories = [
                {"name": "机会", "items": ["方向1", "方向2", "方向3"]},
                {"name": "风险", "items": ["风险1", "风险2"]},
                {"name": "资源", "items": ["内部资源", "外部资源"]},
                {"name": "执行", "items": ["短期", "中期", "长期"]}
            ]

        return {"categories": categories, "validation": {"mutually_exclusive": True, "collectively_exhaustive": len(categories) >= 3}}

    def _suggest_management_team(self, decomposition: Dict, mece: Dict) -> List[str]:
        """建议管理层团队"""
        team = ["strategy", "product", "tech"]
        if "tech" in str(mece) or "技术" in str(decomposition):
            team.append("tech")
        return team[:4]

    def _generate_execution_plan(self, decomposition: Dict, mece: Dict) -> Dict[str, Any]:
        return {
            "phase_1": {"name": "澄清与规划", "duration": "1周", "tasks": ["补充未明确的5W1H", "细化MECE分类"]},
            "phase_2": {"name": "快速验证", "duration": "2-4周", "tasks": ["核心假设测试", "Pivot决策点"]},
            "phase_3": {"name": "规模化执行", "duration": "持续", "tasks": ["全面执行", "持续监控优化"]}
        }


if __name__ == "__main__":
    # 测试
    injector = ThinkingInjector()
    engine = CEOThinkingEngine(injector)

    question = "我想做一个在线教育平台，目标是一年内做到10万付费用户"
    result = engine.decompose(question)

    print("=" * 60)
    print(f"选中 {len(result['thinking_context'].selected_experts)} 个思维专家:")
    for e in result['thinking_context'].selected_experts:
        print(f"  - {e.name_cn} ({e.category})")
    print(f"\n置信度: {result['thinking_context'].confidence:.1%}")
