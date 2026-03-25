#!/usr/bin/env python3
"""
CyberTeam V4 - Strategy 引擎 (L2-策略层)

职责：
1. 5W1H1Y 需求分析
2. MECE 任务拆解
3. 方案设计 (选择思维框架)
4. 输出执行方案 JSON
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


class TaskCategory(Enum):
    STRATEGY = "战略分析"
    DECISION = "决策分析"
    EXECUTION = "执行规划"
    CONTENT = "内容创作"
    DATA = "数据分析"


class ThinkingFramework(Enum):
    SWOT = "SWOT分析"
    PORTER_FIVE = "波特五力"
    BCG = "BCG矩阵"
    FIRST_PRINCIPLE = "第一性原理"
    FIVE_WHY = "5Why分析"
    SIX_HATS = "六顶思考帽"
    REVERSE = "逆向思维"
    WBS = "WBS任务分解"
    OKR = "OKR目标管理"
    PDCA = "PDCA循环"
    MECE = "MECE原则"


@dataclass
class Decomposition:
    """5W1H1Y 分解结果"""
    what: str = ""
    why: str = ""
    who: str = ""
    when: str = ""
    where: str = ""
    how: str = ""
    how_much: str = ""
    status: dict = field(default_factory=lambda: {
        "what": "pending",
        "why": "pending",
        "who": "pending",
        "when": "pending",
        "where": "pending",
        "how": "pending",
        "how_much": "pending"
    })


@dataclass
class MECEOutput:
    """MECE 分类结果"""
    categories: List[dict] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """执行方案"""
    task_id: str
    title: str
    intent: str
    complexity: str
    decomposition: Decomposition
    mece: MECEOutput
    framework: ThinkingFramework
    schedule: List[dict] = field(default_factory=list)
    resources: Dict[str, any] = field(default_factory=dict)


class StrategyEngine:
    """Strategy 需求分析和方案设计引擎"""

    # 任务类型到思维框架的映射
    FRAMEWORK_MAP = {
        (TaskCategory.STRATEGY, "高"): [ThinkingFramework.SWOT, ThinkingFramework.PORTER_FIVE],
        (TaskCategory.STRATEGY, "中"): [ThinkingFramework.SWOT],
        (TaskCategory.DECISION, "高"): [ThinkingFramework.FIRST_PRINCIPLE, ThinkingFramework.REVERSE],
        (TaskCategory.DECISION, "中"): [ThinkingFramework.FIVE_WHY],
        (TaskCategory.EXECUTION, "高"): [ThinkingFramework.WBS, ThinkingFramework.OKR],
        (TaskCategory.EXECUTION, "中"): [ThinkingFramework.PDCA],
        (TaskCategory.CONTENT, "高"): [ThinkingFramework.SIX_HATS, ThinkingFramework.MECE],
        (TaskCategory.CONTENT, "中"): [ThinkingFramework.MECE],
        (TaskCategory.DATA, "高"): [ThinkingFramework.WBS, ThinkingFramework.FIVE_WHY],
        (TaskCategory.DATA, "中"): [ThinkingFramework.MECE]
    }

    def __init__(self):
        self.default_framework = ThinkingFramework.MECE

    def analyze_5w1h1y(self, user_input: str, intent: str) -> Decomposition:
        """5W1H1Y 需求分析"""

        # 基础分析 (TODO: 实际调用 LLM 进行分析)
        decomposition = Decomposition()

        # What: 任务是什么
        decomposition.what = user_input
        decomposition.status["what"] = "extracted"

        # Why: 为什么要做
        decomposition.why = "用户目标驱动"
        decomposition.status["why"] = "extracted"

        # Who: 谁来做 (根据意图)
        who_map = {
            "数据分析": "数据分析部",
            "内容运营": "内容运营部",
            "技术研发": "技术研发部",
            "安全合规": "安全合规部"
        }
        decomposition.who = who_map.get(intent, "多部门协作")
        decomposition.status["who"] = "extracted"

        # When: 时间要求
        decomposition.when = "待确定"
        decomposition.status["when"] = "pending"

        # Where: 执行环境
        decomposition.where = "内部系统"
        decomposition.status["where"] = "extracted"

        # How: 怎么做
        decomposition.how = "部门协作执行"
        decomposition.status["how"] = "extracted"

        # How Much: 资源需求
        decomposition.how_much = "待评估"
        decomposition.status["how_much"] = "pending"

        return decomposition

    def mece_decompose(self, task: str, intent: str) -> MECEOutput:
        """MECE 任务拆解"""

        # 基于意图创建分类
        categories = []

        if intent == "数据分析":
            categories = [
                {"name": "数据收集", "items": ["数据源确定", "数据提取", "数据清洗"]},
                {"name": "分析建模", "items": ["指标计算", "趋势分析", "归因分析"]},
                {"name": "结论输出", "items": ["洞察提炼", "建议生成", "报告撰写"]}
            ]
        elif intent == "内容运营":
            categories = [
                {"name": "用户洞察", "items": ["用户画像", "需求分析", "场景挖掘"]},
                {"name": "内容策划", "items": ["选题确定", "结构设计", "卖点提炼"]},
                {"name": "执行发布", "items": ["文案撰写", "审核校对", "多平台发布"]}
            ]
        elif intent == "技术研发":
            categories = [
                {"name": "需求分析", "items": ["功能定义", "技术方案", "架构设计"]},
                {"name": "开发实现", "items": ["编码实现", "单元测试", "集成测试"]},
                {"name": "部署运维", "items": ["灰度发布", "监控告警", "日志分析"]}
            ]
        else:
            # 默认三分法
            categories = [
                {"name": "规划", "items": ["目标设定", "资源评估", "计划制定"]},
                {"name": "执行", "items": ["任务分解", "进度跟踪", "质量控制"]},
                {"name": "复盘", "items": ["结果评估", "经验总结", "优化建议"]}
            ]

        return MECEOutput(categories=categories)

    def select_framework(self, intent: str, complexity: str) -> ThinkingFramework:
        """选择思维框架"""

        # 映射到任务类别
        category_map = {
            "数据分析": TaskCategory.DATA,
            "内容运营": TaskCategory.CONTENT,
            "技术研发": TaskCategory.EXECUTION,
            "安全合规": TaskCategory.STRATEGY,
            "战略规划": TaskCategory.STRATEGY,
            "人力资源": TaskCategory.STRATEGY,
            "运营支持": TaskCategory.EXECUTION
        }

        category = category_map.get(intent, TaskCategory.EXECUTION)
        key = (category, complexity)

        # 查找匹配的框架
        if key in self.FRAMEWORK_MAP:
            return self.FRAMEWORK_MAP[key][0]

        return self.default_framework

    def design_schedule(self, plan: ExecutionPlan) -> List[dict]:
        """设计执行时间表"""

        schedule = []

        # 基础阶段
        schedule.append({
            "phase": "Phase 1",
            "name": "需求确认",
            "duration": "10分钟",
            "tasks": ["确认用户需求", "澄清疑问"]
        })

        if plan.complexity == "高":
            schedule.append({
                "phase": "Phase 2",
                "name": "专家论证",
                "duration": "30分钟",
                "tasks": ["多角度分析", "方案辩论"]
            })

        schedule.append({
            "phase": "Phase 3" if plan.complexity == "高" else "Phase 2",
            "name": "方案设计",
            "duration": "20分钟",
            "tasks": ["制定执行方案", "风险评估"]
        })

        schedule.append({
            "phase": "Phase 4" if plan.complexity == "高" else "Phase 3",
            "name": "执行实施",
            "duration": "待定",
            "tasks": ["部门执行", "进度监控"]
        })

        schedule.append({
            "phase": "Phase 5" if plan.complexity == "高" else "Phase 4",
            "name": "结果交付",
            "duration": "10分钟",
            "tasks": ["结果汇总", "交付用户"]
        })

        return schedule

    def create_plan(
        self,
        task_id: str,
        user_input: str,
        intent: str,
        complexity: str
    ) -> ExecutionPlan:
        """创建完整执行方案"""

        # 5W1H1Y 分析
        decomposition = self.analyze_5w1h1y(user_input, intent)

        # MECE 拆解
        mece = self.mece_decompose(user_input, intent)

        # 选择思维框架
        framework = self.select_framework(intent, complexity)

        # 创建方案
        plan = ExecutionPlan(
            task_id=task_id,
            title=user_input[:50] + "..." if len(user_input) > 50 else user_input,
            intent=intent,
            complexity=complexity,
            decomposition=decomposition,
            mece=mece,
            framework=framework
        )

        # 设计执行计划
        plan.schedule = self.design_schedule(plan)

        # 资源需求
        plan.resources = {
            "departments": self._infer_departments(intent),
            "skills": self._infer_skills(intent),
            "agents": self._infer_agents(intent, complexity)
        }

        return plan

    def _infer_departments(self, intent: str) -> List[str]:
        """推断需要的部门"""
        dept_map = {
            "数据分析": ["数据分析部"],
            "内容运营": ["内容运营部", "设计创意部"],
            "技术研发": ["技术研发部", "运维部署部"],
            "安全合规": ["安全合规部"],
            "战略规划": ["战略规划部", "项目管理部"],
            "人力资源": ["人力资源部"],
            "运营支持": ["运营支持部"]
        }
        return dept_map.get(intent, ["战略规划部"])

    def _infer_skills(self, intent: str) -> List[str]:
        """推断需要的 Skills"""
        skill_map = {
            "数据分析": ["/aarrr-growth-model", "/ice-scoring"],
            "内容运营": ["/baoyu-post-to-wechat", "/baoyu-image-gen"],
            "技术研发": ["/codex", "/review", "/qa"],
            "安全合规": ["/cso"]
        }
        return skill_map.get(intent, [])

    def _infer_agents(self, intent: str, complexity: str) -> List[str]:
        """推断需要的 Agents"""
        if complexity == "高":
            return ["gsd-planner", "gsd-executor"]
        return ["gsd-executor"]


def main():
    """CLI 测试"""
    import sys
    import uuid

    engine = StrategyEngine()

    # 测试参数
    task_id = str(uuid.uuid4())[:8]
    user_input = sys.argv[1] if len(sys.argv) > 1 else "帮我分析下季度增长策略"
    intent = "数据分析"
    complexity = "高"

    print("\n" + "=" * 50)
    print("Strategy 方案设计")
    print("=" * 50)

    # 创建方案
    plan = engine.create_plan(task_id, user_input, intent, complexity)

    # 输出结果
    print(f"\n任务ID: {plan.task_id}")
    print(f"标题: {plan.title}")
    print(f"意图: {plan.intent}")
    print(f"复杂度: {plan.complexity}")

    print(f"\n【5W1H1Y 分析】")
    print(f"  What: {plan.decomposition.what}")
    print(f"  Why: {plan.decomposition.why}")
    print(f"  Who: {plan.decomposition.who}")
    print(f"  When: {plan.decomposition.when}")
    print(f"  Where: {plan.decomposition.where}")
    print(f"  How: {plan.decomposition.how}")
    print(f"  How Much: {plan.decomposition.how_much}")

    print(f"\n【MECE 分类】")
    for cat in plan.mece.categories:
        print(f"\n  【{cat['name']}】")
        for item in cat.get("items", []):
            print(f"    - {item}")

    print(f"\n【思维框架】: {plan.framework.value}")

    print(f"\n【执行计划】")
    for phase in plan.schedule:
        print(f"\n  【{phase['phase']}】{phase['name']} ({phase['duration']})")
        for task in phase['tasks']:
            print(f"    - {task}")

    print(f"\n【资源需求】")
    print(f"  部门: {plan.resources['departments']}")
    print(f"  Skills: {plan.resources['skills']}")
    print(f"  Agents: {plan.resources['agents']}")


if __name__ == "__main__":
    main()
