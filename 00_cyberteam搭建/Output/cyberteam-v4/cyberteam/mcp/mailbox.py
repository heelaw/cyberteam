"""Mailbox MCP tools."""

from __future__ import annotations

from .helpers import coerce_enum, team_mailbox, to_payload
from cyberteam.team.models import MessageType
from typing import Union, List


def mailbox_send(
    team_name: str,
    from_agent: str,
    to: str,
    content: Optional[str] = None,
    msg_type: Optional[str] = None,
    request_id: Optional[str] = None,
    key: Optional[str] = None,
    proposed_name: Optional[str] = None,
    capabilities: Optional[str] = None,
    feedback: Optional[str] = None,
    reason: Optional[str] = None,
    assigned_name: Optional[str] = None,
    agent_id: Optional[str] = None,
    message_team_name: Optional[str] = None,
    plan_file: Optional[str] = None,
    summary: Optional[str] = None,
    plan: Optional[str] = None,
    last_task: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """Send a message to a team member inbox."""
    return to_payload(
        team_mailbox(team_name).send(
            from_agent=from_agent,
            to=to,
            content=content,
            msg_type=coerce_enum(MessageType, msg_type) or MessageType.message,
            request_id=request_id,
            key=key,
            proposed_name=proposed_name,
            capabilities=capabilities,
            feedback=feedback,
            reason=reason,
            assigned_name=assigned_name,
            agent_id=agent_id,
            team_name=message_team_name,
            plan_file=plan_file,
            summary=summary,
            plan=plan,
            last_task=last_task,
            status=status,
        )
    )


def mailbox_broadcast(
    team_name: str,
    from_agent: str,
    content: str,
    msg_type: Optional[str] = None,
    key: Optional[str] = None,
    exclude: Union[List[str], None]=
) -> List[dict]:
    """Broadcast a message to team inboxes."""
    return to_payload(
        team_mailbox(team_name).broadcast(
            from_agent=from_agent,
            content=content,
            msg_type=coerce_enum(MessageType, msg_type) or MessageType.broadcast,
            key=key,
            exclude=exclude,
        )
    )


def mailbox_receive(team_name: str, agent_name: str, limit: int = 10) -> List[dict]:
    """Receive and consume pending inbox messages."""
    return to_payload(team_mailbox(team_name).receive(agent_name, limit=limit))


def mailbox_peek(team_name: str, agent_name: str) -> List[dict]:
    """Preview pending inbox messages without consuming them."""
    return to_payload(team_mailbox(team_name).peek(agent_name))


def mailbox_peek_count(team_name: str, agent_name: str) -> dict:
    """Get the number of pending inbox messages."""
    return {"agentName": agent_name, "count": team_mailbox(team_name).peek_count(agent_name)}

