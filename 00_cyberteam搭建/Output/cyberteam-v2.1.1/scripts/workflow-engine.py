#!/usr/bin/env python3
"""
CyberTeam v2.1 -- 工作流引擎

功能:
- 定义和执行多步骤工作流
- 支持并行和串行任务
- 状态管理和恢复
- 事件触发和回调

使用方法:
    python3 workflow-engine.py --define workflow.json --execute
    python3 workflow-engine.py --list
    python3 workflow-engine.py --status <workflow-id>
"""

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Any


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskMode(Enum):
    """任务模式"""
    SEQUENTIAL = "sequential"   # 串行执行
    PARALLEL = "parallel"        # 并行执行
    CONDITIONAL = "conditional"  # 条件执行


@dataclass
class WorkflowTask:
    """工作流任务定义"""
    id: str
    name: str
    action: str
    params: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    mode: TaskMode = TaskMode.SEQUENTIAL
    timeout: int = 300  # 秒
    retry: int = 0
    on_success: Optional[str] = None  # 回调任务ID
    on_failure: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class Workflow:
    """工作流定义"""
    id: str
    name: str
    description: str
    version: str = "1.0"
    tasks: list[WorkflowTask] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class TaskExecution:
    """任务执行记录"""
    task_id: str
    status: TaskStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    attempts: int = 0


@dataclass
class WorkflowExecution:
    """工作流执行记录"""
    workflow_id: str
    id: str
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    task_executions: dict[str, TaskExecution] = field(default_factory=dict)
    current_task: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


