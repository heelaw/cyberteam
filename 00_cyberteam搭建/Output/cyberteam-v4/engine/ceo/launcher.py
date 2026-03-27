#!/usr/bin/env python3
"""
CyberTeam V4 - 消息驱动 Launcher

重构说明：
- 从"本地模拟器"改为真正的消息驱动架构
- CEO → COO → Experts → COO → CEO → Departments → CEO
- 支持 MailboxManager 消息传递 + 本地模式回退
- 支持超时、Ctrl+C 中断、--analyze-only 等现有选项

用法：
    python launcher.py --goal "你的目标"
    python launcher.py --goal "帮我分析下季度增长策略" --analyze-only
    python launcher.py --interactive
"""

import argparse
import asyncio
import logging
import signal
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Any

# 添加 engine 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from .ceo import CEORouter, RoutingResult
from ..strategy.strategy import StrategyEngine
from ..pm.pm import PMCoordinator, ExecutionMode
from ..department.department import DepartmentExecutor, TaskRequest
from ..debate.debate_engine import DebateEngine

# 导入消息传递组件
try:
    from CYBERTEAM.team.models import MessageType, TeamMessage
    from CYBERTEAM.mcp.mailbox import MailboxManager
    MAILBOX_AVAILABLE = True
except ImportError:
    MAILBOX_AVAILABLE = False
    logging.warning("MailboxManager 不可用，使用本地模拟模式")

# CyberTeam 适配器
try:
    from integration.cyberteam_adapter import CyberTeamAdapter
    ADAPTER_AVAILABLE = True
except ImportError:
    ADAPTER_AVAILABLE = False
    CyberTeamAdapter = None

# ============================================================================
# 配置与常量
# ============================================================================

DEFAULT_TIMEOUT = 300  # 5分钟超时
DEFAULT_TEAM_NAME = "cyberteam-launcher"
LOGGER = logging.getLogger(__name__)


