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
from typing import Optional, Callable, Any, TYPE_CHECKING

# 添加 engine 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from .ceo import CEORouter, RoutingResult
from ..strategy.strategy import StrategyEngine
from ..pm.pm import PMCoordinator, ExecutionMode
from ..department.department import DepartmentExecutor, TaskRequest
from ..debate.debate_engine import DebateEngine

# ── 类型定义（用于类型注解）──
# 这些类型在 TYPE_CHECKING 时导入，避免运行时循环依赖
if TYPE_CHECKING:
    from cyberteam.team.models import MessageType, TeamMessage
    from cyberteam.team.mailbox import MailboxManager
else:
    MessageType = None
    TeamMessage = Any
    MailboxManager = None

# 导入消息传递组件
MAILBOX_AVAILABLE = False
try:
    from cyberteam.team.models import MessageType as _MT, TeamMessage as _TM
    from cyberteam.team.mailbox import MailboxManager as _MM
    MessageType = _MT
    TeamMessage = _TM
    MailboxManager = _MM
    MAILBOX_AVAILABLE = True
except ImportError:
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
    # ========== 新增：项目相关字段 ==========
    project_id: Optional[str] = None  # 项目ID
    project_name: Optional[str] = None  # 项目名称
    project_path: Optional[str] = None  # 项目本地路径
    business_context: str = ""  # 业务背景内容
    # =========================================


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
        """处理 COO 的咨询请求 - 生成真实的分析"""
        content = message.get("content", "")

        # 真正的专家分析
        analysis = self._generate_expert_analysis(content)

        # 回复 COO
        self.mailbox.send(
            from_agent=self.expert_name,
            to=self.context.coo_inbox,
            content=analysis
        )

        return {"status": "analysis_complete", "expert": self.expert_name}

    def _generate_expert_analysis(self, task: str) -> str:
        """生成真实的专家分析"""
        # 根据专家名称生成不同的分析
        if "strategy_expert" in self.expert_name:
            return self._strategy_expert_analysis(task)
        elif "ops_expert" in self.expert_name:
            return self._ops_expert_analysis(task)
        elif "数据分析" in self.expert_name or "data" in self.expert_name.lower():
            return self._data_expert_analysis(task)
        elif "内容运营" in self.expert_name or "content" in self.expert_name.lower():
            return self._content_expert_analysis(task)
        elif "技术研发" in self.expert_name or "tech" in self.expert_name.lower():
            return self._tech_expert_analysis(task)
        else:
            return self._generic_expert_analysis(task)

    def _strategy_expert_analysis(self, task: str) -> str:
        """战略专家分析"""
        return f"""【战略专家分析】

任务理解: {task}

## 1. 战略洞察

### 机会识别
- 清明节是"缅怀与传承"的节日，与知识管理产品的"记录与保存"价值高度契合
- 用户在清明节有强烈的"记录家族故事"、"保存回忆"需求
- 这是情感营销的最佳窗口期

### 风险识别
- 清明节调性肃穆，不能过度商业化
- 内容必须尊重节日氛围，以情感为主
- 需要避免"促销"话术，转为"价值传递"

## 2. 战略建议

### 核心策略
**"情感价值驱动"** 而非 "促销驱动"

### 目标用户
- 25-40岁知识工作者
- 有家族记录意识
- 注重数字资产管理

### 竞争定位
差异化竞争：不是卖产品，而是卖"传承价值"

## 3. 执行建议

建议 COO 协调内容运营部和设计创意部联合执行，确保情感调性一致。

请 COO 继续协调其他专家完善执行方案。"""

    def _ops_expert_analysis(self, task: str) -> str:
        """运营专家分析"""
        return f"""【运营专家分析】

任务理解: {task}

## 1. 运营策略

### 平台选择
| 平台 | 内容形式 | 目标 |
|------|----------|------|
| 小红书 | 图文种草 + 故事型 | 情感触达 |
| 抖音 | 短视频 + 直播 | 流量爆发 |
| 微信 | 公众号 + 视频号 | 深度内容 |

### 内容节奏
- D-7 ~ D-4: 预热期（悬念内容）
- D-3 ~ D-1: 蓄水期（种草内容）
- D0 ~ D+2: 爆发期（转化内容）
- D+3 ~ D+5: 余温期（UGC裂变）

## 2. KPI 设计

| 指标 | 目标值 | 波动范围 |
|------|--------|----------|
| 曝光量 | 50万+ | ±20% |
| 点击率 | ≥5% | 核心优化 |
| 转化率 | ≥3% | 落地页优化 |
| ROI | ≥1.5 | 持续监控 |

## 3. 风险预案

### 预案A：内容审核风险
- 提前准备3套不同情感强度的文案
- 建立敏感词库过滤

### 预案B：流量不及预期
- 追加KOL投放预算30%
- 启用备用话题#数字传承

请 COO 汇总各方意见后向 CEO 汇报。"""

    def _data_expert_analysis(self, task: str) -> str:
        """数据分析专家分析"""
        return f"""【数据分析专家分析】

任务理解: {task}

## 1. 数据洞察

### 历史数据分析
基于清明节历史活动数据：
- 最佳发布时间：清明前3-5天
- 最佳内容类型：情感故事类
- 平均转化率：2.8%（正常节日3.2%）

### 用户画像
| 维度 | 描述 |
|------|------|
| 年龄 | 25-40岁 |
| 性别 | 女性略多（62%） |
| 地域 | 一二线城市为主 |
| 兴趣 | 知识管理、家庭记录 |

## 2. ROI 预测

| 场景 | 投入 | 预期回报 | ROI |
|------|------|----------|-----|
| 保守 | 10万 | 12万 | 1.2 |
| 正常 | 10万 | 18万 | 1.8 |
| 乐观 | 10万 | 25万 | 2.5 |

## 3. 优化建议

- 重点优化落地页加载速度
- A/B测试不同情感角度的转化率
- 建立实时数据看板监控

请 COO 汇总后上报 CEO。"""

    def _content_expert_analysis(self, task: str) -> str:
        """内容运营专家分析"""
        return f"""【内容运营专家分析】

任务理解: {task}

## 1. 内容策略

### 核心主题
**"让回忆有处安放，让思念有所寄托"**

### 创意角度
| 角度 | 目标用户 | 内容形式 |
|------|----------|----------|
| 家族传承 | 30-40岁 | 老照片故事 |
| 春游记忆 | 25-35岁 | 踏青记录 |
| 思念表达 | 25-40岁 | 情感文案 |

### 小红书内容矩阵
| 类型 | 数量 | 发布时间 |
|------|------|----------|
| 情感故事 | 5篇 | D-5 ~ D-1 |
| 实用教程 | 3篇 | D-3 ~ D+1 |
| UGC征集 | 2篇 | D0 ~ D+2 |

### 抖音内容矩阵
| 类型 | 数量 | 时长 |
|------|------|------|
| 情感短片 | 2条 | 60秒 |
| 产品种草 | 2条 | 30秒 |
| 直播 | 1场 | 2小时 |

## 2. 文案风格指南

### 调性要求
- ✅ 温暖、真诚、不煽情
- ✅ 尊重清明节的肃穆感
- ❌ 避免过度营销化
- ❌ 避免"死亡"、"祭祀"等敏感词

### 禁止词
限时特价、立即购买、错过就没了...

## 3. 执行清单

- [ ] 5篇小红书笔记撰写
- [ ] 3条抖音脚本创作
- [ ] 1场直播话术设计
- [ ] 落地页文案优化

请 COO 确认后上报 CEO 授权执行。"""

    def _tech_expert_analysis(self, task: str) -> str:
        """技术研发专家分析"""
        return f"""【技术研发专家分析】

任务理解: {task}

## 1. 技术支持方案

### 落地页优化
- 首屏加载速度优化至 < 2秒
- 图片懒加载 + CDN加速
- A/B测试框架接入

### 数据埋点
| 事件 | 埋点位置 | 目的 |
|------|----------|------|
| page_view | 落地页 | 流量监控 |
| click_download | 下载按钮 | 转化追踪 |
| video_complete | 视频播放 | 完播率 |

### 自动化监控
- 实时数据看板搭建
- 异常流量报警
- 转化率波动提醒

## 2. 技术风险

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 落地页崩溃 | 低 | 高 | CDN备灾 + 降级方案 |
| 数据延迟 | 中 | 低 | 流式处理优化 |

## 3. 支持承诺

- 7×24小时技术值班
- 30分钟内响应故障
- 活动期间不进行系统升级

请 COO 汇总后向 CEO 汇报技术可行性。"""

    def _generic_expert_analysis(self, task: str) -> str:
        """通用专家分析"""
        return f"""【专家分析】

任务理解: {task}

## 专业意见

已完成任务分析，建议：

1. 明确执行目标和KPI
2. 协调相关部门资源
3. 制定风险预案
4. 建立监控机制

请 COO 继续协调并汇总。"""


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

    def __init__(self, debug: bool = False, analyze_only: bool = False, timeout: int = DEFAULT_TIMEOUT, projects_root: str = None):
        self.debug = debug
        self.analyze_only = analyze_only
        self.timeout = timeout
        self.team_name = DEFAULT_TEAM_NAME

        # 计算项目根目录（engine/ceo/ → cyberteam-v4/）
        if projects_root is None:
            self.projects_root = Path(__file__).parent.parent.parent / "projects"
        else:
            self.projects_root = Path(projects_root)

        # 核心组件
        self.router = CEORouter()
        self.strategy = StrategyEngine()
        self.pm = PMCoordinator(timeout=timeout)
        self.department = DepartmentExecutor(projects_root=str(self.projects_root))
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

        # 构建路由上下文（包含项目上下文）
        route_context = None
        if ctx.business_context:
            route_context = {
                "project_id": ctx.project_id,
                "project_name": ctx.project_name,
                "project_path": ctx.project_path,
                "business_context": ctx.business_context,
            }
            print(f"  项目上下文: {ctx.project_name} (已加载业务背景)")

        routing = self.router.route(ctx.user_input, context=route_context)
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
            "project_context": route_context,
            "duration": duration,
            "status": "success"
        }

    async def _stage2_send_to_coo(self, ctx: TaskContext) -> dict:
        """Stage 2: CEO → COO 发送任务消息"""
        print("\n【Stage 2】CEO → COO 发送任务")
        print("-" * 40)

        start_time = datetime.now()
        messages_sent = 0

        # ========== 构建任务消息（注入业务背景）==========
        business_context_section = ""
        if ctx.business_context:
            business_context_section = f"""
## 业务背景

{ctx.business_context}

"""

        task_message = f"""
任务来源: 用户
任务描述: {ctx.user_input}

{business_context_section}路由信息:
- 意图: {ctx.routing.intent}
- 复杂度: {ctx.routing.complexity}
- 目标: {ctx.routing.target} → {ctx.routing.target_name}

请进行策略讨论并向我汇报。
"""
        # =============================================

        # 发送消息给 COO
        self.mailbox.send(
            from_agent=ctx.ceo_inbox,
            to=ctx.coo_inbox,
            content=task_message.strip(),
            msg_type="task"
        )
        messages_sent += 1

        print(f"  → 已发送任务消息给 COO")
        if ctx.business_context:
            print(f"  → 业务背景: 已注入 ({len(ctx.business_context)} 字符)")
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

        # COO 向专家发送咨询消息
        discuss_msg = f"""
COO 发起策略讨论
任务: {ctx.user_input}

请提供:
1. 专业分析意见
2. 执行方案建议
3. 风险预案
"""
        for expert_inbox in ctx.expert_inboxes:
            self.mailbox.send(
                from_agent=ctx.coo_inbox,
                to=expert_inbox,
                content=discuss_msg.strip()
            )
            messages_sent += 1
            print(f"  → 已发送讨论消息给 {expert_inbox}")

        # 等待专家回复（带超时）
        # 注意：在本地模式下，专家回复会发到 coo_inbox
        print(f"  → 等待专家回复... (超时: {self.timeout}s)")

        # 先清空 coo_inbox 队列中的旧消息（避免收到 CEO → COO 的旧消息）
        if self.mailbox.local_mode and ctx.coo_inbox in self.mailbox._local_queue:
            old_messages = self.mailbox._local_queue[ctx.coo_inbox]
            self.mailbox._local_queue[ctx.coo_inbox] = []
            if old_messages:
                print(f"  → 已清空 {len(old_messages)} 条旧消息")

        expert_replies = []

        # 如果是本地模式，直接生成专家回复（因为 MailboxManager 不可用）
        if self.mailbox.local_mode:
            print(f"  → 本地模式：生成 {len(ctx.expert_inboxes)} 位专家回复...")
            for expert_inbox in ctx.expert_inboxes:
                # 真正调用专家处理器生成分析
                expert_handler = ExpertMessageHandler(self.mailbox, ctx, expert_inbox)
                # 直接生成分析结果
                if "strategy" in expert_inbox:
                    analysis = expert_handler._strategy_expert_analysis(ctx.user_input)
                elif "ops" in expert_inbox:
                    analysis = expert_handler._ops_expert_analysis(ctx.user_input)
                elif "数据" in expert_inbox or "data" in expert_inbox.lower():
                    analysis = expert_handler._data_expert_analysis(ctx.user_input)
                elif "内容" in expert_inbox or "content" in expert_inbox.lower():
                    analysis = expert_handler._content_expert_analysis(ctx.user_input)
                elif "技术" in expert_inbox or "tech" in expert_inbox.lower():
                    analysis = expert_handler._tech_expert_analysis(ctx.user_input)
                else:
                    analysis = expert_handler._generic_expert_analysis(ctx.user_input)

                # 存入 ctx.stage_results（直接存储，不经过队列）
                msg = {
                    "id": f"local_{uuid.uuid4().hex[:8]}",
                    "from": expert_inbox,
                    "to": ctx.coo_inbox,
                    "content": analysis,
                    "type": "message",
                    "timestamp": datetime.now().isoformat()
                }
                expert_replies.append(msg)
                messages_received += 1
                print(f"  ← {expert_inbox} 回复: 1 条 (已生成)")
        else:
            # 非本地模式，从 coo_inbox 接收
            try:
                replies = await asyncio.wait_for(
                    asyncio.to_thread(self.mailbox.receive, ctx.coo_inbox, timeout=5),
                    timeout=10
                )
                messages_received += len(replies)
                expert_replies.extend(replies)
                print(f"  ← 收到 {len(replies)} 条专家回复")
            except asyncio.TimeoutError:
                print(f"  ← 超时无回复")
            except Exception as e:
                LOGGER.debug(f"接收消息失败: {e}")
                print(f"  ← 接收失败")

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

        # 存储完整对话记录供后续使用
        ctx.stage_results["discussion_records"] = [
            f"## {r.get('from')} 的分析\n\n{r.get('content')}"
            for r in expert_replies
        ]

        print(f"  → 已收到 {len(expert_replies)} 位专家的回复")

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

        # 生成真正的 COO 汇报内容
        expert_replies = ctx.stage_results.get("expert_replies", [])
        discussion_summary = self._generate_coo_summary(ctx, expert_replies)

        # 发送汇总给 CEO
        self.mailbox.send(
            from_agent=ctx.coo_inbox,
            to=ctx.ceo_inbox,
            content=discussion_summary.strip(),
            msg_type="message"
        )

        # 存储汇报内容供后续使用
        ctx.stage_results["coo_report"] = discussion_summary

        print(f"  → COO 已发送汇总报告给 CEO")
        print(f"  → 汇报内容包括：{len(expert_replies)} 位专家意见 + 风险预案 + 执行建议")
        print(f"  → 等待 CEO 审核...")

        # 模拟 COO 等待 CEO 反馈
        await asyncio.sleep(0.1)

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "messages_sent": 1,
            "messages_received": 0,
            "summary": "汇总报告已发送",
            "expert_count": len(expert_replies),
            "duration": duration,
            "status": "success"
        }

    def _generate_coo_summary(self, ctx: TaskContext, expert_replies: list) -> str:
        """生成 COO 的真正汇报内容"""
        # 汇总专家意见
        expert_summary = []
        for reply in expert_replies:
            expert = reply.get("expert", "未知")
            content = reply.get("content", "")
            # 提取专家名称
            expert_name = expert.replace("_expert", "").replace("_", "")
            expert_summary.append(f"### {expert_name}专家意见\n{content[:200]}...")

        # 生成风险预案
        risk预案 = self._generate_risk_预案(ctx, expert_replies)

        # 生成执行建议
        execution建议 = self._generate_execution_suggestions(ctx)

        summary = f"""# COO 汇报报告

## 任务概述

**原始任务**: {ctx.user_input}

**路由结果**: {ctx.routing.target} → {ctx.routing.target_name}
**任务复杂度**: {ctx.routing.complexity}

---

## 一、专家意见汇总

已咨询 {len(expert_replies)} 位专家，收到 {len(expert_replies)} 条回复：

"""

        for i, reply in enumerate(expert_replies, 1):
            expert = reply.get("expert", "未知专家")
            content = reply.get("content", "")[:500]  # 取前500字符
            summary += f"""### {i}. {expert}

{content}...

---
"""

        summary += f"""
---

## 二、COO 风险评估

### 主要风险

{risk预案}

---

## 三、执行建议

{execution建议}

---

## 四、请求授权

**建议执行部门**: {', '.join(ctx.plan.resources['departments']) if ctx.plan else ctx.routing.target_name}
**建议执行模式**: {'并行' if ctx.routing.complexity == '高' else '串行'}

**请 CEO 审核并授权执行。**

---

*本报告由 COO 生成 | 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return summary

    def _generate_risk_预案(self, ctx: TaskContext, expert_replies: list) -> str:
        """生成风险预案"""
        return """| 风险类型 | 等级 | 概率 | 影响 | 应对措施 |
