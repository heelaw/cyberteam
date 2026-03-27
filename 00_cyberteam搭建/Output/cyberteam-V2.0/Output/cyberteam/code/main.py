"""
CyberTeam MVP - Main Integration
一句话交代，整个团队干活
"""

from ceo_agent import CEOAgent
from data_agent import DataAgent
from growth_agent import GrowthAgent
from copywriter_agent import CopywriterAgent
from user_agent import UserAgent
from channel_agent import ChannelAgent
from campaign_agent import CampaignAgent
from content_agent import ContentAgent
from community_agent import CommunityAgent
from conversion_agent import ConversionAgent


class CyberTeam:
    """CyberTeam 主控类"""

    def __init__(self):
        self.ceo = CEOAgent()
        self.agents = {
            "data": DataAgent(),
            "growth": GrowthAgent(),
            "copywriter": CopywriterAgent(),
            "user": UserAgent(),
            "channel": ChannelAgent(),
            "campaign": CampaignAgent(),
            "content": ContentAgent(),
            "community": CommunityAgent(),
            "conversion": ConversionAgent()
        }

    def run(self, user_input: str) -> dict:
        """主流程"""
        # 1. CEO 分析问题
        analysis = self.ceo.analyze(user_input)
        print(f"✅ 问题分析完成: {analysis}")

        # 2. 任务分解
        breakdown = self.ceo.mece_breakdown(analysis)
        tasks = self.ceo.decompose(breakdown)
        print(f"✅ 任务分解完成: {len(tasks)} 个任务")

        # 3. 并行执行
        results = []
        for task in tasks:
            agent_name = task["agent"].replace("Agent", "")
            if agent_name in self.agents:
                result = self._execute_task(agent_name, task["task"])
                results.append(result)
                print(f"✅ {agent_name} 完成")

        # 4. 结果聚合
        final_report = self.ceo.aggregate(results)
        print(f"✅ 聚合完成")

        return final_report

    def _execute_task(self, agent_name: str, task: str) -> dict:
        """执行单个任务"""
        agent = self.agents.get(agent_name)
        if not agent:
            return {"status": "unknown agent"}

        # 根据不同agent类型调用不同方法
        if hasattr(agent, 'analyze'):
            return agent.analyze(task)
        elif hasattr(agent, 'plan'):
            return agent.plan(task)
        elif hasattr(agent, 'strategy'):
            return agent.strategy(task)
        elif hasattr(agent, 'build'):
            return agent.build(task)
        else:
            return {"status": "completed"}


def main():
    """入口"""
    print("=" * 50)
    print("🟠 CyberTeam MVP - 一句话交代，整个团队干活")
    print("=" * 50)

    team = CyberTeam()

    # 示例输入
    user_input = "我要做用户增长，提高DAU"
    result = team.run(user_input)

    print("\n" + "=" * 50)
    print("📊 最终报告:")
    print(result)
    print("=" * 50)


if __name__ == "__main__":
    main()
