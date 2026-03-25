#!/usr/bin/env python3
"""
教学目标分析器

帮助用户使用4×4教学目标矩阵分析和设定课程教学目标。
根据学员基础和交付成果，提供SMART目标建议。

Usage:
    objective_analyzer.py
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional
import sys


@dataclass
class TeachingObjective:
    """教学目标"""
    audience_level: str  # 学员基础
    outcome_level: str  # 交付成果
    description: str  # 目标描述
    verb: str  # 行为动词
    is_smart: bool  # 是否符合SMART原则


class ObjectiveAnalyzer:
    """教学目标分析器"""

    # 学员基础层级
    AUDIENCE_LEVELS = [
        "零基础小白",
        "有一定基础",
        "有实践经验",
        "专家级别"
    ]

    # 交付成果层级（简化Bloom分类法）
    OUTCOME_LEVELS = [
        "认知/信息获取",
        "理解/原理掌握",
        "应用/技能操作",
        "分析/综合创新"
    ]

    # 行为动词库
    VERBS = {
        "认知/信息获取": [
            "识别", "列举", "描述", "定义", "命名",
            "复述", "背诵", "指出", "标记", "说出"
        ],
        "理解/原理掌握": [
            "解释", "总结", "说明", "阐述",
            "分类", "比较", "推断", "归纳", "转述"
        ],
        "应用/技能操作": [
            "应用", "运用", "实施", "执行",
            "操作", "演示", "实践", "解决", "完成"
        ],
        "分析/综合创新": [
            "分析", "评价", "评判", "批判",
            "设计", "创造", "构建", "创新", "优化"
        ]
    }

    # 模糊动词（避免使用）
    VAGUE_VERBS = ["了解", "掌握", "熟悉", "知道", "学习", "理解"]

    def __init__(self):
        self.current_audience = 1  # 默认：有一定基础
        self.current_outcome = 2  # 默认：理解/原理掌握
        self.objectives: List[TeachingObjective] = []

    def display_matrix(self):
        """显示4×4矩阵"""
        print("\n" + "=" * 70)
        print("4×4 教学目标矩阵")
        print("=" * 70)
        print("\n交付成果\\学员基础 |", end="")
        for level in self.AUDIENCE_LEVELS:
            print(f" {level[:6]} |", end="")
        print()

        print("-" * 70)

        for i, outcome in enumerate(self.OUTCOME_LEVELS):
            print(f"{outcome[:15]} |", end="")
            for j in range(4):
                marker = " ★ " if (i == self.current_outcome and j == self.current_audience) else "   "
                print(f"{marker} |", end="")
            print()

        print(f"\n当前定位: {self.AUDIENCE_LEVELS[self.current_audience]} × {self.OUTCOME_LEVELS[self.current_outcome]}")
        print()

    def get_position_recommendations(self) -> List[str]:
        """获取当前定位的目标建议"""
        audience = self.AUDIENCE_LEVELS[self.current_audience]
        outcome = self.OUTCOME_LEVELS[self.current_outcome]

        recommendations = []

        # 根据学员基础提供建议
        if self.current_audience == 0:  # 零基础
            recommendations.append("注重建立认知框架，避免过多专业术语")
            recommendations.append("使用类比和比喻降低理解门槛")
        elif self.current_audience == 1:  # 有基础
            recommendations.append("系统化知识梳理，填补知识空白")
            recommendations.append("建立知识体系，关注知识联系")
        elif self.current_audience == 2:  # 有实践
            recommendations.append("理论提升实践，方法论总结")
            recommendations.append("尊重学员经验，解决实际问题")
        else:  # 专家
            recommendations.append("思维模型碰撞，前沿知识分享")
            recommendations.append("促进交流互动，挑战现有认知")

        # 根据交付成果提供建议
        if self.current_outcome == 0:  # 认知
            recommendations.append("提供清晰的知识结构，便于记忆")
        elif self.current_outcome == 1:  # 理解
            recommendations.append("多用案例和对比，帮助理解原理")
        elif self.current_outcome == 2:  # 应用
            recommendations.append("设计充分的练习和实践机会")
        else:  # 分析/创新
            recommendations.append("提供开放性任务，鼓励创新思考")

        return recommendations

    def check_smart(self, description: str) -> Tuple[bool, List[str]]:
        """检查目标是否符合SMART原则"""
        issues = []

        # Specific (具体)
        if any(v in description for v in self.VAGUE_VERBS):
            issues.append("❌ 使用了模糊动词，建议使用更具体的行为动词")

        # Measurable (可衡量)
        if not re.search(r'[0-9]+|个|项|次|条|步|%', description):
            issues.append("⚠️  缺少量化指标，可能难以衡量")

        # Achievable (可达成) - 需要上下文判断
        if len(description) < 10:
            issues.append("⚠️  描述过短，可能不够具体")

        # Relevant (相关) - 需要上下文判断
        # Time-bound (有时限)
        if not re.search(r'(结束时|完成|后|前|周|月|小时|分钟)', description):
            issues.append("⚠️  未明确时间条件")

        is_smart = len([i for i in issues if "❌" in i]) == 0
        return is_smart, issues

    def improve_objective(self, description: str) -> str:
        """改进教学目标描述"""
        improved = description

        # 替换模糊动词
        for vague in self.VAGUE_VERBS:
            if vague in improved:
                # 根据当前交付成果层级推荐动词
                suggested = self.VERBS[self.OUTCOME_LEVELS[self.current_outcome]][0]
                improved = improved.replace(vague, suggested)
                break

        # 添加SMART元素
        if "完成" not in improved:
            improved = improved.replace("能够", "能够在课程结束时完成")
        elif "结束时" not in improved:
            improved = improved.replace("完成", "能够在课程结束时完成")

        return improved

    def interactive_mode(self):
        """交互模式"""
        print("\n" + "=" * 70)
        print("教学目标分析器 - 交互模式")
        print("=" * 70)

        while True:
            self.display_matrix()

            print("\n【选项】")
            print("1. 设置学员基础 (当前: {})".format(self.AUDIENCE_LEVELS[self.current_audience]))
            print("2. 设置交付成果 (当前: {})".format(self.OUTCOME_LEVELS[self.current_outcome]))
            print("3. 添加教学目标")
            print("4. 查看已添加目标")
            print("5. 分析和改进目标")
            print("6. 生成SMART目标建议")
            print("0. 退出")

            choice = input("\n请选择 (0-6): ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self._set_audience_level()
            elif choice == "2":
                self._set_outcome_level()
            elif choice == "3":
                self._add_objective()
            elif choice == "4":
                self._display_objectives()
            elif choice == "5":
                self._analyze_objectives()
            elif choice == "6":
                self._generate_smart_suggestions()
            else:
                print("无效选择")

    def _set_audience_level(self):
        """设置学员基础层级"""
        print("\n学员基础层级:")
        for i, level in enumerate(self.AUDIENCE_LEVELS):
            print(f"{i}. {level}")

        choice = input("\n请选择 (0-3): ").strip()
        try:
            idx = int(choice)
            if 0 <= idx <= 3:
                self.current_audience = idx
                print(f"✅ 已设置为: {self.AUDIENCE_LEVELS[idx]}")
            else:
                print("无效选择")
        except ValueError:
            print("无效输入")

    def _set_outcome_level(self):
        """设置交付成果层级"""
        print("\n交付成果层级:")
        for i, level in enumerate(self.OUTCOME_LEVELS):
            print(f"{i}. {level}")

        choice = input("\n请选择 (0-3): ").strip()
        try:
            idx = int(choice)
            if 0 <= idx <= 3:
                self.current_outcome = idx
                print(f"✅ 已设置为: {self.OUTCOME_LEVELS[idx]}")
            else:
                print("无效选择")
        except ValueError:
            print("无效输入")

    def _add_objective(self):
        """添加教学目标"""
        print("\n添加教学目标")
        print("当前定位: {} × {}".format(
            self.AUDIENCE_LEVELS[self.current_audience],
            self.OUTCOME_LEVELS[self.current_outcome]
        ))

        description = input("请输入目标描述: ").strip()
        if not description:
            print("已取消")
            return

        # 检测使用的动词
        verb = "未知"
        for v in self.VERBS[self.OUTCOME_LEVELS[self.current_outcome]]:
            if v in description:
                verb = v
                break

        is_smart, issues = self.check_smart(description)

        objective = TeachingObjective(
            audience_level=self.AUDIENCE_LEVELS[self.current_audience],
            outcome_level=self.OUTCOME_LEVELS[self.current_outcome],
            description=description,
            verb=verb,
            is_smart=is_smart
        )

        self.objectives.append(objective)
        print("\n✅ 目标已添加")

        if issues:
            print("\nSMART检查结果:")
            for issue in issues:
                print(f"  {issue}")

            improve = input("\n是否需要改进建议? (y/n): ").strip().lower()
            if improve == 'y':
                improved = self.improve_objective(description)
                print(f"\n改进建议: {improved}")

    def _display_objectives(self):
        """显示已添加的目标"""
        if not self.objectives:
            print("\n暂无教学目标")
            return

        print("\n" + "-" * 70)
        print("已添加的教学目标:")
        print("-" * 70)

        for i, obj in enumerate(self.objectives, 1):
            print(f"\n{i}. {obj.description}")
            print(f"   学员基础: {obj.audience_level}")
            print(f"   交付成果: {obj.outcome_level}")
            print(f"   SMART状态: {'✅ 符合' if obj.is_smart else '⚠️  需改进'}")

    def _analyze_objectives(self):
        """分析所有目标"""
        if not self.objectives:
            print("\n暂无教学目标可分析")
            return

        print("\n" + "-" * 70)
        print("教学目标分析")
        print("-" * 70)

        # 统计
        audience_dist = {}
        outcome_dist = {}
        smart_count = sum(1 for o in self.objectives if o.is_smart)

        for obj in self.objectives:
            audience_dist[obj.audience_level] = audience_dist.get(obj.audience_level, 0) + 1
            outcome_dist[obj.outcome_level] = outcome_dist.get(obj.outcome_level, 0) + 1

        print(f"\n总目标数: {len(self.objectives)}")
        print(f"SMART符合率: {smart_count}/{len(self.objectives)} ({smart_count*100//len(self.objectives)}%)")

        print("\n学员基础分布:")
        for level, count in audience_dist.items():
            print(f"  {level}: {count}")

        print("\n交付成果分布:")
        for level, count in outcome_dist.items():
            print(f"  {level}: {count}")

        # 建议
        print("\n" + "-" * 70)
        print("改进建议:")
        print("-" * 70)

        recommendations = self.get_position_recommendations()
        for rec in recommendations:
            print(f"  • {rec}")

    def _generate_smart_suggestions(self):
        """生成SMART目标建议"""
        print("\n" + "-" * 70)
        print("SMART目标建议")
        print("-" * 70)

        print(f"\n当前定位: {self.AUDIENCE_LEVELS[self.current_audience]} × {self.OUTCOME_LEVELS[self.current_outcome]}")
        print("\n推荐的行为动词:")
        for verb in self.VERBS[self.OUTCOME_LEVELS[self.current_outcome]][:5]:
            print(f"  - {verb}")

        print("\n目标描述模板:")
        print(f"  在课程结束时，学员能够[动词][具体内容]，[量化标准]")

        print("\n示例:")
        audience = self.AUDIENCE_LEVELS[self.current_audience]
        outcome = self.OUTCOME_LEVELS[self.current_outcome]
        verb = self.VERBS[outcome][0]

        examples = {
            ("零基础小白", "认知/信息获取"): f"在课程结束时，学员能够{verb}课程中的10个核心概念",
            ("有一定基础", "理解/原理掌握"): f"在课程结束时，学员能够{verb}XX方法的核心原理和适用场景",
            ("有实践经验", "应用/技能操作"): f"在课程结束时，学员能够{verb}XX方法完成一个实际项目",
            ("专家级别", "分析/综合创新"): f"在课程结束时，学员能够{verb}并优化现有的XX框架"
        }

        example = examples.get((audience, outcome))
        if example:
            print(f"  {example}")
        else:
            print(f"  在课程结束时，学员能够{verb}所学内容解决实际问题")


def main():
    """主函数"""
    analyzer = ObjectiveAnalyzer()

    try:
        analyzer.interactive_mode()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
