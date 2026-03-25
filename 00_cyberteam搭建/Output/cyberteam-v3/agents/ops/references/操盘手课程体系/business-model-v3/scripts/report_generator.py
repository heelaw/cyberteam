#!/usr/bin/env python3
"""
最终报告生成脚本
整合各阶段分析结果，生成完整的业务模型分析报告
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReportGenerator:
    """报告生成器"""

    def __init__(self, workflow_dir: str = None, skill_dir: str = None):
        """
        初始化报告生成器

        Args:
            workflow_dir: 输出目录（旧名称保持兼容）
            skill_dir: Skill 目录（用于访问模板）
        """
        if workflow_dir is None:
            # 默认使用 skill 目录下的 output
            skill_base = Path(__file__).parent.parent
            workflow_dir = skill_base / "output"
        self.workflow_dir = Path(workflow_dir)
        self.skill_dir = Path(skill_dir) if skill_dir else Path(__file__).parent.parent
        self.template_path = self.skill_dir / "assets" / "final-report-template.md"

    def load_template(self) -> str:
        """加载报告模板"""
        if self.template_path.exists():
            with open(self.template_path, "r", encoding="utf-8") as f:
                return f.read()
        return self._get_default_template()

    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """# 业务模型分析与优化方案

## 1. 报告概述

| **项目** | **内容** |
|---------|---------|
| 报告名称 | 业务模型分析与优化方案 |
| 分析对象 | {{business_name}} |
| 分析日期 | {{report_date}} |
| 报告类型 | 综合分析报告 |
| 分析目的 | 系统化梳理业务全局视图，分析收入公式，映射转化链路，定义运营指标，并提供针对性的破局点建议 |

