#!/usr/bin/env python3
"""
业务模型验证引擎

可配置的业务逻辑验证规则系统：
1. 数学关系验证
2. 行业基准验证
3. 数据完整性验证
4. 一致性检查
"""

import re
import yaml
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class ValidationResult(Enum):
    """验证结果"""
    PASS = "✅"
    WARNING = "⚠️ "
    ERROR = "❌"
    INFO = "ℹ️ "


@dataclass
class ValidationIssue:
    """验证问题"""
    rule_name: str
    severity: ValidationResult
    message: str
    locations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        location_str = f" ({', '.join(self.locations)})" if self.locations else ""
        return f"{self.severity.value} {self.rule_name}{location_str}: {self.message}"


@dataclass
class ValidationReport:
    """验证报告"""
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    errors: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue):
        """添加问题"""
        self.issues.append(issue)
        self.total_checks += 1

        if issue.severity == ValidationResult.PASS:
            self.passed += 1
        elif issue.severity == ValidationResult.WARNING:
            self.warnings += 1
        elif issue.severity == ValidationResult.ERROR:
            self.errors += 1

    def print_report(self):
        """打印报告"""
        print("\n" + "="*70)
        print("📊 业务模型验证报告")
        print("="*70)

        print(f"\n总检查项: {self.total_checks}")
        print(f"{ValidationResult.PASS.value} 通过: {self.passed}")
        print(f"{ValidationResult.WARNING.value} 警告: {self.warnings}")
        print(f"{ValidationResult.ERROR.value} 错误: {self.errors}")

        if self.issues:
            print("\n" + "-"*70)
            print("详细问题列表:")
            print("-"*70)

            for issue in self.issues:
                print(f"\n{issue}")
                if issue.details:
                    for key, value in issue.details.items():
                        print(f"  - {key}: {value}")

        print("\n" + "="*70)

        if self.errors > 0:
            print(f"⛔ 验证失败：发现 {self.errors} 个错误")
        elif self.warnings > 0:
            print(f"⚠️  验证通过但有 {self.warnings} 个警告")
        else:
            print("🎉 验证全部通过！")

        print("="*70 + "\n")


class ValidationRule:
    """验证规则基类"""

    def __init__(self, name: str, severity: ValidationResult = ValidationResult.ERROR):
        self.name = name
        self.severity = severity

    def validate(self, parameters: Dict[str, Any], document: str) -> Optional[ValidationIssue]:
        """执行验证"""
        raise NotImplementedError


class MathematicalConsistencyRule(ValidationRule):
    """数学一致性规则"""

    def __init__(self, expr: str, **kwargs):
        super().__init__(**kwargs)
        self.expression = expr

    def validate(self, parameters: Dict[str, Any], document: str) -> Optional[ValidationIssue]:
        """验证数学关系"""
        try:
            # 简单实现：支持 ltv > cac 这样的表达式
            if self.expression == "ltv > cac":
                if 'LTV' in parameters and 'CAC' in parameters:
                    ltv = parameters['LTV'].value
                    cac = parameters['CAC'].value

                    if ltv > cac:
                        return None  # 通过
                    else:
                        return ValidationIssue(
                            rule_name=self.name,
                            severity=self.severity,
                            message=f"LTV (${ltv}) 应该大于 CAC (${cac}) 才能盈利",
                            details={'LTV': ltv, 'CAC': cac}
                        )

            elif self.expression == "funnel.is_decreasing()":
                if 'conversion_funnel' in parameters:
                    funnel = parameters['conversion_funnel'].value
                    prev_rate = float('inf')

                    for i, step in enumerate(funnel):
                        if step['rate'] > prev_rate:
                            return ValidationIssue(
                                rule_name=self.name,
                                severity=self.severity,
                                message=f"转化漏斗第{i+1}步不递减: {step['name']} = {step['rate']:.2%}",
                                details={'step': step, 'index': i}
                            )
                        prev_rate = step['rate']

        except Exception as e:
            return ValidationIssue(
                rule_name=self.name,
                severity=ValidationResult.ERROR,
                message=f"验证规则执行失败: {str(e)}"
            )

        return None


class IndustryBenchmarkRule(ValidationRule):
    """行业基准验证规则"""

    def __init__(self, metric: str, industry: str, min_val: float, max_val: float, **kwargs):
        super().__init__(**kwargs)
        self.metric = metric
        self.industry = industry
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, parameters: Dict[str, Any], document: str) -> Optional[ValidationIssue]:
        """验证指标是否在行业基准范围内"""
        if self.metric not in parameters:
            return None

        value = parameters[self.metric].value

        if value < self.min_val or value > self.max_val:
            return ValidationIssue(
                rule_name=self.name,
                severity=ValidationResult.WARNING,
                message=f"{self.metric} (${value:,.0f}) 超出 {self.industry} 行业基准范围 (${self.min_val:,.0f} - ${self.max_val:,.0f})",
                details={
                    'metric': self.metric,
                    'value': value,
                    'industry': self.industry,
                    'expected_range': f"${self.min_val:,.0f} - ${self.max_val:,.0f}"
                }
            )

        return None


