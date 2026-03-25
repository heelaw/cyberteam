#!/usr/bin/env python3
"""
北极星指标六标准评估辅助脚本

用于辅助评估备选指标是否符合六标准筛选条件：
1. 能否反映用户从产品中获得核心价值
2. 能否为产品达到长期商业目标奠定基础
3. 能否反映用户活跃程度
4. 指标变好能否提示整个公司在往好的方向发展
5. 是否简单直观容易获得可拆解
6. 是先导指标还是滞后指标

使用方式:
    python northstar_scorer.py
"""

import json
from typing import Dict, List, Any


def evaluate_metric(name: str, scores: Dict[str, bool]) -> Dict[str, Any]:
    """
    评估单个指标的六标准得分

    Args:
        name: 指标名称
        scores: 各标准的通过状态 {'标准1': True/False, ...}

    Returns:
        评估结果字典
    """
    total = sum(scores.values())
    passed = [k for k, v in scores.items() if v]

    return {
        "name": name,
        "total_score": total,
        "max_score": 6,
        "percentage": round(total / 6, 2),
        "passed": passed,
        "is_qualified": total >= 5,
    }


def rank_metrics(metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    按六标准得分排序

    Args:
        metrics: 指标列表

    Returns:
        排序后的指标列表
    """
    return sorted(metrics, key=lambda x: (x["total_score"], x["percentage"]), reverse=True)


def print_ranking(metrics: List[Dict[str, Any]]) -> None:
    """
    打印排名结果
    """
    print("\n" + "=" * 60)
    print("北极星指标 - 六标准评估排名")
    print("=" * 60)

    for i, m in enumerate(metrics, 1):
        status = "✓ 通过" if m["is_qualified"] else "✗ 未通过"
        print(f"\n#{i} {m['name']} ({status})")
        print(f"   得分: {m['total_score']}/6 ({int(m['percentage']*100)}%)")
        print(f"   通过标准: {', '.join(m['passed']) if m['passed'] else '无'}")

    print("\n" + "=" * 60)


def main():
    # 示例：评估三个备选指标
    candidate_metrics = [
        evaluate_metric(
            "每日总观看时长",
            {
                "标准1_用户价值": True,      # 反映用户获得娱乐价值
                "标准2_商业基础": True,      # 支撑广告变现
                "标准3_用户活跃": True,      # 反映真实观看
                "标准4_整体方向": True,      # 供需都受益
                "标准5_简单直观": True,      # 简单易理解
                "标准6_先导指标": True,      # 实时反映
            }
        ),
        evaluate_metric(
            "每日观看视频用户数",
            {
                "标准1_用户价值": True,
                "标准2_商业基础": True,
                "标准3_用户活跃": True,
                "标准4_整体方向": True,
                "标准5_简单直观": False,    # 定义稍复杂
                "标准6_先导指标": True,
            }
        ),
        evaluate_metric(
            "每周活跃用户数",
            {
                "标准1_用户价值": False,     # 登录不等于获得价值
                "标准2_商业基础": True,
                "标准3_用户活跃": True,
                "标准4_整体方向": True,
                "标准5_简单直观": True,
                "标准6_先导指标": True,
            }
        ),
    ]

    # 排序
    ranked = rank_metrics(candidate_metrics)

    # 打印结果
    print_ranking(ranked)

    # 推荐结果
    qualified = [m for m in ranked if m["is_qualified"]]
    if qualified:
        print(f"\n推荐北极星指标: {qualified[0]['name']} ({qualified[0]['total_score']}/6)")
    else:
        print("\n警告: 没有指标通过5/6的筛选标准")

    # 输出JSON格式
    print("\nJSON输出:")
    print(json.dumps(ranked, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
