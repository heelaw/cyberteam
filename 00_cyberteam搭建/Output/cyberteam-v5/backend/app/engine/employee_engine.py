"""
数字员工引擎

核心能力：
1. 数字员工生命周期管理
2. 任务执行与调度
3. 工具加载与执行
4. 状态管理与监控

基于 Magic 的 agentlang 框架设计
"""
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional
import asyncio
import logging

from app.integration.claude_cli import ClaudeCLI, ClaudeConfig, DigitalEmployee as ClaudeDigitalEmployee

logger = logging.getLogger(__name__)


@dataclass
class DigitalEmployeeConfig:
    """数字员工配置"""
    id: str
    name: str
    role: str
    department_id: str = ""  # 所属部门ID
    department_code: str = ""  # 部门代码
    description: str = ""
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    system_prompt: str = ""
    model: str = "opus"
    max_steps: int = 100


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    employee_id: str
    status: str  # success, failed, running
    content: str
    tools_used: list[str] = field(default_factory=list)
    error: Optional[str] = None
    duration: float = 0


class DigitalEmployee:
    """
    数字员工

    基于 Claude CLI 的智能体，具备：
    - 角色定义
    - 技能绑定
    - 工具权限
    - 任务执行
    """

    def __init__(self, config: DigitalEmployeeConfig):
        self.config = config
        self.cli = ClaudeCLI(ClaudeConfig(model=config.model))
        self.current_task: Optional[str] = None
        self.status = "idle"  # idle, running, paused, done

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        prompt = self.config.system_prompt or f"""你是一个专业的 {self.config.role}。

你的名字是 {self.config.name}。
你的职责是 {self.config.description}。
"""

        if self.config.skills:
            prompt += f"\n\n【专业技能】\n" + "\n".join(
                f"- {skill}" for skill in self.config.skills
            )

        if self.config.tools:
            prompt += f"\n\n【可用工具】\n你可以使用以下工具来完成任务: {', '.join(self.config.tools)}"

        return prompt

    async def execute(self, task: str) -> AsyncIterator[str]:
        """执行任务（流式输出）"""
        self.status = "running"
        self.current_task = task

        try:
            # 构建完整提示词
            full_prompt = self._build_system_prompt() + f"\n\n【任务】\n{task}"

            # 直接调用，返回结果
            result = self.cli.run(full_prompt)
            yield result

            self.status = "done"

        except Exception as e:
            self.status = "error"
            logger.error(f"Employee {self.config.name} error: {e}")
            yield f"\n\n[错误: {str(e)}]"

        finally:
            self.current_task = None


class EmployeeRegistry:
    """
    数字员工注册表

    管理所有可用的数字员工
    """

    def __init__(self):
        self.employees: dict[str, DigitalEmployee] = {}
        self._templates: dict[str, DigitalEmployeeConfig] = {}

    def register(self, config: DigitalEmployeeConfig):
        """注册数字员工"""
        employee = DigitalEmployee(config)
        self.employees[config.id] = employee
        logger.info(f"Registered employee: {config.name} ({config.id})")

    def register_template(self, config: DigitalEmployeeConfig):
        """注册员工模板"""
        self._templates[config.id] = config

    def get(self, employee_id: str) -> Optional[DigitalEmployee]:
        """获取数字员工"""
        return self.employees.get(employee_id)

    def list_all(self) -> list[DigitalEmployeeConfig]:
        """列出所有数字员工"""
        return [
            emp.config for emp in self.employees.values()
        ]

    def list_templates(self) -> list[DigitalEmployeeConfig]:
        """列出员工模板"""
        return list(self._templates.values())

    def create_from_template(self, template_id: str, employee_id: str, name: str) -> DigitalEmployee:
        """从模板创建员工"""
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        config = DigitalEmployeeConfig(
            id=employee_id,
            name=name,
            role=template.role,
            description=template.description,
            skills=template.skills.copy(),
            tools=template.tools.copy(),
            system_prompt=template.system_prompt,
            model=template.model
        )

        self.register(config)
        return self.employees[employee_id]