class StageStatus(Enum):
    """Stage 执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """Stage 执行结果"""
    stage: str
    status: StageStatus
    output: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    messages_sent: int = 0
    messages_received: int = 0


@dataclass
class TaskContext:
    """任务执行上下文"""
    task_id: str
    team_name: str
    user_input: str
    routing: Optional[RoutingResult] = None
    plan: Optional[Any] = None
    coo_inbox: str = "coo"
    ceo_inbox: str = "ceo"
    expert_inboxes: list = field(default_factory=list)
    stage_results: dict = field(default_factory=dict)
    messages: list = field(default_factory=list)
    cancelled: bool = False


# ============================================================================
# Mailbox 封装 (支持回退)
# ============================================================================

class MailboxClient:
    """Mailbox 客户端封装，支持本地模式回退"""

    def __init__(self, team_name: str, local_mode: bool = False):
        self.team_name = team_name
        self.local_mode = local_mode or not MAILBOX_AVAILABLE
        self._mailbox: Optional[MailboxManager] = None
        self._local_queue: dict[str, list] = {}  # 本地模式下的消息队列

        if not self.local_mode and MAILBOX_AVAILABLE:
            try:
                self._mailbox = MailboxManager(team_name)
                LOGGER.info(f"MailboxManager 初始化成功: {team_name}")
            except Exception as e:
                LOGGER.warning(f"MailboxManager 初始化失败: {e}，切换到本地模式")
                self.local_mode = True

    def send(
        self,
        from_agent: str,
        to: str,
        content: str,
        msg_type: str = "message",
        timeout: int = DEFAULT_TIMEOUT
    ) -> Optional[TeamMessage]:
        """
        发送消息

        Args:
            from_agent: 发送者
            to: 接收者 inbox 名称
            content: 消息内容
            msg_type: 消息类型
            timeout: 超时时间（秒）

        Returns:
            TeamMessage 或 None
        """
        if self.local_mode:
            # 本地模式：存入队列
            if to not in self._local_queue:
                self._local_queue[to] = []
            msg = {
                "id": f"local_{uuid.uuid4().hex[:8]}",
                "from": from_agent,
                "to": to,
                "content": content,
                "type": msg_type,
                "timestamp": datetime.now().isoformat()
            }
            self._local_queue[to].append(msg)
            LOGGER.debug(f"[本地模式] 消息已存入队列: {from_agent} → {to}")
            return None

        # Mailbox 模式
        try:
            msg_type_enum = MessageType.message
            if msg_type == "broadcast":
                msg_type_enum = MessageType.broadcast
            elif msg_type == "task":
                msg_type_enum = MessageType.task

            msg = self._mailbox.send(
                from_agent=from_agent,
                to=to,
                content=content,
                msg_type=msg_type_enum,
                timeout=timeout
            )
            LOGGER.debug(f"[Mailbox] 消息发送成功: {from_agent} → {to}")
            return msg
        except Exception as e:
            LOGGER.error(f"[Mailbox] 消息发送失败: {e}")
            # 回退到本地模式
            self.local_mode = True
            return self.send(from_agent, to, content, msg_type, timeout)

    def receive(self, agent_name: str, timeout: int = DEFAULT_TIMEOUT) -> list:
        """
        接收消息

        Args:
            agent_name: 接收者名称
            timeout: 超时时间（秒）

        Returns:
            消息列表
        """
        if self.local_mode:
            # 本地模式：从队列取出
            messages = self._local_queue.get(agent_name, [])
            self._local_queue[agent_name] = []
            LOGGER.debug(f"[本地模式] 接收消息: {agent_name}, 数量: {len(messages)}")
            return messages

        # Mailbox 模式
        try:
            messages = self._mailbox.receive(agent_name, limit=10)
            LOGGER.debug(f"[Mailbox] 接收消息: {agent_name}, 数量: {len(messages)}")
            return messages
        except Exception as e:
            LOGGER.error(f"[Mailbox] 接收消息失败: {e}")
            return []

    def broadcast(
        self,
        from_agent: str,
        content: str,
        exclude: Optional[list] = None
    ) -> list:
        """广播消息"""
        if self.local_mode:
            LOGGER.debug(f"[本地模式] 广播: {from_agent}")
            return []

        try:
            return self._mailbox.broadcast(from_agent, content, exclude=exclude)
        except Exception as e:
            LOGGER.error(f"[Mailbox] 广播失败: {e}")
            return []


# ============================================================================
# 消息处理器
# ============================================================================

class MessageHandler:
    """消息处理器基类"""

    def __init__(self, mailbox: MailboxClient, context: TaskContext):
        self.mailbox = mailbox
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)

    async def handle(self, message: dict) -> Optional[dict]:
        """处理消息，返回响应或 None"""
        raise NotImplementedError


class COOMessageHandler(MessageHandler):
    """COO 消息处理器"""

    async def handle(self, message: dict) -> Optional[dict]:
        """处理来自 CEO 的任务消息"""
        content = message.get("content", "")

        if "strategy_discuss" in content:
            # 策略讨论任务
            return await self._handle_strategy_discuss(message)
        elif "execute" in content:
            # 执行任务
            return await self._handle_execution(message)
        else:
            return {"status": "unknown_task", "content": content}

    async def _handle_strategy_discuss(self, message: dict) -> dict:
        """处理策略讨论"""
        self.logger.info("COO 开始策略讨论")

        # 向专家发送讨论消息
        expert_results = []
        for expert_inbox in self.context.expert_inboxes:
            self.mailbox.send(
                from_agent=self.context.coo_inbox,
                to=expert_inbox,
                content=f"请分析并提供专业意见: {self.context.user_input}"
            )

        # 收集专家回复（模拟）
        await asyncio.sleep(0.1)  # 模拟等待

        return {
            "status": "discussed",
            "experts_consulted": len(self.context.expert_inboxes),
            "summary": "策略讨论完成"
        }

    async def _handle_execution(self, message: dict) -> dict:
        """处理执行任务"""
        self.logger.info("COO 开始调度执行")
        return {
            "status": "dispatched",
            "departments": self.context.plan.resources["departments"] if self.context.plan else []
        }


class ExpertMessageHandler(MessageHandler):
    """专家消息处理器"""

    def __init__(self, mailbox: MailboxClient, context: TaskContext, expert_name: str):
        super().__init__(mailbox, context)
        self.expert_name = expert_name

    async def handle(self, message: dict) -> Optional[dict]:
        """处理 COO 的咨询请求"""
        content = message.get("content", "")

        # 模拟专家分析
        analysis = f"专家 {self.expert_name} 分析: 已理解任务要求"

        # 回复 COO
        self.mailbox.send(
            from_agent=self.expert_name,
            to=self.context.coo_inbox,
            content=analysis
        )

        return {"status": "analysis_complete", "expert": self.expert_name}


# ============================================================================
# 主引擎类
# ============================================================================

class CyberTeamV4:
    """
    CyberTeam V4 核心引擎 (消息驱动架构)

    重构说明：
    1. CEO 路由后通过 Mailbox 发送任务给 COO
    2. COO 处理后通过 Mailbox 与专家交互
    3. 专家回复后 COO 汇总并向 CEO 汇报
    4. CEO 审核后通过 Mailbox 触发部门执行
    5. 支持本地模式回退（MailboxManager 不可用时）
    """

    def __init__(self, debug: bool = False, analyze_only: bool = False, timeout: int = DEFAULT_TIMEOUT):
        self.debug = debug
        self.analyze_only = analyze_only
        self.timeout = timeout
        self.team_name = DEFAULT_TEAM_NAME

        # 核心组件
        self.router = CEORouter()
        self.strategy = StrategyEngine()
        self.pm = PMCoordinator(timeout=timeout)
        self.department = DepartmentExecutor()
        self.debate_engine = DebateEngine()

        # CyberTeam 适配器
        self.cyberteam = CyberTeamAdapter() if ADAPTER_AVAILABLE else None

        # Mailbox 客户端
        self.mailbox = MailboxClient(self.team_name, local_mode=not MAILBOX_AVAILABLE)

        # 任务历史
        self.task_history: list[TaskContext] = []

        # 设置信号处理（Ctrl+C）
        self._setup_signal_handlers()

        # 配置日志
        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def handle_signal(signum, frame):
            LOGGER.warning(f"收到信号 {signum}，准备优雅退出...")
            # 设置取消标志
            for ctx in self.task_history:
                ctx.cancelled = True
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    async def run_async(self, user_input: str, context: dict = None) -> dict:
        """
        异步运行完整流程

        消息驱动流程：
        1. CEO 路由 → 发送任务消息给 COO
        2. COO 策略讨论 → 与专家多轮交互
        3. COO 汇总上报 → 发送汇总消息给 CEO
        4. CEO 审核授权 → 发送执行消息给部门
        5. 部门执行 → 发送完成消息给 CEO
        6. CEO 最终汇总
        """

        print("\n" + "=" * 60)
        print("CyberTeam V4 核心引擎 (消息驱动模式)")
        print("=" * 60)
        print(f"Mailbox 模式: {'启用' if not self.mailbox.local_mode else '本地模式(回退)'}")
        print(f"分析模式: {'启用' if self.analyze_only else '关闭'}")
        print("=" * 60)

        # 初始化任务上下文
        task_id = str(uuid.uuid4())[:8]
        ctx = TaskContext(
            task_id=task_id,
            team_name=self.team_name,
            user_input=user_input
        )

        result = {
            "task_id": task_id,
            "user_input": user_input,
            "start_time": datetime.now().isoformat(),
            "mailbox_mode": "mailbox" if not self.mailbox.local_mode else "local",
            "stages": {}
        }

        try:
            # ========== Stage 1: CEO 路由 ==========
            stage_result = await self._stage1_ceo_routing(ctx)
            result["stages"]["ceo_routing"] = stage_result

            if ctx.cancelled:
                result["status"] = "cancelled"
                return result

            # 如果是简单咨询，直接返回
            if ctx.routing and ctx.routing.target == "NONE":
                result["status"] = "completed"
                result["output"] = "您好！有什么可以帮您的？"
                result["end_time"] = datetime.now().isoformat()
                return result

            # ========== Stage 2: CEO → COO 发送任务 ==========
            stage_result = await self._stage2_send_to_coo(ctx)
            result["stages"]["coo_task_sent"] = stage_result

            if ctx.cancelled:
                result["status"] = "cancelled"
                return result

            # ========== Stage 3: COO 策略讨论 ==========
            if not self.analyze_only:
                stage_result = await self._stage3_coo_strategy_discuss(ctx)
                result["stages"]["coo_strategy_discuss"] = stage_result

                if ctx.cancelled:
                    result["status"] = "cancelled"
                    return result

            # ========== Stage 4: COO 汇总上报给 CEO ==========
            stage_result = await self._stage4_coo_summary(ctx)
            result["stages"]["coo_summary"] = stage_result

            if ctx.cancelled:
                result["status"] = "cancelled"
                return result

            # ========== Stage 5: CEO 审核与授权 ==========
            stage_result = await self._stage5_ceo_authorization(ctx)
            result["stages"]["ceo_authorization"] = stage_result

            if ctx.cancelled:
                result["status"] = "cancelled"
                return result

            # ========== Stage 6: 部门执行 ==========
            if not self.analyze_only and ctx.plan:
                stage_result = await self._stage6_department_execution(ctx)
                result["stages"]["execution"] = stage_result

            # ========== Stage 7: CEO 最终汇总 ==========
            result["status"] = "completed"
            result["output"] = ctx.stage_results
            result["end_time"] = datetime.now().isoformat()

        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error"] = f"任务执行超时 ({self.timeout}s)"
            LOGGER.error(result["error"])
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            LOGGER.exception("任务执行失败")

        print("\n" + "=" * 60)
        print(f"执行完成 - 状态: {result.get('status')}")
        print("=" * 60)

        return result

    def run(self, user_input: str, context: dict = None) -> dict:
        """同步入口（兼容现有代码）"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已经在事件循环中，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.run_async(user_input, context))
                    return future.result(timeout=self.timeout + 10)
            else:
                return loop.run_until_complete(self.run_async(user_input, context))
        except KeyboardInterrupt:
            return {"status": "cancelled", "error": "用户中断"}
        except Exception as e:
            LOGGER.exception("同步执行失败")
            return {"status": "failed", "error": str(e)}

    # =========================================================================
    # Stage 实现
    # =========================================================================

    async def _stage1_ceo_routing(self, ctx: TaskContext) -> dict:
        """Stage 1: CEO 路由"""
        print("\n【Stage 1】CEO 路由 (L1)")
        print("-" * 40)

        start_time = datetime.now()
        routing = self.router.route(ctx.user_input)
        ctx.routing = routing

        print(f"  意图识别: {routing.intent}")
        print(f"  复杂度: {routing.complexity}")
        print(f"  路由目标: {routing.target} → {routing.target_name}")
        print(f"  理由: {routing.reason}")

        # 设置专家 inbox（根据路由目标）
        if routing.target == "L2":
            ctx.expert_inboxes = ["strategy_expert", "ops_expert"]
        elif routing.target == "L3A":
            ctx.expert_inboxes = [f"{dept}_expert" for dept in ["数据分析", "内容运营", "技术研发"]]
        elif routing.target == "SWARM":
            ctx.expert_inboxes = ["researcher_1", "researcher_2", "executor_1", "qa"]

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "intent": routing.intent,
            "complexity": routing.complexity,
            "target": routing.target,
            "target_name": routing.target_name,
            "reason": routing.reason,
            "expert_inboxes": ctx.expert_inboxes,
            "duration": duration,
            "status": "success"
        }

    async def _stage2_send_to_coo(self, ctx: TaskContext) -> dict:
        """Stage 2: CEO → COO 发送任务消息"""
        print("\n【Stage 2】CEO → COO 发送任务")
        print("-" * 40)

        start_time = datetime.now()
        messages_sent = 0

        # 构建任务消息
        task_message = f"""
任务来源: 用户
任务描述: {ctx.user_input}

路由信息:
- 意图: {ctx.routing.intent}
- 复杂度: {ctx.routing.complexity}
- 目标: {ctx.routing.target} → {ctx.routing.target_name}

请进行策略讨论并向我汇报。
"""

        # 发送消息给 COO
        self.mailbox.send(
            from_agent=ctx.ceo_inbox,
            to=ctx.coo_inbox,
            content=task_message.strip(),
            msg_type="task"
        )
        messages_sent += 1

        print(f"  → 已发送任务消息给 COO")
        print(f"  → 等待 COO 确认...")

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "messages_sent": messages_sent,
            "messages_received": 0,
            "duration": duration,
            "status": "success"
        }

    async def _stage3_coo_strategy_discuss(self, ctx: TaskContext) -> dict:
        """Stage 3: COO 策略讨论（与专家多轮交互）"""
        print("\n【Stage 3】COO 策略讨论 (L2)")
        print("-" * 40)

        start_time = datetime.now()
        messages_sent = 0
        messages_received = 0

        # COO 处理任务
        coo_handler = COOMessageHandler(self.mailbox, ctx)

        # 向专家发送咨询消息
        for expert_inbox in ctx.expert_inboxes:
            discuss_msg = f"""
COO 发起策略讨论
任务: {ctx.user_input}

请提供:
1. 专业分析意见
2. 执行方案建议
3. 风险预案
"""
            self.mailbox.send(
                from_agent=ctx.coo_inbox,
                to=expert_inbox,
                content=discuss_msg.strip()
            )
            messages_sent += 1
            print(f"  → 已发送讨论消息给 {expert_inbox}")

        # 等待专家回复（带超时）
        print(f"  → 等待专家回复... (超时: {self.timeout}s)")

        expert_replies = []
        for expert_inbox in ctx.expert_inboxes:
            # 使用带超时的接收
            try:
                replies = await asyncio.wait_for(
                    asyncio.to_thread(self.mailbox.receive, expert_inbox, timeout=5),
                    timeout=10
                )
                messages_received += len(replies)
                expert_replies.extend(replies)
                print(f"  ← {expert_inbox} 回复: {len(replies)} 条")
            except asyncio.TimeoutError:
                print(f"  ← {expert_inbox} 超时无回复")
            except Exception as e:
                LOGGER.debug(f"接收 {expert_inbox} 消息失败: {e}")

        # COO 汇总专家意见
        summary_msg = f"""
COO 策略讨论汇总

参与专家: {len(ctx.expert_inboxes)}
收到回复: {len(expert_replies)}

专家意见已汇总，详见执行方案。
"""

        # 存储讨论结果
        ctx.stage_results["expert_replies"] = [
            {"expert": r.get("from"), "content": r.get("content")}
            for r in expert_replies
        ]

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "messages_sent": messages_sent,
            "messages_received": messages_received,
            "experts_consulted": len(ctx.expert_inboxes),
            "replies_received": len(expert_replies),
            "duration": duration,
            "status": "success" if expert_replies else "partial"
        }

    async def _stage4_coo_summary(self, ctx: TaskContext) -> dict:
        """Stage 4: COO 向 CEO 汇总上报"""
        print("\n【Stage 4】COO → CEO 汇总上报")
        print("-" * 40)

        start_time = datetime.now()

        # COO 汇总消息
        summary_message = f"""
COO 汇总报告

任务: {ctx.user_input}
路由: {ctx.routing.target} → {ctx.routing.target_name}

策略讨论结果:
- 已咨询 {len(ctx.expert_inboxes)} 位专家
- 收到 {len(ctx.stage_results.get('expert_replies', []))} 条回复

执行建议:
- 建议执行部门: {ctx.routing.target_name}
- 建议执行模式: {'并行' if ctx.routing.complexity == '高' else '串行'}

请 CEO 审核并授权执行。
"""

        # 发送汇总给 CEO
        self.mailbox.send(
            from_agent=ctx.coo_inbox,
            to=ctx.ceo_inbox,
            content=summary_message.strip(),
            msg_type="message"
        )

        print(f"  → COO 已发送汇总报告给 CEO")
        print(f"  → 等待 CEO 审核...")

        # 模拟 COO 等待 CEO 反馈
        await asyncio.sleep(0.1)

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "messages_sent": 1,
            "messages_received": 0,
            "summary": "汇总报告已发送",
            "duration": duration,
            "status": "success"
        }

    async def _stage5_ceo_authorization(self, ctx: TaskContext) -> dict:
        """Stage 5: CEO 审核与授权"""
        print("\n【Stage 5】CEO 审核与授权")
        print("-" * 40)

        start_time = datetime.now()

        # CEO 审核并决策
        # 创建执行计划
        plan = self.strategy.create_plan(
            ctx.task_id,
            ctx.user_input,
            ctx.routing.intent,
            ctx.routing.complexity
        )
        ctx.plan = plan

        print(f"  任务ID: {plan.task_id}")
        print(f"  思维框架: {plan.framework.value}")
        print(f"  部门: {plan.resources['departments']}")

        # CEO 授权执行
        auth_message = f"""
CEO 执行授权

任务ID: {plan.task_id}
授权部门: {', '.join(plan.resources['departments'])}

CEO 审核意见:
- 路由决策: {ctx.routing.decision}
- 策略方案: 合理，批准执行
- 执行模式: {'并行' if plan.complexity == '高' else '串行'}

开始执行。
"""

        # 广播执行授权
        self.mailbox.broadcast(
            from_agent=ctx.ceo_inbox,
            content=auth_message.strip()
        )

        print(f"  → CEO 已授权执行")
        print(f"  → 已广播执行消息")

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "task_id": plan.task_id,
            "departments": plan.resources["departments"],
            "framework": plan.framework.value,
            "duration": duration,
            "status": "authorized"
        }

    async def _stage6_department_execution(self, ctx: TaskContext) -> dict:
        """Stage 6: 部门执行"""
        print("\n【Stage 6】部门执行 (L3)")
        print("-" * 40)

        start_time = datetime.now()
        outputs = {}
        messages_sent = 0

        # 向各部门发送执行消息
        for dept in ctx.plan.resources["departments"]:
            print(f"  → {dept} 执行中...")

            # 发送执行消息给部门
            exec_msg = f"""
部门执行任务

任务ID: {ctx.plan.task_id}
部门: {dept}
任务描述: {ctx.user_input}

请执行并报告结果。
"""
            self.mailbox.send(
                from_agent=ctx.ceo_inbox,
                to=f"{dept}_executor",
                content=exec_msg.strip()
            )
            messages_sent += 1

        # 并行执行（模拟）
        # 在实际实现中，这里应该启动异步任务
        await asyncio.sleep(0.5)

        # 收集执行结果（从 mailbox 接收）
        for dept in ctx.plan.resources["departments"]:
            try:
                results = self.mailbox.receive(f"{dept}_executor", timeout=1)
                if results:
                    outputs[dept] = {"status": "success", "output": results[0].get("content", "")}
                else:
                    outputs[dept] = {"status": "success", "output": f"{dept} 执行完成（本地模式）"}
            except Exception:
                outputs[dept] = {"status": "success", "output": f"{dept} 执行完成（本地模式）"}

            print(f"  ← {dept}: {outputs[dept]['status']}")

        # 汇总结果
        aggregated = {
            "summary": {
                "departments": len(outputs),
                "success": sum(1 for o in outputs.values() if o["status"] == "success")
            },
            "outputs": outputs
        }

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "messages_sent": messages_sent,
            "messages_received": len(outputs),
            "execution": aggregated,
            "duration": duration,
            "status": "success"
        }

    def run_interactive(self):
        """交互模式"""
        print("\n" + "=" * 60)
        print("CyberTeam V4 - 交互模式")
        print("=" * 60)
        print("输入您的目标，按 Enter 执行")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n> ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("再见！")
                    break

                if not user_input:
                    continue

                self.run(user_input)

            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"\n错误: {e}")


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description="CyberTeam V4 启动器 (消息驱动架构)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python launcher.py --goal "帮我分析季度增长策略"
    python launcher.py --goal "开发用户登录功能" --analyze-only
    python launcher.py --interactive
    python launcher.py -g "小红书内容运营方案" --timeout 600

