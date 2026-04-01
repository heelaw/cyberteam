#!/usr/bin/env python3
"""
课程结构验证器

检查课程设计的完整性和质量，包括：
- 五要素完整性检查
- 学习体验曲线评估
- 在线学习障碍应对检查
- 教学目标SMART检验

Usage:
    course_validator.py <course_file.md>
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """验证结果"""
    category: str
    item: str
    passed: bool
    message: str


class CourseValidator:
    """课程验证器"""

    # 五要素关键词
    FIVE_ELEMENTS = {
        "教学目标": ["目标", "学会", "能够", "掌握", "理解"],
        "学习内容": ["内容", "章节", "模块", "知识点"],
        "教学活动": ["练习", "讨论", "互动", "作业", "实操"],
        "学习资源": ["资料", "模板", "工具", "参考"],
        "学习评估": ["评估", "测试", "考核", "作业", "验收"]
    }

    # 学习体验关键词
    EXPERIENCE_KEYWORDS = {
        "开场": ["开场", "介绍", "导入", "破冰"],
        "过程": ["互动", "练习", "案例", "讨论"],
        "结尾": ["总结", "回顾", "作业", "行动"]
    }

    # 在线学习障碍应对关键词
    ONLINE_BARRIER_SOLUTIONS = {
        "注意力分散": ["短", "碎片", "互动", "视频"],
        "学习孤独感": ["社群", "群", "助教", "答疑", "讨论区"],
        "认知负荷": ["笔记", "总结", "模板", "清单"],
        "学习落地": ["练习", "作业", "实战", "项目", "行动"]
    }

    # 模糊动词（SMART检查）
    VAGUE_VERBS = ["了解", "熟悉", "知道", "学习"]

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        self.results: List[ValidationResult] = []

    def load_file(self) -> bool:
        """加载课程文件"""
        try:
            if not self.file_path.exists():
                print(f"❌ 文件不存在: {self.file_path}")
                return False

            self.content = self.file_path.read_text(encoding='utf-8')
            return True
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return False

    def validate_all(self) -> List[ValidationResult]:
        """执行所有验证"""
        print("🔍 开始验证课程结构...\n")

        self._validate_five_elements()
        self._validate_experience_curve()
        self._validate_online_barriers()
        self._validate_smart_objectives()
        self._validate_structure()

        return self.results

    def _validate_five_elements(self):
        """验证五要素完整性"""
        print("【1/5】检查五要素完整性...")

        for element, keywords in self.FIVE_ELEMENTS.items():
            found = any(kw in self.content for kw in keywords)
            result = ValidationResult(
                category="五要素检查",
                item=element,
                passed=found,
                message="✅ 已包含" if found else f"⚠️  未发现 '{element}' 相关内容"
            )
            self.results.append(result)
            print(f"  {result.message} - {element}")

    def _validate_experience_curve(self):
        """验证学习体验曲线"""
        print("\n【2/5】检查学习体验设计...")

        for phase, keywords in self.EXPERIENCE_KEYWORDS.items():
            found = any(kw in self.content for kw in keywords)
            result = ValidationResult(
                category="学习体验检查",
                item=phase,
                passed=found,
                message=f"{'✅' if found else '⚠️ '} {phase}阶段"
            )
            self.results.append(result)
            print(f"  {result.message}")

    def _validate_online_barriers(self):
        """验证在线学习障碍应对"""
        print("\n【3/5】检查在线学习障碍应对...")

        for barrier, keywords in self.ONLINE_BARRIER_SOLUTIONS.items():
            found = any(kw in self.content for kw in keywords)
            result = ValidationResult(
                category="在线障碍检查",
                item=barrier,
                passed=found,
                message=f"{'✅' if found else '⚠️ '} {barrier}应对"
            )
            self.results.append(result)
            print(f"  {result.message}")

    def _validate_smart_objectives(self):
        """验证教学目标SMART原则"""
        print("\n【4/5】检查教学目标SMART原则...")

        # 查找目标相关句子
        objective_patterns = [
            r'(学员.*?能够.*?[，。])',
            r'(学习.*?目标.*?[，。])',
            r'(.*?将能够.*?[，。])'
        ]

        objectives_found = 0
        vague_count = 0
        quantified_count = 0

        for pattern in objective_patterns:
            matches = re.findall(pattern, self.content)
            for match in matches:
                objectives_found += 1
                # 检查模糊动词
                if any(v in match for v in self.VAGUE_VERBS):
                    vague_count += 1
                # 检查量化指标
                if re.search(r'[0-9]+|个|项|次|步', match):
                    quantified_count += 1

        if objectives_found > 0:
            print(f"  📊 发现 {objectives_found} 个教学目标相关句子")
            print(f"  {'✅' if vague_count == 0 else '⚠️ '} 模糊动词: {vague_count} 个")
            print(f"  {'✅' if quantified_count > 0 else '⚠️ '} 量化指标: {quantified_count} 个")

            self.results.append(ValidationResult(
                category="SMART检查",
                item="目标数量",
                passed=objectives_found >= 3,
                message=f"发现 {objectives_found} 个目标 (建议至少3个)"
            ))
        else:
            print("  ⚠️  未发现明确的教学目标")
            self.results.append(ValidationResult(
                category="SMART检查",
                item="目标数量",
                passed=False,
                message="未发现明确的教学目标"
            ))

    def _validate_structure(self):
        """验证课程结构"""
        print("\n【5/5】检查课程结构...")

        # 检查标题结构
        headings = re.findall(r'^#{1,3}\s+(.+)$', self.content, re.MULTILINE)
        module_count = len([h for h in headings if '章' in h or '模块' in h or '篇' in h])

        print(f"  📊 发现 {len(headings)} 个标题")
        print(f"  📊 发现 {module_count} 个模块/章节")

        self.results.append(ValidationResult(
            category="结构检查",
            item="标题层级",
            passed=len(headings) >= 5,
            message=f"{len(headings)} 个标题"
        ))

        self.results.append(ValidationResult(
            category="结构检查",
            item="模块数量",
            passed=3 <= module_count <= 10,
            message=f"{module_count} 个模块 (建议3-10个)"
        ))

    def print_summary(self):
        """打印验证摘要"""
        print("\n" + "=" * 60)
        print("验证摘要")
        print("=" * 60)

        # 统计
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print(f"\n总计: {total} 项检查")
        print(f"✅ 通过: {passed} 项")
        print(f"⚠️  需注意: {failed} 项")
        print(f"通过率: {passed*100//total}%")

        # 分类统计
        print("\n分类统计:")
        by_category: Dict[str, List[ValidationResult]] = {}
        for r in self.results:
            if r.category not in by_category:
                by_category[r.category] = []
            by_category[r.category].append(r)

        for category, results in by_category.items():
            cat_passed = sum(1 for r in results if r.passed)
            print(f"  {category}: {cat_passed}/{len(results)} 通过")

        # 改进建议
        if failed > 0:
            print("\n" + "-" * 60)
            print("改进建议:")
            print("-" * 60)

            for result in self.results:
                if not result.passed:
                    print(f"\n• {result.category} - {result.item}")
                    print(f"  {result.message}")

                    # 提供具体建议
                    if result.item == "教学活动":
                        print("  建议: 添加练习、讨论、互动等教学活动")
                    elif result.item == "学习评估":
                        print("  建议: 设计测试、作业、项目等评估方式")
                    elif result.category == "在线障碍检查":
                        print("  建议: 考虑添加相应的应对措施")
                    elif result.category == "SMART检查":
                        print("  建议: 使用具体的行为动词和量化指标")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: course_validator.py <course_file.md>")
        print("\n示例:")
        print("  course_validator.py my_course.md")
        sys.exit(1)

    file_path = sys.argv[1]
    validator = CourseValidator(file_path)

    if not validator.load_file():
        sys.exit(1)

    validator.validate_all()
    validator.print_summary()


if __name__ == "__main__":
    main()
