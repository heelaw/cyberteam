# Q64: ExpertAgent协议设计 —— 思考天团执行层核心组件

**问题**: 设计思考天团专家Agent的标准化调用协议

**背景**: 审查报告指出缺少Transport层、TaskStore、Workspace隔离

**参考**: ClawTeam Agent协议设计

---

## 一、ExpertAgent协议概述

### 1.1 协议定位

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ExpertAgent协议在系统中的位置                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                        用户界面层                                      │  │
│   │   CLI / Web看板 / API                                               │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    ExpertAgentProtocol Layer                          │  │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │  │
│   │   │ TaskStore   │  │  Workspace  │  │  Transport  │                │  │
│   │   │ 任务存储    │  │   隔离      │  │   消息层    │                │  │
│   │   └─────────────┘  └─────────────┘  └─────────────┘                │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                 │
│              ▼                     ▼                     ▼                  │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │
│   │  主持人Agent    │   │   专家Agent池    │   │   外部系统      │       │
│   │  (Orchestrator)│   │ (Expert Agents) │   │ (API/CLI)       │       │
│   └─────────────────┘   └─────────────────┘   └─────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

| 组件 | 功能 | 类比ClawTeam |
|------|------|---------------|
| **TaskStore** | 任务持久化存储 | ClawTeam的tasks.json |
| **Workspace** | Agent工作空间隔离 | ClawTeam的teams/{team}/ |
| **Transport** | Agent间消息传递 | ClawTeam的MailboxManager |
| **ExpertAgent** | 专家Agent实例 | ClawTeam的Agent |

---

## 二、ExpertAgent协议格式

### 2.1 消息格式 (ExpertMessage)

```python
# 定义文件: expert_agent_protocol/messages.py

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional, Any, Dict, List

class MessageType(str, Enum):
    """消息类型枚举"""
    TASK_REQUEST = "task_request"        # 任务请求
    TASK_RESPONSE = "task_response"      # 任务响应
    PROGRESS_UPDATE = "progress_update"  # 进度更新
    STATUS_CHANGE = "status_change"      # 状态变更
    HEARTBEAT = "heartbeat"              # 心跳保活
    ERROR_REPORT = "error_report"        # 错误报告
    RESULT_SUBMISSION = "result_submission"  # 结果提交

class ExpertMessage(BaseModel):
    """ExpertAgent协议消息基类"""

    # 消息标识
    msg_id: str = Field(..., description="全局唯一消息ID")
    msg_type: MessageType = Field(..., description="消息类型")
    timestamp: datetime = Field(default_factory=datetime.now)

    # 发送方信息
    sender: str = Field(..., description="发送方Agent名称")
    sender_role: str = Field(..., description="发送方角色: host/expert/system")

    # 接收方信息
    recipient: Optional[str] = Field(None, description="接收方Agent名称，广播时为空")
    broadcast: bool = Field(False, description="是否为广播消息")

    # 任务关联
    task_id: Optional[str] = Field(None, description="关联的任务ID")
    parent_msg_id: Optional[str] = Field(None, description="父消息ID，用于消息链追踪")

    # 消息内容
    content: Dict[str, Any] = Field(default_factory=dict)

    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskRequest(BaseModel):
    """任务请求消息内容"""

    # 任务定义
    task_id: str
    task_type: str  # "analysis", "debate", "chain", "coordination"
    question: str
    context: Dict[str, Any] = {}

    # 执行参数
    mode: str = "parallel"  # "parallel", "sequential", "debate"
    timeout_seconds: int = 3600
    max_retries: int = 3

    # 专家指定
    required_experts: List[str] = []  # 指定需要的专家
    exclude_experts: List[str] = []   # 排除的专家

    # 约束条件
    constraints: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    """任务响应消息内容"""

    task_id: str
    status: str  # "success", "failed", "partial"

    # 输出内容
    output: Dict[str, Any] = {}
    artifacts: List[Dict[str, Any]] = []  # 产出物列表

    # 执行信息
    duration_seconds: float
    tokens_used: int = 0
    model: str

    # 质量评估
    confidence: float = 1.0  # 0-1
    quality_notes: str = ""
```

### 2.2 任务状态格式 (ExpertTask)