class ConsistencyCheckRule(ValidationRule):
    """一致性检查规则"""

    def __init__(self, metric_pattern: str, **kwargs):
        super().__init__(**kwargs)
        self.metric_pattern = metric_pattern

    def validate(self, parameters: Dict[str, Any], document: str) -> Optional[ValidationIssue]:
        """检查同一指标在不同位置的值是否一致"""
        # 查找匹配的指标
        matching_metrics = [
            (name, param) for name, param in parameters.items()
            if re.search(self.metric_pattern, name, re.IGNORECASE)
        ]

        if len(matching_metrics) < 2:
            return None

        # 检查值是否一致
        values = [param.value for _, param in matching_metrics]
        if len(set(values)) > 1:
            locations = [
                f"{param.locations[0].section} (行{param.locations[0].line_number})"
                for _, param in matching_metrics
            ]

            return ValidationIssue(
                rule_name=self.name,
                severity=ValidationResult.ERROR,
                message=f"指标 {self.metric_pattern} 在不同位置的值不一致",
                details={
                    'values': [{'name': name, 'value': param.value} for name, param in matching_metrics],
                    'locations': locations
                }
            )

        return None


class CompletenessRule(ValidationRule):
    """完整性检查规则"""

    def __init__(self, required_sections: List[str] = None, required_metrics: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.required_sections = required_sections or []
        self.required_metrics = required_metrics or []

    def validate(self, parameters: Dict[str, Any], document: str) -> Optional[ValidationIssue]:
        """检查必需的章节和指标是否存在"""
        missing_sections = []
        missing_metrics = []

        # 检查章节
        for section in self.required_sections:
            if section not in document:
                missing_sections.append(section)

        # 检查指标
        for metric in self.required_metrics:
            if metric not in parameters:
                missing_metrics.append(metric)

        if missing_sections or missing_metrics:
            message_parts = []
            if missing_sections:
                message_parts.append(f"缺少章节: {', '.join(missing_sections)}")
            if missing_metrics:
                message_parts.append(f"缺少指标: {', '.join(missing_metrics)}")

            return ValidationIssue(
                rule_name=self.name,
                severity=ValidationResult.ERROR,
                message="; ".join(message_parts),
                details={
                    'missing_sections': missing_sections,
                    'missing_metrics': missing_metrics
                }
            )

        return None


class ValidationEngine:
    """验证引擎"""

    def __init__(self, config_path: Optional[str] = None):
        self.rules: List[ValidationRule] = []
        self.report = ValidationReport()

        if config_path:
            self.load_rules_from_config(config_path)
        else:
            self.load_default_rules()

    def load_rules_from_config(self, config_path: str):
        """从配置文件加载规则"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 加载规则配置
        if 'mathematical_consistency' in config:
            for rule_config in config['mathematical_consistency']:
                self.rules.append(MathematicalConsistencyRule(**rule_config))

        if 'industry_benchmarks' in config:
            for rule_config in config['industry_benchmarks']:
                self.rules.append(IndustryBenchmarkRule(**rule_config))

        if 'consistency_checks' in config:
            for rule_config in config['consistency_checks']:
                self.rules.append(ConsistencyCheckRule(**rule_config))

        if 'completeness' in config:
            self.rules.append(CompletenessRule(**config['completeness']))

    def load_default_rules(self):
        """加载默认规则集"""
        # 数学一致性
        self.rules.extend([
            MathematicalConsistencyRule(
                name="LTV > CAC",
                expr="ltv > cac",
                severity=ValidationResult.WARNING
            ),
            MathematicalConsistencyRule(
                name="转化漏斗递减",
                expr="funnel.is_decreasing()",
                severity=ValidationResult.ERROR
            ),
        ])

        # 完整性检查
        self.rules.append(
            CompletenessRule(
                name="核心章节完整性",
                required_sections=[
                    '市场分析', '商业模式', '转化路径', '收入公式'
                ],
                required_metrics=['CAC', 'LTV'],
                severity=ValidationResult.WARNING
            )
        )

    def add_rule(self, rule: ValidationRule):
        """添加自定义规则"""
        self.rules.append(rule)

    def add_custom_rule(self, name: str, validation_func: Callable, severity: ValidationResult = ValidationResult.ERROR):
        """添加自定义验证函数"""
        class CustomRule(ValidationRule):
            def validate(self, parameters, document):
                return validation_func(name, parameters, document)

        rule = CustomRule(name=name, severity=severity)
        self.add_rule(rule)

    def validate(self, parameters: Dict[str, Any], document: str) -> ValidationReport:
        """执行所有验证"""
        self.report = ValidationReport()

        for rule in self.rules:
            try:
                issue = rule.validate(parameters, document)
                if issue:
                    self.report.add_issue(issue)
                else:
                    # 通过检查
                    self.report.total_checks += 1
                    self.report.passed += 1
            except Exception as e:
                # 规则执行失败
                self.report.add_issue(
                    ValidationIssue(
                        rule_name=rule.name,
                        severity=ValidationResult.ERROR,
                        message=f"规则执行失败: {str(e)}"
                    )
                )

        return self.report


def main():
    """命令行入口"""
    import sys
    from core.parameter_extractor import ParameterExtractor

    if len(sys.argv) < 2:
        print("Usage: python validation_engine.py <document_path> [config_path]")
        sys.exit(1)

    document_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else None

    # 读取文档
    with open(document_path, 'r', encoding='utf-8') as f:
        document = f.read()

    # 提取参数
    extractor = ParameterExtractor(document_path)
    parameters = extractor.extract_all()

    # 验证
    engine = ValidationEngine(config_path)
    report = engine.validate(parameters, document)
    report.print_report()


if __name__ == '__main__':
    main()
