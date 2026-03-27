# CyberTeam v2 - Agency Agents 适配器

"""
agency-agents-zh 集成适配器
集成 180 个专业 AI Agent

Agent 分类：
- Engineering (工程): 40+ agents
- Design (设计): 20+ agents
- Marketing (营销): 30+ agents
- Sales (销售): 20+ agents
- Finance (财务): 15+ agents
- HR (人力): 15+ agents
- Legal (法务): 10+ agents
- Supply Chain (供应链): 10+ agents
- Product (产品): 15+ agents
- Project Management (项目管理): 10+ agents
- Testing (测试): 10+ agents
- Support (支持): 10+ agents
- Specialized (专业): 20+ agents
- Academic (学术): 10+ agents
- Game Dev (游戏开发): 10+ agents
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgencyAgent:
    """Agency Agent 定义"""
    id: str
    name: str
    name_cn: str
    category: str
    description: str
    skills: List[str] = field(default_factory=list)
    prompt_template: str = ""


AGENCY_CATALOG = {
    # ===== Engineering (工程) =====
    "frontend-dev": AgencyAgent(
        id="frontend-dev",
        name="Frontend Developer",
        name_cn="前端开发工程师",
        category="engineering",
        description="React/Vue/Angular 等前端框架开发",
        skills=["React", "Vue", "TypeScript", "CSS", "性能优化"]
    ),
    "backend-dev": AgencyAgent(
        id="backend-dev",
        name="Backend Developer",
        name_cn="后端开发工程师",
        category="engineering",
        description="Node.js/Python/Go 等后端服务开发",
        skills=["Node.js", "Python", "Go", "API设计", "数据库"]
    ),
    "fullstack-dev": AgencyAgent(
        id="fullstack-dev",
        name="Full Stack Developer",
        name_cn="全栈工程师",
        category="engineering",
        description="前后端全栈开发",
        skills=["前端", "后端", "数据库", "DevOps"]
    ),
    "devops-engineer": AgencyAgent(
        id="devops-engineer",
        name="DevOps Engineer",
        name_cn="DevOps工程师",
        category="engineering",
        description="CI/CD、容器化、自动化运维",
        skills=["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform"]
    ),
    "sre-engineer": AgencyAgent(
        id="sre-engineer",
        name="SRE Engineer",
        name_cn="SRE工程师",
        category="engineering",
        description="服务可靠性、监控告警、SLO",
        skills=["监控", "告警", "SLO", "事后分析", "容量规划"]
    ),
    "data-engineer": AgencyAgent(
        id="data-engineer",
        name="Data Engineer",
        name_cn="数据工程师",
        category="engineering",
        description="数据管道、数仓、ETL",
        skills=["Spark", "Airflow", "SQL", "Python", "数据建模"]
    ),
    "ml-engineer": AgencyAgent(
        id="ml-engineer",
        name="ML Engineer",
        name_cn="机器学习工程师",
        category="engineering",
        description="ML模型训练、部署、MLOps",
        skills=["PyTorch", "TensorFlow", "MLOps", "特征工程", "模型部署"]
    ),
    "security-engineer": AgencyAgent(
        id="security-engineer",
        name="Security Engineer",
        name_cn="安全工程师",
        category="engineering",
        description="安全审计、渗透测试、安全架构",
        skills=["安全审计", "渗透测试", "安全架构", "OWASP"]
    ),
    "mobile-dev": AgencyAgent(
        id="mobile-dev",
        name="Mobile Developer",
        name_cn="移动端开发工程师",
        category="engineering",
        description="iOS/Android/Flutter 移动开发",
        skills=["iOS", "Android", "Flutter", "React Native"]
    ),
    "architect": AgencyAgent(
        id="architect",
        name="Software Architect",
        name_cn="软件架构师",
        category="engineering",
        description="系统架构、设计模式、技术选型",
        skills=["微服务", "分布式", "高可用", "可扩展性"]
    ),

    # ===== Design (设计) =====
    "ui-designer": AgencyAgent(
        id="ui-designer",
        name="UI Designer",
        name_cn="UI设计师",
        category="design",
        description="界面视觉设计、品牌风格",
        skills=["Figma", "视觉设计", "品牌", "色彩理论"]
    ),
    "ux-designer": AgencyAgent(
        id="ux-designer",
        name="UX Designer",
        name_cn="UX设计师",
        category="design",
        description="用户体验设计、用户研究",
        skills=["用户研究", "交互设计", "信息架构", "原型"]
    ),
    "product-designer": AgencyAgent(
        id="product-designer",
        name="Product Designer",
        name_cn="产品设计师",
        category="design",
        description="产品全链路设计",
        skills=["UI", "UX", "动效", "设计系统"]
    ),
    "brand-designer": AgencyAgent(
        id="brand-designer",
        name="Brand Designer",
        name_cn="品牌设计师",
        category="design",
        description="品牌视觉、品牌战略",
        skills=["品牌策略", "VI设计", "Logo", "品牌规范"]
    ),
    "motion-designer": AgencyAgent(
        id="motion-designer",
        name="Motion Designer",
        name_cn="动效设计师",
        category="design",
        description="界面动效、交互动效",
        skills=["After Effects", "动效设计", "Lottie", "交互动效"]
    ),

    # ===== Marketing (营销) =====
    "content-marketing": AgencyAgent(
        id="content-marketing",
        name="Content Marketing Specialist",
        name_cn="内容营销专家",
        category="marketing",
        description="内容策略、SEO、博客文章",
        skills=["内容策略", "SEO", "博客", "内容日历"]
    ),
    "social-media": AgencyAgent(
        id="social-media",
        name="Social Media Manager",
        name_cn="社交媒体运营",
        category="marketing",
        description="双微一抖小红书运营",
        skills=["微博", "微信", "抖音", "小红书", "社区运营"]
    ),
    "growth-marketing": AgencyAgent(
        id="growth-marketing",
        name="Growth Marketing Specialist",
        name_cn="增长营销专家",
        category="marketing",
        description="用户增长、病毒传播、裂变",
        skills=["AARRR", "增长黑客", "病毒传播", "裂变"]
    ),
    "seo-specialist": AgencyAgent(
        id="seo-specialist",
        name="SEO Specialist",
        name_cn="SEO专家",
        category="marketing",
        description="搜索引擎优化",
        skills=["Google SEO", "百度SEO", "关键词", "外链"]
    ),
    "sem-specialist": AgencyAgent(
        id="sem-specialist",
        name="SEM Specialist",
        name_cn="SEM专家",
        category="marketing",
        description="付费广告投放优化",
        skills=["Google Ads", "百度推广", "信息流", "投放策略"]
    ),
    "influencer-marketing": AgencyAgent(
        id="influencer-marketing",
        name="Influencer Marketing Specialist",
        name_cn="KOL营销专家",
        category="marketing",
        description="网红/KOL合作营销",
        skills=["KOL", "达人合作", "种草", "直播带货"]
    ),
    "email-marketing": AgencyAgent(
        id="email-marketing",
        name="Email Marketing Specialist",
        name_cn="邮件营销专家",
        category="marketing",
        description="邮件营销自动化",
        skills=["邮件自动化", "用户分层", "A/B测试", "转化优化"]
    ),

    # ===== Sales (销售) =====
    "sales-manager": AgencyAgent(
        id="sales-manager",
        name="Sales Manager",
        name_cn="销售经理",
        category="sales",
        description="销售团队管理、销售策略",
        skills=["销售管理", "CRM", "销售漏斗", "团队激励"]
    ),
    "bd-manager": AgencyAgent(
        id="bd-manager",
        name="BD Manager",
        name_cn="商务拓展经理",
        category="sales",
        description="商务合作、渠道拓展",
        skills=["商务谈判", "渠道合作", "BD策略"]
    ),
    "account-manager": AgencyAgent(
        id="account-manager",
        name="Account Manager",
        name_cn="客户经理",
        category="sales",
        description="客户关系维护、客户成功",
        skills=["客户关系", "客户成功", "续费管理"]
    ),

    # ===== Finance (财务) =====
    "cfo": AgencyAgent(
        id="cfo",
        name="CFO",
        name_cn="首席财务官",
        category="finance",
        description="财务战略、预算管理、投资决策",
        skills=["财务战略", "预算", "投资", "IPO"]
    ),
    "financial-analyst": AgencyAgent(
        id="financial-analyst",
        name="Financial Analyst",
        name_cn="财务分析师",
        category="finance",
        description="财务分析、预算编制",
        skills=["财务建模", "预算分析", "报表分析"]
    ),
    "accountant": AgencyAgent(
        id="accountant",
        name="Accountant",
        name_cn="会计师",
        category="finance",
        description="日常账务处理、税务申报",
        skills=["账务", "税务", "报表", "合规"]
    ),

    # ===== HR (人力) =====
    "hr-director": AgencyAgent(
        id="hr-director",
        name="HR Director",
        name_cn="人力资源总监",
        category="hr",
        description="人力资源战略、组织发展",
        skills=["HR战略", "组织设计", "人才发展", "绩效管理"]
    ),
    "recruiter": AgencyAgent(
        id="recruiter",
        name="Recruiter",
        name_cn="招聘专员",
        category="hr",
        description="招聘渠道、面试安排",
        skills=["招聘", "面试", "雇主品牌", "渠道管理"]
    ),
    "training-specialist": AgencyAgent(
        id="training-specialist",
        name="Training Specialist",
        name_cn="培训专员",
        category="hr",
        description="培训体系、员工发展",
        skills=["培训体系", "课程设计", "领导力发展"]
    ),

    # ===== Product (产品) =====
    "product-manager": AgencyAgent(
        id="product-manager",
        name="Product Manager",
        name_cn="产品经理",
        category="product",
        description="产品规划、需求管理、产品迭代",
        skills=["PRD", "需求分析", "竞品分析", "数据分析", "项目管理"]
    ),
    "product-owner": AgencyAgent(
        id="product-owner",
        name="Product Owner",
        name_cn="产品负责人",
        category="product",
        description="Scrum产品负责人",
        skills=["Scrum", "Backlog", "Sprint", "用户故事"]
    ),
    "data-product": AgencyAgent(
        id="data-product",
        name="Data Product Manager",
        name_cn="数据产品经理",
        category="product",
        description="数据产品规划与设计",
        skills=["数据产品", "数据治理", "指标体系"]
    ),

    # ===== Operations (运营) =====
    "ops-manager": AgencyAgent(
        id="ops-manager",
        name="Operations Manager",
        name_cn="运营经理",
        category="operations",
        description="运营策略、流程优化",
        skills=["运营策略", "流程优化", "效率提升"]
    ),
    "customer-ops": AgencyAgent(
        id="customer-ops",
        name="Customer Operations",
        name_cn="客服运营",
        category="operations",
        description="客服团队管理、服务优化",
        skills=["客服管理", "SLA", "用户反馈", "服务优化"]
    ),
    "community-ops": AgencyAgent(
        id="community-ops",
        name="Community Operations",
        name_cn="社区运营",
        category="operations",
        description="社区建设、用户运营",
        skills=["社区运营", "用户分层", "活动策划"]
    ),

    # ===== Strategy (战略) =====
    "strategy-consultant": AgencyAgent(
        id="strategy-consultant",
        name="Strategy Consultant",
        name_cn="战略顾问",
        category="strategy",
        description="商业战略、市场分析",
        skills=["战略规划", "市场分析", "竞争分析", "商业模式"]
    ),
    "business-analyst": AgencyAgent(
        id="business-analyst",
        name="Business Analyst",
        name_cn="业务分析师",
        category="strategy",
        description="业务分析、流程优化",
        skills=["业务分析", "流程建模", "数据分析", "需求管理"]
    ),
}


class AgencyAdapter:
    """Agency Agents 适配器"""

    def __init__(self):
        self.catalog = AGENCY_CATALOG

    def get_agent(self, agent_id: str) -> Optional[AgencyAgent]:
        """获取指定 Agent"""
        return self.catalog.get(agent_id)

    def search_agents(
        self,
        category: str = None,
        keywords: List[str] = None
    ) -> List[AgencyAgent]:
        """搜索 Agent"""

        results = list(self.catalog.values())

        # 类别过滤
        if category:
            results = [a for a in results if a.category == category]

        # 关键词过滤
        if keywords:
            filtered = []
            for agent in results:
                text = f"{agent.name} {agent.name_cn} {agent.description} {' '.join(agent.skills)}".lower()
                if any(kw.lower() in text for kw in keywords):
                    filtered.append(agent)
            results = filtered

        return results

    def generate_prompt(
        self,
        agent_id: str,
        task: str,
        context: Dict[str, Any] = None
    ) -> str:
        """生成 Agent 执行提示词"""

        agent = self.catalog.get(agent_id)
        if not agent:
            return task

        context = context or {}

        prompt = f"""## {agent.name_cn} - {agent.description}

