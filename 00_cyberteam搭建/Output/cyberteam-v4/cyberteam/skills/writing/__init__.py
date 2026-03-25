"""Writing Skill - 转化型文案创作技能。

提供完整的9阶段文案创作工作流。
"""

from typing import Any, Dict, Optional
from cyberteam.skills.base import WritingSkill, SkillMetadata


class WritingSkillImpl(WritingSkill):
    """Writing Skill 实现

    转化型文案创作的完整执行指南。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="writing",
            description="Writing Skill：转化型文案创作的完整9阶段工作流",
            version="3.1",
            tags=["文案", "写作", "营销", "转化"],
            triggers=[
                "核心营销战役与新品上市",
                "高价值转化型内容",
                "重要品牌或公关沟通",
                "体系化内容运营建设"
            ],
            requires=[]
        )
        super().__init__(metadata)
        self.current_stage = 0
        self.workflow_data: Dict[str, Any] = {}

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行写作工作流"""
        self.initialize()

        if isinstance(input_data, dict):
            action = input_data.get("action", "help")
        else:
            action = "help"

        if action == "new":
            return await self.start_new_workflow(input_data)
        elif action == "stage":
            stage = input_data.get("stage", 0)
            return await self.execute_stage(stage, input_data.get("data"))
        else:
            return self.get_help()

    async def start_new_workflow(self, task: Any) -> Dict[str, Any]:
        """开始新的文案工作流"""
        self.current_stage = 0
        self.workflow_data = {
            "status": "initialized",
            "task": task,
            "stages_completed": []
        }
        return {
            "message": "文案创作工作流已初始化",
            "current_stage": 0,
            "next_stage": 1,
            "stages": self.get_stage_descriptions()
        }

    async def execute_stage(self, stage: int, data: Any = None) -> Any:
        """执行指定阶段"""
        self.current_stage = stage

        stage_handlers = {
            0: self.stage_0_init,
            1: self.stage_1_user_research,
            2: self.stage_2_selling_points,
            3: self.stage_3_pain_points,
            4: self.stage_4_strategy,
            5: self.stage_5_channel,
            6: self.stage_6_draft,
            7: self.stage_7_optimize,
            8: self.stage_8_tracking,
        }

        handler = stage_handlers.get(stage)
        if handler:
            result = await handler(data)
            if result:
                self.workflow_data["stages_completed"].append(stage)
            return result

        return {"error": f"Unknown stage: {stage}"}

    def get_help(self) -> Dict[str, Any]:
        """获取帮助信息"""
        return {
            "name": "Writing Skill",
            "version": "3.1",
            "description": "转化型文案创作的完整9阶段工作流",
            "stages": self.get_stage_descriptions(),
            "usage": {
                "new": "开始新的文案创作工作流",
                "stage": "执行指定阶段 {stage: 0-8}"
            }
        }

    @staticmethod
    def get_stage_descriptions() -> Dict[int, str]:
        """获取各阶段描述"""
        return {
            0: "工作流初始化 - 确认需求，初始化配置",
            1: "用户需求挖掘 - 深度分析目标人群",
            2: "产品卖点挖掘 - 提取核心差异化卖点",
            3: "痛点定位 - 精准匹配用户痛点",
            4: "需求类型判断 - 确定说服逻辑",
            5: "场景与渠道分析 - 确定内容形式",
            6: "文案撰写 - 产出初稿",
            7: "文案优化 - 审核校对",
            8: "效果追踪 - 复盘迭代"
        }


# Skill 实例
writing_skill = WritingSkillImpl()


async def execute(input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
    """Skill 执行入口"""
    return await writing_skill.execute(input_data, context)