```python
# 定义文件: expert_agent_protocol/task.py

import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    """任务状态枚举"""
    CREATED = "created"           # 已创建
    QUEUED = "queued"             # 已入队
    RUNNING = "running"           # 执行中
    WAITING_DEPS = "waiting_deps" # 等待依赖
    PAUSED = "paused"             # 已暂停
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"      # 已取消

class ExpertTask(BaseModel):
    """ExpertAgent任务模型"""

    # 核心标识
    task_id: str = Field(..., description="全局唯一任务ID")
    question_id: str = Field(..., description="关联的问题ID")

    # 任务定义
    title: str
    description: str
    task_type: str

    # 状态管理
    status: TaskStatus = TaskStatus.CREATED
    progress: int = Field(0, ge=0, le=100)

    # 执行信息
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 专家分配
    assigned_experts: List[str] = []
    running_experts: List[str] = []
    completed_experts: List[str] = []

    # 依赖管理
    depends_on: List[str] = []  # 依赖的任务ID列表
    blocking: List[str] = []    # 被阻塞的任务ID列表

    # 输出
    output: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = []

    # 资源限制
    max_duration_seconds: int = 3600
    max_retries: int = 3
    retry_count: int = 0

class TaskStore:
    """任务存储接口 - 基于JSON文件的任务持久化"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._ensure_dir(self.storage_path)

    def _ensure_dir(self, path: Path):
        """确保目录存在"""
        path.mkdir(parents=True, exist_ok=True)

    def _task_file(self, task_id: str) -> Path:
        """获取任务文件路径"""
        return self.storage_path / f"{task_id}.json"

    def create_task(self, task: ExpertTask) -> ExpertTask:
        """创建任务"""
        task_file = self._task_file(task.task_id)
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task.model_dump(), f, ensure_ascii=False, indent=2)
        return task

    def get_task(self, task_id: str) -> Optional[ExpertTask]:
        """获取任务"""
        task_file = self._task_file(task_id)
        if not task_file.exists():
            return None
        with open(task_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ExpertTask(**data)

    def update_task(self, task: ExpertTask) -> ExpertTask:
        """更新任务"""
        return self.create_task(task)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[ExpertTask]:
        """列出任务"""
        tasks = []
        for task_file in self.storage_path.glob("*.json"):
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            task = ExpertTask(**data)
            if status is None or task.status == status:
                tasks.append(task)
        return tasks

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        task_file = self._task_file(task_id)
        if task_file.exists():
            task_file.unlink()
            return True
        return False

    def get_task_dependencies(self, task_id: str) -> List[ExpertTask]:
        """获取任务依赖链"""
        task = self.get_task(task_id)
        if not task:
            return []
        dependencies = []
        for dep_id in task.depends_on:
            dep_task = self.get_task(dep_id)
            if dep_task:
                dependencies.append(dep_task)
        return dependencies
```

### 2.3 Agent实例格式 (ExpertAgentInstance)

```python
# 定义文件: expert_agent_protocol/agent.py

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

class AgentStatus(str, Enum):
    """Agent实例状态"""
    IDLE = "idle"           # 空闲
    INITIALIZING = "initializing"  # 初始化中
    RUNNING = "running"     # 运行中
    THINKING = "thinking"   # 思考中（等待LLM响应）
    WAITING = "waiting"     # 等待（阻塞/依赖）
    COMPLETED = "completed" # 已完成当前任务
    FAILED = "failed"      # 失败
    TERMINATED = "terminated"  # 已终止

class ExpertAgentInstance(BaseModel):
    """ExpertAgent实例模型"""

    # 实例标识
    instance_id: str = Field(..., description="实例唯一ID")
    expert_name: str = Field(..., description="专家名称，如kahneman, first_principle")
    expert_version: str = Field(default="1.0.0")

    # 任务关联
    current_task_id: Optional[str] = None
    task_history: List[str] = []  # 历史任务ID

    # 状态管理
    status: AgentStatus = AgentStatus.IDLE
    progress: int = Field(0, ge=0, le=100)

    # 执行信息
    started_at: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 资源使用
    tokens_used: int = 0
    api_calls: int = 0

    # 输出
    current_output: Dict[str, Any] = Field(default_factory=dict)

    # 错误追踪
    error_count: int = 0
    last_error: Optional[str] = None

class Workspace(BaseModel):
    """Agent工作空间隔离"""

    workspace_id: str
    task_id: str
    root_path: str

    # 工作空间隔离
    isolated: bool = True
    clean_on_start: bool = True

    # 文件隔离
    input_files: List[str] = []
    output_files: List[str] = []

    # 环境变量
    env_vars: Dict[str, str] = {}
```

---

## 三、Transport层设计

