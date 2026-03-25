# OpenClaw Integration

OpenClaw agents are installed as workspaces containing "SOUL.md", "AGENTS.md", and "IDENTITY.md" files. The installer copies each workspace to `~/.openclaw/agency-agents/` and registers it when the `openclaw` CLI is run.

## Installation

Before installing, generate the OpenClaw workspaces:

```bash
./scripts/convert.sh --tool openclaw
```

## Installation

```bash
./scripts/install.sh --tool openclaw
```

## Activating Agents

After installation, agents can be used via "agentId" in OpenClaw sessions.

If the OpenClaw gateway is already running, restart it after installation:

```bash
openclaw gateway restart
```

## Regeneration

```bash
./scripts/convert.sh --tool openclaw
```
