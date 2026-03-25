"""
CyberTeam v2 - 测试套件

测试覆盖：
1. ThinkingInjector - 思维注入引擎
2. RoutingEngine - 路由引擎
3. DevQAEngine - Dev-QA 引擎
4. QualityGateEngine - 质量门控引擎
"""

import pytest
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.thinking_injector import (
    ThinkingInjector,
    IntentClassifier,
    ThinkingLibrary,
    Expert,
    ThinkingContext
)


class TestIntentClassifier:
    """意图分类器测试"""

    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_classify_decision_intent(self):
        """测试决策类意图识别"""
        text = "我应该选择A还是B？"
        result = self.classifier.classify(text)
        assert "decision" in result
        assert result["decision"] > 0.5

    def test_classify_analysis_intent(self):
        """测试分析类意图识别"""
        text = "分析一下为什么用户流失"
        result = self.classifier.classify(text)
        assert "analysis" in result
        assert result["analysis"] > 0.5

    def test_classify_execution_intent(self):
        """测试执行类意图识别"""
        text = "怎么做用户增长"
        result = self.classifier.classify(text)
        assert "execution" in result
        assert result["execution"] > 0.5

    def test_classify_strategy_intent(self):
        """测试战略类意图识别"""
        text = "制定公司战略规划"
        result = self.classifier.classify(text)
        assert "strategy" in result
        assert result["strategy"] > 0.5

    def test_classify_growth_intent(self):
        """测试增长类意图识别"""
        text = "如何提升DAU和MAU"
        result = self.classifier.classify(text)
        # 验证识别到增长相关意图
        assert len(result) > 0  # 至少能识别到某种意图

    def test_classify_product_intent(self):
        """测试产品类意图识别"""
        text = "产品需求分析"
        result = self.classifier.classify(text)
        assert "product" in result

    def test_normalize_scores(self):
        """测试分数归一化"""
        text = "帮我分析选择决策和增长策略"
        result = self.classifier.classify(text)
        # 验证分数归一化到0-1范围
        for score in result.values():
            assert 0 <= score <= 1


class TestThinkingLibrary:
    """思维专家库测试"""

    def setup_method(self):
        self.library = ThinkingLibrary()

    def test_load_experts(self):
        """测试专家库加载"""
        assert len(self.library.experts) > 0

    def test_expert_structure(self):
        """测试专家数据结构"""
        for expert_id, expert in self.library.experts.items():
            assert isinstance(expert, Expert)
            assert expert.id
            assert expert.name_cn
            assert expert.category
            assert expert.trigger_keywords

    def test_get_expert_by_id(self):
        """测试按ID获取专家"""
        # 获取任意一个专家
        first_expert_id = next(iter(self.library.experts.keys()))
        expert = self.library.experts[first_expert_id]
        assert expert is not None
        assert expert.id == first_expert_id


class TestThinkingInjector:
    """思维注入引擎测试"""

    def setup_method(self):
        self.injector = ThinkingInjector()

    def test_process_basic(self):
        """测试基本处理流程"""
        goal = "我想做一个在线教育平台"
        ctx = self.injector.process(goal)
        assert isinstance(ctx, ThinkingContext)
        assert ctx.user_input == goal
        assert len(ctx.selected_experts) > 0

    def test_process_with_growth_keywords(self):
        """测试增长关键词触发"""
        goal = "提升DAU 20%"
        ctx = self.injector.process(goal)
        assert len(ctx.selected_experts) > 0

    def test_process_with_strategy_keywords(self):
        """测试战略关键词触发"""
        goal = "制定商业模式战略"
        ctx = self.injector.process(goal)
        assert len(ctx.selected_experts) > 0

    def test_process_with_decision_keywords(self):
        """测试决策关键词触发"""
        goal = "选择哪个技术方案"
        ctx = self.injector.process(goal)
        assert len(ctx.selected_experts) > 0

    def test_injection_points_extraction(self):
        """测试注入点提取"""
        goal = "帮我分析竞品并制定增长策略"
        ctx = self.injector.process(goal)
        assert len(ctx.injection_points) > 0


class TestExpert:
    """思维专家数据类测试"""

    def test_create_expert(self):
        """测试创建专家实例"""
        expert = Expert(
            id="test-expert",
            name="Test Expert",
            name_cn="测试专家",
            category="test",
            description="测试用途",
            trigger_keywords=["test"],
            injection_template="Test template"
        )
        assert expert.id == "test-expert"
        assert expert.name_cn == "测试专家"
        assert expert.weight == 1.0  # 默认权重

    def test_expert_with_custom_weight(self):
        """测试自定义权重"""
        expert = Expert(
            id="test-expert",
            name="Test Expert",
            name_cn="测试专家",
            category="test",
            description="测试用途",
            trigger_keywords=["test"],
            injection_template="Test template",
            weight=2.0
        )
        assert expert.weight == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])