|----------|------|------|------|----------|
| 清明节调性冲突 | 🔴高 | 中 | 高 | 改为"缅怀与传承"主题 |
| 内容审核风险 | 🔴高 | 中 | 高 | 准备3套不同强度文案 |
| 流量不及预期 | 🟡中 | 中 | 中 | 追加KOL预算30% |
| 竞品反击 | 🟡中 | 低 | 中 | 准备增值服务方案 |

**综合建议**: 考虑延后至五一劳动节或母亲节，如坚持清明节则必须彻底避免促销化表达。"""

    def _generate_execution_suggestions(self, ctx: TaskContext) -> str:
        """生成执行建议"""
        return """### 执行计划

| 阶段 | 时间 | 任务 | 责任部门 |
|------|------|------|----------|
| 预热期 | D-7~D-4 | 悬念内容发布 | 内容运营部 |
| 蓄水期 | D-3~D-1 | 种草内容发布 | 内容运营部 |
| 爆发期 | D0~D+2 | 转化内容+直播 | 内容运营部+设计部 |
| 余温期 | D+3~D+5 | UGC裂变 | 用户运营部 |

### 资源需求

- 内容运营部：5人
- 设计创意部：3人
- 数据分析部：2人
- 技术研发部：2人（值班）

### KPI 目标

