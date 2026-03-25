#!/usr/bin/env python3
"""
收入公式计算与敏感度分析脚本
用于计算收入、进行敏感度分析和情景模拟
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Variable:
    """变量定义"""
    name: str
    value: float
    unit: str = ""
    description: str = ""


@dataclass
class RevenueFormula:
    """收入公式"""
    name: str
    formula: str
    variables: List[Variable]
    base_revenue: float = 0.0


class RevenueCalculator:
    """收入计算器"""

    def __init__(self):
        self.formulas = []

    def parse_formula(self, formula_str: str, variables: Dict[str, float]) -> str:
        """
        解析并计算公式

        Args:
            formula_str: 公式字符串，如 "流量 × 转化率 × 客单价"
            variables: 变量值字典，如 {"流量": 10000, "转化率": 0.05, "客单价": 100}

        Returns:
            计算结果
        """
        # 将中文运算符转换为 Python 运算符
        expr = formula_str.replace("×", "*").replace("÷", "/")

        # 替换变量名
        for var_name, var_value in variables.items():
            expr = expr.replace(var_name, str(var_value))

        try:
            result = eval(expr)
            return str(result)
        except Exception as e:
            return f"计算错误: {e}"

    def calculate_revenue(self, formula: str, variables: Dict[str, float]) -> float:
        """
        计算收入

        Args:
            formula: 收入公式
            variables: 变量字典

        Returns:
            收入值
        """
        expr = formula.replace("×", "*").replace("÷", "/").replace("流量", "str(流量)").replace("转化率", "str(转化率)").replace("客单价", "str(客单价)")

        for var_name, var_value in variables.items():
            expr = expr.replace(var_name, str(var_value))

        try:
            return float(eval(expr))
        except:
            return 0.0

    def sensitivity_analysis(self, base_revenue: float, variables: Dict[str, float],
                            changes: List[float] = [-0.2, -0.1, 0.1, 0.2]) -> Dict[str, Dict[str, float]]:
        """
        敏感度分析

        Args:
            base_revenue: 基准收入
            variables: 变量字典
            changes: 变化率列表

        Returns:
            敏感度分析结果
        """
        results = {}

        for var_name, var_value in variables.items():
            results[var_name] = {}

            for change in changes:
                # 计算变化后的变量值
                new_value = var_value * (1 + change)
                new_variables = variables.copy()
                new_variables[var_name] = new_value

                # 计算新收入
                new_revenue = self.calculate_revenue_from_dict(new_variables)

                # 计算收入变化
                revenue_change = (new_revenue - base_revenue) / base_revenue if base_revenue > 0 else 0

                results[var_name][f"{change*100:+.0f}%"] = {
                    "变量值": new_value,
                    "收入": new_revenue,
                    "收入变化": f"{revenue_change*100:+.2f}%"
                }

        return results

    def calculate_revenue_from_dict(self, variables: Dict[str, float],
                                    formula: str = "流量*转化率*客单价") -> float:
        """
        从变量字典计算收入

        Args:
            variables: 变量字典
            formula: 收入公式

        Returns:
            收入值
        """
        expr = formula
        for var_name, var_value in variables.items():
            expr = expr.replace(var_name, str(var_value))

        try:
            return float(eval(expr))
        except:
            return 0.0

    def scenario_analysis(self, variables: Dict[str, float],
                         scenarios: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        情景分析

        Args:
            variables: 基准变量
            scenarios: 情景定义，如 {"乐观": {"流量": 1.2, "转化率": 1.1}}

        Returns:
            情景分析结果
        """
        base_revenue = self.calculate_revenue_from_dict(variables)
        results = {"基准": base_revenue}

        for scenario_name, scenario_vars in scenarios.items():
            new_variables = variables.copy()
            for var_name, multiplier in scenario_vars.items():
                if var_name in new_variables:
                    new_variables[var_name] *= multiplier

            scenario_revenue = self.calculate_revenue_from_dict(new_variables)
            results[scenario_name] = {
                "收入": scenario_revenue,
                "vs基准": f"{((scenario_revenue - base_revenue) / base_revenue * 100):+.2f}%"
            }

        return results

    def find_optimal_levers(self, variables: Dict[str, float],
                          constraints: Dict[str, Tuple[float, float]] = None,
                          formula: str = "流量*转化率*客单价") -> Dict[str, Any]:
        """
        寻找最优杠杆（哪些变量优化能带来最大收入增长）

        Args:
            variables: 当前变量值
            constraints: 变量约束，如 {"流量": (0.8, 1.5)} 表示可变化范围
            formula: 收入公式

        Returns:
            优化建议
        """
        base_revenue = self.calculate_revenue_from_dict(variables, formula)

        # 默认约束：各变量可提升 10%-50%
        if constraints is None:
            constraints = {var: (1.0, 1.5) for var in variables.keys()}

        leverage = {}

        for var_name, var_value in variables.items():
            var_min, var_max = constraints.get(var_name, (1.0, 1.5))

            # 计算最大化该变量时的收入
            new_variables = variables.copy()
            new_variables[var_name] = var_value * var_max
            max_revenue = self.calculate_revenue_from_dict(new_variables, formula)

            # 计算收入增长潜力
            growth_potential = (max_revenue - base_revenue) / base_revenue if base_revenue > 0 else 0

            leverage[var_name] = {
                "当前值": var_value,
                "最大值": var_value * var_max,
                "收入潜力": max_revenue,
                "增长潜力": f"{growth_potential*100:.2f}%"
            }

        # 按增长潜力排序
        sorted_leverage = sorted(leverage.items(),
                               key=lambda x: float(x[1]["增长潜力"].rstrip("%")),
                               reverse=True)

        return {
            "基准收入": base_revenue,
            "杠杆排名": [
                {
                    "排名": i + 1,
                    "变量": var,
                    **data
                }
                for i, (var, data) in enumerate(sorted_leverage)
            ]
        }

    def generate_formula_report(self, formula: str, variables: Dict[str, float],
                               base_revenue: float) -> str:
        """
        生成收入公式分析报告

        Args:
            formula: 收入公式
            variables: 变量字典
            base_revenue: 基准收入

        Returns:
            报告文本
        """
        lines = [
            "## 收入公式分析报告",
            "",
            f"**核心收入公式**: {formula}",
            "",
            "### 变量定义",
            ""
        ]

        for var_name, var_value in variables.items():
            lines.append(f"- **{var_name}**: {var_value:,}")

        lines.extend([
            "",
            f"**基准收入**: {base_revenue:,.2f}",
            "",
            "### 敏感度分析",
            ""
        ])

        sensitivity = self.sensitivity_analysis(base_revenue, variables)

        for var_name, var_data in sensitivity.items():
            lines.append(f"#### {var_name}")
            for change, result in var_data.items():
                lines.append(f"- {change}: 收入 {result['收入']:,.2f} ({result['收入变化']})")
            lines.append("")

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="收入公式计算与敏感度分析工具")
    parser.add_argument("--formula", default="流量×转化率×客单价",
                        help="收入公式")
    parser.add_argument("--variables", required=True,
                        help="变量值 (JSON格式)")
    parser.add_argument("--sensitivity", action="store_true",
                        help="执行敏感度分析")
    parser.add_argument("--optimize", action="store_true",
                        help="查找优化杠杆")
    parser.add_argument("--scenarios",
                        help="情景分析 (JSON格式)")

    args = parser.parse_args()

    # 解析变量
    variables = json.loads(args.variables)
    calculator = RevenueCalculator()

    # 计算基准收入
    base_revenue = calculator.calculate_revenue_from_dict(variables)
    print(f"基准收入: {base_revenue:,.2f}\n")

    # 敏感度分析
    if args.sensitivity:
        print("=== 敏感度分析 ===\n")
        sensitivity = calculator.sensitivity_analysis(base_revenue, variables)
        for var_name, var_data in sensitivity.items():
            print(f"{var_name}:")
            for change, result in var_data.items():
                print(f"  {change}: {result['收入']:,.2f} ({result['收入变化']})")
            print()

    # 优化杠杆
    if args.optimize:
        print("=== 优化杠杆分析 ===\n")
        levers = calculator.find_optimal_levers(variables)
        print(f"基准收入: {levers['基准收入']:,.2f}\n")
        print("杠杆排名（按增长潜力）:")
        for item in levers["杠杆排名"]:
            print(f"  {item['排名']}. {item['变量']}: {item['增长潜力']}")

    # 情景分析
    if args.scenarios:
        print("=== 情景分析 ===\n")
        scenarios = json.loads(args.scenarios)
        results = calculator.scenario_analysis(variables, scenarios)
        for scenario, data in results.items():
            if scenario == "基准":
                print(f"{scenario}: {data:,.2f}")
            else:
                print(f"{scenario}: {data['收入']:,.2f} ({data['vs基准']})")


if __name__ == "__main__":
    main()