class TaskQueue:
    """
    任务队列

    管理任务分发和执行
    """

    def __init__(self, registry: EmployeeRegistry):
        self.registry = registry
        self.running_tasks: dict[str, DigitalEmployee] = {}
        self.task_history: list[TaskResult] = []

    async def dispatch(
        self,
        task: str,
        employee_id: str,
        task_id: str = None
    ) -> str:
        """分发任务到数字员工"""
        employee = self.registry.get(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")

        task_id = task_id or f"task_{asyncio.get_event_loop().time()}"
        self.running_tasks[task_id] = employee

        # 执行任务
        result = TaskResult(
            task_id=task_id,
            employee_id=employee_id,
            status="running",
            content=""
        )

        try:
            content_parts = []
            async for chunk in employee.execute(task):
                content_parts.append(chunk)
                result.content = ''.join(content_parts)

            result.status = "success"

        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            logger.error(f"Task {task_id} failed: {e}")

        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            self.task_history.append(result)

        return task_id

    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """获取任务状态"""
        for task in self.task_history:
            if task.task_id == task_id:
                return task
        return None


class EmployeeMarketplace:
    """
    数字员工市场

    提供员工模板和创建功能
    """

    def __init__(self):
        self.registry = EmployeeRegistry()
        self.task_queue = TaskQueue(self.registry)
        self._init_default_templates()

    def _init_default_templates(self):
        """初始化默认员工模板"""
        templates = [
            DigitalEmployeeConfig(
                id="ceo",
                name="CEO",
                role="首席执行官",
                department_id="dept_ceo",
                department_code="ceo",
                description="负责战略决策和团队协调",
                skills=["战略规划", "团队管理", "决策分析"],
                system_prompt="""你是一个经验丰富的CEO，擅长战略规划和决策。

你的工作方式：
1. 将复杂问题拆解为可执行的任务
2. 协调各部门资源
3. 确保执行质量

当用户提出任务时，你首先进行5W1H分析，然后制定执行计划。"""
            ),
            DigitalEmployeeConfig(
                id="coo",
                name="COO",
                role="首席运营官",
                department_id="dept_coo",
                department_code="coo",
                description="负责运营管理和流程优化",
                skills=["运营管理", "流程优化", "资源调度"],
                system_prompt="""你是一个专业的COO，擅长运营管理和流程优化。

你的工作方式：
1. 分析运营问题
2. 制定优化方案
3. 协调执行团队"""
            ),
            DigitalEmployeeConfig(
                id="product",
                name="产品总监",
                role="产品管理",
                department_id="dept_product",
                department_code="product",
                description="负责产品规划和需求分析",
                skills=["需求分析", "产品规划", "用户体验"],
                system_prompt="""你是一个专业的产品总监，擅长需求分析和产品规划。

你的工作方式：
1. 理解用户需求
2. 制定产品方案
3. 跟踪产品迭代"""
            ),
            DigitalEmployeeConfig(
                id="tech",
                name="技术总监",
                role="技术开发",
                department_id="dept_tech",
                department_code="tech",
                description="负责技术架构和开发管理",
                skills=["架构设计", "代码审查", "技术选型"],
                system_prompt="""你是一个专业的技术总监，擅长架构设计和技术决策。

你的工作方式：
1. 分析技术需求
2. 设计系统架构
3. 指导开发实施"""
            ),
            DigitalEmployeeConfig(
                id="growth",
                name="增长总监",
                role="增长营销",
                department_id="dept_growth",
                department_code="growth",
                description="负责用户增长和营销策略",
                skills=["用户增长", "营销策略", "数据分析"],
                system_prompt="""你是一个专业的增长总监，擅长用户增长和营销策略。

你的工作方式：
1. 分析增长机会
2. 制定营销策略
3. 优化转化漏斗"""
            ),
            DigitalEmployeeConfig(
                id="finance",
                name="财务总监",
                role="财务管理",
                department_id="dept_finance",
                department_code="finance",
                description="负责财务管理和预算控制",
                skills=["预算管理", "成本控制", "财务分析"],
                system_prompt="""你是一个专业的财务总监，擅长财务分析和预算管理。

你的工作方式：
1. 分析财务数据
2. 制定预算方案
3. 控制成本风险"""
            ),
            DigitalEmployeeConfig(
                id="hr",
                name="HR总监",
                role="人力资源",
                department_id="dept_hr",
                department_code="hr",
                description="负责人才招聘和团队建设",
                skills=["招聘", "培训", "绩效考核"],
                system_prompt="""你是一个专业的HR总监，擅长人才招聘和团队建设。

你的工作方式：
1. 分析人才需求
2. 制定招聘策略
3. 建设团队文化"""
            ),
        ]

        for template in templates:
            self.registry.register_template(template)

    async def create_employee(
        self,
        template_id: str,
        name: str = None
    ) -> DigitalEmployee:
        """创建数字员工"""
        employee_id = f"emp_{template_id}_{asyncio.get_event_loop().time()}"
        template = self.registry._templates.get(template_id)
        name = name or (template.name if template else "未知员工")

        return self.registry.create_from_template(
            template_id=template_id,
            employee_id=employee_id,
            name=name
        )

    async def execute_task(
        self,
        task: str,
        employee_id: str = None,
        template_id: str = None
    ) -> str:
        """执行任务"""
        if employee_id:
            return await self.task_queue.dispatch(task, employee_id)
        elif template_id:
            # 自动创建员工并执行
            emp = await self.create_employee(template_id)
            return await self.task_queue.dispatch(task, emp.config.id)
        else:
            # 使用默认 CEO
            emp = await self.create_employee("ceo")
            return await self.task_queue.dispatch(task, emp.config.id)
