"""
Loop Detector - 循环检测模块
检测Agent执行过程中的循环模式
"""

from enum import Enum
from typing import Tuple, List, Dict
from collections import Counter


class LoopType(Enum):
    """循环类型枚举"""
    INFINITE_LOOP = "infinite_loop"
    OSCILLATION = "oscillation"
    SPIRAL = "spiral"
    RETRY_LOOP = "retry_loop"


class LoopDetector:
    """循环检测器"""

    # 循环检测阈值
    DEFAULT_MAX_ITERATIONS = 100
    DEFAULT_OSCILLATION_THRESHOLD = 3
    DEFAULT_SPIRAL_THRESHOLD = 0.8

    def __init__(self, max_iterations: int = None):
        self.max_iterations = max_iterations or self.DEFAULT_MAX_ITERATIONS
        self.oscillation_threshold = self.DEFAULT_OSCILLATION_THRESHOLD
        self.spiral_threshold = self.DEFAULT_SPIRAL_THRESHOLD

    def detect(self, agent_id: str, history: List[Dict]) -> Tuple[LoopType, float, Dict]:
        """
        检测循环类型和置信度

        Args:
            agent_id: Agent标识
            history: 执行历史列表

        Returns:
            Tuple[LoopType, float, Dict] - (循环类型, 置信度, 详情)
        """
        if not history or len(history) < 2:
            return (None, 0.0, {})

        # 检查迭代次数超限
        if len(history) >= self.max_iterations:
            return (
                LoopType.INFINITE_LOOP,
                1.0,
                {"iteration_count": len(history), "max_allowed": self.max_iterations}
            )

        # 检测震荡模式（状态在两个值之间反复切换）
        oscillation_result = self._detect_oscillation(history)
        if oscillation_result:
            return oscillation_result

        # 检测螺旋模式（状态逐渐偏离目标）
        spiral_result = self._detect_spiral(history)
        if spiral_result:
            return spiral_result

        # 检测重试循环（相同错误反复出现）
        retry_result = self._detect_retry_loop(history)
        if retry_result:
            return retry_result

        return (None, 0.0, {})

    def _detect_oscillation(self, history: List[Dict]) -> Tuple[LoopType, float, Dict]:
        """检测震荡模式"""
        if len(history) < 4:
            return None

        # 获取状态序列
        states = [h.get("state") or h.get("action") for h in history]

        # 检测两个状态之间的反复切换
        for i in range(len(states) - 3):
            if states[i] == states[i + 2] and states[i + 1] == states[i + 3]:
                if states[i] != states[i + 1]:
                    confidence = min(1.0, (len(states) - i) / 6)
                    return (
                        LoopType.OSCILLATION,
                        confidence,
                        {
                            "state_a": states[i],
                            "state_b": states[i + 1],
                            "switch_count": len(states) // 2,
                            "first_occurrence": i
                        }
                    )
        return None

    def _detect_spiral(self, history: List[Dict]) -> Tuple[LoopType, float, Dict]:
        """检测螺旋模式（状态向量模持续增长）"""
        if len(history) < 5:
            return None

        # 检查是否有progress字段
        progress_values = []
        for h in history:
            if "progress" in h:
                try:
                    progress_values.append(float(h["progress"]))
                except (ValueError, TypeError):
                    pass

        if len(progress_values) >= 5:
            # 检查progress是否持续下降（偏离目标）
            decreases = sum(1 for i in range(1, len(progress_values))
                          if progress_values[i] < progress_values[i-1])
            if decreases / (len(progress_values) - 1) >= self.spiral_threshold:
                return (
                    LoopType.SPIRAL,
                    decreases / (len(progress_values) - 1),
                    {
                        "progress_trend": progress_values,
                        "decrease_ratio": decreases / (len(progress_values) - 1)
                    }
                )

        # 检查是否有distance_to_goal字段
        distances = [h.get("distance_to_goal", float('inf')) for h in history]
        if distances[-1] != float('inf'):
            increases = sum(1 for i in range(1, len(distances))
                          if distances[i] > distances[i-1])
            if increases / (len(distances) - 1) >= self.spiral_threshold:
                return (
                    LoopType.SPIRAL,
                    increases / (len(distances) - 1),
                    {"distance_trend": distances}
                )

        return None

    def _detect_retry_loop(self, history: List[Dict]) -> Tuple[LoopType, float, Dict]:
        """检测重试循环（相同错误反复出现）"""
        if len(history) < 3:
            return None

        # 统计错误类型
        errors = [h.get("error") or h.get("failed_action") for h in history if h.get("error")]
        if not errors:
            return None

        error_counter = Counter(errors)
        most_common_error, count = error_counter.most_common(1)[0]

        if count >= self.oscillation_threshold:
            confidence = min(1.0, count / 6)
            return (
                LoopType.RETRY_LOOP,
                confidence,
                {
                    "repeated_error": most_common_error,
                    "repeat_count": count,
                    "all_errors": dict(error_counter)
                }
            )
        return None

    def analyze_depth(self, history: List[Dict]) -> Dict:
        """
        分析执行深度

        Args:
            history: 执行历史

        Returns:
            Dict - 深度分析结果
        """
        if not history:
            return {"depth": 0, "max_depth_reached": 0, "branching_factor": 0}

        depth = len(history)
        max_depth_reached = depth  # 简化版本

        # 计算分支因子（平均每个状态的后续选项数）
        branching_options = [h.get("available_choices", 1) for h in history]
        avg_branching = sum(branching_options) / len(branching_options) if branching_options else 1

        return {
            "depth": depth,
            "max_depth_reached": max_depth_reached,
            "branching_factor": round(avg_branching, 2),
            "unique_states": len(set(h.get("state") or str(h) for h in history)),
            "loop_risk": "high" if depth > self.max_iterations * 0.8 else "medium" if depth > self.max_iterations * 0.5 else "low"
        }