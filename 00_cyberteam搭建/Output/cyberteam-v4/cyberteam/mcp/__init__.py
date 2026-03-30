"""MCP tool registry for ClawTeam."""

# 注意：在 macOS 上 cyberteam/ 和 CYBERTEAM/ 是同一目录
# 使用相对导入避免循环导入
from .tools.board import board_overview, board_team
from .tools.cost import cost_summary
from .tools.mailbox import (
    mailbox_broadcast,
    mailbox_peek,
    mailbox_peek_count,
    mailbox_receive,
    mailbox_send,
)
from .tools.plan import plan_approve, plan_get, plan_reject, plan_submit
from .tools.task import task_create, task_get, task_list, task_stats, task_update
from .tools.team import (
    team_create,
    team_get,
    team_list,
    team_member_add,
    team_members_list,
)
from .tools.workspace import (
    workspace_agent_diff,
    workspace_agent_summary,
    workspace_cross_branch_log,
    workspace_file_owners,
)
from .tools.sessions import (
    sessions_spawn,
    sessions_send,
    sessions_list,
    sessions_stop,
)

# 导出 Tool 类
from .client import MCPClient
from .server import MCPServerManager
from .registry import ToolRegistry

TOOL_FUNCTIONS = [
    team_list,
    team_get,
    team_members_list,
    team_create,
    team_member_add,
    task_list,
    task_get,
    task_stats,
    task_create,
    task_update,
    mailbox_send,
    mailbox_broadcast,
    mailbox_receive,
    mailbox_peek,
    mailbox_peek_count,
    plan_submit,
    plan_get,
    plan_approve,
    plan_reject,
    board_overview,
    board_team,
    cost_summary,
    workspace_agent_diff,
    workspace_file_owners,
    workspace_cross_branch_log,
    workspace_agent_summary,
    sessions_spawn,
    sessions_send,
    sessions_list,
    sessions_stop,
]

__all__ = ["TOOL_FUNCTIONS", "MCPClient", "MCPServerManager", "ToolRegistry"]
