"""API v1 数据访问层 - 处理 Project、Conversation、Message 的数据库操作。"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, Conversation, Message


# ── Project Repository ──

class ProjectRepository:
    """项目数据访问层。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        name: str,
        user_id: str,
        goal: str = "",
        description: Optional[str] = None,
        tags: List[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """创建新项目。"""
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            goal=goal,
            description=description,
            tags=tags or [],
            extra_data=extra_data or {},
            status="active",
            task_count=0,
        )
        self.session.add(project)
        await self.session.flush()
        return project

    async def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Project]:
        """列出用户的所有项目。"""
        stmt = select(Project).where(Project.status == "active")
        if status:
            stmt = stmt.where(Project.status == status)
        stmt = stmt.order_by(Project.updated_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, project_id: str) -> Optional[Project]:
        """获取单个项目。"""
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self,
        project_id: str,
        name: Optional[str] = None,
        goal: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
    ) -> Optional[Project]:
        """更新项目。"""
        update_values: Dict[str, Any] = {}
        if name is not None:
            update_values["name"] = name
        if goal is not None:
            update_values["goal"] = goal
        if description is not None:
            update_values["description"] = description
        if tags is not None:
            update_values["tags"] = tags
        if status is not None:
            update_values["status"] = status

        stmt = (
            update(Project)
            .where(Project.id == project_id)
            .values(**update_values)
            .returning(Project)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, project_id: str) -> bool:
        """删除项目（软删除，设置状态为 deleted）。"""
        stmt = (
            update(Project)
            .where(Project.id == project_id)
            .values(status="deleted")
            .returning(Project)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def increment_task_count(self, project_id: str) -> Optional[Project]:
        """增加任务计数。"""
        stmt = (
            update(Project)
            .where(Project.id == project_id)
            .values(task_count=Project.task_count + 1)
            .returning(Project)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


# ── Conversation Repository ──

class ConversationRepository:
    """会话数据访问层。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: str,
        title: Optional[str] = None,
        project_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Conversation:
        """创建新会话。"""
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title or "新对话",
            project_id=project_id,
            meta=meta or {},
            status="active",
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Conversation]:
        """列出用户的所有会话。"""
        stmt = select(Conversation).where(Conversation.user_id == user_id)
        if status:
            stmt = stmt.where(Conversation.status == status)
        if project_id:
            stmt = stmt.where(Conversation.project_id == project_id)
        stmt = stmt.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, conversation_id: str) -> Optional[Conversation]:
        """获取单个会话。"""
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, conversation_id: str) -> bool:
        """删除会话（软删除，设置状态为 deleted）。"""
        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(status="deleted")
            .returning(Conversation)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def update_title(
        self,
        conversation_id: str,
        title: str,
    ) -> Optional[Conversation]:
        """更新会话标题。"""
        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(title=title)
            .returning(Conversation)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


# ── Message Repository ──

class MessageRepository:
    """消息数据访问层。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: str,
        sender_type: str,
        content: Optional[str] = None,
        sender_id: Optional[str] = None,
        sender_name: Optional[str] = None,
        department: Optional[str] = None,
        content_type: str = "markdown",
        meta: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> Message:
        """创建新消息。"""
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            department=department,
            content=content,
            content_type=content_type,
            meta=meta or {},
            parent_id=parent_id,
        )
        self.session.add(message)
        await self.session.flush()

        # 更新会话的 updated_at 时间戳
        await self._touch_conversation(conversation_id)

        return message

    async def list_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        """列出会话的所有消息。"""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, message_id: str) -> Optional[Message]:
        """获取单条消息。"""
        stmt = select(Message).where(Message.id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_conversation(self, conversation_id: str) -> int:
        """统计会话的消息数量。"""
        stmt = (
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def _touch_conversation(self, conversation_id: str) -> None:
        """更新会话的 updated_at 时间戳。"""
        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=datetime.utcnow())
        )
        await self.session.execute(stmt)


# ── 自定义 Agent Repository ──

class CustomAgentRepository:
    """自定义 Agent 数据访问层（基于 Skill 模型）。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """列出自定义 Agent（基于 Skill 模型的 user_id 标记）。

        注意：Skill 模型中没有 user_id 字段，这里假设通过 tags 或 meta 来标记。
        实际实现可能需要调整 Skill 模型或使用其他方式关联用户。
        """
        # 临时实现：返回所有自定义创建的 Skills
        # 生产环境需要添加 user_id 字段或关联表
        from app.models import Skill

        stmt = (
            select(Skill)
            .where(Skill.author == user_id)  # 假设使用 author 字段标记创建者
            .order_by(Skill.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        skills = list(result.scalars().all())

        # 转换为 Agent 格式
        return [
            {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
                "author": skill.author,
                "created_at": skill.created_at.isoformat() if skill.created_at else None,
            }
            for skill in skills
        ]

    async def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取单个自定义 Agent。"""
        from app.models import Skill

        stmt = select(Skill).where(Skill.id == agent_id)
        result = await self.session.execute(stmt)
        skill = result.scalar_one_or_none()

        if not skill:
            return None

        return {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "category": skill.category,
            "author": skill.author,
            "created_at": skill.created_at.isoformat() if skill.created_at else None,
        }
