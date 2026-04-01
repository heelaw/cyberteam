#!/usr/bin/env python3
"""
工作流状态管理脚本
用于管理业务模型梳理工作流的状态、配置和进度跟踪
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class WorkflowManager:
    """工作流状态管理器"""

    def __init__(self, workflow_dir: str = None):
        """
        初始化工作流管理器

        Args:
            workflow_dir: 输出根目录（旧名称保持兼容）
        """
        if workflow_dir is None:
            # 默认使用 skill 目录下的 output
            skill_base = Path(__file__).parent.parent
            workflow_dir = skill_base / "output"
        self.workflow_dir = Path(workflow_dir)
        self.state_file = self.workflow_dir / "workflow_state.json"
        self.state = self._load_state()
        # 根据项目名称设置项目子目录
        self._update_project_dir()

    def _load_state(self) -> Dict[str, Any]:
        """加载工作流状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_default_state()
        return self._create_default_state()

    def _update_project_dir(self):
        """根据项目名称更新项目子目录"""
        project_name = self.state.get("config", {}).get("project_name", None)
        if project_name:
            # 将项目名称作为子目录
            project_dir = self.workflow_dir / project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            self.project_dir = project_dir
        else:
            # 没有项目名称时使用默认目录
            self.project_dir = self.workflow_dir

    def _create_default_state(self) -> Dict[str, Any]:
        """创建默认工作流状态"""
        return {
            "workflow_id": self._generate_workflow_id(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_stage": 0,
            "completed_stages": [],
            "auto_execute": False,
            "config": {},
            "stage_outputs": {}
        }

    def _generate_workflow_id(self) -> str:
        """生成工作流 ID"""
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def save_state(self):
        """保存工作流状态"""
        self.state["updated_at"] = datetime.now().isoformat()
        # 更新项目目录（可能在初始化时设置了项目名称）
        self._update_project_dir()
        self.project_dir.mkdir(parents=True, exist_ok=True)
        # 使用项目子目录保存状态文件
        state_file = self.project_dir / "workflow_state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        初始化工作流 (Stage 0)

        Args:
            config: 用户配置信息

        Returns:
            初始化后的状态
        """
        self.state.update({
            "current_stage": 0,
            "config": config,
            "auto_execute": config.get("auto_execute", False)
        })
        self.save_state()
        return self.state

    def advance_stage(self, stage_num: int, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        推进到下一阶段

        Args:
            stage_num: 当前阶段编号
            output_data: 当前阶段的输出数据

        Returns:
            更新后的状态
        """
        # 记录当前阶段输出
        stage_key = f"stage_{stage_num}"
        self.state["stage_outputs"][stage_key] = {
            "completed_at": datetime.now().isoformat(),
            "data": output_data
        }

        # 更新已完成阶段列表
        if stage_num not in self.state["completed_stages"]:
            self.state["completed_stages"].append(stage_num)

        # 更新当前阶段
        self.state["current_stage"] = stage_num + 1

        self.save_state()
        return self.state

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键，None 则返回全部配置
            default: 默认值

        Returns:
            配置值
        """
        if key is None:
            return self.state.get("config", {})
        return self.state.get("config", {}).get(key, default)

    def set_config(self, key: str, value: Any):
        """
        设置配置项

        Args:
            key: 配置键
            value: 配置值
        """
        if "config" not in self.state:
            self.state["config"] = {}
        self.state["config"][key] = value
        self.save_state()

    def get_stage_output(self, stage_num: int) -> Optional[Dict[str, Any]]:
        """
        获取指定阶段的输出

        Args:
            stage_num: 阶段编号

        Returns:
            阶段输出数据，不存在则返回 None
        """
        stage_key = f"stage_{stage_num}"
        return self.state.get("stage_outputs", {}).get(stage_key)

    def is_auto_execute(self) -> bool:
        """是否自动执行模式"""
        return self.state.get("auto_execute", False)

    def get_progress(self) -> Dict[str, Any]:
        """
        获取工作流进度

        Returns:
            进度信息
        """
        total_stages = 7  # Stage 0-6
        current = self.state.get("current_stage", 0)
        completed = len(self.state.get("completed_stages", []))

        return {
            "workflow_id": self.state.get("workflow_id"),
            "current_stage": current,
            "completed_stages": completed,
            "total_stages": total_stages,
            "progress_percent": round((completed / total_stages) * 100, 1),
            "is_complete": current >= total_stages,
            "auto_execute": self.is_auto_execute()
        }

    def get_status_summary(self) -> str:
        """
        获取状态摘要文本

        Returns:
            状态摘要
        """
        progress = self.get_progress()
        stage_names = [
            "工作流初始化",
            "业务模型映射",
            "收入公式分析",
            "转化链路分析",
            "运营指标定义",
            "破局点建议",
            "最终报告生成"
        ]

        lines = [
            "📊 业务模型梳理工作流状态",
            "",
            f"工作流 ID: {progress['workflow_id']}",
            f"当前阶段: Stage {progress['current_stage']}",
            f"已完成: {progress['completed_stages']}/{progress['total_stages']} ({progress['progress_percent']}%)",
            f"执行模式: {'自动执行' if progress['auto_execute'] else '手动执行'}",
            "",
            "各阶段状态:"
        ]

        for i, name in enumerate(stage_names):
            status = "✅ 已完成" if i in self.state.get("completed_stages", []) else \
                     "⏳ 进行中" if i == progress['current_stage'] else "⏸️ 待开始"
            lines.append(f"  Stage {i} ({name}): {status}")

        if progress['is_complete']:
            lines.append("", "🎉 工作流已全部完成！")

        return "\n".join(lines)

    def reset(self):
        """重置工作流状态"""
        self.state = self._create_default_state()
        self.save_state()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="业务模型梳理工作流管理工具")
    parser.add_argument("command", choices=["status", "reset", "init"],
                        help="命令: status(查看状态), reset(重置), init(初始化)")
    parser.add_argument("--workflow-dir", default="output",
                        help="输出目录 (默认: output)")

    args = parser.parse_args()
    manager = WorkflowManager(args.workflow_dir)

    if args.command == "status":
        print(manager.get_status_summary())
    elif args.command == "reset":
        manager.reset()
        print("✅ 工作流状态已重置")
    elif args.command == "init":
        manager.initialize({})
        print("✅ 工作流已初始化")


if __name__ == "__main__":
    main()