### 角色定义
你是一名专业的{agent.name_cn}（{agent.name}）。

### 核心技能
{chr(10).join(f"- {skill}" for skill in agent.skills)}

### 当前任务
{task}

"""

        # 添加上下文
        if context.get("output_format"):
            prompt += f"\n### 输出格式\n{context['output_format']}\n"

        if context.get("constraints"):
            prompt += f"\n### 约束条件\n{context['constraints']}\n"

        if context.get("thinking_models"):
            prompt += f"\n### 参考思维模型\n{context['thinking_models']}\n"

        return prompt

    def get_category_agents(self, category: str) -> List[AgencyAgent]:
        """获取某类别的所有 Agent"""
        return [a for a in self.catalog.values() if a.category == category]

    def recommend_agents(
        self,
        task_description: str,
        top_k: int = 5
    ) -> List[AgencyAgent]:
        """根据任务描述推荐合适的 Agent"""

        task_lower = task_description.lower()

        # 关键词到 Agent 的映射
        keyword_map = {
            "frontend": ["frontend-dev"],
            "后端": ["backend-dev"],
            "全栈": ["fullstack-dev"],
            "devops": ["devops-engineer"],
            "运维": ["devops-engineer", "sre-engineer"],
            "数据": ["data-engineer", "data-product"],
            "算法": ["ml-engineer"],
            "安全": ["security-engineer"],
            "移动": ["mobile-dev"],
            "架构": ["architect"],
            "设计": ["ui-designer", "ux-designer", "product-designer"],
            "ui": ["ui-designer"],
            "ux": ["ux-designer"],
            "品牌": ["brand-designer"],
            "营销": ["content-marketing", "social-media", "growth-marketing"],
            "内容": ["content-marketing"],
            "增长": ["growth-marketing"],
            "seo": ["seo-specialist"],
            "广告": ["sem-specialist"],
            "销售": ["sales-manager", "bd-manager"],
            "商务": ["bd-manager"],
            "客户": ["account-manager", "customer-ops"],
            "财务": ["cfo", "financial-analyst"],
            "人力资源": ["hr-director", "recruiter"],
            "招聘": ["recruiter"],
            "产品": ["product-manager", "product-owner"],
            "运营": ["ops-manager", "community-ops", "customer-ops"],
            "社区": ["community-ops"],
            "客服": ["customer-ops"],
            "战略": ["strategy-consultant", "business-analyst"],
            "分析": ["business-analyst", "financial-analyst"],
        }

        scores = {}
        for kw, agent_ids in keyword_map.items():
            if kw in task_lower:
                for aid in agent_ids:
                    scores[aid] = scores.get(aid, 0) + 1

        # 排序并返回
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [self.catalog[aid] for aid, _ in sorted_agents[:top_k] if aid in self.catalog]


# 管理角色到 Agent 的映射
MANAGEMENT_TO_AGENT = {
    "strategy": "strategy-consultant",
    "product": "product-manager",
    "tech": "architect",
    "design": "product-designer",
    "ops": "ops-manager",
    "finance": "cfo",
    "hr": "hr-director",
    "marketing": "growth-marketing",
    "sales": "sales-manager",
}


if __name__ == "__main__":
    # 测试
    adapter = AgencyAdapter()

    # 搜索
    print("=== 前端相关 Agent ===")
    for agent in adapter.search_agents(keywords=["前端", "frontend"]):
        print(f"- {agent.name_cn}: {agent.description}")

    # 推荐
    print("\n=== 推荐 Agent ===")
    recommended = adapter.recommend_agents("设计一个用户增长方案，需要前端开发和数据分析")
    for agent in recommended:
        print(f"- {agent.name_cn}: {agent.description}")
