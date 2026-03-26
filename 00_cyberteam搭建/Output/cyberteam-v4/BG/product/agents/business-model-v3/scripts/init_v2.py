#!/usr/bin/env python3
"""
Cyberwiz Business Model Analyzer v2.0 初始化脚本

功能：
1. 验证安装
2. 创建项目结构
3. 生成示例文档
4. 运行测试验证
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")

    missing = []

    try:
        import yaml
        print("   ✅ PyYAML")
    except ImportError:
        missing.append("PyYAML")

    if missing:
        print(f"\n❌ 缺少依赖: {', '.join(missing)}")
        print("\n安装命令:")
        print(f"   pip install {' '.join(missing)}")
        return False

    print("✅ 所有依赖已安装\n")
    return True


def verify_structure():
    """验证目录结构"""
    print("📁 验证目录结构...")

    required_dirs = [
        'frameworks',
        'modules',
        'templates',
        'core',
        'validators',
        'tools',
        'config',
    ]

    base_path = Path(__file__).parent.parent

    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            print(f"   ⚠️  缺少目录: {dir_name}")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 已创建: {dir_name}")
        else:
            print(f"   ✅ {dir_name}")

    print(f"\n基础路径: {base_path}")
    return True


def test_parameter_extractor():
    """测试参数提取器"""
    print("\n🧪 测试参数提取器...")

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.parameter_extractor import ParameterExtractor

        # 创建测试文档
        test_doc = Path(__file__).parent.parent / 'test_document.md'
        test_content = """
# 测试业务模型

## 核心指标

- CAC: $175
- LTV: $3025
- 转化率: 5.76%

## 转化漏斗

[触达] → [完播] → [兴趣]
 100%     30%      8%
"""

        with open(test_doc, 'w', encoding='utf-8') as f:
            f.write(test_content)

        # 提取参数
        extractor = ParameterExtractor(str(test_doc))
        params = extractor.extract_all()

        print(f"   ✅ 成功提取 {len(params)} 个参数")

        # 清理
        test_doc.unlink()

        return True
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


def test_validation_engine():
    """测试验证引擎"""
    print("\n🧪 测试验证引擎...")

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from validators.validation_engine import ValidationEngine, ValidationResult

        engine = ValidationEngine()
        print(f"   ✅ 验证引擎初始化成功")
        print(f"   ✅ 已加载 {len(engine.rules)} 条默认规则")

        return True
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


def generate_example_config():
    """生成示例配置"""
    print("\n📝 生成示例配置...")

    config_example = """
# 示例项目配置

project:
  name: "示例项目"
  framework: "o2o-preorder"
  version: "1.0"

metrics:
  cac:
    value: 175
    currency: "USD"
    benchmark: "$50-500"

  ltv:
    value: 3025
    currency: "USD"
    benchmark: "$500-2000"

conversion_funnel:
  - step: "触达"
    rate: 1.0
  - step: "完播"
    rate: 0.30
  - step: "兴趣"
    rate: 0.08
  - step: "预约"
    rate: 0.06
"""

    config_path = Path(__file__).parent.parent / 'config' / 'example_project.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_example)

    print(f"   ✅ 已生成: {config_path}")
    return True


def print_quick_start():
    """打印快速开始指南"""
    print("\n" + "="*70)
    print("🚀 快速开始")
    print("="*70)

    print("""
1. 提取文档参数:
   python core/parameter_extractor.py path/to/document.md

2. 验证业务模型:
   python validators/validation_engine.py path/to/document.md

3. 更新指标:
   python tools/incremental_updater.py path/to/document.md update_metric "CAC" 175

4. 查看帮助:
   cat QUICKSTART.md
   cat README.md
""")

    print("="*70)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎯 Cyberwiz Business Model Analyzer v2.0")
    print("   初始化和测试")
    print("="*70 + "\n")

    # 1. 检查依赖
    if not check_dependencies():
        return 1

    # 2. 验证结构
    verify_structure()

    # 3. 测试组件
    success = True
    success = test_parameter_extractor() and success
    success = test_validation_engine() and success

    # 4. 生成示例配置
    generate_example_config()

    # 5. 打印快速开始
    print_quick_start()

    if success:
        print("\n🎉 初始化完成！所有测试通过。\n")
        return 0
    else:
        print("\n⚠️  初始化完成，但有测试失败。请检查错误信息。\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
