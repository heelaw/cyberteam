#!/usr/bin/env python3
"""
模板验证工具
验证各阶段输入的完整性，并提供模板字段填充辅助
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TemplateValidator:
    """模板验证器"""

    def __init__(self, skill_dir: str = None):
        """
        初始化验证器

        Args:
            skill_dir: Skill 目录
        """
        self.skill_dir = Path(skill_dir) if skill_dir else Path(__file__).parent.parent
        self.assets_dir = self.skill_dir / "assets"

    def validate_stage_input(self, stage_num: int, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证指定阶段的输入数据

        Args:
            stage_num: 阶段编号 (1-5)
            data: 输入数据

        Returns:
            (是否有效, 错误/警告列表)
        """
        validators = {
            1: self._validate_stage_1,
            2: self._validate_stage_2,
            3: self._validate_stage_3,
            4: self._validate_stage_4,
            5: self._validate_stage_5
        }

        validator = validators.get(stage_num)
        if validator:
            return validator(data)

        return False, [f"未知的阶段编号: {stage_num}"]

    def _validate_stage_1(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Stage 1: 业务模型映射"""
        errors = []

        required_fields = {
            "商业模式": ["市场定位", "价值主张", "收入模式", "渠道策略"],
            "商业经营模型": ["成本结构", "利润模型", "现金流"],
            "业务模型": ["核心业务流程", "资源配置", "核心能力"]
        }

        for section, fields in required_fields.items():
            if section not in data:
                errors.append(f"缺少 {section} 部分")
            else:
                for field in fields:
                    if field not in data[section]:
                        errors.append(f"{section} 中缺少 {field}")

        return len(errors) == 0, errors

    def _validate_stage_2(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Stage 2: 收入公式分析"""
        errors = []

        if "核心收入公式" not in data:
            errors.append("缺少核心收入公式")

        if "收入构成" not in data:
            errors.append("缺少收入构成分析")

        if "关键变量" not in data:
            errors.append("缺少关键变量定义")
        else:
            # 验证变量定义格式
            for var in data.get("关键变量", []):
                if "名称" not in var or "基准值" not in var:
                    errors.append(f"变量定义不完整: {var}")

        return len(errors) == 0, errors

    def _validate_stage_3(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Stage 3: 转化链路分析"""
        errors = []

        if "转化路径" not in data:
            errors.append("缺少转化路径定义")

        if "转化节点" not in data:
            errors.append("缺少转化节点定义")
        else:
            nodes = data["转化节点"]
            if len(nodes) < 2:
                errors.append("转化节点数量不足（至少需要2个）")

            # 验证节点数据
            for node in nodes:
                if "名称" not in node:
                    errors.append(f"节点缺少名称: {node}")
                if "转化率" not in node and "预估转化率" not in node:
                    errors.append(f"节点缺少转化率: {node.get('名称', '未知')}")

        return len(errors) == 0, errors

    def _validate_stage_4(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Stage 4: 运营指标定义"""
        errors = []

        if "指标体系" not in data:
            errors.append("缺少指标体系定义")
        else:
            required_levels = ["顶层指标", "中层指标", "底层指标"]
            for level in required_levels:
                if level not in data["指标体系"]:
                    errors.append(f"缺少 {level}")

        # 验证指标定义完整性
        if "核心指标" not in data:
            errors.append("缺少核心指标定义")
        else:
            for metric in data["核心指标"]:
                if "名称" not in metric:
                    errors.append(f"指标缺少名称: {metric}")
                if "计算公式" not in metric:
                    errors.append(f"指标缺少计算公式: {metric.get('名称', '未知')}")
                if "目标值" not in metric:
                    errors.append(f"指标缺少目标值: {metric.get('名称', '未知')}")

        return len(errors) == 0, errors

    def _validate_stage_5(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证 Stage 5: 破局点建议"""
        errors = []

        if "核心瓶颈" not in data:
            errors.append("缺少核心瓶颈识别")

        if "破局策略" not in data:
            errors.append("缺少破局策略定义")
        else:
            strategies = data["破局策略"]
            strategy_types = ["短期策略", "中期策略", "长期策略"]

            for strategy_type in strategy_types:
                if strategy_type not in strategies:
                    errors.append(f"缺少 {strategy_type}")
                else:
                    for strategy in strategies[strategy_type]:
                        if "策略名称" not in strategy:
                            errors.append(f"{strategy_type} 缺少策略名称")
                        if "具体措施" not in strategy:
                            errors.append(f"{strategy_type} 缺少具体措施")
                        if "预期效果" not in strategy:
                            errors.append(f"{strategy_type} 缺少预期效果")

        return len(errors) == 0, errors

    def extract_template_placeholders(self, template_path: str = None) -> List[str]:
        """
        从模板文件中提取占位符

        Args:
            template_path: 模板文件路径

        Returns:
            占位符列表
        """
        if template_path is None:
            template_path = self.assets_dir / "final-report-template.md"

        template_file = Path(template_path)
        if not template_file.exists():
            return []

        with open(template_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取 {{placeholder}} 格式的占位符
        pattern = r'\{\{([^}]+)\}\}'
        placeholders = re.findall(pattern, content)

        return sorted(set(placeholders))

    def get_template_fill_guide(self, stage_num: int) -> Dict[str, Any]:
        """
        获取指定阶段的模板填充指南

        Args:
            stage_num: 阶段编号

        Returns:
            填充指南字典
        """
        guides = {
            1: {
                "stage_name": "业务模型映射",
                "template_file": "business-model-template.md",
                "required_fields": {
                    "商业模式": {
                        "市场定位": "目标市场、用户群体、竞争格局",
                        "价值主张": "核心价值、差异化优势",
                        "收入模式": "收入来源、定价策略",
                        "渠道策略": "获客渠道、分销网络"
                    },
                    "商业经营模型": {
                        "成本结构": "固定成本、可变成本、边际成本",
                        "利润模型": "毛利率、净利率、ROI",
                        "现金流": "收入周期、支出周期、资金周转率"
                    },
                    "业务模型": {
                        "核心业务流程": "价值链、关键环节",
                        "资源配置": "人力、技术、资金",
                        "核心能力": "技术优势、运营能力、品牌影响力"
                    }
                }
            },
            2: {
                "stage_name": "收入公式分析",
                "template_file": "revenue-formula-template.md",
                "required_fields": {
                    "收入构成": ["直接收入", "间接收入", "增值收入"],
                    "核心收入公式": "如：收入 = 流量 × 转化率 × 客单价",
                    "关键变量": ["变量名称", "基准值", "变化范围", "影响程度"]
                }
            },
            3: {
                "stage_name": "转化链路分析",
                "template_file": "conversion-funnel-template.md",
                "required_fields": {
                    "转化路径": ["接触", "了解", "考虑", "决策", "转化", "留存", "推荐"],
                    "转化节点": ["节点名称", "转化率", "行业平均", "优化空间"],
                    "潜在流失点": ["流失节点", "流失原因", "影响程度"]
                }
            },
            4: {
                "stage_name": "运营指标定义",
                "template_file": "operational-metrics-template.md",
                "required_fields": {
                    "顶层指标": ["总收入", "净利润", "市场份额", "用户规模"],
                    "中层指标": ["总流量", "转化率", "客单价", "用户留存率"],
                    "底层指标": ["各转化节点指标", "计算公式", "目标值", "监测频率"]
                }
            },
            5: {
                "stage_name": "破局点建议",
                "template_file": "breakthrough-points-template.md",
                "required_fields": {
                    "核心瓶颈": ["瓶颈类型", "具体表现", "影响程度", "根本原因"],
                    "破局策略": {
                        "短期策略": ["策略名称", "具体措施", "预期效果", "资源需求"],
                        "中期策略": ["策略名称", "具体措施", "预期效果", "资源需求"],
                        "长期策略": ["策略名称", "具体措施", "预期效果", "资源需求"]
                    },
                    "风险评估": ["策略", "潜在风险", "应对预案"]
                }
            }
        }

        return guides.get(stage_num, {})

    def validate_completeness(self, data: Dict[str, Any], stage_num: int) -> Tuple[bool, float, List[str]]:
        """
        验证数据完整度

        Args:
            data: 要验证的数据
            stage_num: 阶段编号

        Returns:
            (是否完整, 完整度百分比, 缺失字段列表)
        """
        guide = self.get_template_fill_guide(stage_num)
        if not guide:
            return False, 0.0, ["未找到该阶段的填充指南"]

        required_fields = guide.get("required_fields", {})
        missing = []

        def check_fields(fields, prefix=""):
            """递归检查字段"""
            local_missing = []
            total = 0
            found = 0

            for key, value in fields.items():
                total += 1
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, list):
                    # 这是一个列表字段
                    if key not in data or not data[key]:
                        local_missing.append(full_key)
                    else:
                        found += 1
                elif isinstance(value, dict):
                    # 这是一个嵌套字段
                    if key in data and isinstance(data[key], dict):
                        sub_missing, sub_total, sub_found = check_fields(value, full_key)
                        local_missing.extend(sub_missing)
                        total += sub_total - 1
                        found += sub_found
                    else:
                        local_missing.append(full_key)
                else:
                    # 这是一个字符串字段
                    if key not in data or not data[key]:
                        local_missing.append(full_key)
                    else:
                        found += 1

            return local_missing, total, found

        missing, total, found = check_fields(required_fields)
        completeness = (found / total * 100) if total > 0 else 0

        return len(missing) == 0, completeness, missing


def main():
    """命令行入口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="业务模型模板验证工具")
    parser.add_argument("--stage", type=int, required=True,
                        help="阶段编号 (1-5)")
    parser.add_argument("--data", help="输入数据文件 (JSON)")
    parser.add_argument("--check-template", action="store_true",
                        help="检查模板占位符")
    parser.add_argument("--fill-guide", action="store_true",
                        help="显示填充指南")
    parser.add_argument("--skill-dir",
                        help="Skill 目录（默认自动检测）")

    args = parser.parse_args()

    validator = TemplateValidator(args.skill_dir)

    if args.check_template:
        placeholders = validator.extract_template_placeholders()
        print("模板占位符:")
        for p in placeholders:
            print(f"  - {{{{{p}}}}}")

    elif args.fill_guide:
        guide = validator.get_template_fill_guide(args.stage)
        if guide:
            print(f"\n=== Stage {args.stage}: {guide['stage_name']} ===")
            print(f"模板文件: {guide['template_file']}")
            print("\n必需字段:")
            print(json.dumps(guide['required_fields'], indent=2, ensure_ascii=False))

    elif args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)

        is_valid, errors = validator.validate_stage_input(args.stage, data)

        if is_valid:
            print("✅ 验证通过")
        else:
            print("❌ 验证失败:")
            for error in errors:
                print(f"  - {error}")

        # 检查完整度
        is_complete, completeness, missing = validator.validate_completeness(data, args.stage)
        print(f"\n完整度: {completeness:.1f}%")
        if missing:
            print("缺失字段:")
            for field in missing:
                print(f"  - {field}")


if __name__ == "__main__":
    main()
