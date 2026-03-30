#!/usr/bin/env python3
"""
Playground 自动生成器
从 CyberTeam 产出的文档中提取数据，自动填充 Playground HTML 模板

使用方法:
    python generate_playground.py --project <项目目录> --output <输出文件>
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import json


class PlaygroundGenerator:
    """Playground HTML 生成器"""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.data = {}
        self.template = self._load_template()

    def _load_template(self) -> str:
        """加载 Playground HTML 模板"""
        # 使用 v8 作为基础模板
        template_path = Path(__file__).parent / "活动看板_v8.html"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    def extract_from_docs(self) -> Dict:
        """从项目文档中提取数据"""
        docs_dir = self.project_dir / "01_Agent会议纪要" / "对话记录"

        data = {
            "project_name": self._extract_project_name(),
            "ceo_alignment": self._extract_ceo_alignment(docs_dir / "对话_01_CEO对齐_20260327.md"),
            "strategy": self._extract_strategy(docs_dir / "对话_02_策略讨论_20260327.md"),
            "risk": self._extract_risk(docs_dir / "对话_03_风险预案_20260327.md"),
            "ceo_report": self._extract_ceo_report(docs_dir / "对话_04_CEO汇报_20260327.md"),
        }
        return data

    def _extract_project_name(self) -> str:
        """提取项目名称"""
        # 从 metadata.yaml 读取
        metadata_path = self.project_dir / "00_项目资料" / "metadata.yaml"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'name[:\s]+(.+)', content)
                if match:
                    return match.group(1).strip()
        # 默认从目录名提取
        return self.project_dir.name

    def _extract_ceo_alignment(self, path: Path) -> Dict:
        """提取 CEO 对齐数据"""
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取北极星指标
        target_match = re.search(r'北极星指标[：:]\s*(\d+[万台]+)', content)
        timeline_match = re.search(r'(\d{4}[年/]\d{1,2}[月/]\d{1,2}[日-]?\d*)', content)
        budget_match = re.search(r'预算[：:]\s*(\d+[万]+)', content)

        return {
            "target": target_match.group(1) if target_match else "30,000台",
            "timeline": timeline_match.group(1) if timeline_match else "4月29日-5月5日",
            "budget": budget_match.group(1) if budget_match else "100万+20万应急",
        }

    def _extract_strategy(self, path: Path) -> Dict:
        """提取策略讨论数据"""
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取卖点优先级
        po_match = re.search(r'P0[：:]\s*([^P\n]+)', content)
        theme_match = re.search(r'核心主题[：:]\s*["""]?([^"""\n]+)["""]?', content)

        # 提取渠道销量占比
        channel_sales = {}
        channels = ['小红书', '抖音', '电商', '微信公众号', '知乎', 'B站', '微博']
        for channel in channels:
            match = re.search(f'{channel}[^\d]*(\d+)%', content)
            if match:
                channel_sales[channel] = match.group(1)

        return {
            "theme": theme_match.group(1).strip() if theme_match else "家的数字空间，每一刻都同步",
            "po": po_match.group(1).strip() if po_match else "手机内存焦虑+家庭共享",
            "channel_sales": channel_sales,
        }

    def _extract_risk(self, path: Path) -> Dict:
        """提取风险预案数据"""
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取风险列表
        risks = []
        risk_pattern = r'[R\d+][^\n]*\s*([^\n]+)'
        for match in re.finditer(risk_pattern, content):
            risk_text = match.group(1).strip()
            if risk_text and len(risk_text) > 10:
                risks.append(risk_text)
                if len(risks) >= 8:
                    break

        # 提取分层响应
        layers = []
        layer_patterns = [
            r'第一层[^<]{0,50}[<{]',
            r'第二层[^<]{0,50}[<{]',
            r'第三层[^<]{0,50}[<{]',
        ]
        for i, pattern in enumerate(layer_patterns):
            match = re.search(pattern, content)
            if match:
                layers.append(match.group(0)[:50])

        return {
            "risks": risks[:8],
            "layers": layers,
        }

    def _extract_ceo_report(self, path: Path) -> Dict:
        """提取 CEO 汇报数据"""
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取分层目标
        targets = []
        target_pattern = r'(保底|挑战|极限)\s*(\d+[万台]+)\s*\([^)]+\)'
        for match in re.finditer(target_pattern, content):
            targets.append({
                "type": match.group(1),
                "value": match.group(2),
            })

        # 提取渠道曝光和转化率
        channels = []
        channel_pattern = r'\|\s*([^|]+)\s*\|[^|]+\|[^|]+\|[^|]+\|([^|]+台)'
        for match in re.finditer(channel_pattern, content):
            channel_name = match.group(1).strip()
            sales = match.group(2).strip()
            if channel_name and sales and channel_name != '渠道':
                channels.append({"name": channel_name, "sales": sales})

        return {
            "targets": targets,
            "channels": channels,
        }

    def calculate_funnel(self, channel: str, exposure: float, rates: Dict) -> Dict:
        """计算漏斗数据"""
        calculations = {
            "小红书": {
                "exposure": exposure,
                "view": exposure * 0.45,
                "click": exposure * 0.45 * rates.get("ctr", 0.03),
                "collect": exposure * 0.45 * rates.get("ctr", 0.03) * 0.15,
                "convert": exposure * 0.45 * rates.get("ctr", 0.03) * 0.15 * rates.get("cvr", 0.008),
            },
            "抖音": {
                "exposure": exposure,
                "view": exposure * 0.60,
                "click": exposure * 0.60 * rates.get("ctr", 0.08),
                "convert": exposure * 0.60 * rates.get("ctr", 0.08) * rates.get("cvr", 0.05),
            },
            "电商": {
                "exposure": exposure,
                "click": exposure * 0.15,
                "cart": exposure * 0.15 * rates.get("cart", 0.20),
                "convert": exposure * 0.15 * rates.get("cart", 0.20) * rates.get("cvr", 0.30),
            }
        }
        return calculations.get(channel, calculations["小红书"])

    def generate(self, output_path: Optional[str] = None) -> str:
        """生成 Playground HTML"""
        # 提取数据
        self.data = self.extract_from_docs()

        # 填充模板
        html = self.template

        # 替换项目名称
        html = html.replace("绿联NAS DXP2800 五一营销活动", self.data.get("project_name", "项目 Playground"))

        # 替换核心指标
        ceo = self.data.get("ceo_alignment", {})
        html = html.replace("30,000", ceo.get("target", "30,000").replace(",", "").replace("台", ""))

        # 填充文档卡片内容
        # 这里可以进一步定制文档摘要的提取

        output_path = output_path or f"活动看板_{self.data.get('project_name', 'auto')}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path


def main():
    parser = argparse.ArgumentParser(description="Playground 自动生成器")
    parser.add_argument("--project", "-p", required=True, help="项目目录路径")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--version", "-v", default="auto", help="版本号")

    args = parser.parse_args()

    generator = PlaygroundGenerator(args.project)
    output_path = generator.generate(args.output)

    print(f"✅ Playground 生成完成: {output_path}")
    print(f"📊 提取的文档数据: {json.dumps(generator.data, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
