# MCP Memory Integration

> Provides persistent memory across sessions for any agent using the Model Context Protocol (MCP).

## What It Does

By default, agents in the agency start each session from scratch. Context is manually passed between agents and sessions via copy-paste. The MCP memory server changes this:

- **Cross-session memory**: Agents remember decisions, deliverables, and context from previous sessions
- **Handoff continuity**: When one agent hands off work to another, the receiving agent can accurately recall what was done — no more copy-paste
- **Rollback on failure**: When QA checks fail or an architecture decision proves wrong, rollback to a known-good state instead of starting over

## Setup

You need an MCP server that provides memory tools: "remember", "recall", "rollback", and "search". Add it to your MCP client configuration (Claude Code, Cursor, etc.):

```json
{
  "mcpServers": {
    "memory": {
      "command": "your-mcp-memory-server",
      "args": []
    }
  }
}
```

Any MCP server that exposes "remember", "recall", "rollback", and "search" tools will work. Check the [MCP ecosystem](https://modelcontextprotocol.io) for available implementations.

## How to Add Memory to Any Agent

To enhance existing agents with persistent memory, add the **Memory Integration** section to the agent's prompt. This section instructs the agent to use MCP memory tools at key moments.

### Template

```markdown
## Memory Integration

When you start a session:
- Recall relevant context from previous sessions using your role and the current project as search terms
- Review any memories tagged with your agent name to pick up where you left off

When you make key decisions or complete deliverables:
- Remember the decision or deliverable with descriptive tags (your agent name, the project, the topic)
- Include enough context that a future session — or a different agent — can understand what was done and why

When handing off to another agent:
- Remember your deliverables tagged for the receiving agent
- Include the handoff metadata: what you completed, what's pending, and what the next agent needs to know

When something fails and you need to recover:
- Search for the last known-good state
- Use rollback to restore to that point rather than rebuilding from scratch
```

### What Agents Do With It

When given the above instructions, the LLM automatically uses the MCP memory tools:

- `remember` — Store decisions, deliverables, or context snapshots with tags
- `recall` — Search for relevant memories by keywords, tags, or semantic similarity
- `rollback` — Restore to a previous state when something goes wrong
- `search` — Find specific memories across sessions and agents

No code changes to agent files. No API calls to write. MCP tools handle everything.

## Example: Enhanced Backend Architect

See [backend-architect-with-memory.md](backend-architect-with-memory.md) for a complete example — a standard backend architect agent with a memory integration section added.

## Example: Memory-Driven Workflow

See [workflow-with-memory.md](../../examples/workflow-with-memory.md) for a Startup MVP workflow enhanced with persistent memory, showing how agents pass context through memory instead of copy-paste.

## Tips

- **Consistent tagging**: Use your agent name and project name as tags on every memory. This makes recall reliable.
- **Let the LLM decide what's important**: Memory instructions are guidance, not strict rules. The LLM figures out when to remember and what to remember.
- **Rollback is the killer feature**: When the Reality Checker fails to deliver a working deliverable, the original agent can rollback to its last checkpoint rather than trying to manually undo changes.