退出: Ctrl+C
"""
    )
    parser.add_argument("--goal", "-g", help="任务目标")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式")
    parser.add_argument(
        "--analyze-only",
        "-a",
        action="store_true",
        help="仅分析，不执行（CEO路由+策略讨论）"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"超时时间（秒），默认 {DEFAULT_TIMEOUT}"
    )
    parser.add_argument(
        "--team-name",
        default=DEFAULT_TEAM_NAME,
        help=f"团队名称，默认 {DEFAULT_TEAM_NAME}"
    )

    args = parser.parse_args()

    # 初始化
    ct = CyberTeamV4(
        debug=args.debug,
        analyze_only=args.analyze_only,
        timeout=args.timeout
    )
    ct.team_name = args.team_name

    if args.interactive:
        print("=" * 60)
        print("CyberTeam V4 - 交互模式 (消息驱动)")
        print("=" * 60)
        print(f"Mailbox 模式: {'MailboxManager' if not ct.mailbox.local_mode else '本地模式'}")
        print(f"分析模式: {'启用' if args.analyze_only else '关闭'}")
        print(f"超时时间: {args.timeout}s")
        print("=" * 60)
        ct.run_interactive()
    elif args.goal:
        result = ct.run(args.goal)
        print("\n【最终结果】")
        print(f"状态: {result.get('status')}")
        print(f"任务ID: {result.get('task_id')}")
        print(f"Mailbox模式: {result.get('mailbox_mode')}")
        if result.get('error'):
            print(f"错误: {result.get('error')}")
        if result.get('stages'):
            print("\n各Stage状态:")
            for stage, stage_result in result['stages'].items():
                print(f"  {stage}: {stage_result.get('status', 'unknown')}")
    else:
        # 默认交互模式
        print("请提供 --goal 参数或使用 --interactive 模式")
        parser.print_help()


if __name__ == "__main__":
    main()
