"""Sessions MCP tools — spawn, send, and list agent sessions.

Implements the IMA spawn protocol:
- sessions_spawn: fire-and-forget launch with timeout/cleanup/model-selection
- sessions_send: bidirectional ping-pong (up to 5 rounds)
- sessions_list: list active sessions with status
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from cyberteam.mcp.helpers import require_team, to_payload
from cyberteam.spawn.sessions import SessionStore, SessionState
from cyberteam.team.mailbox import MailboxManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _store(team_name: str) -> SessionStore:
    return SessionStore(team_name)


def _mailbox(team_name: str) -> MailboxManager:
    return MailboxManager(team_name)


def _resolve_skill(agent_id: str) -> dict[str, Any]:
    """Resolve SOUL/SKILL from agent registry for spawn context.

    Returns skill dict from skills/ registry or empty dict.
    """
    try:
        from cyberteam.team.manager import TeamManager
        config = TeamManager._load_config_for_resolve(None)
        if not config:
            return {}
        for member in config.members:
            if member.agent_id == agent_id:
                skill_dir = member.extra.get("skill_dir", "")
                if skill_dir:
                    import os
                    skill_file = os.path.join(skill_dir, "SKILL.md")
                    if os.path.exists(skill_file):
                        return {"skill_dir": skill_dir, "skill_path": skill_file}
                return {"agent_id": agent_id, "agent_name": member.name}
        return {}
    except Exception:
        return {}


def _build_spawn_context(
    team_name: str,
    agent_name: str,
    task: str,
    context: Optional[dict[str, Any]] = None,
) -> str:
    """Build context block for spawned agent prompt."""
    parts = [f"## Task\n{task}"]

    # Inject cross-agent context if available
    try:
        from cyberteam.workspace.context import inject_context
        ctx = inject_context(team_name, agent_name, None)
        if ctx and "No cross-agent context" not in ctx:
            parts.append(f"\n## Context\n{ctx}")
    except Exception:
        pass

    # Inject skill context
    if context and context.get("skill_summary"):
        parts.append(f"\n## Skill Context\n{context['skill_summary']}")

    # Coordination protocol
    parts.extend([
        "",
        "## Coordination Protocol",
        f"- Use `clawteam task list {team_name} --owner {agent_name}` to see your tasks.",
        f"- Starting a task: `clawteam task update {team_name} <task-id> --status in_progress`",
        "- Before marking a task completed, commit your changes with git.",
        f"- Finishing a task: `clawteam task update {team_name} <task-id> --status completed`",
        f"- When you finish all tasks, send a summary to the leader:",
        f'  `clawteam inbox send {team_name} <leader_name> "All tasks completed. <brief summary>"`',
        f"- If you are blocked or need help, message the leader:",
        f'  `clawteam inbox send {team_name} <leader_name> "Need help: <description>"`',
    ])
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# sessions_spawn — fire-and-forget agent launch
# ---------------------------------------------------------------------------

def sessions_spawn(
    team_name: str,
    agent_name: str,
    agent_id: str,
    agent_type: str,
    task: str,
    prompt: Optional[str] = None,
    model: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
    skip_permissions: bool = False,
    workspace_dir: Optional[str] = None,
    isolated_workspace: bool = False,
    leader_name: str = "leader",
    context: Optional[dict[str, Any]] = None,
) -> dict:
    """Spawn a new agent session (fire-and-forget).

    This tool launches an agent asynchronously and returns immediately
    with a session_id. Use sessions_list to check status and sessions_send
    to communicate with the spawned agent.

    Args:
        team_name: Team to spawn in
        agent_name: Unique name for the agent
        agent_id: Agent type ID (e.g. "code-reviewer", "python-reviewer")
        agent_type: Agent type string (e.g. "general-purpose", "python")
        task: Task description for the agent
        prompt: Additional system prompt override (optional)
        model: Model selection hint (e.g. "opus", "haiku", "sonnet")
        timeout_seconds: Auto-cleanup timeout (optional)
        skip_permissions: Skip permission prompts
        workspace_dir: Working directory override
        isolated_workspace: Use isolated git worktree
        leader_name: Name of the team leader (for coordination)
        context: Additional context dict (e.g. {"skill_summary": "..."})

    Returns:
        dict with session_id, agent_name, team_name, status
    """
    require_team(team_name)

    # Generate session ID
    session_id = uuid.uuid4().hex[:12]

    # Build the agent prompt
    task_prompt = _build_spawn_context(team_name, agent_name, task, context)
    final_prompt = f"{prompt}\n\n{task_prompt}" if prompt else task_prompt

    # Resolve skill context for agent
    skill_info = _resolve_skill(agent_id)

    # Determine spawn command
    import os
    clawteam_bin = os.environ.get("CLAWTEAM_BIN", "clawteam")

    # Build command: openclaw agent or clawteam equivalent
    command = [clawteam_bin, "spawn"]

    # Model selection via env hint
    env = os.environ.copy()
    if model:
        env["CLAWTEAM_MODEL_HINT"] = model

    # Timeout annotation
    if timeout_seconds:
        env["CLAWTEAM_TIMEOUT"] = str(timeout_seconds)
        command.extend(["--timeout", str(timeout_seconds)])

    # Use TmuxBackend for spawn
    try:
        from cyberteam.spawn.tmux_backend import TmuxBackend
        backend = TmuxBackend()
    except Exception as exc:
        return {
            "sessionId": session_id,
            "agentName": agent_name,
            "teamName": team_name,
            "status": "error",
            "error": f"Failed to initialize spawn backend: {exc}",
        }

    try:
        result = backend.spawn(
            command=["openclaw", "agent"],
            agent_name=agent_name,
            agent_id=agent_id,
            agent_type=agent_type,
            team_name=team_name,
            prompt=final_prompt,
            env=env,
            cwd=workspace_dir,
            skip_permissions=skip_permissions,
        )
    except Exception as exc:
        result = f"Error: spawn failed: {exc}"

    # Persist session state
    store = _store(team_name)
    store.save(
        agent_name=agent_name,
        session_id=session_id,
        last_task_id=agent_id,
        state={
            "status": "running" if "spawned" in result.lower() or "Agent" in result else "error",
            "result": result,
            "timeout": timeout_seconds,
            "model": model,
            "skill_info": skill_info,
            "prompt_length": len(final_prompt),
            "spawn_backend": "tmux",
        },
    )

    # Register with team manager
    try:
        from cyberteam.team.manager import TeamManager
        TeamManager.add_member(
            team_name=team_name,
            member_name=agent_name,
            agent_id=agent_id,
            agent_type=agent_type,
            user="",
        )
    except Exception:
        pass  # Non-critical

    status = "spawned" if "spawned" in result.lower() else "error"
    ret = {
        "sessionId": session_id,
        "agentName": agent_name,
        "agentId": agent_id,
        "agentType": agent_type,
        "teamName": team_name,
        "status": status,
        "spawnResult": result,
        "timeoutSeconds": timeout_seconds,
        "modelHint": model,
        "promptLength": len(final_prompt),
    }
    if status == "error":
        ret["error"] = result if isinstance(result, str) else str(result)
    return ret


# ---------------------------------------------------------------------------
# sessions_send — bidirectional ping-pong (up to 5 rounds)
# ---------------------------------------------------------------------------

def sessions_send(
    team_name: str,
    session_id: str,
    from_agent: str,
    to_agent: str,
    content: str,
    msg_type: str = "message",
    round_limit: int = 5,
) -> dict:
    """Send a message to a spawned agent session and get a response (ping-pong).

    Implements bidirectional communication with up to `round_limit` rounds
    of back-and-forth messaging. The sub-agent responds via mailbox.

    Args:
        team_name: Team name
        session_id: Session ID returned from sessions_spawn
        from_agent: Sending agent name (typically the orchestrator)
        to_agent: Recipient agent name
        content: Message content
        msg_type: Message type (message, task, response, error)
        round_limit: Maximum ping-pong rounds (default 5)

    Returns:
        dict with round count, response content, and status
    """
    require_team(team_name)

    mailbox = _mailbox(team_name)
    store = _store(team_name)

    # Validate session exists
    session = store.load(to_agent)
    if not session:
        return {
            "sessionId": session_id,
            "teamName": team_name,
            "fromAgent": from_agent,
            "toAgent": to_agent,
            "status": "error",
            "error": f"No session found for agent '{to_agent}'",
        }

    round_count = 0
    max_rounds = min(max(round_limit, 1), 5)

    # Send initial message
    request_id = uuid.uuid4().hex[:12]
    mailbox.send(
        from_agent=from_agent,
        to=to_agent,
        content=content,
        msg_type=msg_type,
        request_id=request_id,
    )
    round_count += 1

    # Ping-pong: wait for response
    response_content = ""
    response_received = False

    for _ in range(max_rounds - 1):
        # Wait briefly for response (up to 30 seconds total)
        import time
        for _ in range(30):
            messages = mailbox.receive(from_agent, limit=5)
            for msg in messages:
                if msg.request_id == request_id or msg.from_agent == to_agent:
                    response_content = msg.content or ""
                    response_received = True
                    round_count += 1
                    break
            if response_received:
                break
            time.sleep(1)
        if response_received:
            break

    # Update session state
    if session:
        state = dict(session.state) if session.state else {}
        state.setdefault("rounds", 0)
        state["rounds"] += round_count
        state["last_interaction"] = content[:100]
        store.save(
            agent_name=to_agent,
            session_id=session_id,
            last_task_id=session.last_task_id,
            state=state,
        )

    return {
        "sessionId": session_id,
        "teamName": team_name,
        "fromAgent": from_agent,
        "toAgent": to_agent,
        "requestId": request_id,
        "roundCount": round_count,
        "response": response_content,
        "status": "ok" if response_received else "timeout",
        "message": "Response received" if response_received else f"No response after {max_rounds} rounds",
    }


# ---------------------------------------------------------------------------
# sessions_list — list active sessions
# ---------------------------------------------------------------------------

def sessions_list(
    team_name: str,
    status_filter: Optional[str] = None,
    agent_name_filter: Optional[str] = None,
) -> dict:
    """List active sessions for a team.

    Returns all sessions with their current state, including
    alive/dead status from the spawn registry.

    Args:
        team_name: Team name
        status_filter: Optional filter by status (running, dead, completed, error)
        agent_name_filter: Optional filter by agent name prefix

    Returns:
        dict with sessions list and counts
    """
    require_team(team_name)

    store = _store(team_name)
    sessions = store.list_sessions()

    # Enrich with alive status from registry
    enriched = []
    dead_count = 0
    running_count = 0

    try:
        from cyberteam.spawn.registry import get_registry, is_agent_alive

        registry = get_registry(team_name)
        for session in sessions:
            alive = is_agent_alive(team_name, session.agent_name)
            state = dict(session.state) if session.state else {}

            # Determine effective status
            if alive is True:
                effective_status = "running"
                running_count += 1
            elif alive is False:
                effective_status = "dead"
                dead_count += 1
            else:
                effective_status = state.get("status", "unknown")

            # Apply filters
            if status_filter and effective_status != status_filter:
                continue
            if agent_name_filter and not session.agent_name.startswith(agent_name_filter):
                continue

            enriched.append({
                "sessionId": session.session_id or session.last_task_id,
                "agentName": session.agent_name,
                "teamName": session.team_name,
                "status": effective_status,
                "alive": alive,
                "lastTaskId": session.last_task_id,
                "savedAt": session.saved_at,
                "rounds": state.get("rounds", 0),
                "timeout": state.get("timeout"),
                "model": state.get("model"),
                "skillInfo": state.get("skill_info", {}),
                "promptLength": state.get("prompt_length"),
            })
    except Exception:
        # Fallback without registry enrichment
        for session in sessions:
            state = dict(session.state) if session.state else {}
            effective_status = state.get("status", "unknown")
            if status_filter and effective_status != status_filter:
                continue
            if agent_name_filter and not session.agent_name.startswith(agent_name_filter):
                continue
            enriched.append({
                "sessionId": session.session_id or session.last_task_id,
                "agentName": session.agent_name,
                "teamName": session.team_name,
                "status": effective_status,
                "alive": None,
                "lastTaskId": session.last_task_id,
                "savedAt": session.saved_at,
                "rounds": state.get("rounds", 0),
                "timeout": state.get("timeout"),
            })

    return {
        "teamName": team_name,
        "sessions": enriched,
        "total": len(enriched),
        "running": running_count,
        "dead": dead_count,
        "statusFilter": status_filter,
        "agentNameFilter": agent_name_filter,
    }


# ---------------------------------------------------------------------------
# sessions_stop — stop a spawned session
# ---------------------------------------------------------------------------

def sessions_stop(
    team_name: str,
    agent_name: str,
    session_id: Optional[str] = None,
    timeout_seconds: float = 3.0,
) -> dict:
    """Stop a spawned agent session.

    Args:
        team_name: Team name
        agent_name: Agent name to stop
        session_id: Optional session ID
        timeout_seconds: Graceful shutdown timeout

    Returns:
        dict with stop status
    """
    require_team(team_name)

    try:
        from cyberteam.spawn.registry import stop_agent
        result = stop_agent(team_name, agent_name, timeout_seconds=timeout_seconds)
    except Exception as exc:
        return {
            "agentName": agent_name,
            "teamName": team_name,
            "status": "error",
            "error": str(exc),
        }

    # Update session state
    store = _store(team_name)
    session = store.load(agent_name)
    if session:
        state = dict(session.state) if session.state else {}
        state["status"] = "stopped"
        state["stopped_at"] = __import__("datetime").datetime.now().isoformat()
        store.save(
            agent_name=agent_name,
            session_id=session_id or session.session_id,
            last_task_id=session.last_task_id,
            state=state,
        )

    return {
        "agentName": agent_name,
        "teamName": team_name,
        "status": "stopped" if result else "not_found",
        "graceful": result,
    }