### 3.1 Transport架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Transport层架构                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │                      ExpertMailboxManager                          │   │
│   │                                                                    │   │
│   │  - 消息序列化/反序列化                                              │   │
│   │  - 消息队列管理                                                    │   │
│   │  - 委托给Transport                                                │   │
│   └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │                    ExpertTransport (ABC)                           │   │
│   │                                                                    │   │
│   │  deliver(recipient, message)    投递消息                          │   │
│   │  fetch(agent, limit, consume)   获取消息                          │   │
│   │  count(agent)                   未读计数                          │   │
│   │  broadcast(message)             广播消息                           │   │
│   │  list_agents()                  列出所有Agent                     │   │
│   └───────────────────────────────────────────────────────────────────┘   │
│                          │                    │                             │
│           ┌─────────────┴─────────────┐     │                             │
│           ▼                           ▼     ▼                             │
│   ┌─────────────────┐       ┌─────────────────┐                           │
│   │ FileTransport   │       │  ZMQTransport   │  (可选)                    │
│   │                 │       │                 │                            │
│   │ 基于文件系统    │       │ 基于ZMQ P2P     │                            │
│   │ 实现消息传递    │       │ 实现实时通信    │                            │
│   │                │       │                 │                            │
│   │ 离线存储兜底   │       │ +FileTransport  │                            │
│   │                │       │  作为离线兜底   │                            │
│   └─────────────────┘       └─────────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Transport接口定义

```python
# 定义文件: expert_agent_protocol/transport.py

from abc import ABC, abstractmethod
from typing import List, Optional
from .messages import ExpertMessage

class ExpertTransport(ABC):
    """ExpertAgent消息传输抽象层"""

    @abstractmethod
    def deliver(self, recipient: str, message: ExpertMessage) -> bool:
        """投递消息到指定接收方"""
        pass

    @abstractmethod
    def fetch(self, agent: str, limit: int = 10, consume: bool = True) -> List[ExpertMessage]:
        """获取消息"""
        pass

    @abstractmethod
    def count(self, agent: str) -> int:
        """获取未读消息数量"""
        pass

    @abstractmethod
    def broadcast(self, message: ExpertMessage, exclude: List[str] = None) -> int:
        """广播消息"""
        pass

    @abstractmethod
    def list_agents(self) -> List[str]:
        """列出所有可通信的Agent"""
        pass

    @abstractmethod
    def close(self):
        """关闭传输层"""
        pass

class FileTransport(ExpertTransport):
    """基于文件系统的Transport实现"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self._ensure_dir(self.workspace_root)

    def _ensure_dir(self, path: Path):
        """确保目录存在"""
        path.mkdir(parents=True, exist_ok=True)

    def _inbox_path(self, agent: str) -> Path:
        """获取agent的inbox目录"""
        return self.workspace_root / "messages" / agent / "inbox"

    def _outbox_path(self, agent: str) -> Path:
        """获取agent的outbox目录"""
        return self.workspace_root / "messages" / agent / "outbox"

    def deliver(self, recipient: str, message: ExpertMessage) -> bool:
        """写入消息到接收方的inbox"""
        try:
            inbox = self._inbox_path(recipient)
            self._ensure_dir(inbox)
            msg_file = inbox / f"{message.msg_id}.json"
            with open(msg_file, 'w', encoding='utf-8') as f:
                json.dump(message.model_dump(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to deliver message to {recipient}: {e}")
            return False

    def fetch(self, agent: str, limit: int = 10, consume: bool = True) -> List[ExpertMessage]:
        """读取inbox中的消息"""
        inbox = self._inbox_path(agent)
        if not inbox.exists():
            return []
        messages = []
        for msg_file in sorted(inbox.glob("*.json"))[:limit]:
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            messages.append(ExpertMessage(**data))
            if consume:
                msg_file.unlink()  # 消费后删除
        return messages

    def count(self, agent: str) -> int:
        """统计未读消息"""
        inbox = self._inbox_path(agent)
        if not inbox.exists():
            return 0
        return len(list(inbox.glob("*.json")))

    def broadcast(self, message: ExpertMessage, exclude: List[str] = None) -> int:
        """广播消息到所有Agent"""
        exclude = exclude or []
        agents = [a for a in self.list_agents() if a not in exclude]
        count = 0
        for agent in agents:
            if self.deliver(agent, message):
                count += 1
        return count

    def list_agents(self) -> List[str]:
        """列出所有Agent目录"""
        messages_dir = self.workspace_root / "messages"
        if not messages_dir.exists():
            return []
        return [d.name for d in messages_dir.iterdir() if d.is_dir()]

class ZMQTransport(ExpertTransport):
    """基于ZMQ P2P的Transport实现"""

    def __init__(self, bind_address: str = "tcp://127.0.0.1:*"):
        self.bind_address = bind_address
        self._context = None
        self._socket = None
        self._file_transport = None  # 离线存储兜底
        self._connected = False

    def _ensure_connected(self):
        """确保ZMQ连接已建立"""
        if self._connected:
            return
        try:
            import zmq
            self._context = zmq.Context()
            self._socket = self._context.socket(zmq.PUB)
            self._socket.bind(self.bind_address)
            # 同时初始化 FileTransport 作为离线兜底
            self._file_transport = FileTransport(
                str(Path.home() / "thinking-team" / "workspace"))
            self._connected = True
        except ImportError:
            logger.warning("zmq not installed, falling back to FileTransport")
            self._file_transport = FileTransport(
                str(Path.home() / "thinking-team" / "workspace"))
            self._connected = True

    def deliver(self, recipient: str, message: ExpertMessage) -> bool:
        """通过ZMQ发送消息"""
        try:
            self._ensure_connected()
            if self._socket:
                # ZMQ 发送
                import zmq
                msg_data = json.dumps(message.model_dump()).encode('utf-8')
                self._socket.send_multipart([recipient.encode('utf-8'), msg_data])
                return True
        except Exception as e:
            logger.error(f"ZMQ deliver failed: {e}, falling back to file")
        # 回退到 FileTransport
        if self._file_transport:
            return self._file_transport.deliver(recipient, message)
        return False

    def fetch(self, agent: str, limit: int = 10, consume: bool = True) -> List[ExpertMessage]:
        """接收ZMQ消息"""
        # ZMQ Fetch 通常由订阅者主动接收
        # 此处使用 FileTransport 作为消息缓存的读取接口
        if self._file_transport:
            return self._file_transport.fetch(agent, limit, consume)
        return []

    def close(self):
        """关闭传输层"""
        if self._socket:
            self._socket.close()
        if self._context:
            self._context.term()
        self._connected = False
```

