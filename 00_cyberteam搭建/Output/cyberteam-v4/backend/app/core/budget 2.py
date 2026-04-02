"""多级预算控制 - 抄 Magic。

设计理念：
- 三级预算控制：组织级 > 项目级 > Agent级
- 按日聚合使用量
- 支持预算检查（执行前）和使用量记录（执行后）
- 预算预警机制

预算层级：
- organization: 组织全局预算
- project: 项目级预算
- agent: 单个 Agent 预算

数据存储：
- 实时使用量：内存缓存（可选 Redis）
- 持久化：数据库 budget_tracking 表
"""

from datetime import date, datetime
from typing import Optional, Dict
import logging

log = logging.getLogger("cyberteam.budget")


class BudgetTracker:
    """多级预算追踪器。

    用法:
        tracker = BudgetTracker(db_session)
        # 执行前检查
        allowed = await tracker.check_budget("agent", "growth_director", estimated_cost=0.05)
        # 执行后记录
        await tracker.record_usage("agent", "growth_director", tokens=1500, cost=0.05, model="claude-sonnet-4-6")
    """

    # 默认预算限制（美元）
    DEFAULT_LIMITS: Dict[str, float] = {
        "organization": 100.0,
        "project": 50.0,
        "agent": 10.0,
    }

    # 预算预警阈值（使用量占限制的百分比）
    WARNING_THRESHOLD = 0.8  # 80%
    CRITICAL_THRESHOLD = 0.95  # 95%

    def __init__(self, db=None):
        """初始化预算追踪器。

        Args:
            db: 数据库会话（可选，为空时使用内存存储）
        """
        self.db = db
        # 内存缓存: {(entity_type, entity_id, date): {"tokens": int, "cost": float}}
        self._cache: Dict[tuple, Dict] = {}
        # 预算限制覆盖: {(entity_type, entity_id): limit}
        self._limit_overrides: Dict[tuple, float] = {}

    async def check_budget(
        self,
        entity_type: str,
        entity_id: str,
        estimated_cost: float,
    ) -> bool:
        """检查预算是否允许执行。

        Args:
            entity_type: 实体类型（organization/project/agent）
            entity_id: 实体ID
            estimated_cost: 预估费用（美元）

        Returns:
            True 表示预算允许，False 表示超出预算
        """
        today = date.today()
        usage = await self._get_today_usage(entity_type, entity_id, today)
        limit = await self._get_budget_limit(entity_type, entity_id)
        total_after = usage + estimated_cost

        if total_after > limit:
            log.warning(
                f"Budget exceeded: {entity_type}/{entity_id} "
                f"usage={usage:.4f} + estimated={estimated_cost:.4f} > limit={limit:.4f}"
            )
            return False

        # 预警检查
        ratio = total_after / limit
        if ratio >= self.CRITICAL_THRESHOLD:
            log.warning(
                f"Budget critical: {entity_type}/{entity_id} "
                f"will be at {ratio:.1%} after this operation"
            )
        elif ratio >= self.WARNING_THRESHOLD:
            log.info(
                f"Budget warning: {entity_type}/{entity_id} "
                f"will be at {ratio:.1%} after this operation"
            )

        return True

    async def record_usage(
        self,
        entity_type: str,
        entity_id: str,
        tokens: int,
        cost: float,
        model: str = "",
    ) -> None:
        """记录使用量。

        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            tokens: Token 数量
            cost: 费用（美元）
            model: 使用的模型
        """
        today = date.today()
        cache_key = (entity_type, entity_id, today)

        if cache_key not in self._cache:
            self._cache[cache_key] = {"tokens": 0, "cost": 0.0}

        self._cache[cache_key]["tokens"] += tokens
        self._cache[cache_key]["cost"] += cost

        log.info(
            f"Usage recorded: {entity_type}/{entity_id} "
            f"tokens={tokens} cost=${cost:.6f} model={model}"
        )

        # 如果有数据库，写入持久化
        if self.db:
            await self._persist_usage(entity_type, entity_id, today, tokens, cost)

    async def get_usage_summary(
        self,
        entity_type: str,
        entity_id: str,
        target_date: Optional[date] = None,
    ) -> Dict:
        """获取使用量汇总。

        Returns:
            {"tokens": int, "cost": float, "limit": float, "usage_ratio": float}
        """
        target = target_date or date.today()
        usage_cost = await self._get_today_usage(entity_type, entity_id, target)
        limit = await self._get_budget_limit(entity_type, entity_id)

        cache_key = (entity_type, entity_id, target)
        tokens = self._cache.get(cache_key, {}).get("tokens", 0)

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "date": target.isoformat(),
            "tokens": tokens,
            "cost": usage_cost,
            "limit": limit,
            "usage_ratio": round(usage_cost / limit, 4) if limit > 0 else 0,
            "remaining": round(limit - usage_cost, 4),
        }

    def set_budget_limit(self, entity_type: str, entity_id: str, limit: float) -> None:
        """设置预算限制覆盖。"""
        self._limit_overrides[(entity_type, entity_id)] = limit
        log.info(f"Budget limit set: {entity_type}/{entity_id} = ${limit:.2f}")

    async def _get_today_usage(self, entity_type: str, entity_id: str, today: date) -> float:
        """获取当日使用量。"""
        cache_key = (entity_type, entity_id, today)
        if cache_key in self._cache:
            return self._cache[cache_key]["cost"]

        # 如果有数据库，从数据库查询
        if self.db:
            try:
                from sqlalchemy import select
                from ..models import BudgetTracking

                stmt = select(BudgetTracking).where(
                    BudgetTracking.entity_type == entity_type,
                    BudgetTracking.entity_id == entity_id,
                    BudgetTracking.period == today,
                )
                result = await self.db.execute(stmt)
                record = result.scalar_one_or_none()
                if record:
                    self._cache[cache_key] = {
                        "tokens": record.tokens_used,
                        "cost": float(record.cost_usd or 0),
                    }
                    return float(record.cost_usd or 0)
            except Exception as e:
                log.warning(f"Failed to query budget from DB: {e}")

        return 0.0

    async def _get_budget_limit(self, entity_type: str, entity_id: str) -> float:
        """获取预算限制。"""
        # 优先使用覆盖值
        override = self._limit_overrides.get((entity_type, entity_id))
        if override is not None:
            return override

        # 如果有数据库，从数据库查询
        if self.db:
            try:
                from sqlalchemy import select
                from ..models import BudgetTracking

                today = date.today()
                stmt = select(BudgetTracking.budget_limit).where(
                    BudgetTracking.entity_type == entity_type,
                    BudgetTracking.entity_id == entity_id,
                    BudgetTracking.period == today,
                )
                result = await self.db.execute(stmt)
                limit = result.scalar_one_or_none()
                if limit is not None:
                    return float(limit)
            except Exception as e:
                log.warning(f"Failed to query budget limit from DB: {e}")

        return self.DEFAULT_LIMITS.get(entity_type, 10.0)

    async def _persist_usage(
        self,
        entity_type: str,
        entity_id: str,
        target_date: date,
        tokens: int,
        cost: float,
    ) -> None:
        """将使用量持久化到数据库。"""
        try:
            from sqlalchemy import select
            from ..models import BudgetTracking

            stmt = select(BudgetTracking).where(
                BudgetTracking.entity_type == entity_type,
                BudgetTracking.entity_id == entity_id,
                BudgetTracking.period == target_date,
            )
            result = await self.db.execute(stmt)
            record = result.scalar_one_or_none()

            if record:
                record.tokens_used = (record.tokens_used or 0) + tokens
                record.cost_usd = (float(record.cost_usd or 0)) + cost
            else:
                record = BudgetTracking(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    period=target_date,
                    tokens_used=tokens,
                    cost_usd=cost,
                    budget_limit=await self._get_budget_limit(entity_type, entity_id),
                )
                self.db.add(record)

            await self.db.commit()
        except Exception as e:
            log.error(f"Failed to persist budget usage: {e}")
            if self.db:
                await self.db.rollback()
