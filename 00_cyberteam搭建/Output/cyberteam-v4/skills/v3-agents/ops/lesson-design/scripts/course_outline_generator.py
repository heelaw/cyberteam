#!/usr/bin/env python3
"""
课程大纲生成器

根据课程定位和教学目标，自动生成课程大纲框架。
支持三种课程设计逻辑：内容消费型、学习交互型、行动动机改变型。

Usage:
    course_outline_generator.py
    然后按提示输入课程信息
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict
import sys


@dataclass
class CourseModule:
    """课程模块"""
    name: str
    description: str
    duration_minutes: int
    objectives: List[str]


@dataclass
class CourseOutline:
    """课程大纲"""
    course_name: str
    target_audience: str
    design_logic: str  # 内容消费型/学习交互型/行动动机改变型
    total_duration_minutes: int
    modules: List[CourseModule]


class CourseOutlineGenerator:
    """课程大纲生成器"""

    # 预设的课程模板
    TEMPLATES = {
        "内容消费型": {
            "structure": "知识讲解 → 案例分析 → 方法总结",
            "interaction": "较低",
            "modules": [
                {"name": "基础认知篇", "ratio": 0.25},
                {"name": "核心方法篇", "ratio": 0.35},
                {"name": "实践案例篇", "ratio": 0.25},
                {"name": "总结提升篇", "ratio": 0.15}
            ]
        },
        "学习交互型": {
            "structure": "问题导入 → 知识讲解 → 练习实操 → 答疑反馈",
            "interaction": "中等",
            "modules": [
                {"name": "问题发现篇", "ratio": 0.15},
                {"name": "方法学习篇", "ratio": 0.30},
                {"name": "实战练习篇", "ratio": 0.35},
                {"name": "反馈优化篇", "ratio": 0.20}
            ]
        },
        "行动动机改变型": {
            "structure": "认知唤醒 → 方法传授 → 行动设计 → 跟踪反馈",
            "interaction": "较高",
            "modules": [
                {"name": "认知觉醒篇", "ratio": 0.20},
                {"name": "方法赋能篇", "ratio": 0.25},
                {"name": "行动设计篇", "ratio": 0.30},
                {"name": "习惯养成篇", "ratio": 0.25}
            ]
        }
    }

    def __init__(self):
        self.course_info = {}

    def collect_input(self):
        """收集用户输入"""
        print("=" * 60)
        print("课程大纲生成器")
        print("=" * 60)
        print()

        self.course_info["course_name"] = input("课程名称: ").strip() or "未命名课程"
        self.course_info["target_audience"] = input("目标学员: ").strip() or "通用学员"

        print("\n请选择课程设计逻辑:")
        print("1. 内容消费型 (知识密集，适合理论类课程)")
        print("2. 学习交互型 (练结合，适合技能类课程)")
        print("3. 行动动机改变型 (行为改变，适合习惯养成类课程)")

        choice = input("\n请输入选择 (1/2/3): ").strip()
        logic_map = {"1": "内容消费型", "2": "学习交互型", "3": "行动动机改变型"}
        self.course_info["design_logic"] = logic_map.get(choice, "内容消费型")

        total_hours = input("\n课程总时长 (小时，默认4小时): ").strip()
        self.course_info["total_duration_minutes"] = int(float(total_hours or "4") * 60)

        num_modules = input("\n模块数量 (默认4个): ").strip()
        self.course_info["num_modules"] = int(num_modules or "4")

        print()

    def generate_outline(self) -> CourseOutline:
        """生成课程大纲"""
        logic = self.course_info["design_logic"]
        template = self.TEMPLATES[logic]

        modules = []
        template_modules = template["modules"]

        # 调整模块数量
        if self.course_info["num_modules"] != len(template_modules):
            template_modules = self._adjust_modules(
                template_modules,
                self.course_info["num_modules"]
            )

        for i, mod in enumerate(template_modules, 1):
            duration = int(self.course_info["total_duration_minutes"] * mod["ratio"])

            module = CourseModule(
                name=f"{i}. {mod['name']}",
                description=f"{self.course_info['course_name']} - {mod['name']}内容",
                duration_minutes=duration,
                objectives=self._generate_objectives(i, mod["name"])
            )
            modules.append(module)

        outline = CourseOutline(
            course_name=self.course_info["course_name"],
            target_audience=self.course_info["target_audience"],
            design_logic=logic,
            total_duration_minutes=self.course_info["total_duration_minutes"],
            modules=modules
        )

        return outline

    def _adjust_modules(self, original_modules, target_count):
        """调整模块数量"""
        if target_count <= len(original_modules):
            return original_modules[:target_count]

        # 需要增加模块，拆分最大的模块
        result = original_modules.copy()
        while len(result) < target_count:
            # 找到最大的模块
            max_idx = max(range(len(result)), key=lambda i: result[i]["ratio"])
            max_module = result[max_idx]

            # 拆分
            new_ratio = max_module["ratio"] / 2
            result[max_idx]["ratio"] = new_ratio

            # 插入新模块
            new_module = {
                "name": max_module["name"].replace("篇", "") + "进阶",
                "ratio": new_ratio
            }
            result.insert(max_idx + 1, new_module)

        return result

    def _generate_objectives(self, index: int, module_name: str) -> List[str]:
        """生成模块学习目标"""
        base_objectives = {
            1: ["建立基础认知框架", "理解核心概念定义"],
            2: ["掌握关键方法论", "学习操作步骤流程"],
            3: ["完成实战练习", "应用所学解决问题"],
            4: ["总结核心要点", "规划后续行动"]
        }

        if index <= 4:
            return base_objectives.get(index, ["理解模块内容", "掌握核心知识"])
        else:
            return [f"掌握{module_name}相关内容"]

    def display_outline(self, outline: CourseOutline):
        """显示课程大纲"""
        print("=" * 60)
        print(f"《{outline.course_name}》课程大纲")
        print("=" * 60)
        print()
        print(f"课程定位: {outline.target_audience}")
        print(f"设计逻辑: {outline.design_logic}")
        print(f"设计结构: {self.TEMPLATES[outline.design_logic]['structure']}")
        print(f"互动程度: {self.TEMPLATES[outline.design_logic]['interaction']}")
        print(f"总时长: {outline.total_duration_minutes // 60}小时{outline.total_duration_minutes % 60}分钟")
        print()
        print("-" * 60)
        print("课程模块")
        print("-" * 60)

        for module in outline.modules:
            print(f"\n{module.name}")
            print(f"  时长: {module.duration_minutes}分钟")
            print(f"  目标:")
            for obj in module.objectives:
                print(f"    - {obj}")

        print()
        print("-" * 60)

    def save_outline(self, outline: CourseOutline, filename: str = None):
        """保存课程大纲到文件"""
        if filename is None:
            filename = f"{outline.course_name.replace(' ', '_')}_outline.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(outline), f, ensure_ascii=False, indent=2)

        print(f"\n✅ 大纲已保存到: {filename}")

    def save_markdown(self, outline: CourseOutline, filename: str = None):
        """保存为Markdown格式"""
        if filename is None:
            filename = f"{outline.course_name.replace(' ', '_')}_outline.md"

        lines = []
        lines.append(f"# 《{outline.course_name}》课程大纲\n")
        lines.append("## 课程信息\n")
        lines.append(f"- **目标学员**: {outline.target_audience}")
        lines.append(f"- **设计逻辑**: {outline.design_logic}")
        lines.append(f"- **总时长**: {outline.total_duration_minutes // 60}小时{outline.total_duration_minutes % 60}分钟\n")

        lines.append("## 课程模块\n")

        for module in outline.modules:
            lines.append(f"### {module.name}\n")
            lines.append(f"**时长**: {module.duration_minutes}分钟\n")
            lines.append("**学习目标**:")
            for obj in module.objectives:
                lines.append(f"- {obj}")
            lines.append("")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✅ Markdown大纲已保存到: {filename}")


def main():
    """主函数"""
    generator = CourseOutlineGenerator()

    try:
        generator.collect_input()
        outline = generator.generate_outline()
        generator.display_outline(outline)

        save = input("\n是否保存大纲? (y/n): ").strip().lower()
        if save == 'y':
            generator.save_markdown(outline)

    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
