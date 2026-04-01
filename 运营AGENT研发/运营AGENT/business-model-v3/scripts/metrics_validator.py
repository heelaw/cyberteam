#!/usr/bin/env python3
"""
运营指标验证脚本
验证运营指标定义的完整性和合理性
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MetricLevel(Enum):
    """指标层级"""
    TOP = "顶层指标"
    MIDDLE = "中层指标"
    BOTTOM = "底层指标"


@dataclass
class Metric:
    """指标定义"""
    name: str
    level: MetricLevel
    formula: str = ""
    target_value: float = 0.0
    baseline_value: float = 0.0
    unit: str = ""
    frequency: str = "日度"
    description: str = ""

    def is_valid(self) -> Tuple[bool, List[str]]:
        """验证指标定义是否完整"""
        errors = []

        if not self.name:
            errors.append("缺少指标名称")

        if not self.formula:
            errors.append("缺少计算公式")

        if self.target_value == 0 and self.level != MetricLevel.BOTTOM:
            errors.append("缺少目标值")

        return len(errors) == 0, errors


class MetricsValidator:
    """运营指标验证器"""

    def __init__(self):
        self.metrics = []

    def load_metrics(self, metrics_data: Dict[str, Any]) -> List[Metric]:
        """
        加载指标数据

        Args:
            metrics_data: 指标数据，格式：
                {
                    "顶层指标": [...],
                    "中层指标": [...],
                    "底层指标": [...]
                }

        Returns:
            Metric 列表
        """
        self.metrics = []

        level_mapping = {
            "顶层指标": MetricLevel.TOP,
            "中层指标": MetricLevel.MIDDLE,
            "底层指标": MetricLevel.BOTTOM
        }

        for level_name, level_data in metrics_data.items():
            level = level_mapping.get(level_name, MetricLevel.BOTTOM)

            for metric_data in level_data:
                if isinstance(metric_data, dict):
                    metric = Metric(
                        name=metric_data.get("名称", metric_data.get("name", "")),
                        level=level,
                        formula=metric_data.get("计算公式", metric_data.get("formula", "")),
                        target_value=metric_data.get("目标值", metric_data.get("target_value", 0)),
                        baseline_value=metric_data.get("基准值", metric_data.get("baseline_value", 0)),
                        unit=metric_data.get("单位", metric_data.get("unit", "")),
                        frequency=metric_data.get("监测频率", metric_data.get("frequency", "日度")),
                        description=metric_data.get("描述", metric_data.get("description", ""))
                    )
                    self.metrics.append(metric)

        return self.metrics

    def validate_all(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        验证所有指标

        Returns:
            (是否全部有效, 错误列表)
        """
        all_valid = True
        errors = []

        for i, metric in enumerate(self.metrics):
            is_valid, metric_errors = metric.is_valid()
            if not is_valid:
                all_valid = False
                errors.append({
                    "指标": metric.name,
                    "层级": metric.level.value,
                    "错误": metric_errors
                })

        return all_valid, errors

    def check_hierarchy(self) -> Tuple[bool, List[str]]:
        """
        检查指标层级结构

        Returns:
            (结构是否合理, 问题列表)
        """
        issues = []

        # 检查是否有各层级的指标
        level_counts = {
            MetricLevel.TOP: 0,
            MetricLevel.MIDDLE: 0,
            MetricLevel.BOTTOM: 0
        }

        for metric in self.metrics:
            level_counts[metric.level] += 1

        if level_counts[MetricLevel.TOP] == 0:
            issues.append("缺少顶层指标")

        if level_counts[MetricLevel.MIDDLE] == 0:
            issues.append("缺少中层指标")

        if level_counts[MetricLevel.BOTTOM] == 0:
            issues.append("缺少底层指标")

        # 检查数量比例是否合理
        total = sum(level_counts.values())
        if total > 0:
            top_ratio = level_counts[MetricLevel.TOP] / total
            middle_ratio = level_counts[MetricLevel.MIDDLE] / total
            bottom_ratio = level_counts[MetricLevel.BOTTOM] / total

            if top_ratio > 0.5:
                issues.append(f"顶层指标占比过高 ({top_ratio*100:.1f}%)，建议控制在20%以内")

            if bottom_ratio < 0.4:
                issues.append(f"底层指标占比过低 ({bottom_ratio*100:.1f}%)，建议应占40%以上")

        return len(issues) == 0, issues

    def check_formula_syntax(self) -> List[Dict[str, Any]]:
        """
        检查公式语法

        Returns:
            有问题的公式列表
        """
        issues = []

        for metric in self.metrics:
            if not metric.formula:
                continue

            # 检查公式中是否包含基本的运算符
            has_operator = any(op in metric.formula for op in ["+", "-", "*", "/", "×", "÷"])

            # 检查是否有未闭合的括号
            open_parens = metric.formula.count("(")
            close_parens = metric.formula.count(")")

            if not has_operator and "=" not in metric.formula:
                issues.append({
                    "指标": metric.name,
                    "公式": metric.formula,
                    "问题": "公式缺少运算符"
                })

            if open_parens != close_parens:
                issues.append({
                    "指标": metric.name,
                    "公式": metric.formula,
                    "问题": "括号不匹配"
                })

        return issues

    def check_target_achievable(self) -> List[Dict[str, Any]]:
        """
        检查目标值的合理性

        Returns:
            不合理的目标列表
        """
        issues = []

        for metric in self.metrics:
            if metric.target_value == 0 or metric.baseline_value == 0:
                continue

            # 计算目标相对基准的增长率
            growth_rate = (metric.target_value - metric.baseline_value) / metric.baseline_value

            # 如果增长率超过 100%，标记为警告
            if growth_rate > 1.0:
                issues.append({
                    "指标": metric.name,
                    "基准值": metric.baseline_value,
                    "目标值": metric.target_value,
                    "增长率": f"{growth_rate*100:.1f}%",
                    "警告": "目标值过高，可能难以达成"
                })
            # 如果增长率是负数（目标值低于基准），标记为警告
            elif growth_rate < 0:
                issues.append({
                    "指标": metric.name,
                    "基准值": metric.baseline_value,
                    "目标值": metric.target_value,
                    "增长率": f"{growth_rate*100:.1f}%",
                    "警告": "目标值低于基准值，请确认是否正确"
                })

        return issues

    def generate_metrics_summary(self) -> Dict[str, Any]:
        """
        生成指标体系摘要

        Returns:
            摘要信息
        """
        level_counts = {level: 0 for level in MetricLevel}
        for metric in self.metrics:
            level_counts[metric.level] += 1

        return {
            "指标总数": len(self.metrics),
            "顶层指标": level_counts[MetricLevel.TOP],
            "中层指标": level_counts[MetricLevel.MIDDLE],
            "底层指标": level_counts[MetricLevel.BOTTOM],
            "监测频率分布": self._get_frequency_distribution()
        }

    def _get_frequency_distribution(self) -> Dict[str, int]:
        """获取监测频率分布"""
        freq_dist = {}
        for metric in self.metrics:
            freq = metric.frequency
            freq_dist[freq] = freq_dist.get(freq, 0) + 1
        return freq_dist

    def get_metrics_by_level(self, level: MetricLevel) -> List[Metric]:
        """按层级获取指标"""
        return [m for m in self.metrics if m.level == level]

    def generate_validation_report(self) -> str:
        """
        生成验证报告

        Returns:
            报告文本
        """
        lines = [
            "## 运营指标验证报告",
            ""
        ]

        # 摘要
        summary = self.generate_metrics_summary()
        lines.extend([
            "### 指标体系摘要",
            "",
            f"- 指标总数: {summary['指标总数']}",
            f"- 顶层指标: {summary['顶层指标']} 个",
            f"- 中层指标: {summary['中层指标']} 个",
            f"- 底层指标: {summary['底层指标']} 个",
            "",
            "### 监测频率分布",
            ""
        ])

        for freq, count in summary["监测频率分布"].items():
            lines.append(f"- {freq}: {count} 个指标")

        # 验证结果
        is_valid, errors = self.validate_all()
        lines.extend([
            "",
            "### 指标定义验证",
            ""
        ])

        if is_valid:
            lines.append("✅ 所有指标定义完整")
        else:
            lines.append(f"❌ 发现 {len(errors)} 个指标定义问题:")
            for error in errors:
                lines.append(f"  - {error['层级']} - {error['指标']}: {', '.join(error['错误'])}")

        # 层级结构检查
        hierarchy_valid, hierarchy_issues = self.check_hierarchy()
        lines.extend([
            "",
            "### 层级结构验证",
            ""
        ])

        if hierarchy_valid:
            lines.append("✅ 层级结构合理")
        else:
            lines.append("⚠️ 层级结构存在潜在问题:")
            for issue in hierarchy_issues:
                lines.append(f"  - {issue}")

        # 公式语法检查
        formula_issues = self.check_formula_syntax()
        lines.extend([
            "",
            "### 公式语法检查",
            ""
        ])

        if not formula_issues:
            lines.append("✅ 所有公式语法正确")
        else:
            lines.append(f"⚠️ 发现 {len(formula_issues)} 个公式问题:")
            for issue in formula_issues:
                lines.append(f"  - {issue['指标']}: {issue['问题']}")

        # 目标值合理性检查
        target_issues = self.check_target_achievable()
        lines.extend([
            "",
            "### 目标值合理性检查",
            ""
        ])

        if not target_issues:
            lines.append("✅ 所有目标值设置合理")
        else:
            lines.append(f"⚠️ 发现 {len(target_issues)} 个目标值需要关注:")
            for issue in target_issues:
                lines.append(f"  - {issue['指标']}: {issue['警告']} (基准: {issue['基准值']}, 目标: {issue['目标值']})")

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="运营指标验证工具")
    parser.add_argument("--metrics", required=True,
                        help="指标数据 (JSON格式或文件路径)")
    parser.add_argument("--report", action="store_true",
                        help="生成完整报告")
    parser.add_argument("--check-formula", action="store_true",
                        help="检查公式语法")
    parser.add_argument("--check-target", action="store_true",
                        help="检查目标值合理性")

    args = parser.parse_args()

    # 加载指标数据
    try:
        # 尝试作为文件读取
        with open(args.metrics, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 作为 JSON 字符串解析
        metrics_data = json.loads(args.metrics)

    validator = MetricsValidator()
    validator.load_metrics(metrics_data)

    print(f"✅ 加载了 {len(validator.metrics)} 个指标\n")

    # 生成报告
    if args.report:
        report = validator.generate_validation_report()
        print(report)
    else:
        # 基本验证
        is_valid, errors = validator.validate_all()
        hierarchy_valid, hierarchy_issues = validator.check_hierarchy()

        print(f"指标定义验证: {'✅ 通过' if is_valid else '❌ 失败'}")
        if not is_valid:
            for error in errors:
                print(f"  - {error['指标']}: {', '.join(error['错误'])}")

        print(f"\n层级结构验证: {'✅ 合理' if hierarchy_valid else '⚠️ 有问题'}")
        if not hierarchy_valid:
            for issue in hierarchy_issues:
                print(f"  - {issue}")

        # 公式检查
        if args.check_formula:
            formula_issues = validator.check_formula_syntax()
            print(f"\n公式语法检查: {'✅ 正确' if not formula_issues else '⚠️ 有问题'}")

        # 目标值检查
        if args.check_target:
            target_issues = validator.check_target_achievable()
            print(f"\n目标值检查: {'✅ 合理' if not target_issues else '⚠️ 需要关注'}")
            for issue in target_issues:
                print(f"  - {issue['指标']}: {issue['警告']}")


if __name__ == "__main__":
    main()
