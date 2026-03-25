# OpenCode Integration

OpenCode agents are ".md" files with YAML frontmatter stored in `.opencode/agents/`. The converter maps named colors to hex codes and adds `mode: subagent` so agents are invoked on-demand via `@agent-name` rather than cluttering the main agent selector.

## Installation

```bash
# Run from your project root
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool opencode
```

This creates `.opencode/agents/<slug>.md` files in your project directory.

## Activating Agents

In OpenCode, use the "@" prefix to call subagents:

```
@frontend-developer help build this component.
```

```
@reality-checker review this PR.
```

You can also select agents from the agent picker in the OpenCode UI.

## Agent Format

Each generated agent file contains:

```yaml
---
name: Frontend Developer
description: Expert frontend developer specializing in modern web technologies...
mode: subagent
color: "#00FFFF"
---
```

- **Mode: subagent** — Agents are available on-demand and won't show up in the main tab cycle list
- **Color** — Hex codes (named colors in source files are automatically converted)

## Project vs Global

Agents in `.opencode/agents/` are **project-scoped**. To make them available globally across all projects, copy them to your OpenCode config directory:

```bash
mkdir -p ~/.config/opencode/agents
cp integrations/opencode/agents/*.md ~/.config/opencode/agents/
```

## Regeneration

```bash
./scripts/convert.sh --tool opencode
```