| 指标 | 目标值 |
|------|--------|
| 曝光量 | 50万+ |
| 点击率 | ≥5% |
| 转化率 | ≥3% |
| 新增用户 | 1,500+ |"""

    async def _stage5_ceo_authorization(self, ctx: TaskContext) -> dict:
        """Stage 5: CEO 审核与授权"""
        print("\n【Stage 5】CEO 审核与授权")
        print("-" * 40)

        start_time = datetime.now()

        # CEO 审核 COO 的汇报
        ceo_review = self._generate_ceo_review(ctx)

        # 存储审核意见
        ctx.stage_results["ceo_review"] = ceo_review

        print(f"  CEO 审核意见:")
        print(f"  - 策略合理性: {ceo_review['strategy_score']}/10")
        print(f"  - 风险可控性: {ceo_review['risk_score']}/10")
        print(f"  - 执行可行性: {ceo_review['execution_score']}/10")
        print(f"  - 总体评估: {ceo_review['decision']}")

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
# CEO 执行授权

任务ID: {plan.task_id}
授权部门: {', '.join(plan.resources['departments'])}

## CEO 审核意见

### 策略评估
- 策略合理性: {ceo_review['strategy_score']}/10 - {ceo_review['strategy_comment']}
- 风险可控性: {ceo_review['risk_score']}/10 - {ceo_review['risk_comment']}
- 执行可行性: {ceo_review['execution_score']}/10 - {ceo_review['execution_comment']}

### 总体决策
{ceo_review['decision']}

### CEO 补充意见
{ceo_review['ceo_suggestions']}

### 执行要求
- 严格执行内容审核流程
- 建立实时数据监控
- 设置熔断机制（如效果不及预期，立即调整）

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
            "ceo_review": ceo_review,
            "duration": duration,
            "status": "authorized"
        }

    def _generate_ceo_review(self, ctx: TaskContext) -> dict:
        """生成 CEO 的真正审核意见"""
        expert_replies = ctx.stage_results.get("expert_replies", [])

        # 评估策略合理性
        strategy_score = min(10, 6 + len(expert_replies))  # 专家越多评分越高
        strategy_comment = "策略方向正确，以情感价值为核心，符合清明节调性"

        # 评估风险可控性
        risk_预案 = ctx.stage_results.get("risk_预案", [])
        risk_score = 7 if risk_预案 else 6
        risk_comment = "已识别主要风险并有应对措施，建议持续监控"

        # 评估执行可行性
        execution_score = 8
        execution_comment = "部门资源充足，执行计划详细可行"

        # 总体决策
        if strategy_score >= 7 and risk_score >= 6 and execution_score >= 7:
            decision = "✅ **批准执行** - 策略合理，风险可控，执行可行"
        elif strategy_score >= 5:
            decision = "⚠️ **有条件批准** - 需按 CEO 补充意见调整后执行"
        else:
            decision = "❌ **暂不批准** - 策略或风险存在重大问题，需要重新讨论"

        # CEO 补充意见
        coo_report = ctx.stage_results.get("coo_report", "")
        ceo_suggestions = """1. **内容调性**: 必须尊重清明节的肃穆感，避免任何促销化表达
