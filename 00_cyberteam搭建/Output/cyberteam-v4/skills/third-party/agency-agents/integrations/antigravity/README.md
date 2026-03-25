# Antigravity Integration

Installs all 61 Agency agents as Antigravity skills. Each agent is prefixed with "agency-" to avoid conflicts with existing skills.

## Installation

```bash
./scripts/install.sh --tool antigravity
```

This copies files from "integrations/antigravity/" to `~/.gemini/antigravity/skills/`.

## Activating Skills

In Antigravity, activate agents via their slug:

```
Use the agency-frontend-developer skill to review this component.
```

Available slugs follow the "agency-<agent-name>" pattern, for example:
- `agency-frontend-developer`
- `agency-backend-architect`
- `agency-reality-checker`
- `agency-growth-hacker`

## Regeneration

After modifying agents, regenerate the skill files:

```bash
./scripts/convert.sh --tool antigravity
```

## File Format

Each skill is a `SKILL.md` file with Antigravity-compatible frontmatter:

```yaml
---
name: agency-frontend-developer
description: Expert frontend developer specializing in...
risk: low
source: community
date_added: '2026-03-08'
---
```
