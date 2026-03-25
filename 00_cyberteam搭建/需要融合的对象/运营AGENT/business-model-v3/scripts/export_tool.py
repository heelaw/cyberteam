#!/usr/bin/env python3
"""
报告导出工具
将业务模型分析报告导出为不同格式（PDF/HTML/Excel）
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReportExporter:
    """报告导出器"""

    def __init__(self, workflow_dir: str = None):
        """
        初始化导出器

        Args:
            workflow_dir: 输出目录（旧名称保持兼容）
        """
        if workflow_dir is None:
            # 默认使用 skill 目录下的 output
            skill_base = Path(__file__).parent.parent
            workflow_dir = skill_base / "output"
        self.workflow_dir = Path(workflow_dir)
        self.report_dir = self.workflow_dir / "06-final-report"

    def find_latest_report(self) -> Optional[Path]:
        """
        查找最新的报告文件

        Returns:
            报告文件路径，不存在则返回 None
        """
        if not self.report_dir.exists():
            return None

        reports = list(self.report_dir.glob("*.md"))
        if not reports:
            return None

        # 按修改时间排序，返回最新的
        reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return reports[0]

    def read_report(self, report_path: Path = None) -> Optional[str]:
        """
        读取报告内容

        Args:
            report_path: 报告路径，为 None 则自动查找最新报告

        Returns:
            报告内容
        """
        if report_path is None:
            report_path = self.find_latest_report()

        if report_path is None or not report_path.exists():
            return None

        with open(report_path, "r", encoding="utf-8") as f:
            return f.read()

    def export_to_html(self, report_path: Path = None,
                      output_path: Path = None) -> Optional[str]:
        """
        导出为 HTML

        Args:
            report_path: 源报告路径
            output_path: 输出路径

        Returns:
            导出文件路径
        """
        content = self.read_report(report_path)
        if content is None:
            return None

        # 如果未指定输出路径，使用默认路径
        if output_path is None:
            if report_path is None:
                report_path = self.find_latest_report()
            output_path = report_path.parent / f"{report_path.stem}.html"

        # 简单的 Markdown 到 HTML 转换
        html = self._markdown_to_html(content)

        # 保存文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return str(output_path)

    def _markdown_to_html(self, markdown: str) -> str:
        """
        简单的 Markdown 转 HTML

        Args:
            markdown: Markdown 内容

        Returns:
            HTML 内容
        """
        html = markdown

        # 转换标题
        html = html.replace("### ", "<h3>").replace("\n", "</h3>\n", 1)
        html = html.replace("## ", "<h2>").replace("\n", "</h2>\n", 1)
        html = html.replace("# ", "<h1>").replace("\n", "</h1>\n", 1)

        # 转换粗体
        html = html.replace("**", "<strong>").replace("**", "</strong>")

        # 转换表格（简单处理）
        lines = html.split("\n")
        in_table = False
        result = []

        for line in lines:
            if line.startswith("|") and line.endswith("|"):
                if not in_table:
                    result.append("<table>")
                    in_table = True

                # 跳过分隔行
                if "---" in line:
                    continue

                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                tag = "th" if not result[-1].endswith("</tr>") else "td"
                result.append(f"<tr>{''.join(f'<{tag}>{cell}</{tag}>' for cell in cells)}</tr>")
            else:
                if in_table:
                    result.append("</table>")
                    in_table = False
                result.append(f"<p>{line}</p>" if line else "<br>")

        if in_table:
            result.append("</table>")

        # 包装成完整的 HTML 文档
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>业务模型分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        strong {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    {''.join(result)}
</body>
</html>"""

        return full_html

    def export_to_txt(self, report_path: Path = None,
                     output_path: Path = None) -> Optional[str]:
        """
        导出为纯文本

        Args:
            report_path: 源报告路径
            output_path: 输出路径

        Returns:
            导出文件路径
        """
        content = self.read_report(report_path)
        if content is None:
            return None

        if output_path is None:
            if report_path is None:
                report_path = self.find_latest_report()
            output_path = report_path.parent / f"{report_path.stem}.txt"

        # 移除 Markdown 格式符号
        txt = content
        txt = txt.replace("#", "")
        txt = txt.replace("**", "")
        txt = txt.replace("|", " | ")
        txt = txt.replace("---", "---")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(txt)

        return str(output_path)

    def export_summary(self, report_path: Path = None,
                      output_path: Path = None) -> Optional[str]:
        """
        导出执行摘要

        Args:
            report_path: 源报告路径
            output_path: 输出路径

        Returns:
            导出文件路径
        """
        content = self.read_report(report_path)
        if content is None:
            return None

        if output_path is None:
            if report_path is None:
                report_path = self.find_latest_report()
            output_path = report_path.parent / f"{report_path.stem}-summary.md"

        # 提取关键信息生成摘要
        lines = content.split("\n")
        summary = []
        capture = False

        # 提取核心发现、关键建议等关键部分
        keywords = ["核心发现", "关键建议", "破局策略", "优化建议"]
        for i, line in enumerate(lines):
            if any(kw in line for kw in keywords):
                capture = True
            if capture:
                summary.append(line)
                if line.strip() == "" and len(summary) > 10:
                    break

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(summary))

        return str(output_path)

    def create_export_package(self, formats: List[str] = None) -> Dict[str, Any]:
        """
        创建导出包（包含多种格式）

        Args:
            formats: 要导出的格式列表，如 ["html", "txt", "summary"]

        Returns:
            导出结果
        """
        if formats is None:
            formats = ["html", "txt", "summary"]

        report_path = self.find_latest_report()
        if report_path is None:
            return {"error": "未找到报告文件"}

        results = {
            "source": str(report_path),
            "exports": {}
        }

        for fmt in formats:
            if fmt == "html":
                path = self.export_to_html(report_path)
                results["exports"]["html"] = path
            elif fmt == "txt":
                path = self.export_to_txt(report_path)
                results["exports"]["txt"] = path
            elif fmt == "summary":
                path = self.export_summary(report_path)
                results["exports"]["summary"] = path

        return results

    def generate_export_report(self) -> str:
        """
        生成导出报告

        Returns:
            报告文本
        """
        lines = [
            "# 导出报告",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        report_path = self.find_latest_report()
        if report_path:
            lines.extend([
                f"源报告: {report_path.name}",
                f"报告大小: {report_path.stat().st_size} bytes",
                f"修改时间: {datetime.fromtimestamp(report_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}",
                ""
            ])

            # 尝试导出各种格式
            html_path = self.export_to_html(report_path)
            if html_path:
                lines.append(f"✅ HTML 导出: {html_path}")

            txt_path = self.export_to_txt(report_path)
            if txt_path:
                lines.append(f"✅ TXT 导出: {txt_path}")

            summary_path = self.export_summary(report_path)
            if summary_path:
                lines.append(f"✅ 摘要导出: {summary_path}")
        else:
            lines.append("⚠️ 未找到可导出的报告")

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="业务模型报告导出工具")
    parser.add_argument("--workflow-dir", default="output",
                        help="输出目录 (默认: output)")
    parser.add_argument("--report",
                        help="指定报告文件路径")
    parser.add_argument("--format", choices=["html", "txt", "summary", "all"],
                        default="html", help="导出格式")
    parser.add_argument("--output", "-o",
                        help="输出文件路径")

    args = parser.parse_args()

    exporter = ReportExporter(args.workflow_dir)

    if args.format == "all":
        results = exporter.create_export_package()
        if "error" in results:
            print(f"❌ {results['error']}")
        else:
            print("✅ 导出完成:")
            for fmt, path in results["exports"].items():
                print(f"  {fmt.upper()}: {path}")
    elif args.format == "html":
        path = exporter.export_to_html(
            Path(args.report) if args.report else None,
            Path(args.output) if args.output else None
        )
        if path:
            print(f"✅ HTML 导出: {path}")
        else:
            print("❌ 导出失败：未找到报告文件")
    elif args.format == "txt":
        path = exporter.export_to_txt(
            Path(args.report) if args.report else None,
            Path(args.output) if args.output else None
        )
        if path:
            print(f"✅ TXT 导出: {path}")
        else:
            print("❌ 导出失败：未找到报告文件")
    elif args.format == "summary":
        path = exporter.export_summary(
            Path(args.report) if args.report else None,
            Path(args.output) if args.output else None
        )
        if path:
            print(f"✅ 摘要导出: {path}")
        else:
            print("❌ 导出失败：未找到报告文件")


if __name__ == "__main__":
    main()