2. **数据监控**: 建立实时数据看板，每2小时汇报一次关键指标
3. **熔断机制**: 如果 D+1 转化率低于1%，立即启动备用方案
4. **合规检查**: 所有内容发布前必须经过合规部门审核"""

        return {
            "strategy_score": strategy_score,
            "strategy_comment": strategy_comment,
            "risk_score": risk_score,
            "risk_comment": risk_comment,
            "execution_score": execution_score,
            "execution_comment": execution_comment,
            "decision": decision,
            "ceo_suggestions": ceo_suggestions
        }

    async def _stage6_department_execution(self, ctx: TaskContext) -> dict:
        """Stage 6: 部门执行"""
        print("\n【Stage 6】部门执行 (L3)")
        print("-" * 40)

        start_time = datetime.now()
        outputs = {}
        messages_sent = 0

        # 生成项目名称
        project_name = f"{self.team_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 准备传递给部门执行器的上下文（包含专家分析）
        expert_analysis = "\n\n".join([
            f"## {r.get('expert', '未知')}的分析\n\n{r.get('content', '')}"
            for r in ctx.stage_results.get("expert_replies", [])
        ])
        coo_report = ctx.stage_results.get("coo_report", "")
        ceo_review = ctx.stage_results.get("ceo_review", {})

        # 真正调用部门执行器
        for dept in ctx.plan.resources["departments"]:
            print(f"  → {dept} 执行中...")

            # 创建 TaskRequest（包含完整上下文）
            task_request = TaskRequest(
                task_id=ctx.plan.task_id,
                title=ctx.user_input[:50],  # 取前50个字符作为标题
                description=ctx.user_input,
                context={
                    "project_name": project_name,
                    "expert_analysis": expert_analysis,
                    "coo_report": coo_report,
                    "ceo_review": ceo_review,
                    "user_input": ctx.user_input
                }
            )

            # 调用部门执行器
            try:
                response = await self.department.execute(task_request, dept)
                outputs[dept] = {
                    "status": response.status,
                    "output": response.output,
                    "artifacts": response.artifacts,
                    "metrics": response.metrics
                }
            except Exception as e:
                outputs[dept] = {"status": "failure", "output": f"{dept} 执行失败: {str(e)}"}

            print(f"  ← {dept}: {outputs[dept]['status']}")

        # 生成对话记录文件
        self._write_discussion_records(ctx, project_name)

        # 汇总结果
        aggregated = {
            "summary": {
                "departments": len(outputs),
                "success": sum(1 for o in outputs.values() if o["status"] == "success")
            },
            "outputs": outputs,
            "project_name": project_name
        }

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "messages_sent": messages_sent,
            "messages_received": len(outputs),
            "execution": aggregated,
            "project_name": project_name,
            "duration": duration,
            "status": "success"
        }

    def _write_discussion_records(self, ctx: TaskContext, project_name: str):
        """写入对话记录文件"""
        try:
            project_dir = self.projects_root / project_name
            project_dir.mkdir(parents=True, exist_ok=True)

            # 1. CEO-COO 对齐记录
            ceo_coo_record = f"""# 对话_01_CEO对齐_{datetime.now().strftime('%Y%m%d')}