{{#each sections}}
## {{@key}}

{{this}}
{{/each}}

## 8. 总结与结论

### 8.1 核心发现

{{core_findings}}

### 8.2 关键建议

{{key_recommendations}}

### 8.3 长期发展展望

{{long_term_outlook}}

---

*报告生成时间: {{generated_at}}*
"""

    def load_stage_outputs(self) -> Dict[str, Any]:
        """
        加载各阶段输出

        Returns:
            各阶段的输出数据
        """
        # 这里可以集成 workflow_manager 来获取状态
        # 现在先从文件系统读取
        outputs = {}

        stage_dirs = {
            1: "01-business-model",
            2: "02-revenue-formula",
            3: "03-conversion-funnel",
            4: "04-operational-metrics",
            5: "05-breakthrough-points"
        }

        for stage_num, dir_name in stage_dirs.items():
            stage_dir = self.workflow_dir / dir_name
            if stage_dir.exists():
                files = list(stage_dir.glob("*.md"))
                if files:
                    with open(files[-1], "r", encoding="utf-8") as f:
                        outputs[f"stage_{stage_num}"] = f.read()

        return outputs

    def generate(self, config: Dict[str, Any], outputs: Dict[str, Any]) -> str:
        """
        生成最终报告

        Args:
            config: 工作流配置
            outputs: 各阶段输出数据

        Returns:
            生成的报告内容
        """
        template = self.load_template()

        # 准备替换变量
        variables = {
            "business_name": config.get("business_name", "未指定"),
            "report_date": datetime.now().strftime("%Y年%m月%d日"),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "business_type": config.get("business_type", ""),
            "business_stage": config.get("business_stage", "")
        }

        # 提取各阶段内容
        sections = self._extract_sections(outputs)

        # 提取核心发现和建议
        core_findings = self._extract_core_findings(outputs)
        key_recommendations = self._extract_key_recommendations(outputs)

        # 替换模板变量
        report = self._render_template(template, variables, sections, core_findings, key_recommendations)

        return report

    def _extract_sections(self, outputs: Dict[str, Any]) -> Dict[str, str]:
        """从各阶段输出中提取章节内容"""
        sections = {
            "2. 业务模型架构": outputs.get("stage_1", "待补充"),
            "3. 收入公式分析": outputs.get("stage_2", "待补充"),
            "4. 转化链路分析": outputs.get("stage_3", "待补充"),
            "5. 运营指标体系": outputs.get("stage_4", "待补充"),
            "6. 破局点分析与建议": outputs.get("stage_5", "待补充")
        }
        return sections

    def _extract_core_findings(self, outputs: Dict[str, Any]) -> str:
        """提取核心发现"""
        findings = []

        # 从各阶段输出中提取关键发现
        for stage_key, content in outputs.items():
            if "核心发现" in content or "关键发现" in content:
                # 简单的提取逻辑，实际可以更复杂
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "核心发现" in line or "关键发现" in line:
                        # 提取后续几行
                        excerpt = "\n".join(lines[i:i+5])
                        findings.append(excerpt)
                        break

        return "\n\n".join(findings) if findings else "基于以上分析，建议优化核心转化链路，提升关键运营指标。"

    def _extract_key_recommendations(self, outputs: Dict[str, Any]) -> str:
        """提取关键建议"""
        recommendations = []

        # 从 Stage 5（破局点建议）中提取
        stage_5 = outputs.get("stage_5", "")
        if "破局策略" in stage_5:
            lines = stage_5.split("\n")
            for i, line in enumerate(lines):
                if "短期策略" in line or "中期策略" in line:
                    recommendations.append(line)

        return "\n".join(recommendations[:5]) if recommendations else "建议优先实施短期优化策略，快速提升业务指标。"

    def _render_template(self, template: str, variables: Dict[str, str],
                        sections: Dict[str, str], core_findings: str,
                        key_recommendations: str) -> str:
        """渲染模板"""
        report = template

        # 替换基本变量
        for key, value in variables.items():
            report = report.replace(f"{{{{{key}}}}}", value)

        # 替换章节内容
        report = report.replace("{{core_findings}}", core_findings)
        report = report.replace("{{key_recommendations}}", key_recommendations)
        report = report.replace("{{long_term_outlook}}", "建议持续监测运营指标，根据数据反馈不断优化业务模型。")

        # 替换各章节
        for section_name, content in sections.items():
            placeholder = f"{{{{section_{section_name.split('.')[0]}_content}}}}"
            report = report.replace(placeholder, content)

        return report

    def save_report(self, report: str, business_name: str = "business") -> str:
        """
        保存报告到文件

        Args:
            report: 报告内容
            business_name: 业务名称

        Returns:
            保存的文件路径
        """
        # 创建输出目录
        output_dir = self.workflow_dir / "06-final-report"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{business_name}-{date_str}-final-report.md"
        filepath = output_dir / filename

        # 保存文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

        return str(filepath)

    def generate_and_save(self, config: Dict[str, Any],
                         outputs: Optional[Dict[str, Any]] = None) -> str:
        """
        生成并保存报告

        Args:
            config: 工作流配置
            outputs: 各阶段输出，为 None 则自动加载

        Returns:
            保存的文件路径
        """
        if outputs is None:
            outputs = self.load_stage_outputs()

        report = self.generate(config, outputs)
        business_name = config.get("business_name", "business").lower().replace(" ", "-")
        filepath = self.save_report(report, business_name)

        return filepath


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="业务模型分析报告生成工具")
    parser.add_argument("--workflow-dir", default="output",
                        help="输出目录 (默认: output)")
    parser.add_argument("--skill-dir",
                        help="Skill 目录（默认自动检测）")
    parser.add_argument("--business-name", required=True,
                        help="业务/公司名称")
    parser.add_argument("--business-type",
                        help="业务类型 (toB/toC/toG)")
    parser.add_argument("--business-stage",
                        help="业务阶段 (初创期/成长期/成熟期)")
    parser.add_argument("--output", "-o",
                        help="输出文件路径（可选）")

    args = parser.parse_args()

    # 准备配置
    config = {
        "business_name": args.business_name,
        "business_type": args.business_type or "未指定",
        "business_stage": args.business_stage or "未指定"
    }

    # 创建生成器
    generator = ReportGenerator(args.workflow_dir, args.skill_dir)

    # 生成报告
    filepath = generator.generate_and_save(config)

    print(f"✅ 报告已生成: {filepath}")


if __name__ == "__main__":
    main()
