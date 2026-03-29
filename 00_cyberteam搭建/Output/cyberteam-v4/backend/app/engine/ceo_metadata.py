"""CEO部门Metadata定义 — 部门YAML配置格式。

定义每个部门的技能矩阵、路由规则、Leader配置。
CEO智能路由基于此metadata进行任务分配。
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════════════════════
# 部门Metadata YAML格式定义
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RoutingRule:
    """路由规则 - 关键词触发条件。"""
    keywords: List[str]  # 触发关键词
    weight: float = 1.0  # 匹配权重
    description: str = ""  # 规则描述


@dataclass
class SkillDefinition:
    """技能定义。"""
    skill_id: str
    name: str
    level: int = 3  # 1=专家, 2=总监, 3=专员
    description: str = ""


@dataclass
class LeaderConfig:
    """部门Leader配置。"""
    role: str  # 如"运营总监"
    skills: List[str]  # 所需技能列表
    decision_making: str = "collaborative"  # collaborative/authoritative/delegate


@dataclass
class ExecutorConfig:
    """执行Agent配置。"""
    role: str  # 如"运营专家"
    skills: List[str]  # 执行所需技能
    output_format: str = "markdown"  # markdown/json/report
    review_required: bool = True  # 是否需要封驳审核


@dataclass
class DepartmentMetadata:
    """部门Metadata - 完整定义。"""
    department_id: str
    name: str
    description: str
    responsibility: str  # 核心职责

    # 技能矩阵
    skills: List[SkillDefinition]

    # 路由规则
    routing_rules: List[RoutingRule]

    # 配置
    leader: LeaderConfig
    executor: ExecutorConfig

    # 元数据
    parent_id: Optional[str] = None  # 上级部门
    price_tier: str = "免费"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "department_id": self.department_id,
            "name": self.name,
            "description": self.description,
            "responsibility": self.responsibility,
            "skills": [{"skill_id": s.skill_id, "name": s.name, "level": s.level} for s in self.skills],
            "routing_rules": [
                {"keywords": r.keywords, "weight": r.weight, "description": r.description}
                for r in self.routing_rules
            ],
            "leader": {
                "role": self.leader.role,
                "skills": self.leader.skills,
                "decision_making": self.leader.decision_making,
            },
            "executor": {
                "role": self.executor.role,
                "skills": self.executor.skills,
                "output_format": self.executor.output_format,
                "review_required": self.executor.review_required,
            },
            "parent_id": self.parent_id,
            "price_tier": self.price_tier,
            "tags": self.tags,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 内置部门Metadata (8个部门)
# ═══════════════════════════════════════════════════════════════════════════════

DEPARTMENT_METADATA: Dict[str, DepartmentMetadata] = {

    "ceo": DepartmentMetadata(
        department_id="ceo",
        name="CEO",
        description="首席执行官，负责整体战略和决策",
        responsibility="战略决策、任务分配、资源协调、风险管控",
        skills=[
            SkillDefinition("strategy", "战略规划", 1),
            SkillDefinition("decision", "决策制定", 1),
            SkillDefinition("resource", "资源分配", 1),
            SkillDefinition("risk", "风险管理", 1),
            SkillDefinition("coordination", "任务协调", 1),
        ],
        routing_rules=[
            RoutingRule(["战略", "规划", "顶层设计", "商业模式"], 1.0, "战略相关任务"),
            RoutingRule(["决策", "拍板", "定夺"], 1.0, "决策类任务"),
            RoutingRule(["资源", "分配", "预算"], 0.8, "资源配置任务"),
            RoutingRule(["风险", "危机", "合规"], 0.9, "风险管控任务"),
        ],
        leader=LeaderConfig(
            role="首席执行官",
            skills=["战略规划", "决策制定", "资源分配", "风险管理"],
            decision_making="authoritative",
        ),
        executor=ExecutorConfig(
            role="CEO直接执行",
            skills=["战略规划", "决策制定"],
            output_format="report",
            review_required=False,
        ),
        tags=["战略", "决策", "协调"],
    ),

    "product": DepartmentMetadata(
        department_id="product",
        name="产品部",
        description="需求分析、产品设计、功能规划",
        responsibility="产品规划、需求分析、原型设计、用户研究",
        skills=[
            SkillDefinition("requirement", "需求分析", 2),
            SkillDefinition("planning", "产品规划", 2),
            SkillDefinition("prototype", "原型设计", 3),
            SkillDefinition("user_research", "用户研究", 2),
        ],
        routing_rules=[
            RoutingRule(["产品", "功能", "需求", "PRD", "需求文档"], 1.0, "产品需求任务"),
            RoutingRule(["原型", "设计稿", "交互", "流程图"], 0.9, "原型设计任务"),
            RoutingRule(["用户研究", "调研", "访谈", "问卷"], 0.9, "用户研究任务"),
            RoutingRule(["竞品分析", "产品对比", "功能对比"], 0.8, "竞品分析任务"),
        ],
        leader=LeaderConfig(
            role="产品总监",
            skills=["需求分析", "产品规划", "用户研究"],
            decision_making="collaborative",
        ),
        executor=ExecutorConfig(
            role="产品专家",
            skills=["需求分析", "产品规划", "原型设计"],
            output_format="markdown",
            review_required=True,
        ),
        parent_id="ceo",
        price_tier="基础",
        tags=["产品", "需求", "原型"],
    ),

    "engineering": DepartmentMetadata(
        department_id="engineering",
        name="技术部",
        description="技术方案、架构设计，开发实现",
        responsibility="系统架构、后端开发、前端开发、测试运维",
        skills=[
            SkillDefinition("architecture", "系统架构", 1),
            SkillDefinition("backend", "后端开发", 2),
            SkillDefinition("frontend", "前端开发", 2),
            SkillDefinition("devops", "DevOps", 2),
            SkillDefinition("testing", "测试", 3),
        ],
        routing_rules=[
            RoutingRule(["架构", "系统设计", "技术选型"], 1.0, "架构设计任务"),
            RoutingRule(["用户登录", "登录功能", "功能开发", "代码", "实现", "开发"], 1.0, "开发任务"),
            RoutingRule(["前端", "React", "Vue", "页面"], 0.9, "前端任务"),
            RoutingRule(["后端", "API", "数据库", "服务", "登录", "认证"], 0.9, "后端任务"),
            RoutingRule(["测试", "UT", "集成测试", "e2e"], 0.8, "测试任务"),
            RoutingRule(["部署", "CI/CD", "Docker", "K8s"], 0.8, "运维任务"),
        ],
        leader=LeaderConfig(
            role="技术总监",
            skills=["系统架构", "后端开发", "前端开发"],
            decision_making="authoritative",
        ),
        executor=ExecutorConfig(
            role="技术专家",
            skills=["后端开发", "前端开发"],
            output_format="code",
            review_required=True,
        ),
        parent_id="ceo",
        price_tier="专业",
        tags=["技术", "开发", "架构"],
    ),

    "design": DepartmentMetadata(
        department_id="design",
        name="设计部",
        description="UI设计、用户体验，品牌视觉",
        responsibility="UI设计、UX设计、品牌视觉、动效设计",
        skills=[
            SkillDefinition("ui", "UI设计", 2),
            SkillDefinition("ux", "UX设计", 2),
            SkillDefinition("brand", "品牌设计", 2),
            SkillDefinition("motion", "动效设计", 3),
        ],
        routing_rules=[
            RoutingRule(["设计", "UI", "界面", "视觉"], 1.0, "UI设计任务"),
            RoutingRule(["用户体验", "UX", "交互", "体验优化"], 0.9, "UX任务"),
            RoutingRule(["品牌", "VI", "Logo", "视觉规范"], 0.9, "品牌设计任务"),
            RoutingRule(["海报", "Banner", "运营图"], 0.8, "运营设计任务"),
        ],
        leader=LeaderConfig(
            role="设计总监",
            skills=["UI设计", "UX设计", "品牌设计"],
            decision_making="collaborative",
        ),
        executor=ExecutorConfig(
            role="设计专家",
            skills=["UI设计", "UX设计"],
            output_format="image",
            review_required=True,
        ),
        parent_id="ceo",
        price_tier="基础",
        tags=["设计", "UI", "UX"],
    ),

    "operations": DepartmentMetadata(
        department_id="operations",
        name="运营部",
        description="用户增长、内容运营、活动策划",
        responsibility="用户增长、内容运营、活动策划、数据分析",
        skills=[
            SkillDefinition("growth", "用户运营", 2),
            SkillDefinition("content", "内容运营", 2),
            SkillDefinition("activity", "活动策划", 2),
            SkillDefinition("data", "数据分析", 2),
        ],
        routing_rules=[
            RoutingRule(["运营", "增长", "拉新", "留存", "促活"], 1.0, "运营任务"),
            RoutingRule(["内容", "文案", "内容创作", "选题"], 0.9, "内容运营任务"),
            RoutingRule(["活动", "策划", "方案", " Campaign"], 1.0, "活动策划任务"),
            RoutingRule(["数据", "分析", "报表", "指标"], 0.8, "数据分析任务"),
            RoutingRule(["用户画像", "标签", "分层"], 0.8, "用户研究任务"),
        ],
        leader=LeaderConfig(
            role="运营总监",
            skills=["用户运营", "活动策划", "数据分析"],
            decision_making="collaborative",
        ),
        executor=ExecutorConfig(
            role="运营专家",
            skills=["内容运营", "活动策划"],
            output_format="markdown",
            review_required=True,
        ),
        parent_id="ceo",
        price_tier="免费",
        tags=["运营", "增长", "内容"],
    ),

    "marketing": DepartmentMetadata(
        department_id="marketing",
        name="市场部",
        description="市场营销，品牌推广、渠道拓展",
        responsibility="品牌营销、效果营销、内容营销、渠道推广",
        skills=[
            SkillDefinition("brand_marketing", "品牌营销", 2),
            SkillDefinition("performance_marketing", "效果营销", 2),
            SkillDefinition("content_marketing", "内容营销", 2),
            SkillDefinition("channel", "渠道推广", 2),
        ],
        routing_rules=[
            RoutingRule(["市场", "营销", "推广", "获客", "推广方案", "营销方案", "品牌推广方案", "品牌方案"], 1.0, "市场营销任务"),
            RoutingRule(["品牌", "品牌定位", "品牌建设"], 0.9, "品牌营销任务"),
            RoutingRule(["投放", "广告", "SEM", "信息流"], 0.9, "效果营销任务"),
            RoutingRule(["渠道", "分发", "BD", "合作"], 0.8, "渠道任务"),
            RoutingRule(["小红书", "抖音", "微信", "微博"], 0.7, "社交营销任务"),
        ],
        leader=LeaderConfig(
            role="市场总监",
            skills=["品牌营销", "效果营销", "渠道推广"],
            decision_making="authoritative",
        ),
        executor=ExecutorConfig(
            role="营销专家",
            skills=["内容营销", "渠道推广"],
            output_format="markdown",
            review_required=True,
        ),
        parent_id="ceo",
        price_tier="基础",
        tags=["营销", "品牌", "渠道"],
    ),

    "finance": DepartmentMetadata(
        department_id="finance",
        name="财务部",
        description="预算规划，成本控制，投资分析",
        responsibility="预算管理、成本控制、财务分析、投资决策",
        skills=[
            SkillDefinition("budget", "预算管理", 1),
            SkillDefinition("cost_control", "成本控制", 2),
            SkillDefinition("financial_analysis", "财务分析", 2),
            SkillDefinition("investment", "投资决策", 1),
        ],
        routing_rules=[
            RoutingRule(["财务", "预算", "成本", "支出"], 1.0, "财务任务"),
            RoutingRule(["投资", "融资", "估值", "回报"], 0.9, "投资分析任务"),
            RoutingRule(["盈利", "收入", "利润", "亏损"], 0.8, "盈利分析任务"),
            RoutingRule(["报表", "财务报表", "审计"], 0.9, "报表任务"),
        ],
        leader=LeaderConfig(
            role="财务总监",
            skills=["预算管理", "财务分析", "投资决策"],
            decision_making="authoritative",
        ),
        executor=ExecutorConfig(
            role="财务专家",
            skills=["成本控制", "财务分析"],
            output_format="report",
            review_required=True,
        ),
        parent_id="ceo",
        price_tier="专业",
        tags=["财务", "预算", "投资"],
    ),

    "hr": DepartmentMetadata(
        department_id="hr",
        name="人力部",
        description="招聘方案、团队激励，文化建设",
        responsibility="招聘猎才、培训发展、绩效考核、团队建设",
        skills=[
            SkillDefinition("recruit", "招聘猎才", 2),
            SkillDefinition("training", "培训发展", 2),
            SkillDefinition("performance", "绩效考核", 2),
            SkillDefinition("culture", "文化建设", 2),
        ],
        routing_rules=[
            RoutingRule(["招聘", "猎头", "人才", "JD"], 1.0, "招聘任务"),
            RoutingRule(["培训", "学习", "课程", "提升"], 0.9, "培训任务"),
            RoutingRule(["绩效", "KPI", "OKR", "考核"], 0.9, "绩效任务"),
            RoutingRule(["团队", "文化建设", "氛围", "凝聚力"], 0.8, "文化建设任务"),
        ],
        leader=LeaderConfig(
            role="人力总监",
            skills=["招聘", "培训发展", "绩效考核"],
            decision_making="collaborative",
        ),
        executor=ExecutorConfig(
            role="人力专家",
            skills=["招聘", "培训"],
            output_format="document",
            review_required=True,
        ),
        parent_id="ceo",
        price_tier="免费",
        tags=["人力", "招聘", "培训"],
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# CEO智能路由引擎
# ═══════════════════════════════════════════════════════════════════════════════


class CEORouter:
    """CEO智能路由引擎。

    基于任务内容和部门Metadata进行智能路由。
    """

    def __init__(self):
        self.departments = DEPARTMENT_METADATA

    def route(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """路由任务到最合适的部门。

        Args:
            task: 任务描述
            context: 上下文信息 (可选)

        Returns:
            路由结果包含: target_department, match_score, reasoning
        """
        task_lower = task.lower()

        # 计算每个部门的匹配分数
        scores = {}
        for dept_id, metadata in self.departments.items():
            if dept_id == "ceo":
                # CEO默认处理战略级任务
                scores[dept_id] = self._calculate_score(task_lower, metadata, context)
                continue

            score = self._calculate_score(task_lower, metadata, context)
            if score > 0:
                scores[dept_id] = score

        if not scores:
            # 默认路由到operations
            return {
                "target_department": "operations",
                "match_score": 0.0,
                "reasoning": "无匹配部门，默认路由到运营部",
                "alternative_departments": [],
            }

        # 排序
        sorted_depts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_dept = sorted_depts[0]

        return {
            "target_department": top_dept[0],
            "match_score": top_dept[1],
            "reasoning": self._generate_reasoning(task, top_dept[0]),
            "alternative_departments": [
                {"department_id": d[0], "score": d[1]}
                for d in sorted_depts[1:4] if d[1] > 0.1
            ],
        }

    def _calculate_score(
        self,
        task: str,
        metadata: DepartmentMetadata,
        context: Optional[Dict[str, Any]],
    ) -> float:
        """计算任务与部门的匹配分数。"""
        score = 0.0
        matched_rules = []

        for rule in metadata.routing_rules:
            for keyword in rule.keywords:
                if keyword.lower() in task:
                    score += rule.weight
                    matched_rules.append(keyword)
                    break  # 每个rule只计算一次

        # 检查技能匹配
        if context and "required_skills" in context:
            required_skills = context["required_skills"]
            available_skills = [s.skill_id for s in metadata.skills]
            skill_match = len(set(required_skills) & set(available_skills)) / len(required_skills)
            score += skill_match * 0.5

        # 检查标签匹配
        if context and "tags" in context:
            tag_match = len(set(context["tags"]) & set(metadata.tags)) / len(context["tags"])
            score += tag_match * 0.3

        return score

    def _generate_reasoning(self, task: str, department_id: str) -> str:
        """生成路由理由。"""
        metadata = self.departments.get(department_id)
        if not metadata:
            return "无法生成理由"

        matched_keywords = []
        for rule in metadata.routing_rules:
            for keyword in rule.keywords:
                if keyword.lower() in task.lower():
                    matched_keywords.append(keyword)
                    break

        if matched_keywords:
            return f"命中关键词: {', '.join(matched_keywords)}，适合{metadata.name}的{metadata.responsibility}"
        else:
            return f"根据任务内容，{metadata.name}最合适负责: {metadata.responsibility}"

    def get_department_metadata(self, department_id: str) -> Optional[Dict[str, Any]]:
        """获取部门Metadata。"""
        metadata = self.departments.get(department_id)
        return metadata.to_dict() if metadata else None

    def list_all_departments(self) -> List[Dict[str, Any]]:
        """列出所有部门Metadata。"""
        return [m.to_dict() for m in self.departments.values()]


# 全局路由实例
ceo_router = CEORouter()