### 3.3 文件存储结构

```
workspace/tasks/{task_id}/
# P1修正: 遵循 Q69 统一存储规范，根路径为 thinking-team/
├── task.json                      # 任务主文件
├── metadata.json                  # 任务元数据
│
├── inbox/                        # 接收消息
│   ├── host/                     # 来自主持人的消息
│   │   ├── msg-001.json
│   │   └── msg-002.json
│   └── {expert_name}/            # 来自其他专家的消息
│       ├── msg-001.json
│       └── msg-002.json
│
├── outbox/                       # 发送消息
│   ├── host/
│   │   └── msg-001.json
│   └── {expert_name}/
│       └── msg-001.json
│
├── tasks/                        # 子任务（每个专家一个子任务）
│   ├── kahneman/
│   │   ├── task.json            # 子任务状态
│   │   ├── output.md            # 专家输出
│   │   └── logs/
│   │       └── execution.log
│   ├── first_principle/
│   │   └── ...
│   └── ...
│
├── artifacts/                   # 产出物
│   ├── reports/
│   │   └── final_report.md
│   └── data/
│       └── structured_output.json
│
└── board.json                    # 看板状态（实时更新）
```

---

## 四、与ClawTeam集成策略

### 4.1 集成模式选择

| 集成方式 | 优点 | 缺点 | 适用场景 |
|----------|------|------|----------|
| **复用ClawTeam** | 功能完整，开箱即用 | 需学习ClawTeam CLI | 新项目启动 |
| **适配器模式** | 保持现有架构，渐进迁移 | 需要维护适配层 | 现有系统迁移 |
| **参考设计** | 完全自主可控 | 需从头实现 | 深度定制需求 |

**推荐**: 适配器模式 - 复用ClawTeam的核心概念，通过适配器接入

### 4.2 适配器实现

```python
# 定义文件: expert_agent_protocol/adapters/cyberteam_adapter.py

from ..transport import ExpertTransport, ExpertMessage
from ..messages import MessageType
from .cyberteam_bridge import ClawTeamBridge

class ClawTeamAdapter(ExpertTransport):
    """ClawTeam适配器 - 将ExpertAgent协议转换为ClawTeam消息"""

    def __init__(self, cyberteam_config: dict):
        self.bridge = ClawTeamBridge(cyberteam_config)
        self._local_cache = {}  # 本地消息缓存

    def deliver(self, recipient: str, message: ExpertMessage) -> bool:
        """转换为ClawTeam消息格式并发送"""

        # ExpertMessage → ClawTeam TeamMessage
        ct_message = self._to_cyberteam_message(message)

        # 通过ClawTeam发送
        return self.bridge.send(recipient, ct_message)

    def fetch(self, agent: str, limit: int = 10, consume: bool = True) -> List[ExpertMessage]:
        """获取ClawTeam消息并转换为ExpertMessage"""

        ct_messages = self.bridge.receive(agent, limit, consume)

        # ClawTeam TeamMessage → ExpertMessage
        return [self._from_cyberteam_message(m) for m in ct_messages]

    def _to_cyberteam_message(self, msg: ExpertMessage) -> dict:
        """转换为ClawTeam消息格式"""
        return {
            "id": msg.msg_id,
            "type": msg.msg_type.value,
            "sender": msg.sender,
            "recipient": msg.recipient,
            "payload": msg.content,
            "metadata": msg.metadata,
        }

    def _from_cyberteam_message(self, ct_msg: dict) -> ExpertMessage:
        """从ClawTeam消息转换"""
        return ExpertMessage(
            msg_id=ct_msg["id"],
            msg_type=MessageType(ct_msg["type"]),
            sender=ct_msg["sender"],
            recipient=ct_msg.get("recipient"),
            content=ct_msg.get("payload", {}),
            metadata=ct_msg.get("metadata", {}),
        )
```

