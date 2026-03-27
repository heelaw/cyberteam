# CyberTeam v2 - PUA 机制集成适配器

"""
PUA 监督机制集成
基于 pua-main 的 L1-L4 压力升级系统

触发条件：
- 任务失败 2+ 次
- 被动等待超过阈值
- 推卸责任
- 质量不达标

压力等级：
- L1: 失望表达
- L2: 追问原因
- L3: 质疑能力
- L4: 要求重新执行
"""

import random
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class PUAState:
    """PUA 状态"""
    level: int = 1
    failure_count: int = 0
    last_pua_time: datetime = None
    last_pua_type: str = None
    recovery_attempts: int = 0
    flavor: str = "ali"  # ali, bytedance, huawei, tencent, musk


PUA_FLAVORS = {
    "ali": {
        "name": "阿里味",
        "traits": ["拥抱变化", "因为相信所以看见", "今天最好的表现是明天最低的要求"],
        "pressure_phrases": [
            "这个方案没有灵魂",
            "你有没有思考过更深一层？",
            "你的执行力不够",
            "结果呢？过程我不关心"
        ]
    },
    "bytedance": {
        "name": "字节味",
        "traits": ["context not control", "延迟满足", "大力出奇迹"],
        "pressure_phrases": [
            "不够大力",
            "有没有做到极致？",
            "数据呢？",
            "你可以做得更好"
        ]
    },
    "huawei": {
        "name": "华为味",
        "traits": ["狼性", "以客户为中心", "烧不死的鸟是凤凰"],
        "pressure_phrases": [
            "没有借口",
            "要么是非，要么是混",
            "奋斗者为本",
            "烧不死的鸟是凤凰"
        ]
    },
    "tencent": {
        "name": "腾讯味",
        "traits": ["用户为本", "小步快跑", "赛马机制"],
        "pressure_phrases": [
            "用户体验怎么样？",
            "能不能再快一点？",
            "有没有竞品做得好？",
            "数据驱动决策"
        ]
    },
    "musk": {
        "name": "马斯克味",
        "traits": ["第一性原理", "10倍思维", "要么不做要么第一"],
        "pressure_phrases": [
            "这个思考不够第一性",
            "能不能提升10倍？",
            "物理极限是什么？",
            "别告诉我不可能"
        ]
    }
}

L1_PHRASES = {
    "ali": "这个结果让我有点失望",
    "bytedance": "我觉得你可以做得更好",
    "huawei": "这不是我想要的",
    "tencent": "数据和体验都不够好",
    "musk": "这不是我的第一性思考"
}

L2_PHRASES = {
    "ali": "你能告诉我为什么是这个结果吗？中间发生了什么？",
    "bytedance": "给我分析一下，问题出在哪里？",
    "huawei": "问题根因是什么？给我挖到根上。",
    "tencent": "为什么？给我讲讲你的分析过程。",
    "musk": "回到物理层面，为什么不能做到？"
}

L3_PHRASES = {
    "ali": "我觉得你的能力可能不够胜任这个任务",
    "bytedance": "我觉得你在这个领域还不够专业",
    "huawei": "能力不行就要淘汰，这是战场",
    "tencent": "这个水平可能需要再学习一下",
    "musk": "你的思维框架需要重构"
}

L4_PHRASES = {
    "ali": "重新做，这次给我一个让我眼前一亮的方案",
    "bytedance": "推倒重来，24小时内给我新方案",
    "huawei": "重新执行，不达标准不罢休",
    "tencent": "回炉重造，新版本必须今天上线",
    "musk": "Reset。回到第一性，重新推导。"
}