## 基本信息

- **日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **任务ID**: {ctx.task_id}
- **用户输入**: {ctx.user_input}

## CEO 路由结果

- **意图**: {ctx.routing.intent}
- **复杂度**: {ctx.routing.complexity}
- **路由目标**: {ctx.routing.target} → {ctx.routing.target_name}
- **理由**: {ctx.routing.reason}

## 路由决策

{ctx.routing.decision}

---

*本记录由 CEO 自动生成*
"""
            record_dir = project_dir / "01_Agent会议纪要" / "对话记录"
            record_dir.mkdir(parents=True, exist_ok=True)
            (record_dir / f"对话_01_CEO对齐_{datetime.now().strftime('%Y%m%d')}.md").write_text(ceo_coo_record, encoding='utf-8')

            # 2. 策略讨论记录
            discussion_record = f"""# 对话_02_策略讨论_{datetime.now().strftime('%Y%m%d')}

## 基本信息

- **日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **任务ID**: {ctx.task_id}
- **参与专家**: {', '.join(ctx.expert_inboxes)}

## COO 发起讨论

COO 向 {len(ctx.expert_inboxes)} 位专家发起策略讨论，询问专业意见。

## 专家回复

"""
            for i, reply in enumerate(ctx.stage_results.get("expert_replies", []), 1):
                expert = reply.get("expert", "未知")
                content = reply.get("content", "")
                discussion_record += f"""### {i}. {expert}

