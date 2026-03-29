#!/usr/bin/env python3
"""
Playground 模板引擎 v2
支持从 CyberTeam 文档自动提取数据并填充 Playground

核心原理：
1. 定义 Playground 模板占位符 {{placeholder}}
2. 从文档中提取对应数据
3. 替换占位符生成最终 HTML
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PlaygroundConfig:
    """Playground 配置"""
    project_name: str = "新项目"
    version: str = "auto"
   北极星指标: str = "待定"
    目标销量: str = "待定"
    时间窗口: str = "待定"
    预算: str = "待定"
    主题: str = "待定"
    核心卖点: str = "待定"

    # 漏斗参数
    小红书曝光: int = 750
    小红书点击率: float = 3.0
    小红书收藏率: float = 15.0
    小红书转化率: float = 0.8

    抖音曝光: int = 1000
    抖音点击率: float = 8.0
    抖音下单率: float = 5.0

    电商曝光: int = 500
    电商加购率: float = 20.0
    电商下单率: float = 30.0

    # 风险数据
    risks: List[Dict] = field(default_factory=list)

    # 目标分层
    targets: List[Dict] = field(default_factory=list)

    # 文档摘要
    docs: Dict[str, Dict] = field(default_factory=dict)


class PlaygroundTemplateEngine:
    """Playground HTML 模板引擎"""

    # 模板占位符定义
    PLACEHOLDERS = {
        # 头部
        "{{project_name}}": "project_name",
        "{{version}}": "version",
        "{{北极星指标}}": "北极星指标",
        "{{目标销量}}": "目标销量",
        "{{时间窗口}}": "时间窗口",
        "{{预算}}": "预算",

        # 漏斗 - 小红书
        "{{小红书曝光}}": "小红书曝光",
        "{{小红书点击率}}": "小红书点击率",
        "{{小红书收藏率}}": "小红书收藏率",
        "{{小红书转化率}}": "小红书转化率",

        # 漏斗 - 抖音
        "{{抖音曝光}}": "抖音曝光",
        "{{抖音点击率}}": "抖音点击率",
        "{{抖音下单率}}": "抖音下单率",

        # 漏斗 - 电商
        "{{电商曝光}}": "电商曝光",
        "{{电商加购率}}": "电商加购率",
        "{{电商下单率}}": "电商下单率",

        # 主题
        "{{主题}}": "主题",
        "{{核心卖点}}": "核心卖点",
    }

    def __init__(self, template_path: Optional[str] = None):
        self.template_path = template_path or self._find_latest_template()
        self.template = self._load_template()
        self.config = PlaygroundConfig()

    def _find_latest_template(self) -> Path:
        """找到最新的 Playground 模板"""
        playground_dir = Path(__file__).parent
        templates = list(playground_dir.glob("活动看板_v*.html"))
        if templates:
            # 按名称排序，取最新的
            templates.sort(key=lambda x: x.name)
            return templates[-1]
        raise FileNotFoundError("未找到 Playground 模板文件")

    def _load_template(self) -> str:
        """加载模板文件"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def calculate_funnel(self) -> Dict[str, Dict]:
        """计算漏斗数据"""
        # 小红书
        xhs_exposure = self.config.小红书曝光 * 10000
        xhs_view = xhs_exposure * 0.45
        xhs_click = xhs_view * (self.config.小红书点击率 / 100)
        xhs_collect = xhs_click * (self.config.小红书收藏率 / 100)
        xhs_qty = xhs_collect * (self.config.小红书转化率 / 100)

        # 抖音
        dy_exposure = self.config.抖音曝光 * 10000
        dy_view = dy_exposure * 0.60
        dy_click = dy_view * (self.config.抖音点击率 / 100)
        dy_qty = dy_click * (self.config.抖音下单率 / 100)

        # 电商
        ec_exposure = self.config.电商曝光 * 10000
        ec_click = ec_exposure * 0.15
        ec_cart = ec_click * (self.config.电商加购率 / 100)
        ec_qty = ec_cart * (self.config.电商下单率 / 100)

        return {
            "小红书": {
                "曝光": xhs_exposure,
                "观看": xhs_view,
                "点击": xhs_click,
                "收藏": xhs_collect,
                "转化": xhs_qty,
                "销量": round(xhs_qty),
                "营业额": round(xhs_qty * 999 / 10000, 1),
            },
            "抖音": {
                "曝光": dy_exposure,
                "观看": dy_view,
                "点击": dy_click,
                "转化": dy_qty,
                "销量": round(dy_qty),
                "营业额": round(dy_qty * 999 / 10000, 1),
            },
            "电商": {
                "曝光": ec_exposure,
                "点击": ec_click,
                "加购": ec_cart,
                "转化": ec_qty,
                "销量": round(ec_qty),
                "营业额": round(ec_qty * 999 / 10000, 1),
            }
        }

    def render(self) -> str:
        """渲染模板"""
        html = self.template
        funnel = self.calculate_funnel()

        # 替换简单占位符
        replacements = {
            "{{project_name}}": self.config.project_name,
            "{{version}}": f"v{datetime.now().strftime('%m%d')}",
            "{{北极星指标}}": self.config.北极星指标,
            "{{目标销量}}": self.config.目标销量,
            "{{时间窗口}}": self.config.时间窗口,
            "{{预算}}": self.config.预算,
            "{{主题}}": self.config.主题,
            "{{核心卖点}}": self.config.核心卖点,

            # 漏斗数值（计算后）
            "{{小红书销量}}": f"约{funnel['小红书']['销量']:,}台",
            "{{抖音销量}}": f"约{funnel['抖音']['销量']:,}台",
            "{{电商销量}}": f"约{funnel['电商']['销量']:,}台",
            "{{总销量}}": f"约{funnel['小红书']['销量'] + funnel['抖音']['销量'] + funnel['电商']['销量']:,}台",
            "{{总营业额}}": f"约{(funnel['小红书']['营业额'] + funnel['抖音']['营业额'] + funnel['电商']['营业额']):,}万元",

            # 模拟器初始值
            "{{xhs_exposure_val}}": str(self.config.小红书曝光),
            "{{xhs_ctr_val}}": str(self.config.小红书点击率),
            "{{xhs_cvr_val}}": str(self.config.小红书转化率),
            "{{dy_exposure_val}}": str(self.config.抖音曝光),
            "{{dy_ctr_val}}": str(self.config.抖音点击率),
            "{{dy_cvr_val}}": str(self.config.抖音下单率),
            "{{ec_exposure_val}}": str(self.config.电商曝光),
            "{{ec_cart_val}}": str(self.config.电商加购率),
            "{{ec_cvr_val}}": str(self.config.电商下单率),
        }

        for placeholder, value in replacements.items():
            html = html.replace(placeholder, str(value))

        return html

    def save(self, output_path: str):
        """保存渲染结果"""
        html = self.render()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Playground 生成完成: {output_path}")