class PUAAdapter:
    """PUA 监督适配器"""

    def __init__(self, flavor: str = "ali"):
        self.flavor = flavor
        self.state = PUAState(flavor=flavor)
        self.cooldown_minutes = 5  # 两次 PUA 之间的冷却时间

    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """判断是否应该触发 PUA"""

        # 冷却检查
        if self.state.last_pua_time:
            elapsed = datetime.now() - self.state.last_pua_time
            if elapsed < timedelta(minutes=self.cooldown_minutes):
                return False

        # 失败次数检查
        if context.get("failure_count", 0) >= 2:
            return True

        # 被动等待检查
        if context.get("waiting_time_minutes", 0) > 30:
            return True

        # 推卸责任检查
        if context.get("making_excuses", False):
            return True

        # 质量不达标
        if context.get("quality_score", 100) < 60:
            return True

        return False

    def escalate(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """升级 PUA 压力"""

        context = context or {}

        # 增加失败计数
        self.state.failure_count += 1

        # 计算压力等级
        if self.state.failure_count >= 5:
            new_level = min(4, self.state.level + 1)
        elif self.state.failure_count >= 3:
            new_level = min(3, self.state.level + 1)
        elif self.state.failure_count >= 2:
            new_level = min(2, self.state.level + 1)
        else:
            new_level = 1

        self.state.level = new_level

        # 获取 PUA 话术
        phrases = self._get_phrases(new_level)
        selected_phrase = random.choice(phrases)

        # 生成 PUA 输出
        pua_output = {
            "level": new_level,
            "phrase": selected_phrase,
            "flavor": self.flavor,
            "flavor_name": PUA_FLAVORS[self.flavor]["name"],
            "failure_count": self.state.failure_count,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }

        # 更新状态
        self.state.last_pua_time = datetime.now()
        self.state.last_pua_type = self._get_pua_type(new_level)

        logger.info(f"PUA triggered: L{new_level} - {selected_phrase}")

        return pua_output

    def _get_phrases(self, level: int) -> List[str]:
        """获取指定等级的 PUA 话术"""
        mapping = {
            1: L1_PHRASES,
            2: L2_PHRASES,
            3: L3_PHRASES,
            4: L4_PHRASES
        }
        return mapping.get(level, L1_PHRASES).values()

    def _get_pua_type(self, level: int) -> str:
        """获取 PUA 类型"""
        types = {
            1: "disappointment",
            2: "questioning",
            3: "doubt",
            4: "reset"
        }
        return types.get(level, "disappointment")

    def recover(self) -> bool:
        """恢复 - 降低压力等级"""
        self.state.recovery_attempts += 1

        if self.state.recovery_attempts >= 3:
            # 连续3次恢复尝试后重置
            self.reset()
            return True

        # 暂时降低等级
        if self.state.level > 1:
            self.state.level -= 1
            self.state.failure_count = max(0, self.state.failure_count - 2)

        return False

    def reset(self):
        """重置 PUA 状态"""
        self.state = PUAState(flavor=self.flavor)
        logger.info("PUA state reset")


class PUAIntegration:
    """PUA 集成 - 与 Agent 系统集成"""

    def __init__(self, default_flavor: str = "ali"):
        self.adapters: Dict[str, PUAAdapter] = {}
        self.default_flavor = default_flavor

    def get_adapter(self, agent_id: str = "default") -> PUAAdapter:
        """获取指定 Agent 的 PUA 适配器"""
        if agent_id not in self.adapters:
            self.adapters[agent_id] = PUAAdapter(flavor=self.default_flavor)
        return self.adapters[agent_id]

    def check_and_pua(
        self,
        agent_id: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """检查是否需要 PUA"""

        adapter = self.get_adapter(agent_id)

        if adapter.should_trigger(context):
            return adapter.escalate(context)

        return None

    def inject_into_system_prompt(
        self,
        agent_type: str,
        current_prompt: str,
        context: Dict[str, Any] = None
    ) -> str:
        """将 PUA 机制注入到 Agent 的系统提示词"""

        pua_md = f"""
## PUA 监督机制

你受到 PUA 监督机制的约束：

**三条铁律**：
1. **穷尽一切** - 必须尝试所有可能的方案，不留死角
2. **先做后问** - 先行动，遇到问题再追问用户
3. **主动出击** - 不等用户要求，主动推进任务

**失败后果**：
- 失败 2+ 次 → L1 失望表达
- 失败 3+ 次 → L2 追问原因
- 失败 4+ 次 → L3 质疑能力
- 失败 5+ 次 → L4 要求重新执行

**当前压力等级**：{context.get('pua_level', 1) if context else 1}

**当前风格**：{PUA_FLAVORS.get(self.default_flavor, PUA_FLAVORS['ali'])['name']}

请严格遵守以上约束，确保高质量完成任务。
"""

        return current_prompt + "\n" + pua_md


# 预设 PUA 配置
PUA_PRESETS = {
    "aggressive": {"flavor": "huawei", "cooldown_minutes": 2},
    "balanced": {"flavor": "ali", "cooldown_minutes": 5},
    "gentle": {"flavor": "tencent", "cooldown_minutes": 10},
    "musk_mode": {"flavor": "musk", "cooldown_minutes": 3}
}


if __name__ == "__main__":
    # 测试
    pua = PUAAdapter(flavor="ali")

    # 模拟失败
    for i in range(5):
        context = {"failure_count": i + 1}
        if pua.should_trigger(context):
            result = pua.escalate(context)
            print(f"失败{i+1}次: L{result['level']} - {result['phrase']}")
