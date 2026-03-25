#!/usr/bin/env python3
"""
工作流状态检查脚本
用于检查工作流进度、文件状态和完整性
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class WorkflowStatusChecker:
    """工作流状态检查器"""

    def __init__(self, workflow_dir: str = None):
        """
        初始化状态检查器

        Args:
            workflow_dir: 输出目录（旧名称保持兼容）
        """
        if workflow_dir is None:
            # 默认使用 skill 目录下的 output
            skill_base = Path(__file__).parent.parent
            workflow_dir = skill_base / "output"
        self.workflow_dir = Path(workflow_dir)
        self.state_file = self.workflow_dir / "workflow_state.json"

        # 定义各阶段目录
        self.stage_dirs = {
            0: "00-init",
            1: "01-business-model",
            2: "02-revenue-formula",
            3: "03-conversion-funnel",
            4: "04-operational-metrics",
            5: "05-breakthrough-points",
            6: "06-final-report"
        }

        self.stage_names = {
            0: "工作流初始化",
            1: "业务模型映射",
            2: "收入公式分析",
            3: "转化链路分析",
            4: "运营指标定义",
            5: "破局点建议",
            6: "最终报告生成"
        }

    def check_workflow_exists(self) -> bool:
        """检查工作流是否存在"""
        return self.workflow_dir.exists()

    def load_state(self) -> Optional[Dict[str, Any]]:
        """加载工作流状态"""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def check_stage_files(self, stage_num: int) -> Dict[str, Any]:
        """
        检查指定阶段的文件

        Args:
            stage_num: 阶段编号

        Returns:
            文件状态信息
        """
        stage_dir_name = self.stage_dirs.get(stage_num)
        if not stage_dir_name:
            return {"error": f"无效的阶段编号: {stage_num}"}

        stage_dir = self.workflow_dir / stage_dir_name

        if not stage_dir.exists():
            return {
                "stage": stage_num,
                "status": "未开始",
                "exists": False,
                "files": []
            }

        # 查找所有文件
        files = []
        for ext in ["*.md", "*.json", "*.txt"]:
            files.extend(stage_dir.glob(ext))

        file_info = []
        for file in sorted(files, key=lambda f: f.stat().st_mtime, reverse=True):
            stat = file.stat()
            file_info.append({
                "name": file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return {
            "stage": stage_num,
            "stage_name": self.stage_names.get(stage_num, ""),
            "status": "已完成" if file_info else "已创建但无文件",
            "exists": True,
            "files": file_info
        }

    def check_all_stages(self) -> List[Dict[str, Any]]:
        """
        检查所有阶段的状态

        Returns:
            各阶段状态列表
        """
        stages = []

        for stage_num in range(7):
            stage_info = self.check_stage_files(stage_num)
            stages.append(stage_info)

        return stages

    def get_completion_status(self) -> Dict[str, Any]:
        """
        获取完成状态

        Returns:
            完成状态信息
        """
        stages = self.check_all_stages()
        completed = sum(1 for s in stages if s.get("status") == "已完成")
        total = len(stages)

        # 从状态文件中获取当前阶段
        state = self.load_state()
        current_stage = state.get("current_stage", 0) if state else 0
        completed_stages = state.get("completed_stages", []) if state else []

        return {
            "total_stages": total,
            "completed": completed,
            "current_stage": current_stage,
            "completed_stages": completed_stages,
            "progress_percent": round((completed / total) * 100, 1) if total > 0 else 0,
            "is_complete": completed >= total
        }

    def get_next_action(self) -> Optional[str]:
        """
        获取下一步建议

        Returns:
            下一步行动建议
        """
        state = self.load_state()
        if not state:
            return "建议使用 /new 初始化工作流"

        current_stage = state.get("current_stage", 0)

        if current_stage >= 6:
            return "工作流已完成！可以使用 /report 查看最终报告"

        stage_name = self.stage_names.get(current_stage, "")
        return f"建议进入 Stage {current_stage} ({stage_name})"

    def identify_issues(self) -> List[str]:
        """
        识别工作流中的问题

        Returns:
            问题列表
        """
        issues = []

        # 检查工作流目录是否存在
        if not self.check_workflow_exists():
            issues.append("工作流目录不存在")
            return issues

        # 检查状态文件
        if not self.state_file.exists():
            issues.append("工作流状态文件不存在")
        else:
            state = self.load_state()
            if not state:
                issues.append("工作流状态文件损坏")

        # 检查各阶段文件
        stages = self.check_all_stages()
        for stage in stages:
            if stage.get("exists") and not stage.get("files"):
                issues.append(f"Stage {stage['stage']} ({stage.get('stage_name', '')}) 目录为空")

        return issues

    def generate_status_report(self) -> str:
        """
        生成状态报告

        Returns:
            报告文本
        """
        lines = [
            "📊 业务模型梳理工作流状态报告",
            "",
            f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # 基本状态
        if not self.check_workflow_exists():
            lines.extend([
                "⚠️ 工作流尚未初始化",
                "",
                "建议：使用 /new 命令开始新的工作流"
            ])
            return "\n".join(lines)

        # 完成状态
        completion = self.get_completion_status()
        state = self.load_state()

        lines.extend([
            f"工作流 ID: {state.get('workflow_id', '未知') if state else '未知'}",
            f"当前阶段: Stage {completion['current_stage']}",
            f"已完成: {completion['completed']}/{completion['total_stages']} ({completion['progress_percent']}%)",
            f"执行模式: {'自动执行' if state.get('auto_execute', False) else '手动执行'}" if state else "",
            ""
        ])

        # 各阶段状态
        lines.extend(["各阶段状态:", ""])

        stages = self.check_all_stages()
        for stage in stages:
            status_emoji = {
                "已完成": "✅",
                "已创建但无文件": "📁",
                "未开始": "⏸️"
            }.get(stage.get("status", "未开始"), "❓")

            lines.append(
                f"{status_emoji} Stage {stage['stage']} ({stage.get('stage_name', '')}): {stage.get('status', '未知')}"
            )

            # 显示最新文件
            if stage.get("files"):
                latest_file = stage["files"][0]
                lines.append(f"   最新文件: {latest_file['name']} ({latest_file['size']} bytes)")

        # 下一步建议
        lines.extend(["", "---", "", "下一步建议:"])
        next_action = self.get_next_action()
        lines.append(f"  {next_action}")

        # 问题列表
        issues = self.identify_issues()
        if issues:
            lines.extend(["", "⚠️ 注意事项:"])
            for issue in issues:
                lines.append(f"  - {issue}")

        return "\n".join(lines)

    def get_stage_summary(self, stage_num: int) -> str:
        """
        获取指定阶段的摘要

        Args:
            stage_num: 阶段编号

        Returns:
            阶段摘要文本
        """
        stage_info = self.check_stage_files(stage_num)

        lines = [
            f"Stage {stage_num} ({self.stage_names.get(stage_num, '未知')})",
            "",
            f"状态: {stage_info.get('status', '未知')}",
            ""
        ]

        if stage_info.get("files"):
            lines.append("文件列表:")
            for file in stage_info["files"]:
                lines.append(f"  - {file['name']} ({file['size']} bytes, 修改于 {file['modified']})")
        elif stage_info.get("exists"):
            lines.append("目录已创建但无文件")

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="工作流状态检查工具")
    parser.add_argument("--workflow-dir", default="output",
                        help="输出目录 (默认: output)")
    parser.add_argument("--stage", type=int,
                        help="检查指定阶段")
    parser.add_argument("--issues", action="store_true",
                        help="仅显示问题")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出")

    args = parser.parse_args()

    checker = WorkflowStatusChecker(args.workflow_dir)

    if args.stage is not None:
        # 检查特定阶段
        summary = checker.get_stage_summary(args.stage)
        print(summary)
    elif args.issues:
        # 仅显示问题
        issues = checker.identify_issues()
        if issues:
            print("发现的问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 未发现问题")
    elif args.json:
        # JSON 输出
        status = {
            "completion": checker.get_completion_status(),
            "stages": checker.check_all_stages(),
            "issues": checker.identify_issues(),
            "next_action": checker.get_next_action()
        }
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        # 完整报告
        report = checker.generate_status_report()
        print(report)


if __name__ == "__main__":
    main()
