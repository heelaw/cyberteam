# Aider Integration

All 61 agents are merged into a single "CONVENTIONS.md" file. Aider automatically reads this file when it exists in the project root.

## Installation

```bash
# Run from your project root
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool aider
```

## Activating Agents

In your Aider session, reference agents by name:

```
Use the Frontend Developer agent to refactor this component.
```

```
Apply the Reality Checker agent to verify this is production-ready.
```

## Manual Usage

You can also pass the conventions file directly:

```bash
aider --read CONVENTIONS.md
```

## Regeneration

```bash
./scripts/convert.sh --tool aider
```