### 4.3 兼容层设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         兼容层架构设计                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   思考天团系统                                                              │
│   │                                                                         │
│   │  ┌─────────────────────────────────────────────────────────────────┐   │
│   │  │                  ExpertAgentProtocol Layer                      │   │
│   │  │                                                                  │   │
│   │  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│   │  │   │  TaskStore   │  │  Workspace   │  │  Transport   │       │   │
│   │  │   │              │  │              │  │              │       │   │
│   │  │   │  (JSON文件)  │  │  (目录隔离)  │  │  (可切换)   │       │   │
│   │  │   └──────────────┘  └──────────────┘  └──────────────┘       │   │
│   │  └─────────────────────────────────────────────────────────────────┘   │
│   │                                    │                                    │
│   │              ┌─────────────────────┼─────────────────────┐             │
│   │              │                     │                     │              │
│   │              ▼                     ▼                     ▼              │
│   │   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐  │
│   │   │  FileTransport  │   │  ZMQTransport   │   │ ClawTeamAdapter │  │
│   │   │  (默认实现)     │   │   (可选)        │   │   (可选)        │  │
│   │   └─────────────────┘   └─────────────────┘   └─────────────────┘  │
│   │                                                                         │
└───┼─────────────────────────────────────────────────────────────────────────┘
    │
    │ 配置切换
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│   配置文件: expert_agent_config.toml                                        │
│                                                                             │
│   # 默认: 使用本地文件系统                                                  │
│   [transport]                                                               │
│   type = "file"                                                             │
│   workspace_root = "./workspace"                                            │
│                                                                             │
│   # 可选: 使用ClawTeam                                                     │
│   # [transport]                                                             │
│   # type = "cyberteam"                                                       │
│   # cyberteam_path = "/path/to/cyberteam"                                     │
│   # team_name = "thinking-team"                                            │
│                                                                             │
│   # 可选: 使用ZMQ实时通信                                                  │
│   # [transport]                                                             │
│   # type = "zmq"                                                            │
│   # bind_address = "tcp://127.0.0.1:5555"                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 五、任务状态追踪机制

### 5.1 任务状态机

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          任务状态机                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│      ┌─────────┐      分发任务       ┌─────────┐                          │
│      │ CREATED │ ─────────────────▶ │ QUEUED  │                          │
│      └─────────┘                    └────┬────┘                          │
│                                          │                                 │
│                         ┌─────────────────┼─────────────────┐              │
│                         ▼                 ▼                 ▼               │
│                  ┌─────────┐       ┌─────────┐       ┌─────────┐          │
│           依赖满足 │ RUNNING │       │ WAITING │       │ PAUSED │          │
│           ──────▶ │         │ ◀──── │   DEPS  │       │         │          │
│                  └────┬────┘       └─────────┘       └─────────┘          │
│                       │                                                  │
│          ┌────────────┼────────────┐                                     │
│          ▼            ▼            ▼                                     │
│   ┌───────────┐ ┌───────────┐ ┌───────────┐                              │
│   │COMPLETED  │ │ FAILED    │ │ CANCELLED │                              │
│   │  成功完成  │ │  执行失败  │ │  用户取消  │                              │
│   └───────────┘ └───────────┘ └───────────┘                              │
│                                                                             │
│   状态转移规则:                                                             │
│   - CREATED → QUEUED: 任务被主持人分发                                      │
│   - QUEUED → RUNNING: 任务开始执行                                         │
│   - RUNNING → WAITING_DEPS: 等待依赖任务完成                               │
│   - RUNNING → PAUSED: 用户/系统暂停                                       │
│   - WAITING_DEPS → RUNNING: 依赖满足                                       │
│   - PAUSED → RUNNING: 恢复执行                                            │
│   - RUNNING → COMPLETED: 成功完成                                          │
│   - RUNNING → FAILED: 执行失败                                             │
│   - ANY → CANCELLED: 用户取消                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 状态追踪实现

