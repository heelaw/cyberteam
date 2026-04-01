#!/usr/bin/env python3
"""
增量更新工具

支持业务模型文档的增量更新：
1. 单个指标更新
2. 转化漏斗更新
3. 章节追加
4. 影响分析
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class UpdateImpact:
    """更新影响分析"""
    affected_metrics: List[str] = field(default_factory=list)
    affected_sections: List[str] = field(default_factory=list)
    value_changes: Dict[str, Tuple[Any, Any]] = field(default_factory=list)
    estimated_effort: str = ""


@dataclass
class UpdateResult:
    """更新结果"""
    success: bool
    changes_made: int
    impact: UpdateImpact
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None


class IncrementalUpdater:
    """增量更新器"""

    def __init__(self, document_path: str):
        self.document_path = Path(document_path)
        self.document = self._read_document()
        self.backup_path = None

    def _read_document(self) -> str:
        """读取文档"""
        with open(self.document_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _backup_document(self):
        """备份文档"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.document_path.parent / '.backups'
        backup_dir.mkdir(exist_ok=True)

        self.backup_path = backup_dir / f"{self.document_path.stem}_{timestamp}{self.document_path.suffix}"

        with open(self.backup_path, 'w', encoding='utf-8') as f:
            f.write(self.document)

        print(f"💾 已备份到: {self.backup_path}")

    def _save_document(self):
        """保存文档"""
        with open(self.document_path, 'w', encoding='utf-8') as f:
            f.write(self.document)

    def find_metric_locations(self, metric_name: str) -> List[Dict[str, Any]]:
        """查找指标在文档中的所有位置"""
        locations = []
        pattern = re.compile(re.escape(metric_name), re.IGNORECASE)

        for match in pattern.finditer(self.document):
            # 获取上下文
            start = max(0, match.start() - 50)
            end = min(len(self.document), match.end() + 50)
            context = self.document[start:end]

            # 识别章节
            section = self._identify_section(match.start())

            # 计算行号
            line_number = self.document[:match.start()].count('\n') + 1

            locations.append({
                'position': match.start(),
                'line_number': line_number,
                'section': section,
                'context': context
            })

        return locations

    def _identify_section(self, position: int) -> str:
        """根据位置识别章节"""
        before = self.document[:position]
        matches = list(re.finditer(r'#+\s+(.+)', before))
        return matches[-1].group(1) if matches else 'Unknown'

    def analyze_impact(self, metric_name: str, new_value: Any) -> UpdateImpact:
        """分析更新影响"""
        impact = UpdateImpact()

        # 查找相关指标
        if metric_name.upper() == 'CAC':
            # CAC变化会影响 LTV:CAC 比率
            impact.affected_metrics = ['CAC', 'LTV:CAC', 'ROI']
            impact.affected_sections = ['6. 流量渠道', '7. 运营指标', '附录']
            impact.estimated_effort = "中等（需要重新计算比率）"

        elif metric_name.upper() == 'LTV':
            impact.affected_metrics = ['LTV', 'LTV:CAC', 'ROI']
            impact.affected_sections = ['3. 收入公式', '7. 运营指标', '附录']
            impact.estimated_effort = "中等"

        elif '转化' in metric_name or 'conversion' in metric_name.lower():
            impact.affected_metrics = ['整体转化率', '曝光需求', '预算需求']
            impact.affected_sections = ['4. 转化链路', '6. 流量渠道', '附录']
            impact.estimated_effort = "高（需要重新计算曝光需求）"

        return impact

    def update_metric(self, metric_name: str, new_value: Any,
                     scope: str = 'all') -> UpdateResult:
        """
        更新单个指标

        Args:
            metric_name: 指标名称
            new_value: 新值
            scope: 更新范围 ('all', 'summary_only', 'specific_section')

        Returns:
            UpdateResult
        """
        # 备份
        self._backup_document()

        # 分析影响
        impact = self.analyze_impact(metric_name, new_value)

        print(f"\n📊 更新指标: {metric_name}")
        print(f"   新值: {new_value}")
        print(f"\n📍 影响范围:")
        print(f"   - 影响指标: {', '.join(impact.affected_metrics)}")
        print(f"   - 影响章节: {', '.join(impact.affected_sections)}")
        print(f"   - 预估工作量: {impact.estimated_effort}")

        # 查找所有位置
        locations = self.find_metric_locations(metric_name)

        if not locations:
            return UpdateResult(
                success=False,
                changes_made=0,
                impact=impact,
                error=f"未找到指标 '{metric_name}'"
            )

        # 执行更新
        changes_made = 0
        warnings = []

        for loc in locations:
            old_value = self._extract_value_at_location(loc)

            if old_value is not None and old_value != new_value:
                # 替换值
                old_text = self.document[loc['position']:loc['position']+len(str(old_value))]
                new_text = str(new_value)

                # 尝试保持格式
                if '$' in old_text:
                    new_text = f"${new_value}"

                self.document = (
                    self.document[:loc['position']] +
                    new_text +
                    self.document[loc['position']+len(old_text):]
                )

                changes_made += 1
                impact.value_changes[f"{loc['section']}:行{loc['line_number']}"] = (old_value, new_value)

                print(f"   ✏️  {loc['section']} (行{loc['line_number']}): {old_value} → {new_value}")

        # 保存
        if changes_made > 0:
            self._save_document()
            print(f"\n✅ 已更新 {changes_made} 处")

            # 生成变更记录
            self._log_change(metric_name, new_value, impact)

            return UpdateResult(
                success=True,
                changes_made=changes_made,
                impact=impact,
                warnings=warnings
            )
        else:
            print("\n⚠️  未找到需要更新的值")
            return UpdateResult(
                success=False,
                changes_made=0,
                impact=impact,
                warnings=warnings
            )

    def _extract_value_at_location(self, location: Dict) -> Optional[Any]:
        """从指定位置提取值"""
        context = location['context']
        # 简单实现：查找数字
        match = re.search(r'\$?(\d+,?\d*(?:\.\d+)?)', context)
        if match:
            return match.group(1)
        return None

    def _log_change(self, metric_name: str, new_value: Any, impact: UpdateImpact):
        """记录变更"""
        changelog_path = self.document_path.parent / 'CHANGELOG.md'

        entry = f"""
## [{datetime.now().strftime('%Y-%m-%d %H:%M')}] 更新指标: {metric_name}

### 变更
- **指标**: {metric_name}
- **新值**: {new_value}

### 影响范围
- **影响指标**: {', '.join(impact.affected_metrics)}
- **影响章节**: {', '.join(impact.affected_sections)}

### 变更详情
"""

        for loc, (old_val, new_val) in impact.value_changes.items():
            entry += f"- {loc}: {old_val} → {new_val}\n"

        entry += "\n---\n"

        with open(changelog_path, 'a', encoding='utf-8') as f:
            f.write(entry)

        print(f"📝 已记录变更到: {changelog_path}")

    def update_funnel_step(self, step_name: str, new_rate: float) -> UpdateResult:
        """更新转化漏斗的单个步骤"""
        # 备份
        self._backup_document()

        print(f"\n🔄 更新转化漏斗: {step_name}")
        print(f"   新转化率: {new_rate:.2%}")

        # 查找漏斗定义
        funnel_pattern = re.compile(
            rf'[\[（]({re.escape(step_name)})[\]）]\s*[→→]\s*(\d+\.?\d*)%',
            re.MULTILINE
        )

        matches = list(funnel_pattern.finditer(self.document))

        if not matches:
            return UpdateResult(
                success=False,
                changes_made=0,
                impact=UpdateImpact(),
                error=f"未找到漏斗步骤 '{step_name}'"
            )

        changes_made = 0
        old_rate = None

        for match in matches:
            old_rate = float(match.group(2)) / 100
            old_text = match.group(0)
            new_text = f"[{step_name}] → {new_rate*100:.1f}%"

            self.document = (
                self.document[:match.start()] +
                new_text +
                self.document[match.end():]
            )

            changes_made += 1
            print(f"   ✏️  已更新")

        if changes_made > 0:
            # 重新计算整体转化率
            print(f"\n⚠️  注意：转化率从 {old_rate:.2%} 变为 {new_rate:.2%}")
            print(f"   需要手动更新整体转化率、曝光需求、预算等衍生指标")

            self._save_document()

            return UpdateResult(
                success=True,
                changes_made=changes_made,
                impact=UpdateImpact(
                    affected_metrics=['整体转化率', '曝光需求', '预算需求'],
                    affected_sections=['4. 转化链路', '6. 流量渠道'],
                    estimated_effort="高"
                )
            )

        return UpdateResult(
            success=False,
            changes_made=0,
            impact=UpdateImpact(),
            error="更新失败"
        )


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python incremental_updater.py <document_path> <command> [args...]")
        print("\nCommands:")
        print("  update_metric <metric_name> <new_value>")
        print("  update_funnel <step_name> <new_rate>")
        sys.exit(1)

    document_path = sys.argv[1]
    command = sys.argv[2]

    updater = IncrementalUpdater(document_path)

    if command == "update_metric":
        if len(sys.argv) < 5:
            print("Usage: update_metric <metric_name> <new_value>")
            sys.exit(1)

        metric_name = sys.argv[3]
        new_value = sys.argv[4]

        # 尝试解析为数字
        try:
            new_value = float(new_value)
        except ValueError:
            pass

        result = updater.update_metric(metric_name, new_value)

        if result.success:
            print(f"\n✅ 更新成功，共修改 {result.changes_made} 处")
        else:
            print(f"\n❌ 更新失败: {result.error}")
            sys.exit(1)

    elif command == "update_funnel":
        if len(sys.argv) < 5:
            print("Usage: update_funnel <step_name> <new_rate>")
            sys.exit(1)

        step_name = sys.argv[3]
        new_rate = float(sys.argv[4])

        result = updater.update_funnel_step(step_name, new_rate)

        if not result.success:
            print(f"\n❌ 更新失败: {result.error}")
            sys.exit(1)


if __name__ == '__main__':
    main()