class CyberTeamDocExtractor:
    """从 CyberTeam 文档中提取数据"""

    @staticmethod
    def from_project_dir(project_dir: str) -> PlaygroundConfig:
        """从项目目录提取配置"""
        config = PlaygroundConfig()
        project_dir = Path(project_dir)

        # 读取 metadata.yaml
        metadata_path = project_dir / "00_项目资料" / "metadata.yaml"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单解析 YAML（实际项目可用 pyyaml）
                for line in content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        value = value.strip()
                        if key in ['name', 'project_name']:
                            config.project_name = value
                        elif key == 'target':
                            config.目标销量 = value
                        elif key == 'timeline':
                            config.时间窗口 = value
                        elif key == 'budget':
                            config.预算 = value

        # 读取对话文档
        docs_dir = project_dir / "01_Agent会议纪要" / "对话记录"

        # CEO对齐
        ceo_align = docs_dir / "对话_01_CEO对齐_20260327.md"
        if ceo_align.exists():
            with open(ceo_align, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取北极星指标
                match = re.search(r'北极星指标[：:]\s*([^\n]+)', content)
                if match:
                    config.北极星指标 = match.group(1).strip()
                # 提取目标
                match = re.search(r'(\d+[万]?台)', content)
                if match:
                    config.目标销量 = match.group(1)

        # 策略讨论
        strategy = docs_dir / "对话_02_策略讨论_20260327.md"
        if strategy.exists():
            with open(strategy, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取主题
                match = re.search(r'核心主题[：:]\s*["""]?([^"""\n]+)["""]?', content)
                if match:
                    config.主题 = match.group(1).strip()
                # 提取卖点
                match = re.search(r'P0[：:]\s*([^\n]+)', content)
                if match:
                    config.核心卖点 = match.group(1).strip()[:50]

        # CEO汇报 - 提取漏斗参数
        ceo_report = docs_dir / "对话_04_CEO汇报_20260327.md"
        if ceo_report.exists():
            with open(ceo_report, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取各渠道参数
                xhs_match = re.search(r'小红书[^\d]*(\d+)万[^\d]*(\d+)%[^\d]*(\d+)%', content)
                if xhs_match:
                    config.小红书曝光 = int(xhs_match.group(1))
                    config.小红书点击率 = float(xhs_match.group(2))
                    config.小红书转化率 = float(xhs_match.group(3))

        return config


def generate_playground(
    project_dir: str,
    output_path: Optional[str] = None,
    config_overrides: Optional[Dict] = None
) -> str:
    """
    生成 Playground 的主入口

    Args:
        project_dir: CyberTeam 项目目录
        output_path: 输出文件路径
        config_overrides: 配置覆盖值

    Returns:
        生成的 HTML 文件路径
    """
    # 1. 从项目目录提取配置
    config = CyberTeamDocExtractor.from_project_dir(project_dir)

    # 2. 应用覆盖配置
    if config_overrides:
        for key, value in config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)

    # 3. 创建模板引擎
    engine = PlaygroundTemplateEngine()
    engine.config = config

    # 4. 生成输出路径
    if not output_path:
        project_name = config.project_name or Path(project_dir).name
        output_path = f"活动看板_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    # 5. 渲染并保存
    engine.save(output_path)

    return output_path


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Playground 自动生成器 v2")
    parser.add_argument("--project", "-p", required=True, help="CyberTeam 项目目录")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--config", "-c", type=json.loads, help="配置覆盖 JSON")

    args = parser.parse_args()

    output = generate_playground(
        project_dir=args.project,
        output_path=args.output,
        config_overrides=args.config
    )

    print(f"\n📊 Playground 路径: {output}")
