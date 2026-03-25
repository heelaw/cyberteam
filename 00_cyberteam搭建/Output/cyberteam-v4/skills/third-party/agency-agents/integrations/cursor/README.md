# Cursor Integration

Converts all 61 Agency agents into Cursor ".mdc" rule files. Rules are **project-scoped** — install them from your project root.

## Installation

```bash
# Run from your project root
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool cursor
```

This creates `.cursor/rules/<agent-slug>.mdc` files in your project.

## Activating Rules

In Cursor, reference the agent in your prompt:

```
@frontend-developer Review this React component for performance issues.
```

Or enable a rule by editing its frontmatter:

```yaml
---
description: Expert frontend developer...
globs: "**/*.tsx,**/*.ts"
alwaysApply: true
---
```

## Regeneration

```bash
./scripts/convert.sh --tool cursor
```