class WorkflowEngine:
    """工作流引擎"""

    # 内置任务操作
    BUILTIN_ACTIONS = {
        'echo': lambda params: params.get('message', ''),
        'run': lambda params: params.get('command', ''),
        'sleep': lambda params: params.get('seconds', 1),
        'notify': lambda params: params.get('message', ''),
        'script': lambda params: params.get('path', ''),
    }

    def __init__(self, storage_dir: str = ".cyberteam/workflows"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_execution: Optional[WorkflowExecution] = None
        self.callbacks: dict[str, Callable] = {}

    def load_workflow(self, file_path: str) -> Workflow:
        """加载工作流定义"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"工作流文件不存在: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tasks = [
            WorkflowTask(
                id=t.get('id', ''),
                name=t['name'],
                action=t['action'],
                params=t.get('params', {}),
                depends_on=t.get('depends_on', []),
                mode=TaskMode(t.get('mode', 'sequential')),
                timeout=t.get('timeout', 300),
                retry=t.get('retry', 0),
            )
            for t in data.get('tasks', [])
        ]

        return Workflow(
            id=data.get('id', ''),
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0'),
            tasks=tasks,
            metadata=data.get('metadata', {}),
        )

    def save_workflow(self, workflow: Workflow, file_path: str):
        """保存工作流定义"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'version': workflow.version,
            'tasks': [
                {
                    'id': t.id,
                    'name': t.name,
                    'action': t.action,
                    'params': t.params,
                    'depends_on': t.depends_on,
                    'mode': t.mode.value,
                    'timeout': t.timeout,
                    'retry': t.retry,
                }
                for t in workflow.tasks
            ],
            'metadata': workflow.metadata,
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def list_workflows(self) -> list[dict]:
        """列出所有工作流"""
        workflows = []
        for path in self.storage_dir.glob("*.json"):
            try:
                workflow = self.load_workflow(str(path))
                workflows.append({
                    'id': workflow.id,
                    'name': workflow.name,
                    'description': workflow.description,
                    'version': workflow.version,
                    'tasks': len(workflow.tasks),
                    'file': str(path),
                })
            except:
                pass
        return workflows

    def can_execute_task(self, task: WorkflowTask, execution: WorkflowExecution) -> bool:
        """检查任务是否可以执行"""
        if task.id in execution.task_executions:
            return False

        for dep_id in task.depends_on:
            if dep_id not in execution.task_executions:
                return False
            if execution.task_executions[dep_id].status != TaskStatus.COMPLETED:
                return False

        return True

    def execute_task(self, task: WorkflowTask, execution: WorkflowExecution) -> TaskExecution:
        """执行单个任务"""
        task_exec = TaskExecution(
            task_id=task.id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now(),
        )

        execution.task_executions[task.id] = task_exec
        execution.current_task = task.id

        action = self.BUILTIN_ACTIONS.get(task.action)

        if not action:
            # 尝试执行自定义脚本
            try:
                result = self._execute_custom_action(task)
                task_exec.result = result
                task_exec.status = TaskStatus.COMPLETED
            except Exception as e:
                task_exec.error = str(e)
                task_exec.status = TaskStatus.FAILED
        else:
            try:
                result = action(task.params)
                task_exec.result = result
                task_exec.status = TaskStatus.COMPLETED
            except Exception as e:
                if task.retry > 0:
                    task_exec.attempts += 1
                    if task_exec.attempts < task.retry:
                        return self.execute_task(task, execution)
                task_exec.error = str(e)
                task_exec.status = TaskStatus.FAILED

        task_exec.end_time = datetime.now()
        return task_exec

    def _execute_custom_action(self, task: WorkflowTask) -> str:
        """执行自定义动作"""
        script_path = task.params.get('path')
        if script_path and Path(script_path).exists():
            import subprocess
            result = subprocess.run(
                ['python3', script_path] + list(task.params.get('args', [])),
                capture_output=True,
                text=True,
                timeout=task.timeout,
            )
            return result.stdout or result.stderr
        return f"Unknown action: {task.action}"

    def execute_workflow(self, workflow: Workflow, pause_on_failure: bool = True) -> WorkflowExecution:
        """执行工作流"""
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            id=str(uuid.uuid4())[:8],
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now(),
        )

        self.current_execution = execution

        print(f"开始执行工作流: {workflow.name} ({execution.id})")

        pending_tasks = list(workflow.tasks)
        completed_tasks = set()

        while pending_tasks and execution.status == WorkflowStatus.RUNNING:
            tasks_to_run = []

            for task in pending_tasks:
                if self.can_execute_task(task, execution):
                    tasks_to_run.append(task)

            if not tasks_to_run:
                # 检查是否有任务失败
                failed = [
                    t for t in pending_tasks
                    if t.id in execution.task_executions
                    and execution.task_executions[t.id].status == TaskStatus.FAILED
                ]
                if failed:
                    if pause_on_failure:
                        execution.status = WorkflowStatus.FAILED
                        print(f"工作流失败: {failed[0].name}")
                    else:
                        # 跳过失败任务的依赖
                        for task in pending_tasks:
                            if task.id not in completed_tasks:
                                execution.task_executions[task.id] = TaskExecution(
                                    task_id=task.id,
                                    status=TaskStatus.SKIPPED,
                                )
                                completed_tasks.add(task.id)
                break

            # 执行任务
            for task in tasks_to_run:
                print(f"  执行任务: {task.name}")
                self.execute_task(task, execution)

                if execution.task_executions[task.id].status == TaskStatus.COMPLETED:
                    completed_tasks.add(task.id)
                    pending_tasks.remove(task)

                    # 触发成功回调
                    if task.on_success:
                        callback = self.callbacks.get(task.on_success)
                        if callback:
                            callback(execution.task_executions[task.id])
                else:
                    if pause_on_failure:
                        execution.status = WorkflowStatus.FAILED
                        break

        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.COMPLETED

        execution.end_time = datetime.now()
        self.current_execution = None

        # 保存执行记录
        self._save_execution(execution)

        print(f"工作流完成: {execution.status.value}")
        return execution

    def pause(self):
        """暂停当前工作流"""
        if self.current_execution:
            self.current_execution.status = WorkflowStatus.PAUSED
            print("工作流已暂停")

    def resume(self) -> WorkflowExecution:
        """恢复暂停的工作流"""
        if not self.current_execution or self.current_execution.status != WorkflowStatus.PAUSED:
            raise ValueError("没有可恢复的工作流")

        self.current_execution.status = WorkflowStatus.RUNNING
        # 重新加载工作流并继续执行
        workflows = self.list_workflows()
        for wf_data in workflows:
            if wf_data['id'] == self.current_execution.workflow_id:
                workflow = self.load_workflow(wf_data['file'])
                return self.execute_workflow(workflow)

        raise ValueError("找不到原始工作流定义")

    def cancel(self):
        """取消当前工作流"""
        if self.current_execution:
            self.current_execution.status = WorkflowStatus.CANCELLED
            print("工作流已取消")

    def get_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取执行状态"""
        path = self.storage_dir / f"execution_{execution_id}.json"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return WorkflowExecution(**data)
        return None

    def _save_execution(self, execution: WorkflowExecution):
        """保存执行记录"""
        path = self.storage_dir / f"execution_{execution.id}.json"
        data = {
            'workflow_id': execution.workflow_id,
            'id': execution.id,
            'status': execution.status.value,
            'start_time': execution.start_time.isoformat(),
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'task_executions': {
                tid: {
                    'task_id': te.task_id,
                    'status': te.status.value,
                    'start_time': te.start_time.isoformat() if te.start_time else None,
                    'end_time': te.end_time.isoformat() if te.end_time else None,
                    'result': str(te.result) if te.result else None,
                    'error': te.error,
                    'attempts': te.attempts,
                }
                for tid, te in execution.task_executions.items()
            },
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def register_callback(self, event: str, callback: Callable):
        """注册回调函数"""
        self.callbacks[event] = callback


def main():
    parser = argparse.ArgumentParser(
        description='CyberTeam v2.1 -- 工作流引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('--define', '-d', help='定义文件路径')
    parser.add_argument('--execute', '-e', action='store_true', help='执行工作流')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有工作流')
    parser.add_argument('--status', '-s', help='查看执行状态')
    parser.add_argument('--pause', action='store_true', help='暂停当前工作流')
    parser.add_argument('--resume', action='store_true', help='恢复工作流')
    parser.add_argument('--cancel', action='store_true', help='取消工作流')
    parser.add_argument('--output', '-o', help='输出目录')

    args = parser.parse_args()

    engine = WorkflowEngine(args.output or ".cyberteam/workflows")

    if args.list:
        print("CyberTeam v2.1 -- 工作流列表\n")
        workflows = engine.list_workflows()
        if not workflows:
            print("  没有定义的工作流")
        for wf in workflows:
            print(f"  {wf['id']}: {wf['name']} (v{wf['version']})")
            print(f"    描述: {wf['description']}")
            print(f"    任务数: {wf['tasks']}")
            print(f"    文件: {wf['file']}")
            print()

    elif args.define and args.execute:
        print(f"加载工作流: {args.define}")
        workflow = engine.load_workflow(args.define)
        print(f"工作流: {workflow.name}\n")
        execution = engine.execute_workflow(workflow)
        print(f"\n执行ID: {execution.id}")
        print(f"状态: {execution.status.value}")

    elif args.status:
        execution = engine.get_status(args.status)
        if execution:
            print(f"工作流执行状态: {execution.workflow_id}\n")
            print(f"  执行ID: {execution.id}")
            print(f"  状态: {execution.status}")
            print(f"  开始时间: {execution.start_time}")
            print(f"  结束时间: {execution.end_time or '进行中'}")
            print(f"\n任务执行:")
            for tid, task_exec in execution.task_executions.items():
                print(f"  {tid}: {task_exec.status.value}")
                if task_exec.error:
                    print(f"    错误: {task_exec.error}")
        else:
            print(f"未找到执行记录: {args.status}")

    elif args.pause:
        engine.pause()
    elif args.resume:
        engine.resume()
    elif args.cancel:
        engine.cancel()
    else:
        parser.print_help()

    return 0


if __name__ == '__main__':
    sys.exit(main())