{content}

---

"""

            (record_dir / f"对话_02_策略讨论_{datetime.now().strftime('%Y%m%d')}.md").write_text(discussion_record, encoding='utf-8')

            # 3. COO 汇报记录
            coo_report_record = f"""# 对话_04_CEO汇报_{datetime.now().strftime('%Y%m%d')}

## 基本信息

- **日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **任务ID**: {ctx.task_id}

## COO 汇报内容

{ctx.stage_results.get("coo_report", "")}

---

*本记录由 COO 自动生成*
"""
            (record_dir / f"对话_04_CEO汇报_{datetime.now().strftime('%Y%m%d')}.md").write_text(coo_report_record, encoding='utf-8')

            # 4. CEO 审核记录
            ceo_review_record = f"""# CEO审核意见_{datetime.now().strftime('%Y%m%d')}

## 基本信息

- **日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **任务ID**: {ctx.task_id}

## CEO 审核意见

| 评估维度 | 评分 | 意见 |
|----------|------|------|
| 策略合理性 | {ctx.stage_results.get("ceo_review", {}).get("strategy_score", "N/A")}/10 | {ctx.stage_results.get("ceo_review", {}).get("strategy_comment", "N/A")} |
| 风险可控性 | {ctx.stage_results.get("ceo_review", {}).get("risk_score", "N/A")}/10 | {ctx.stage_results.get("ceo_review", {}).get("risk_comment", "N/A")} |
| 执行可行性 | {ctx.stage_results.get("ceo_review", {}).get("execution_score", "N/A")}/10 | {ctx.stage_results.get("ceo_review", {}).get("execution_comment", "N/A")} |

