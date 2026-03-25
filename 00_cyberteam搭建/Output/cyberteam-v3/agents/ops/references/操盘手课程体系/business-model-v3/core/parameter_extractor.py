#!/usr/bin/env python3
"""
业务模型参数提取器

从业务文档中自动提取关键参数，支持：
1. 指标识别（CAC、LTV、转化率等）
2. 转化漏斗提取
3. 财务数据提取
4. 参数依赖关系分析
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class ParameterLocation:
    """参数在文档中的位置"""
    file_path: str
    section: str
    line_number: int
    context: str  # 前后文用于验证


@dataclass
class Parameter:
    """参数定义"""
    name: str
    value: Any
    type: str  # 'metric', 'rate', 'ratio', 'financial', 'text'
    locations: List[ParameterLocation] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)  # 依赖的其他参数
    formula: Optional[str] = None  # 如果是计算得出的


class ParameterExtractor:
    """参数提取器"""

    # 常见指标的正则模式
    PATTERNS = {
        'percentage': r'(\d+\.?\d*)%',
        'currency': r'\$?\s*(\d+,?\d*(?:\.\d+)?)\s*(?:USD|美元|美金)?',
        'ratio': r'(\d+\.?\d*):\s*(\d+\.?\d*)',
        'funnel_step': r'[\[（](.+?)[\]）]\s*[→→]\s*(\d+\.?\d*)%',
        'cac': r'CAC[：:\s]*(\$?\s*(\d+,?\d*(?:\.\d+)?))',
        'ltv': r'LTV[：:\s]*(\$?\s*(\d+,?\d*(?:\.\d+)?))',
        'roi': r'ROI[：:\s]*(\d+\.?\d*)x',
        'conversion_rate': r'转化率[：:\s]*(\d+\.?\d*)%',
    }

    def __init__(self, document_path: str):
        self.document_path = Path(document_path)
        self.document = self._read_document()
        self.parameters: Dict[str, Parameter] = {}

    def _read_document(self) -> str:
        """读取文档内容"""
        with open(self.document_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_all(self) -> Dict[str, Parameter]:
        """提取所有参数"""
        print("🔍 开始提取参数...")

        # 1. 提取转化率
        self._extract_conversion_rates()

        # 2. 提取财务指标
        self._extract_financial_metrics()

        # 3. 提取转化漏斗
        self._extract_conversion_funnel()

        # 4. 分析依赖关系
        self._analyze_dependencies()

        print(f"✅ 提取完成，共找到 {len(self.parameters)} 个参数")
        return self.parameters

    def _extract_conversion_rates(self):
        """提取所有转化率"""
        for match in re.finditer(self.PATTERNS['percentage'], self.document):
            value = float(match.group(1))
            context = self._get_context(match.start())

            # 尝试识别这是哪个指标的转化率
            metric_name = self._identify_conversion_metric(context)

            if metric_name:
                self._add_parameter(
                    name=metric_name,
                    value=value / 100,  # 转换为小数
                    type='rate',
                    context=context
                )

    def _extract_financial_metrics(self):
        """提取财务指标"""
        # CAC
        for match in re.finditer(self.PATTERNS['cac'], self.document, re.IGNORECASE):
            value = self._parse_currency(match.group(1))
            self._add_parameter(
                name='CAC',
                value=value,
                type='metric',
                context=self._get_context(match.start())
            )

        # LTV
        for match in re.finditer(self.PATTERNS['ltv'], self.document, re.IGNORECASE):
            value = self._parse_currency(match.group(1))
            self._add_parameter(
                name='LTV',
                value=value,
                type='metric',
                context=self._get_context(match.start())
            )

        # ROI
        for match in re.finditer(self.PATTERNS['roi'], self.document, re.IGNORECASE):
            value = float(match.group(1))
            self._add_parameter(
                name='ROI',
                value=value,
                type='ratio',
                context=self._get_context(match.start())
            )

    def _extract_conversion_funnel(self):
        """提取转化漏斗"""
        # 查找转化漏斗的定义
        funnel_pattern = r'([触达完播兴趣预约付款扫描].*?)\s*[→→]\s*(\d+\.?\d*)%'

        funnel_steps = []
        for match in re.finditer(funnel_pattern, self.document):
            step_name = match.group(1).strip()
            conversion_rate = float(match.group(2)) / 100
            funnel_steps.append({
                'name': step_name,
                'rate': conversion_rate
            })

        if funnel_steps:
            # 计算整体转化率
            overall_rate = 1.0
            for step in funnel_steps:
                overall_rate *= step['rate']

            self._add_parameter(
                name='overall_conversion_rate',
                value=overall_rate,
                type='rate',
                formula=' × '.join([f"{step['rate']:.4f}" for step in funnel_steps])
            )

            # 保存漏斗结构
            self._add_parameter(
                name='conversion_funnel',
                value=funnel_steps,
                type='structure'
            )

    def _identify_conversion_metric(self, context: str) -> Optional[str]:
        """根据上下文识别转化率指标名称"""
        context_lower = context.lower()

        # 关键词映射
        keywords_map = {
            '完播': 'completion_rate',
            '点击': 'click_through_rate',
            '兴趣': 'interest_rate',
            '预约': 'booking_rate',
            '付款': 'payment_rate',
            '到店': 'visit_rate',
            '转化': 'conversion_rate',
        }

        for keyword, metric_name in keywords_map.items():
            if keyword in context:
                return metric_name

        return None

    def _parse_currency(self, value_str: str) -> float:
        """解析货币字符串"""
        # 移除$、逗号等
        cleaned = re.sub(r'[\$\s,]', '', value_str)
        return float(cleaned)

    def _get_context(self, position: int, window: int = 50) -> str:
        """获取指定位置周围的上下文"""
        start = max(0, position - window)
        end = min(len(self.document), position + window)
        return self.document[start:end]

    def _add_parameter(self, name: str, value: Any, type: str,
                      context: str = '', formula: str = None):
        """添加或更新参数"""
        # 计算行号
        line_number = self.document[:self.document.find(context)].count('\n') + 1 if context else 0

        location = ParameterLocation(
            file_path=str(self.document_path),
            section=self._identify_section(context),
            line_number=line_number,
            context=context
        )

        if name in self.parameters:
            # 参数已存在，添加位置
            self.parameters[name].locations.append(location)
            # 检查值是否一致
            if self.parameters[name].value != value:
                print(f"⚠️  参数 {name} 值不一致: {self.parameters[name].value} vs {value}")
        else:
            # 新参数
            self.parameters[name] = Parameter(
                name=name,
                value=value,
                type=type,
                locations=[location],
                formula=formula
            )

    def _identify_section(self, context: str) -> str:
        """根据上下文识别章节"""
        # 简单实现：查找最近的 ## 标题
        pos = self.document.find(context)
        before = self.document[:pos]
        matches = list(re.finditer(r'##\s+(.+)', before))
        return matches[-1].group(1) if matches else 'Unknown'

    def _analyze_dependencies(self):
        """分析参数间的依赖关系"""
        # LTV:CAC 比率依赖 LTV 和 CAC
        if 'LTV' in self.parameters and 'CAC' in self.parameters:
            ratio_name = 'LTV_CAC_ratio'
            if ratio_name not in self.parameters:
                ltv = self.parameters['LTV'].value
                cac = self.parameters['CAC'].value
                if cac > 0:
                    self._add_parameter(
                        name=ratio_name,
                        value=ltv / cac,
                        type='ratio',
                        formula=f'LTV / CAC = {ltv} / {cac}'
                    )
                    self.parameters[ratio_name].depends_on = ['LTV', 'CAC']

    def export_to_json(self, output_path: str):
        """导出参数到JSON文件"""
        serializable_params = {}
        for name, param in self.parameters.items():
            serializable_params[name] = {
                'value': param.value,
                'type': param.type,
                'locations': [
                    {
                        'file': loc.file_path,
                        'section': loc.section,
                        'line': loc.line_number,
                    }
                    for loc in param.locations
                ],
                'depends_on': param.depends_on,
                'formula': param.formula
            }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_params, f, indent=2, ensure_ascii=False)

        print(f"✅ 参数已导出到: {output_path}")

    def get_parameter_summary(self) -> str:
        """获取参数摘要"""
        summary = ["# 参数提取摘要\n"]
        summary.append(f"## 共提取 {len(self.parameters)} 个参数\n")

        # 按类型分组
        by_type = {}
        for name, param in self.parameters.items():
            if param.type not in by_type:
                by_type[param.type] = []
            by_type[param.type].append(name)

        for type_name, params in by_type.items():
            summary.append(f"\n### {type_name.upper()} ({len(params)}个)")
            for param_name in params:
                param = self.parameters[param_name]
                summary.append(f"- **{param_name}**: {param.value}")
                if param.formula:
                    summary.append(f"  - 公式: {param.formula}")
                if param.depends_on:
                    summary.append(f"  - 依赖: {', '.join(param.depends_on)}")

        return '\n'.join(summary)


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parameter_extractor.py <document_path> [output_json_path]")
        sys.exit(1)

    document_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'parameters.json'

    extractor = ParameterExtractor(document_path)
    parameters = extractor.extract_all()

    # 导出JSON
    extractor.export_to_json(output_path)

    # 打印摘要
    print("\n" + "="*60)
    print(extractor.get_parameter_summary())
    print("="*60)


if __name__ == '__main__':
    main()
