"""
Skill 注册表

管理所有可用的技能
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """技能定义"""
    id: str
    name: str  # 技能名称
    description: str  # 技能描述
    category: str  # 分类：analysis, writing, execution, research
    prompt_template: str  # 调用此技能时的提示词模板
    keywords: list[str] = field(default_factory=list)  # 触发关键词
    tools: list[str] = field(default_factory=list)  # 可用工具
    examples: list[str] = field(default_factory=list)  # 使用示例

    def match(self, task: str) -> float:
        """计算任务与技能的匹配度"""
        task_lower = task.lower()
        score = 0.0

        # 关键词匹配
        for kw in self.keywords:
            if kw.lower() in task_lower:
                score += 1.0

        return score


class SkillRegistry:
    """技能注册表"""

    def __init__(self):
        self.skills: dict[str, Skill] = {}
        self._init_default_skills()

    def _init_default_skills(self):
        """初始化默认技能"""
        skills = [
            Skill(
                id="analysis",
                name="分析技能",
                description="分析问题、制定策略、风险评估",
                category="analysis",
                prompt_template="你是一个专业的分析师。请对以下任务进行全面分析：\n\n{task}\n\n请提供：\n1. 问题分析\n2. 方案选项\n3. 建议方案\n4. 风险提示",
                keywords=["分析", "评估", "策略", "方案", "风险", "建议"],
                examples=["分析市场趋势", "评估项目风险", "制定营销策略"]
            ),
            Skill(
                id="writing",
                name="写作技能",
                description="文案撰写、内容创作、文档编写",
                category="writing",
                prompt_template="你是一个专业的文案专家。请根据以下任务创作内容：\n\n{task}\n\n要求：\n1. 语言流畅\n2. 重点突出\n3. 适合目标受众",
                keywords=["写", "文案", "内容", "创作", "报告", "方案"],
                examples=["写一篇推广文案", "创建项目报告", "撰写产品说明"],
                tools=["claude_writer"]
            ),
            Skill(
                id="research",
                name="调研技能",
                description="信息收集、数据分析、竞品调研",
                category="research",
                prompt_template="你是一个专业的市场调研分析师。请调研以下内容：\n\n{task}\n\n请提供：\n1. 信息来源\n2. 关键数据\n3. 结论建议",
                keywords=["调研", "调查", "搜索", "研究", "分析数据", "竞品"],
                examples=["调研竞争对手", "调查用户需求", "搜索市场数据"],
                tools=["web_search"]
            ),
            Skill(
                id="coding",
                name="编程技能",
                description="代码编写、技术方案、架构设计",
                category="execution",
                prompt_template="你是一个资深技术专家。请处理以下技术任务：\n\n{task}\n\n请提供：\n1. 解决方案\n2. 代码实现\n3. 关键说明",
                keywords=["代码", "编程", "开发", "技术", "架构", "实现"],
                examples=["写一个排序算法", "设计系统架构", "修复bug"],
                tools=["code_editor"]
            ),
            Skill(
                id="execution",
                name="执行技能",
                description="任务执行、流程自动化、操作指导",
                category="execution",
                prompt_template="你是一个执行专家。请完成以下任务：\n\n{task}\n\n请：\n1. 明确步骤\n2. 给出结果\n3. 说明注意事项",
                keywords=["执行", "完成", "做", "实现", "操作", "处理"],
                examples=["执行市场推广", "完成数据整理", "处理客户问题"],
                tools=["task_runner"]
            ),
        ]

        for skill in skills:
            self.skills[skill.id] = skill
        logger.info(f"Initialized {len(skills)} skills")

    def register(self, skill: Skill):
        """注册技能"""
        self.skills[skill.id] = skill

    def get(self, skill_id: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(skill_id)

    def find_best_match(self, task: str) -> Optional[Skill]:
        """找到最佳匹配的技能"""
        if not task:
            return None

        best_score = 0.0
        best_skill = None

        for skill in self.skills.values():
            score = skill.match(task)
            if score > best_score:
                best_score = score
                best_skill = skill

        # 至少需要0.5分才匹配
        if best_score >= 0.5:
            return best_skill

        # 默认返回写作技能
        return self.skills.get("writing")

    def list_by_category(self, category: str) -> list[Skill]:
        """按分类列出技能"""
        return [s for s in self.skills.values() if s.category == category]

    def list_all(self) -> list[Skill]:
        """列出所有技能"""
        return list(self.skills.values())

    def build_prompt(self, task: str) -> str:
        """根据任务构建提示词"""
        skill = self.find_best_match(task)

        if skill:
            return skill.prompt_template.format(task=task)

        # 如果没有匹配，返回默认提示词
        return f"请处理以下任务：\n\n{task}"


# 全局技能注册表
skill_registry = SkillRegistry()