```python
# 定义文件: expert_agent_protocol/state_tracker.py

from typing import Dict, List, Optional, Callable
from datetime import datetime
from .task import ExpertTask, TaskStatus, TaskStore
from .messages import ExpertMessage, MessageType

class TaskStateTracker:
    """任务状态追踪器"""

    def __init__(self, task_store: TaskStore):
        self.task_store = task_store
        self._subscribers: Dict[str, List[Callable]] = {}  # 状态变更回调

    def on_status_change(self, task_id: str, callback: Callable):
        """订阅任务状态变更"""
        if task_id not in self._subscribers:
            self._subscribers[task_id] = []
        self._subscribers[task_id].append(callback)

    def transition_status(self, task_id: str, new_status: TaskStatus,
                         reason: str = None) -> ExpertTask:
        """状态转换"""
        task = self.task_store.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        old_status = task.status

        # 验证状态转换合法性
        if not self._is_valid_transition(old_status, new_status):
            raise ValueError(f"Invalid transition: {old_status} → {new_status}")

        # 执行转换
        task.status = new_status
        now = datetime.now()

        if new_status == TaskStatus.RUNNING and old_status != TaskStatus.RUNNING:
            task.started_at = now
        elif new_status == TaskStatus.COMPLETED:
            task.completed_at = now
        elif new_status == TaskStatus.FAILED:
            task.completed_at = now

        # 更新任务
        task = self.task_store.update_task(task)

        # 触发回调
        self._notify_subscribers(task_id, old_status, new_status)

        return task

    def _is_valid_transition(self, from_status: TaskStatus,
                             to_status: TaskStatus) -> bool:
        """验证状态转换是否合法"""
        valid_transitions = {
            TaskStatus.CREATED: [TaskStatus.QUEUED, TaskStatus.CANCELLED],
            TaskStatus.QUEUED: [TaskStatus.RUNNING, TaskStatus.WAITING_DEPS, TaskStatus.CANCELLED],
            TaskStatus.RUNNING: [TaskStatus.COMPLETED, TaskStatus.FAILED,
                               TaskStatus.PAUSED, TaskStatus.WAITING_DEPS, TaskStatus.CANCELLED],
            TaskStatus.WAITING_DEPS: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
            TaskStatus.PAUSED: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
            TaskStatus.COMPLETED: [],
            TaskStatus.FAILED: [TaskStatus.QUEUED, TaskStatus.CANCELLED],  # 可重试
            TaskStatus.CANCELLED: [],
        }
        return to_status in valid_transitions.get(from_status, [])

    def _notify_subscribers(self, task_id: str, old_status: TaskStatus,
                          new_status: TaskStatus):
        """通知订阅者"""
        if task_id in self._subscribers:
            for callback in self._subscribers[task_id]:
                callback(task_id, old_status, new_status)

class TaskDependencyResolver:
    """任务依赖解析器"""

    def __init__(self, task_store: TaskStore):
        self.task_store = task_store

    def resolve_dependencies(self, task_id: str) -> List[str]:
        """解析任务依赖，返回可执行的任务列表"""
        task = self.task_store.get_task(task_id)
        if not task:
            return []

        # 递归检查依赖
        ready_tasks = []
        for dep_id in task.depends_on:
            dep_task = self.task_store.get_task(dep_id)
            if dep_task and dep_task.status == TaskStatus.COMPLETED:
                ready_tasks.append(dep_id)

        return ready_tasks

    def update_blocking(self, task_id: str):
        """更新阻塞关系"""
        task = self.task_store.get_task(task_id)
        if not task or task.status != TaskStatus.COMPLETED:
            return

        # 解除被阻塞任务的阻塞状态
        for blocked_id in task.blocking:
            blocked_task = self.task_store.get_task(blocked_id)
            if blocked_task and blocked_task.status == TaskStatus.WAITING_DEPS:
                # 检查是否还有其他未满足的依赖
                remaining_deps = [
                    d for d in blocked_task.depends_on
                    if self.task_store.get_task(d).status != TaskStatus.COMPLETED
                ]
                if not remaining_deps:
                    # 所有依赖满足，转换为RUNNING
                    pass  # 通过StateTracker转换
```

---

## 六、并行执行实现

### 6.1 并行执行架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         并行执行架构                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     任务调度器 (TaskScheduler)                        │  │
│   │                                                                      │  │
│   │  - 任务队列管理                                                      │  │
│   │  - 资源分配                                                          │  │
│   │  - 并发控制                                                          │  │
│   │  - 负载均衡                                                          │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                 │
│              ▼                     ▼                     ▼                  │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │
│   │   Worker 1     │   │   Worker 2     │   │   Worker N     │       │
│   │                 │   │                 │   │                 │       │
│   │ ExpertAgent实例 │   │ ExpertAgent实例 │   │ ExpertAgent实例 │       │
│   │ kahneman        │   │ first_principle │   │ six_hats        │       │
│   │                 │   │                 │   │                 │       │
│   │ Process (独立)  │   │ Process (独立)  │   │ Process (独立)  │       │
│   └─────────────────┘   └─────────────────┘   └─────────────────┘       │
│                                                                             │
│   每个Worker:                                                               │
│   - 独立的Python进程                                                        │
│   - 独立的工作空间 (thinking-team/workspace/tasks/{task_id}/tasks/{expert}/) # P1修正: Q69规范 │
│   - 通过Transport进行消息通信                                              │
│   - 通过TaskStore共享状态                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 调度器实现

