# Claude Code Integration

The agency was built for Claude Code. No conversion needed — agents work natively using the existing `.md` + YAML frontmatter format.

## Installation

```bash
# Copy all agents to your Claude Code agents directory
./scripts/install.sh --tool claude-code

# Or manually copy a category
cp engineering/*.md ~/.claude/agents/
```

## Activating Agents

In any Claude Code session, reference agents by name:

```
Activate Frontend Developer and help me build a React component.
```

```
Use the Reality Checker agent to verify this feature is production-ready.
```

## Agent Directory

Agents are organized into different departments. See the [main README](../../README.md) for the complete list.
