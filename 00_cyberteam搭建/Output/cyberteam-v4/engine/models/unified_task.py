# engine/models/unified_task.py
"""Unified Task Context - Single source of truth for task lifecycle"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any

# 使用相对导入避免触发 engine/__init__.py
try:
    from engine.models.phase import TaskPhase, TRANSITION_RULES, InvalidTransitionError
    from engine.models.department import Department
except ImportError:
    # fallback for isolated testing
    from pathlib import Path
    import sys
    _parent = Path(__file__).parent.parent
    if str(_parent) not in sys.path:
        sys.path.insert(0, str(_parent))
    from models.phase import TaskPhase, TRANSITION_RULES, InvalidTransitionError
    from models.department import Department


@dataclass
class FlowEntry:
    """Record of a state transition."""

    from_phase: Optional[TaskPhase]
    to_phase: TaskPhase
    reason: str
    triggered_by: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DepartmentResult:
    """Result from department execution."""

    department: Department
    output: str
    status: str  # "success" / "failed" / "blocked"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedTask:
    """
    Unified task context that spans the entire task lifecycle.

    Combines:
    - Execution state (StateMachine)
    - Discussion workflow (COO workflow)
    - Flow log (complete audit trail)
    - Department execution results
    """

    task_id: str
    trace_id: str

    # Identity
    title: str = ""
    description: str = ""
    user_input: str = ""
    priority: str = "normal"  # "low" / "normal" / "high" / "critical"

    # Execution state
    phase: TaskPhase = TaskPhase.INTAKE
    target_department: Optional[Department] = None

    # COO workflow (for tasks that need discussion)
    workflow_phase: str = "layer1"  # "layer1" / "layer2" / "layer3" / "layer4" / "completed"

    # Audit trail
    flow_log: List[FlowEntry] = field(default_factory=list)
    progress_log: List[str] = field(default_factory=list)

    # Department execution results
    department_results: Dict[Department, DepartmentResult] = field(default_factory=dict)

    # Quality
    quality_score: Optional[float] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def add_flow(
        self,
        from_phase: Optional[TaskPhase],
        to_phase: TaskPhase,
        reason: str,
        triggered_by: str,
        metadata: dict = None,
    ) -> None:
        """Add a flow log entry."""
        entry = FlowEntry(
            from_phase=from_phase,
            to_phase=to_phase,
            reason=reason,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )
        self.flow_log.append(entry)
        self.updated_at = datetime.now()

    def transition_to(self, new_phase: TaskPhase, reason: str, triggered_by: str) -> None:
        """
        Transition to a new phase with validation.

        Raises:
            InvalidTransitionError: If the transition is not allowed.
        """
        if not self.can_transition_to(new_phase):
            raise InvalidTransitionError(
                f"Cannot transition from {self.phase.value} to {new_phase.value}"
            )
        self.add_flow(self.phase, new_phase, reason, triggered_by)
        self.phase = new_phase
        self.updated_at = datetime.now()

        if new_phase in {TaskPhase.DONE, TaskPhase.CANCELLED, TaskPhase.FAILED, TaskPhase.TIMEOUT}:
            self.completed_at = datetime.now()

    def can_transition_to(self, target: TaskPhase) -> bool:
        """Check if transition to target phase is allowed."""
        allowed = TRANSITION_RULES.get(self.phase, set())
        return target in allowed

    def is_terminal(self) -> bool:
        """Check if current phase is a terminal state."""
        return self.phase in {TaskPhase.DONE, TaskPhase.CANCELLED, TaskPhase.FAILED, TaskPhase.TIMEOUT}

    def assign_department(self, department: Department) -> None:
        """Assign task to a department."""
        self.target_department = department
        self.updated_at = datetime.now()

    def record_department_result(self, result: DepartmentResult) -> None:
        """Record the result of department execution."""
        self.department_results[result.department] = result
        self.updated_at = datetime.now()

    def add_progress(self, message: str) -> None:
        """Add a progress log entry."""
        self.progress_log.append(f"[{datetime.now().isoformat()}] {message}")
        self.updated_at = datetime.now()
