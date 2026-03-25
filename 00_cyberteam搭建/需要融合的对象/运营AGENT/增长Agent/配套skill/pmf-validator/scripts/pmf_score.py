#!/usr/bin/env python3
"""
PMF验证评分计算器

功能描述:
    计算PMF验证报告的质量分数，帮助评估五步验证法的执行情况

使用方式:
    python pmf_score.py --input <pmf_report.json> --output <result.json>
    python pmf_score.py --interactive

输入格式 (JSON):
    {
        "step1_user_profile": true/false,
        "step1_profile_dimensions": 数量,
        "step2_demand_verified": true/false,
        "step2_demand_count": 数量,
        "step3_positioning_clear": true/false,
        "step4_mvp_features": 数量,
        "step5_test_executed": true/fless
    }

输出格式 (JSON):
    {
        "total_score": 分数,
        "pass": true/false,
        "details": [
            {"step": "步骤名", "score": 分数, "max": 最高分},
            ...
        ]
    }
"""

import json
import sys
import argparse
from typing import Dict, List, Any


def calculate_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """计算PMF验证评分"""

    # 权重配置
    weights = {
        "step1": 0.20,   # 目标用户
        "step2": 0.25,   # 用户需求
        "step3": 0.15,   # 核心定位
        "step4": 0.20,   # MVP功能
        "step5": 0.20    # 用户验证
    }

    thresholds = {
        "step1_profile_dimensions": 3,
        "step2_demand_count": 3,
        "step4_mvp_features": 5
    }

    details = []
    total_score = 0.0

    # Step 1: 目标用户
    step1_score = 0
    if data.get("step1_user_profile", False):
        step1_score += 50
        # 检查画像维度
        dimensions = data.get("step1_profile_dimensions", 0)
        if dimensions >= thresholds["step1_profile_dimensions"]:
            step1_score += 50
    step1_max = 100
    details.append({
        "step": "Step 1: 确定目标用户",
        "score": step1_score,
        "max": step1_max,
        "description": "用户画像完整性"
    })
    total_score += (step1_score / step1_max) * weights["step1"]

    # Step 2: 用户需求
    step2_score = 0
    if data.get("step2_demand_verified", False):
        step2_score += 50
        demands = data.get("step2_demand_count", 0)
        if demands >= thresholds["step2_demand_count"]:
            step2_score += 50
    step2_max = 100
    details.append({
        "step": "Step 2: 挖掘用户需求",
        "score": step2_score,
        "max": step2_max,
        "description": "需求验证和数量"
    })
    total_score += (step2_score / step2_max) * weights["step2"]

    # Step 3: 核心定位
    step3_score = 100 if data.get("step3_positioning_clear", False) else 0
    step3_max = 100
    details.append({
        "step": "Step 3: 确定核心定位",
        "score": step3_score,
        "max": step3_max,
        "description": "定位陈述清晰度"
    })
    total_score += (step3_score / step3_max) * weights["step3"]

    # Step 4: MVP功能
    step4_score = 0
    mvp_features = data.get("step4_mvp_features", 0)
    if mvp_features > 0:
        # 5个以内满分，超过则递减
        if mvp_features <= thresholds["step4_mvp_features"]:
            step4_score = 100
        else:
            step4_score = max(0, 100 - (mvp_features - thresholds["step4_mvp_features"]) * 20)
    step4_max = 100
    details.append({
        "step": "Step 4: 规划MVP功能",
        "score": step4_score,
        "max": step4_max,
        "description": f"MVP功能精简度({mvp_features}项)"
    })
    total_score += (step4_score / step4_max) * weights["step4"]

    # Step 5: 用户验证
    step5_score = 100 if data.get("step5_test_executed", False) else 0
    step5_max = 100
    details.append({
        "step": "Step 5: 验证MVP接受度",
        "score": step5_score,
        "max": step5_max,
        "description": "用户测试执行"
    })
    total_score += (step5_score / step5_max) * weights["step5"]

    # 判断是否通过
    pass_threshold = 0.85

    return {
        "total_score": round(total_score, 2),
        "pass": total_score >= pass_threshold,
        "pass_threshold": pass_threshold,
        "details": details
    }


def interactive_mode():
    """交互式输入模式"""
    print("\n=== PMF验证评分计算器 ===\n")

    data = {}

    # Step 1
    print("Step 1: 确定目标用户")
    data["step1_user_profile"] = input("  是否建立了用户画像? (y/n): ").strip().lower() == 'y'
    if data["step1_user_profile"]:
        try:
            data["step1_profile_dimensions"] = int(input("  用户画像包含几个维度? (人口统计/行为特征/心理特征/使用场景): "))
        except ValueError:
            data["step1_profile_dimensions"] = 0

    # Step 2
    print("\nStep 2: 挖掘用户需求")
    data["step2_demand_verified"] = input("  需求是否经过用户验证? (y/n): ").strip().lower() == 'y'
    if data["step2_demand_verified"]:
        try:
            data["step2_demand_count"] = int(input("  列出几个需求? "))
        except ValueError:
            data["step2_demand_count"] = 0

    # Step 3
    print("\nStep 3: 确定核心定位")
    data["step3_positioning_clear"] = input("  是否形成清晰的产品定位陈述? (y/n): ").strip().lower() == 'y'

    # Step 4
    print("\nStep 4: 规划MVP功能")
    try:
        data["step4_mvp_features"] = int(input("  MVP包含几个功能? "))
    except ValueError:
        data["step4_mvp_features"] = 0

    # Step 5
    print("\nStep 5: 验证MVP接受度")
    data["step5_test_executed"] = input("  是否执行了用户测试? (y/n): ").strip().lower() == 'y'

    return data


def main():
    parser = argparse.ArgumentParser(
        description="PMF验证评分计算器 - 计算五步验证法的执行质量"
    )
    parser.add_argument(
        "--input", "-i",
        help="输入JSON文件路径"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出JSON文件路径"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="交互式输入模式"
    )

    args = parser.parse_args()

    # 获取数据
    if args.interactive:
        data = interactive_mode()
    elif args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"错误: 文件 {args.input} 不存在")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"错误: 文件 {args.input} 不是有效的JSON")
            sys.exit(1)
    else:
        print("请指定 --input 或 --interactive 模式")
        parser.print_help()
        sys.exit(1)

    # 计算分数
    result = calculate_score(data)

    # 输出结果
    print("\n=== 评分结果 ===\n")
    print(f"总分: {result['total_score']*100:.0f}%")
    print(f"通过: {'是' if result['pass'] else '否'}")
    print(f"阈值: {result['pass_threshold']*100:.0f}%\n")

    print("各步骤得分:")
    for detail in result["details"]:
        status = "✓" if detail["score"] >= 50 else "✗"
        print(f"  {status} {detail['step']}: {detail['score']}/{detail['max']} ({detail.get('description', '')})")

    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
