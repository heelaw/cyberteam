"""协作引擎持久化集成补丁 - 展示如何将 CollaborationEngine 与数据库集成。

这个文件展示了对 collaboration.py 的关键修改，以支持 Handoff 和 CollaborationTask 的持久化。

关键修改点：
1. __init__ 方法：添加 db_session 参数
2. plan_collaboration 方法：使用 CollaborationRepository 创建数据库记录
3. execute_with_real_agents 方法：更新数据库状态
4. _create_handoff 方法：使用数据库创建 Handoff

使用方式：
- 在原有 collaboration.py 基础上应用这些修改
- 或者使用这个文件作为参考进行重构
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.engine.collaboration_repository import CollaborationRepository
from app.models import CollaborationTaskState, HandoffStatus


class CollaborationEngineWithPersistence:
    """集成持久化的协作引擎 - 更新版本示例。

    这个类展示了如何在原有 CollaborationEngine 基础上添加数据库持久化。
    """

    def __init__(self, db_session: AsyncSession):
        """初始化协作引擎。

        Args:
            db_session: SQLAlchemy 异步会话，用于数据库操作
        """
        self.router = CEORouter()
        self.db_session = db_session
        self.repo = CollaborationRepository(db_session)
        # 保留内存缓存用于快速访问
        self.active_tasks: Dict[str, CollaborationTask] = {}

    async def plan_collaboration(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> CollaborationTask:
        """规划协作链路（持久化版本）。

        关键修改：
        - 使用 CollaborationRepository 创建数据库记录
        - 返回的数据类包含数据库 ID
        """
        # Step 1: 智能路由
        route_result = self.router.route(task, context)
        primary_dept = route_result["target_department"]
        alternatives = route_result.get("alternative_departments", [])

        # Step 2: 判断协作需求
        collaborating_depts = self._detect_collaboration_need(
            task, primary_dept, alternatives, context
        )

        # Step 3: 构建匹配分数字典
        match_scores = {primary_dept: route_result["match_score"]}
        for alt in alternatives:
            match_scores[alt["department_id"]] = alt["score"]

        # Step 4: 创建数据库记录（关键修改）
        db_task = await self.repo.create_collaboration_task(
            original_task=task,
            primary_department=primary_dept,
            collaborating_departments=collaborating_depts,
            match_scores=match_scores,
            creator="system",
        )

        # Step 5: 创建内存对象（保持兼容性）
        collab_task = CollaborationTask(
            task_id=db_task.task_id,
            original_task=task,
            status=TaskStatus.ROUTING,
            primary_department=primary_dept,
            collaborating_departments=collaborating_depts,
            match_scores=match_scores,
            _db_id=db_task.id,  # 添加数据库ID引用
        )

        # Step 6: 生成 Handoff 链路（如果有协作需求）
        if collaborating_depts:
            collab_task.execution_chain = await self._create_handoff_chain(
                db_task.task_id, primary_dept, collaborating_depts, context
            )

        # 缓存到内存
        self.active_tasks[db_task.task_id] = collab_task

        return collab_task

    async def _create_handoff_chain(
        self,
        task_id: str,
        primary_dept: str,
        collaborating_depts: List[str],
        context: Optional[Dict[str, Any]],
    ) -> List[HandoffRecord]:
        """创建 Handoff 链路（持久化版本）。

        关键修改：
        - 使用 CollaborationRepository 创建数据库记录
        - 每个 Handoff 都会保存到数据库
        """
        execution_chain = []
        previous_dept = primary_dept

        for dept in collaborating_depts:
            # 创建数据库记录
            db_handoff = await self.repo.create_handoff(
                task_id=task_id,
                from_department=previous_dept,
                to_department=dept,
                context={
                    "original_context": context or {},
                    "handoff_type": "sequential",
                },
                notes=f"从 {previous_dept} 移交到 {dept}",
            )

            # 创建内存对象
            handoff = HandoffRecord(
                handoff_id=db_handoff.handoff_id,
                task_id=task_id,
                from_department=previous_dept,
                to_department=dept,
                status=HandoffStatus.PENDING,
                context=context or {},
                _db_id=db_handoff.id,  # 添加数据库ID引用
            )

            execution_chain.append(handoff)
            previous_dept = dept

        return execution_chain

    async def execute_with_real_agents(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """使用真实Agent执行器执行协作链路（持久化版本）。

        关键修改：
        - 更新数据库状态为 IN_PROGRESS
        - 每个 Handoff 完成时更新数据库
        - 任务完成时更新最终状态和结果
        """
        # Step 1: 规划（已包含数据库创建）
        collab_task = await self.plan_collaboration(task, context)

        # Step 2: 更新任务状态为 IN_PROGRESS（关键修改）
        await self.repo.update_collaboration_task_status(
            collab_task.task_id,
            CollaborationTaskState.IN_PROGRESS,
        )

        # Step 3: 单部门执行路径
        if not collab_task.execution_chain:
            return await self._execute_single_department(
                collab_task, task, context
            )

        # Step 4: 多部门协作执行路径
        return await self._execute_collaboration_chain(
            collab_task, task, context
        )

    async def _execute_single_department(
        self,
        collab_task: CollaborationTask,
        task: str,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """执行单部门任务（持久化版本）。"""
        executor_cls = DEPARTMENT_EXECUTORS.get(collab_task.primary_department)

        if executor_cls and executor_cls != AgentExecutor:
            executor = executor_cls()
            result = await executor.execute(task, context or {})

            # 更新任务结果（关键修改）
            await self.repo.update_collaboration_task_results(
                collab_task.task_id,
                results={collab_task.primary_department: result.to_dict()},
                final_output={
                    "task_id": collab_task.task_id,
                    "original_task": task,
                    "collaboration_summary": {
                        "departments_involved": [collab_task.primary_department],
                        "total_departments": 1,
                        "results_count": 1,
                    },
                    "execution_chain": [{
                        "department": collab_task.primary_department,
                        "output": result.to_dict(),
                        "timestamp": datetime.utcnow().isoformat(),
                    }],
                    "primary_department": collab_task.primary_department,
                    "final_recommendation": "单一部门执行完成",
                },
            )

            # 更新任务状态为 COMPLETED
            await self.repo.update_collaboration_task_status(
                collab_task.task_id,
                CollaborationTaskState.COMPLETED,
            )

            return {
                "task_id": collab_task.task_id,
                "original_task": task,
                "collaboration_summary": {
                    "departments_involved": [collab_task.primary_department],
                    "total_departments": 1,
                    "results_count": 1,
                },
                "execution_chain": [{
                    "department": collab_task.primary_department,
                    "output": result.to_dict(),
                    "timestamp": datetime.utcnow().isoformat(),
                }],
                "primary_department": collab_task.primary_department,
                "final_recommendation": "单一部门执行完成",
            }

        raise ValueError(f"未找到 {collab_task.primary_department} 的执行器")

    async def _execute_collaboration_chain(
        self,
        collab_task: CollaborationTask,
        task: str,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """执行协作链路（持久化版本）。"""
        ordered_results = []
        previous_result = None

        for handoff in collab_task.execution_chain:
            dept_id = handoff.to_department

            # 更新 Handoff 状态为 IN_PROGRESS（关键修改）
            await self.repo.update_handoff_status(
                handoff.handoff_id,
                HandoffStatus.IN_PROGRESS,
            )

            executor_cls = DEPARTMENT_EXECUTORS.get(dept_id)

            if executor_cls and executor_cls != AgentExecutor:
                executor = executor_cls()
                result = await executor.execute(
                    task,
                    {"previous_results": previous_result},
                )
                handoff.result = result.to_dict()
            else:
                result = self._simulate_department_execution(
                    dept_id, task, previous_result
                )
                handoff.result = result.to_dict()

            # 更新 Handoff 状态为 COMPLETED（关键修改）
            await self.repo.update_handoff_status(
                handoff.handoff_id,
                HandoffStatus.COMPLETED,
                result=handoff.result,
            )

            ordered_results.append({
                "department": dept_id,
                "output": handoff.result,
                "timestamp": datetime.utcnow().isoformat(),
            })

            previous_result = handoff.result
            collab_task.results[dept_id] = handoff.result

        # 更新任务最终状态和结果（关键修改）
        final_output = {
            "task_id": collab_task.task_id,
            "original_task": task,
            "collaboration_summary": {
                "departments_involved": [h.to_department for h in collab_task.execution_chain],
                "total_departments": len(collab_task.execution_chain),
                "results_count": len(ordered_results),
            },
            "execution_chain": ordered_results,
            "primary_department": collab_task.primary_department,
            "final_recommendation": self._generate_recommendation(ordered_results),
        }

        await self.repo.update_collaboration_task_results(
            collab_task.task_id,
            results=collab_task.results,
            final_output=final_output,
        )

        await self.repo.update_collaboration_task_status(
            collab_task.task_id,
            CollaborationTaskState.COMPLETED,
        )

        return final_output

    # ── 查询方法 ──

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态（从数据库）。"""
        return await self.repo.get_collaboration_statistics(task_id)

    async def list_handoffs(
        self,
        task_id: str,
        status: Optional[HandoffStatus] = None,
    ) -> List[Dict[str, Any]]:
        """列出任务的所有 Handoff（从数据库）。"""
        handoffs = await self.repo.list_handoffs_by_task(task_id, status)
        return [h.to_dict() for h in handoffs]
