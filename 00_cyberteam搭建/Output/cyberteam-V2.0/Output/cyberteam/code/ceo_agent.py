"""
CyberTeam CEO Agent - 问题分析与任务分发
实现 5W1H + MECE 方法论
"""

class CEOAgent:
    """CEO Agent 负责问题分析和任务分发"""

    def __init__(self):
        self.frameworks = self._load_frameworks()
        self.experts = self._load_experts()

    def _load_frameworks(self):
        """加载思维框架"""
        return {
            "5w1h": ["What", "Why", "Who", "When", "Where", "How"],
            "mece": ["相互独立", "完全穷尽"],
            "pest": ["政治", "经济", "社会", "技术"],
            "swot": ["优势", "劣势", "机会", "威胁"]
        }

    def _load_experts(self):
        """加载专家Agent列表"""
        return {
            "增长": ["增长Agent", "增长Agent2"],
            "数据": ["数据Agent", "数据Agent2"],
            "文案": ["文案Agent", "文案Agent2"],
            "用户": ["用户Agent", "用户Agent2"],
            "渠道": ["渠道Agent", "渠道Agent2"],
            "活动": ["活动Agent", "活动Agent2"],
            "内容": ["内容Agent", "内容Agent2"],
            "社群": ["社群Agent", "社群Agent2"],
            "转化": ["转化Agent", "转化Agent2"]
        }

    def analyze(self, user_input: str) -> dict:
        """5W1H 分析"""
        return {
            "what": self._extract_what(user_input),
            "why": self._extract_why(user_input),
            "who": self._extract_who(user_input),
            "when": self._extract_when(user_input),
            "where": self._extract_where(user_input),
            "how": self._extract_how(user_input)
        }

    def mece_breakdown(self, analysis: dict) -> list:
        """MECE 拆解"""
        breakdown = []
        for key, value in analysis.items():
            if value:
                breakdown.append({
                    "aspect": key,
                    "detail": value,
                    "independent": True
                })
        return breakdown

    def decompose(self, breakdown: list) -> list:
        """任务分解"""
        tasks = []
        for item in breakdown:
            agent_type = self._match_agent(item["aspect"])
            tasks.append({
                "task": item["detail"],
                "agent": self.experts.get(agent_type, ["运营专家"])[0],
                "priority": "P0"
            })
        return tasks

    def _match_agent(self, aspect: str) -> str:
        """匹配合适的Agent"""
        mapping = {
            "what": "数据",
            "why": "增长",
            "who": "用户",
            "when": "活动",
            "where": "渠道",
            "how": "转化"
        }
        return mapping.get(aspect, "运营")

    def _extract_what(self, text: str) -> str:
        return f"核心需求: {text[:50]}"

    def _extract_why(self, text: str) -> str:
        return "目标价值分析中"

    def _extract_who(self, text: str) -> str:
        return "目标用户分析中"

    def _extract_when(self, text: str) -> str:
        return "时间线规划中"

    def _extract_where(self, text: str) -> str:
        return "渠道分析中"

    def _extract_how(self, text: str) -> str:
        return "执行方案规划中"

    def aggregate(self, results: list) -> dict:
        """结果聚合"""
        return {
            "summary": "方案汇总完成",
            "tasks": results,
            "status": "completed"
        }


if __name__ == "__main__":
    ceo = CEOAgent()
    result = ceo.analyze("用户增长方案")
    print(result)