```python
# 定义文件: expert_agent_protocol/scheduler.py

import asyncio
from typing import List, Dict, Optional, Set
from datetime import datetime
from .task import ExpertTask, TaskStatus, TaskStore
from .agent import ExpertAgentInstance, AgentStatus
from .transport import ExpertTransport

class TaskScheduler:
    """任务调度器 - 负责并行执行管理"""

    def __init__(self,
                 task_store: TaskStore,
                 transport: ExpertTransport,
                 max_concurrent: int = 4):
        self.task_store = task_store
        self.transport = transport
        self.max_concurrent = max_concurrent

        self._running_tasks: Dict[str, ExpertTask] = {}
        self._workers: Dict[str, ExpertAgentInstance] = {}
        self._task_queue: asyncio.Queue = asyncio.Queue()

    async def submit_task(self, task: ExpertTask) -> str:
        """提交任务到调度器"""
        # 验证依赖
        if not self._check_dependencies(task):
            task.status = TaskStatus.WAITING_DEPS
        else:
            task.status = TaskStatus.QUEUED

        task = self.task_store.create_task(task)
        await self._task_queue.put(task)
        return task.task_id

    async def _check_dependencies(self, task: ExpertTask) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.depends_on:
            dep_task = self.task_store.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    async def run(self):
        """运行调度器"""
        while True:
            # 获取可执行任务
            while len(self._running_tasks) >= self.max_concurrent:
                await asyncio.sleep(1)

            task = await self._task_queue.get()
            await self._execute_task(task)

    async def _execute_task(self, task: ExpertTask):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        self.task_store.update_task(task)
        self._running_tasks[task.task_id] = task

        try:
            # 启动所有需要的专家Agent
            for expert_name in task.assigned_experts:
                await self._start_expert_agent(task.task_id, expert_name)

            # 等待所有专家完成
            await self._wait_for_completion(task)

            # 任务完成
            task.status = TaskStatus.COMPLETED

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.errors.append(str(e))

        finally:
            self.task_store.update_task(task)
            del self._running_tasks[task.task_id]

    async def _start_expert_agent(self, task_id: str, expert_name: str):
        """启动专家Agent实例"""
        # 创建Agent实例
        instance = ExpertAgentInstance(
            instance_id=f"{task_id}_{expert_name}",
            expert_name=expert_name,
            status=AgentStatus.RUNNING,
            current_task_id=task_id,
        )

        # 分配工作空间
        # P1修正: 遵循 Q69 统一存储规范
        workspace_path = f"thinking-team/workspace/tasks/{task_id}/tasks/{expert_name}"

        # 发送任务请求消息
        from .messages import ExpertMessage, MessageType, TaskRequest

        request_content = TaskRequest(
            task_id=task_id,
            task_type="analysis",
            question="",  # 从主任务获取
            mode="parallel"
        )

        message = ExpertMessage(
            msg_id=f"msg_{task_id}_{expert_name}",
            msg_type=MessageType.TASK_REQUEST,
            sender="host",
            recipient=expert_name,
            task_id=task_id,
            content=request_content.model_dump()
        )

        self.transport.deliver(expert_name, message)

    async def _wait_for_completion(self, task: ExpertTask):
        """等待任务完成"""
        while True:
            # 检查所有专家的状态
            all_completed = True
            for expert_name in task.assigned_experts:
                instance_id = f"{task.task_id}_{expert_name}"
                # 检查ExpertAgent状态
                # ...

                if not self._is_expert_completed(instance_id):
                    all_completed = False

            if all_completed:
                break

            await asyncio.sleep(1)

    def _is_expert_completed(self, instance_id: str) -> bool:
        """检查专家是否完成"""
        # 从TaskStore获取实例状态
        # ...
        return True
```

### 6.3 执行模式支持

