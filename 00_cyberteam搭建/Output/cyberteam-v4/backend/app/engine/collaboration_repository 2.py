"""协作引擎持久化服务层 - 处理 Handoff 和 CollaborationTask 的数据库操作。"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import HandoffRecord, CollaborationTask, HandoffStatus, CollaborationTaskState


class CollaborationRepository:
    """协作引擎数据访问层 - 负责所有协作相关的数据库操作。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── CollaborationTask 操作 ──

    async def create_collaboration_task(
        self,
        original_task: str,
        primary_department: Optional[str] = None,
        collaborating_departments: List[str] = None,
        match_scores: Dict[str, float] = None,
        creator: str = "system",
        tags: List[str] = None,
    ) -> CollaborationTask:
        """创建新的协作任务。"""
        task = CollaborationTask(
            task_id=str(uuid.uuid4()),
            original_task=original_task,
            primary_department=primary_department,
            collaborating_departments=collaborating_departments or [],
            match_scores=match_scores or {},
            creator=creator,
            tags=tags or [],
            status=CollaborationTaskState.PENDING,
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_collaboration_task(self, task_id: str) -> Optional[CollaborationTask]:
        """根据 task_id 获取协作任务。"""
        stmt = select(CollaborationTask).where(CollaborationTask.task_id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_collaboration_task_status(
        self,
        task_id: str,
        status: CollaborationTaskState,
    ) -> Optional[CollaborationTask]:
        """更新协作任务状态。"""
        stmt = (
            update(CollaborationTask)
            .where(CollaborationTask.task_id == task_id)
            .values(status=status)
            .returning(CollaborationTask)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_collaboration_task_results(
        self,
        task_id: str,
        results: Dict[str, Any],
        final_output: Optional[Dict[str, Any]] = None,
    ) -> Optional[CollaborationTask]:
        """更新协作任务结果。"""
        update_values = {"results": results}
        if final_output is not None:
            update_values["final_output"] = final_output

        stmt = (
            update(CollaborationTask)
            .where(CollaborationTask.task_id == task_id)
            .values(**update_values)
            .returning(CollaborationTask)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_handoff_count(
        self,
        task_id: str,
        completed: bool = False,
    ) -> Optional[CollaborationTask]:
        """增加 Handoff 计数。"""
        if completed:
            stmt = (
                update(CollaborationTask)
                .where(CollaborationTask.task_id == task_id)
                .values(
                    completed_handoffs=CollaborationTask.completed_handoffs + 1,
                )
                .returning(CollaborationTask)
            )
        else:
            stmt = (
                update(CollaborationTask)
                .where(CollaborationTask.task_id == task_id)
                .values(
                    total_handoffs=CollaborationTask.total_handoffs + 1,
                )
                .returning(CollaborationTask)
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_collaboration_tasks(
        self,
        status: Optional[CollaborationTaskState] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CollaborationTask]:
        """列出协作任务（支持状态过滤和分页）。"""
        stmt = select(CollaborationTask)
        if status:
            stmt = stmt.where(CollaborationTask.status == status)
        stmt = stmt.order_by(CollaborationTask.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ── HandoffRecord 操作 ──

    async def create_handoff(
        self,
        task_id: str,
        from_department: str,
        to_department: str,
        context: Dict[str, Any],
        notes: Optional[str] = None,
    ) -> HandoffRecord:
        """创建新的 Handoff 记录。"""
        handoff = HandoffRecord(
            handoff_id=str(uuid.uuid4()),
            task_id=task_id,
            from_department=from_department,
            to_department=to_department,
            status=HandoffStatus.PENDING,
            context=context,
            notes=notes,
        )
        self.session.add(handoff)
        await self.session.flush()

        # 增加任务的 total_handoffs 计数
        await self.increment_handoff_count(task_id, completed=False)

        return handoff

    async def get_handoff(self, handoff_id: str) -> Optional[HandoffRecord]:
        """根据 handoff_id 获取 Handoff 记录。"""
        stmt = select(HandoffRecord).where(HandoffRecord.handoff_id == handoff_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_handoffs_by_task(
        self,
        task_id: str,
        status: Optional[HandoffStatus] = None,
    ) -> List[HandoffRecord]:
        """列出指定任务的所有 Handoff 记录。"""
        stmt = select(HandoffRecord).where(HandoffRecord.task_id == task_id)
        if status:
            stmt = stmt.where(HandoffRecord.status == status)
        stmt = stmt.order_by(HandoffRecord.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_handoff_status(
        self,
        handoff_id: str,
        status: HandoffStatus,
        result: Optional[Dict[str, Any]] = None,
    ) -> Optional[HandoffRecord]:
        """更新 Handoff 状态。"""
        update_values: Dict[str, Any] = {"status": status}
        if status == HandoffStatus.COMPLETED:
            update_values["completed_at"] = datetime.utcnow()
        if result is not None:
            update_values["result"] = result

        stmt = (
            update(HandoffRecord)
            .where(HandoffRecord.handoff_id == handoff_id)
            .values(**update_values)
            .returning(HandoffRecord)
        )
        db_result = await self.session.execute(stmt)
        handoff = db_result.scalar_one_or_none()

        # 如果 Handoff 完成，增加任务的 completed_handoffs 计数
        if handoff and status == HandoffStatus.COMPLETED:
            await self.increment_handoff_count(handoff.task_id, completed=True)

        return handoff

    async def update_handoff_result(
        self,
        handoff_id: str,
        result: Dict[str, Any],
    ) -> Optional[HandoffRecord]:
        """更新 Handoff 结果。"""
        stmt = (
            update(HandoffRecord)
            .where(HandoffRecord.handoff_id == handoff_id)
            .values(result=result)
            .returning(HandoffRecord)
        )
        db_result = await self.session.execute(stmt)
        return db_result.scalar_one_or_none()

    async def delete_handoff(self, handoff_id: str) -> bool:
        """删除 Handoff 记录。"""
        stmt = delete(HandoffRecord).where(HandoffRecord.handoff_id == handoff_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # ── 统计查询 ──

    async def get_collaboration_statistics(
        self,
        task_id: str,
    ) -> Dict[str, Any]:
        """获取指定任务的协作统计信息。"""
        task = await self.get_collaboration_task(task_id)
        if not task:
            return {}

        handoffs = await self.list_handoffs_by_task(task_id)

        # 统计各状态的 Handoff 数量
        status_counts = {}
        for handoff in handoffs:
            status = handoff.status.value if isinstance(handoff.status, HandoffStatus) else handoff.status
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "task_id": task_id,
            "task_status": task.status.value if isinstance(task.status, CollaborationTaskState) else task.status,
            "total_handoffs": task.total_handoffs,
            "completed_handoffs": task.completed_handoffs,
            "pending_handoffs": status_counts.get("pending", 0),
            "in_progress_handoffs": status_counts.get("in_progress", 0),
            "completed_handoffs": status_counts.get("completed", 0),
            "failed_handoffs": status_counts.get("failed", 0),
            "completion_rate": task.completed_handoffs / task.total_handoffs if task.total_handoffs > 0 else 0,
        }
