#!/usr/bin/env python3
"""
转化漏斗分析脚本
用于分析转化路径、计算转化率、识别流失点和优化机会
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FunnelNode:
    """漏斗节点"""
    name: str
    users: int
    conversion_rate: float = 0.0
    dropoff_rate: float = 0.0
    description: str = ""


@dataclass
class DropoffPoint:
    """流失点"""
    from_node: str
    to_node: str
    dropoff_count: int
    dropoff_rate: float
    severity: str = "medium"  # low, medium, high


class FunnelAnalyzer:
    """转化漏斗分析器"""

    def __init__(self):
        self.nodes = []
        self.dropoffs = []

    def calculate_funnel(self, nodes_data: List[Dict[str, Any]]) -> List[FunnelNode]:
        """
        计算转化漏斗

        Args:
            nodes_data: 节点数据列表，格式：
                [
                    {"name": "接触", "users": 10000},
                    {"name": "点击", "users": 5000},
                    ...
                ]

        Returns:
            FunnelNode 列表
        """
        if not nodes_data:
            return []

        self.nodes = []
        prev_users = None

        for i, node_data in enumerate(nodes_data):
            name = node_data["name"]
            users = node_data["users"]
            description = node_data.get("description", "")

            # 计算转化率（相对于首个节点）
            if i == 0:
                conversion_rate = 1.0
                dropoff_rate = 0.0
            else:
                conversion_rate = users / nodes_data[0]["users"] if nodes_data[0]["users"] > 0 else 0
                # 计算流失率（相对于上一节点）
                if prev_users and prev_users > 0:
                    dropoff_rate = (prev_users - users) / prev_users
                else:
                    dropoff_rate = 0.0

            node = FunnelNode(
                name=name,
                users=users,
                conversion_rate=conversion_rate,
                dropoff_rate=dropoff_rate,
                description=description
            )
            self.nodes.append(node)
            prev_users = users

        return self.nodes

    def identify_dropoffs(self, threshold: float = 0.3) -> List[DropoffPoint]:
        """
        识别流失点

        Args:
            threshold: 流失率阈值，超过此值视为重要流失点

        Returns:
            DropoffPoint 列表
        """
        self.dropoffs = []

        for i in range(len(self.nodes) - 1):
            current = self.nodes[i]
            next_node = self.nodes[i + 1]

            dropoff_count = current.users - next_node.users
            dropoff_rate = current.dropoff_rate

            # 评估严重程度
            if dropoff_rate >= 0.5:
                severity = "high"
            elif dropoff_rate >= threshold:
                severity = "medium"
            else:
                severity = "low"

            dropoff = DropoffPoint(
                from_node=current.name,
                to_node=next_node.name,
                dropoff_count=dropoff_count,
                dropoff_rate=dropoff_rate,
                severity=severity
            )
            self.dropoffs.append(dropoff)

        return self.dropoffs

    def get_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """
        获取优化机会

        Returns:
            优化建议列表
        """
        opportunities = []

        for dropoff in self.dropoffs:
            if dropoff.severity in ["medium", "high"]:
                opportunity = {
                    "位置": f"{dropoff.from_node} → {dropoff.to_node}",
                    "流失率": f"{dropoff.dropoff_rate*100:.1f}%",
                    "流失人数": dropoff.dropoff_count,
                    "严重程度": dropoff.severity,
                    "建议": self._get_optimization_suggestion(dropoff)
                }
                opportunities.append(opportunity)

        return opportunities

    def _get_optimization_suggestion(self, dropoff: DropoffPoint) -> str:
        """获取优化建议"""
        suggestions = {
            "接触 → 点击": "优化文案、视觉设计，提升吸引力",
            "点击 → 浏览": "优化页面加载速度，改进导航设计",
            "浏览 → 咨询": "增强产品信息展示，添加信任元素",
            "咨询 → 购买": "优化客服响应，简化购买流程",
            "购买 → 复购": "提升产品质量，建立用户关系",
            "复购 → 推荐": "设计激励机制，鼓励社交分享"
        }

        key = f"{dropoff.from_node} → {dropoff.to_node}"
        return suggestions.get(key, "分析用户行为数据，找出流失原因并针对性优化")

    def calculate_potential_gain(self, node_index: int, target_conversion: float) -> Dict[str, Any]:
        """
        计算提升某节点转化率后的潜在收益

        Args:
            node_index: 节点索引
            target_conversion: 目标转化率

        Returns:
            潜在收益分析
        """
        if node_index >= len(self.nodes) or node_index < 1:
            return {"error": "无效的节点索引"}

        current_node = self.nodes[node_index]
        first_node = self.nodes[0]

        # 当前转化用户数
        current_converted = current_node.users

        # 目标转化用户数
        target_converted = int(first_node.users * target_conversion)

        # 增量用户
        gain_users = target_converted - current_converted

        # 假设每用户价值为 100 元（可根据实际情况调整）
        avg_user_value = 100
        gain_revenue = gain_users * avg_user_value

        return {
            "节点": current_node.name,
            "当前转化率": f"{current_node.conversion_rate*100:.1f}%",
            "目标转化率": f"{target_conversion*100:.1f}%",
            "当前用户数": current_converted,
            "目标用户数": target_converted,
            "增量用户": gain_users,
            "预估收入增加": f"{gain_revenue:,.0f} 元"
        }

    def compare_with_industry(self, industry_benchmarks: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        与行业基准对比

        Args:
            industry_benchmarks: 行业基准数据，格式：
                {"点击": 0.05, "浏览": 0.03, ...}

        Returns:
            对比结果列表
        """
        comparisons = []

        for node in self.nodes:
            if node.name in industry_benchmarks:
                benchmark = industry_benchmarks[node.name]
                current = node.conversion_rate
                diff = current - benchmark

                comparison = {
                    "节点": node.name,
                    "当前转化率": f"{current*100:.2f}%",
                    "行业基准": f"{benchmark*100:.2f}%",
                    "差异": f"{diff*100:+.2f}%",
                    "评估": "优秀" if diff > 0.01 else ("需改进" if diff < -0.01 else "持平")
                }
                comparisons.append(comparison)

        return comparisons

    def generate_funnel_report(self) -> str:
        """
        生成转化漏斗分析报告

        Returns:
            报告文本
        """
        lines = [
            "## 转化漏斗分析报告",
            "",
            "### 漏斗概览",
            "",
            "| 节点 | 用户数 | 整体转化率 | 流失率 |",
            "|------|--------|-----------|--------|"
        ]

        for node in self.nodes:
            lines.append(
                f"| {node.name} | {node.users:,} | {node.conversion_rate*100:.2f}% | {node.dropoff_rate*100:.2f}% |"
            )

        lines.extend([
            "",
            "### 流失点分析",
            "",
            "| 位置 | 流失率 | 流失人数 | 严重程度 |",
            "|------|--------|----------|----------|"
        ])

        for dropoff in self.dropoffs:
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(dropoff.severity, "")
            lines.append(
                f"| {dropoff.from_node} → {dropoff.to_node} | {dropoff.dropoff_rate*100:.1f}% | "
                f"{dropoff.dropoff_count:,} | {severity_emoji} {dropoff.severity} |"
            )

        opportunities = self.get_optimization_opportunities()
        if opportunities:
            lines.extend([
                "",
                "### 优化建议",
                ""
            ])
            for opp in opportunities:
                lines.extend([
                    f"**{opp['位置']}** (流失率: {opp['流失率']})",
                    f"- 建议: {opp['建议']}",
                    ""
                ])

        return "\n".join(lines)

    def visualize_funnel(self) -> str:
        """
        生成简单的文本可视化漏斗

        Returns:
            可视化文本
        """
        if not self.nodes:
            return "无数据"

        lines = ["转化漏斗可视化:", ""]

        max_users = self.nodes[0].users
        max_width = 50  # 最大显示宽度（字符）

        for node in self.nodes:
            width = int((node.users / max_users) * max_width)
            bar = "█" * width
            lines.append(f"{node.name:8} {bar} {node.users:,} ({node.conversion_rate*100:.1f}%)")

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="转化漏斗分析工具")
    parser.add_argument("--nodes", required=True,
                        help="节点数据 (JSON格式)")
    parser.add_argument("--threshold", type=float, default=0.3,
                        help="流失率阈值 (默认: 0.3)")
    parser.add_argument("--benchmarks",
                        help="行业基准 (JSON格式)")
    parser.add_argument("--visualize", action="store_true",
                        help="显示可视化漏斗")

    args = parser.parse_args()

    # 解析节点数据
    nodes_data = json.loads(args.nodes)
    analyzer = FunnelAnalyzer()

    # 计算漏斗
    nodes = analyzer.calculate_funnel(nodes_data)
    print(f"✅ 分析了 {len(nodes)} 个转化节点\n")

    # 识别流失点
    dropoffs = analyzer.identify_dropoffs(args.threshold)
    print(f"✅ 识别出 {len(dropoffs)} 个流失点\n")

    # 生成报告
    report = analyzer.generate_funnel_report()
    print(report)

    # 可视化
    if args.visualize:
        print("\n" + analyzer.visualize_funnel())

    # 行业对比
    if args.benchmarks:
        benchmarks = json.loads(args.benchmarks)
        comparisons = analyzer.compare_with_industry(benchmarks)
        print("\n### 行业基准对比\n")
        print("| 节点 | 当前 | 基准 | 差异 | 评估 |")
        print("|------|------|------|------|------|")
        for comp in comparisons:
            print(f"| {comp['节点']} | {comp['当前转化率']} | {comp['行业基准']} | "
                  f"{comp['差异']} | {comp['评估']} |")


if __name__ == "__main__":
    main()
