# Windsurf Integration

All 61 Agency agents are consolidated into a single ".windsurfrules" file. Rules are **project-scoped** — install them from your project root.

## Installation

```bash
# Run from your project root
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool windsurf
```

## Activating Agents

In Windsurf, reference agents by name in your prompt:

```
Use the Frontend Developer agent to build this component.
```

## Regeneration

```bash
./scripts/convert.sh --tool windsurf
```