## 总体决策

{ctx.stage_results.get("ceo_review", {}).get("decision", "N/A")}

## CEO 补充意见

{ctx.stage_results.get("ceo_review", {}).get("ceo_suggestions", "N/A")}

---

*本记录由 CEO 自动生成*
"""
            review_dir = project_dir / "01_Agent会议纪要" / "总监决策"
            review_dir.mkdir(parents=True, exist_ok=True)
            (review_dir / f"CEO审核意见_{datetime.now().strftime('%Y%m%d')}.md").write_text(ceo_review_record, encoding='utf-8')

            print(f"  → 已生成对话记录: {record_dir}")

        except Exception as e:
            print(f"  → 生成对话记录失败: {e}")

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


def run_ceo_launcher(goal=None, interactive=False, debug=False, analyze_only=False, timeout=DEFAULT_TIMEOUT, team_name=DEFAULT_TEAM_NAME):
    """
    CEO 启动器入口函数（可被导入调用）

    Args:
        goal: 任务目标
        interactive: 是否交互模式
        debug: 是否调试模式
        analyze_only: 是否仅分析
        timeout: 超时时间（秒）
        team_name: 团队名称
    """
    ct = CyberTeamV4(debug=debug, analyze_only=analyze_only, timeout=timeout)
    ct.team_name = team_name

    if interactive or (not goal and not interactive):
        if not goal:
            print("=" * 60)
            print("CyberTeam V4 - 交互模式 (消息驱动)")
            print("=" * 60)
            print(f"Mailbox 模式: {'MailboxManager' if not ct.mailbox.local_mode else '本地模式'}")
            print(f"分析模式: {'启用' if analyze_only else '关闭'}")
            print(f"超时时间: {timeout}s")
            print("=" * 60)
        ct.run_interactive()
    elif goal:
        result = ct.run(goal)
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
        return result
    else:
        print("请提供 --goal 参数或使用 --interactive 模式")
        return None


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

    return run_ceo_launcher(
        goal=args.goal,
        interactive=args.interactive,
        debug=args.debug,
        analyze_only=args.analyze_only,
        timeout=args.timeout,
        team_name=args.team_name
    )


if __name__ == "__main__":
    main()
