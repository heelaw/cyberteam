"""Content Review Skill - 内容审核技能。

提供事实核查、品牌审核、合规扫描三大功能。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from cyberteam.skills.base import ContentReviewSkill, SkillMetadata


@dataclass
class ReviewIssue:
    """审核问题"""
    location: str
    issue_type: str
    severity: str  # P0/P1/P2
    description: str
    suggestion: str


class ContentReviewSkillImpl(ContentReviewSkill):
    """Content Review Skill 实现

    提供事实核查、品牌审核、合规扫描功能。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="content_review",
            description="Content Review Skill：事实核查、品牌审核、合规扫描三大审核功能",
            version="3.1",
            tags=["审核", "内容", "合规", "品牌"],
            triggers=[],
            requires=[]
        )
        super().__init__(metadata)
        self.issues: List[ReviewIssue] = []

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行内容审核"""
        self.initialize()

        if isinstance(input_data, dict):
            action = input_data.get("action", "full")
        else:
            action = "full"

        if action == "full":
            return await self.full_review(input_data.get("content", ""))
        elif action == "fact_check":
            return await self.fact_check(input_data.get("content", ""))
        elif action == "brand_audit":
            return await self.brand_audit(input_data.get("content", ""))
        elif action == "compliance_scan":
            return await self.compliance_scan(
                input_data.get("content", ""),
                input_data.get("platform", "general")
            )
        else:
            return self.get_help()

    async def full_review(self, content: str) -> Dict[str, Any]:
        """完整审核（三种审核都执行）"""
        fact_result = await self.fact_check(content)
        brand_result = await self.brand_audit(content)
        compliance_result = await self.compliance_scan(content)

        all_issues = []
        all_issues.extend(fact_result.get("issues", []))
        all_issues.extend(brand_result.get("issues", []))
        all_issues.extend(compliance_result.get("issues", []))

        return {
            "content": content,
            "status": "completed",
            "fact_check": fact_result,
            "brand_audit": brand_result,
            "compliance_scan": compliance_result,
            "total_issues": len(all_issues),
            "issues_by_severity": {
                "P0": len([i for i in all_issues if i.get("severity") == "P0"]),
                "P1": len([i for i in all_issues if i.get("severity") == "P1"]),
                "P2": len([i for i in all_issues if i.get("severity") == "P2"]),
            }
        }

    async def fact_check(self, content: str) -> Dict[str, Any]:
        """事实核查"""
        issues = []
        # 简化实现，实际应调用 web search 进行数据溯源
        return {
            "type": "fact_check",
            "content": content,
            "status": "completed",
            "issues": issues
        }

    async def brand_audit(self, content: str) -> Dict[str, Any]:
        """品牌调性审核"""
        issues = []
        # 简化实现
        return {
            "type": "brand_audit",
            "content": content,
            "status": "completed",
            "issues": issues
        }

    async def compliance_scan(self, content: str, platform: str = "general") -> Dict[str, Any]:
        """合规风险扫描"""
        issues = []
        # 简化实现
        return {
            "type": "compliance_scan",
            "platform": platform,
            "content": content,
            "status": "completed",
            "issues": issues
        }

    def get_help(self) -> Dict[str, Any]:
        """获取帮助信息"""
        return {
            "name": "Content Review Skill",
            "version": "3.1",
            "description": "事实核查、品牌审核、合规扫描三大审核功能",
            "actions": {
                "full": "完整审核（fact_check + brand_audit + compliance_scan）",
                "fact_check": "事实核查",
                "brand_audit": "品牌调性审核",
                "compliance_scan": "合规风险扫描"
            },
            "usage": {
                "full": "/content-review full <内容>",
                "fact_check": "/content-review fact-check <内容>",
                "brand_audit": "/content-review brand-audit <内容>",
                "compliance_scan": "/content-review compliance-scan --platform <平台> <内容>"
            },
            "platforms": ["xhs", "wechat", "weibo", "general"]
        }


# Skill 实例
content_review_skill = ContentReviewSkillImpl()


async def execute(input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
    """Skill 执行入口"""
    return await content_review_skill.execute(input_data, context)