```python
# 定义文件: expert_agent_protocol/execution_modes.py

from enum import Enum
from typing import List

class ExecutionMode(str, Enum):
    """执行模式"""
    PARALLEL = "parallel"      # 并行执行
    SEQUENTIAL = "sequential"  # 顺序执行
    DEBATE = "debate"          # 辩论模式
    CHAIN = "chain"            # 链式执行

class ExecutionStrategy:
    """执行策略 - 根据模式分配任务"""

    @staticmethod
    def plan_execution(mode: ExecutionMode,
                      experts: List[str],
                      task_id: str) -> List[List[str]]:
        """规划执行方案"""

        if mode == ExecutionMode.PARALLEL:
            # 所有专家同时执行
            return [experts]

        elif mode == ExecutionMode.SEQUENTIAL:
            # 每个专家依次执行
            return [[e] for e in experts]

        elif mode == ExecutionMode.DEBATE:
            # 辩论模式: 轮流发表观点
            return [[e] for e in experts]  # 每轮一个专家

        elif mode == ExecutionMode.CHAIN:
            # 链式模式: A完成 → B开始
            return [[e] for e in experts]

        return [experts]
```

---

## 七、CLI与API接口

### 7.1 CLI命令

```bash
# ExpertAgent CLI

# 任务管理
expert-agent create --question "如何提升DAU 10%？" --mode parallel
expert-agent status <task_id>
expert-agent list --status running
expert-agent cancel <task_id>
expert-agent retry <task_id>

# 专家管理
expert-agent experts list
expert-agent experts info kahneman

# 消息操作
expert-agent message send kahneman --content "请分析..."
expert-agent message inbox
expert-agent message outbox

# 看板
expert-agent board show <task_id>
expert-agent board watch <task_id>

# 配置
expert-agent config set transport file
expert-agent config set transport zmq --address tcp://127.0.0.1:5555
expert-agent config set transport cyberteam --team thinking-team
```

### 7.2 API接口

```python
# FastAPI 接口定义

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="ExpertAgent Protocol API")

# ========== 任务接口 ==========

@app.post("/api/tasks")
async def create_task(request: CreateTaskRequest):
    """创建任务"""
    pass

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务状态"""
    pass

@app.get("/api/tasks")
async def list_tasks(status: Optional[str] = None):
    """列出任务"""
    pass

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """取消任务"""
    pass

@app.post("/api/tasks/{task_id}/retry")
async def retry_task(task_id: str):
    """重试任务"""
    pass

# ========== 专家接口 ==========

@app.get("/api/experts")
async def list_experts():
    """列出可用专家"""
    pass

@app.get("/api/experts/{expert_name}")
async def get_expert_info(expert_name: str):
    """获取专家信息"""
    pass

@app.get("/api/tasks/{task_id}/experts")
async def get_task_experts(task_id: str):
    """获取任务的专家状态"""
    pass

# ========== 消息接口 ==========

@app.get("/api/agents/{agent_name}/messages")
async def get_messages(agent_name: str, limit: int = 10):
    """获取消息"""
    pass

@app.post("/api/agents/{agent_name}/messages")
async def send_message(agent_name: str, message: MessageRequest):
    """发送消息"""
    pass

# ========== 看板接口 ==========

@app.get("/api/tasks/{task_id}/board")
async def get_board(task_id: str):
    """获取看板状态"""
    pass

@app.websocket("/ws/tasks/{task_id}/board")
async def board_websocket(websocket, task_id: str):
    """看板WebSocket"""
    pass
```

---

## 八、总结

### 8.1 协议核心要素

| 要素 | 定义 |
|------|------|
| **消息格式** | ExpertMessage (JSON序列化的Pydantic模型) |
| **任务存储** | TaskStore + JSON文件 |
| **工作空间** | 每个任务独立目录，任务内专家子目录隔离 |
| **传输层** | 可切换的Transport (File/ZMQ/ClawTeam) |
| **状态追踪** | TaskStateTracker + 状态机 |
| **并行执行** | TaskScheduler + 异步Worker |

### 8.2 与ClawTeam集成策略

- **推荐方式**: 适配器模式
- **配置切换**: 通过`expert_agent_config.toml`指定Transport类型
- **ClawTeam适配器**: 将ExpertMessage转换为ClawTeam消息格式

### 8.3 任务状态追踪

- **状态机**: CREATED → QUEUED → RUNNING → COMPLETED/FAILED
- **依赖管理**: depends_on + blocking 双向关联
- **实时更新**: 通过Transport的消息机制

### 8.4 并行执行

- **最大并发**: 可配置 (默认4)
- **Worker**: 每个ExpertAgent独立进程
- **模式**: 支持PARALLEL/SEQUENTIAL/DEBATE/CHAIN

---

**设计日期**: 2026-03-21

**文档编号**: Q64

**参考文档**:
- Q16: ClawTeam功能分析与融合方案
- Q18: 思考天团系统全景设计报告
- Q60: 异步任务支持设计
- ClawTeam-main/docs/transport-architecture.md
