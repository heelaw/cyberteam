"""Report Writer 专业 Agent。

负责生成结构化报告，整理分析结果。
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from cyberteam.agents.base import SpecializedAgent, AgentMetadata


class ReportWriter(SpecializedAgent):
    """Report Writer - 报告撰写器

    负责生成结构化报告，整理分析结果。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="report_writer",
            description="Report Writer：生成结构化报告，整理分析结果",
            version="1.0.0",
            tags=["报告", "文档", "撰写", "整理"],
            capabilities=[
                "结构化写作",
                "数据分析整理",
                "多格式输出",
                "模板填充",
                "审校校对"
            ]
        )
        super().__init__(metadata)
        self.sections: List[Dict[str, Any]] = []

    def _do_initialize(self) -> None:
        """初始化报告撰写器"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """生成报告结构"""
        return {
            "writer": self.metadata.name,
            "mode": "report_generation",
            "input": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行报告撰写任务"""
        result = await self.think(task)
        return result

    def add_section(self, title: str, content: str, level: int = 1) -> None:
        """添加章节"""
        self.sections.append({
            "title": title,
            "content": content,
            "level": level
        })

    def clear_sections(self) -> None:
        """清除所有章节"""
        self.sections.clear()

    async def write_report(self, title: str, author: str = "CyberTeam") -> Dict[str, Any]:
        """撰写报告"""
        report_content = []
        for section in self.sections:
            heading = "#" * section["level"] + " " + section["title"]
            report_content.append(heading)
            report_content.append(section["content"])
            report_content.append("")

        report_md = "\n".join(report_content)

        return {
            "title": title,
            "author": author,
            "created_at": datetime.now().isoformat(),
            "sections_count": len(self.sections),
            "content": report_md,
            "summary": self._generate_summary()
        }

    def _generate_summary(self) -> str:
        """生成摘要"""
        if not self.sections:
            return "报告无内容"

        titles = [s["title"] for s in self.sections[:5]]
        if len(self.sections) > 5:
            titles.append(f"... 等 {len(self.sections)} 个章节")

        return "报告包含: " + " | ".join(titles)
