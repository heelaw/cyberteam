# 会话适配器合约

本文档定义了规范的 ECC 会话快照合约
`ecc.session.v1`。

合同执行时间为
`scripts/lib/session-adapters/canonical-session.js`。该文档是
适配器和消费者的规范规范。

## 目的

ECC 有多个会话源：

- tmux 编排的工作树会话
- 克劳德本地会话历史
- 未来的线束和控制平面后端

适配器将这些源标准化为一个控制平面安全的快照形状，以便
检查、持久性和未来的 UI 层不依赖于特定于线束的
文件或运行时详细信息。

## 规范快照

每个适配器必须返回一个具有以下顶级形状的 JSON 可序列化对象：```json
{
  "schemaVersion": "ecc.session.v1",
  "adapterId": "dmux-tmux",
  "session": {
    "id": "workflow-visual-proof",
    "kind": "orchestrated",
    "state": "active",
    "repoRoot": "/tmp/repo",
    "sourceTarget": {
      "type": "session",
      "value": "workflow-visual-proof"
    }
  },
  "workers": [
    {
      "id": "seed-check",
      "label": "seed-check",
      "state": "running",
      "branch": "feature/seed-check",
      "worktree": "/tmp/worktree",
      "runtime": {
        "kind": "tmux-pane",
        "command": "codex",
        "pid": 1234,
        "active": false,
        "dead": false
      },
      "intent": {
        "objective": "Inspect seeded files.",
        "seedPaths": ["scripts/orchestrate-worktrees.js"]
      },
      "outputs": {
        "summary": [],
        "validation": [],
        "remainingRisks": []
      },
      "artifacts": {
        "statusFile": "/tmp/status.md",
        "taskFile": "/tmp/task.md",
        "handoffFile": "/tmp/handoff.md"
      }
    }
  ],
  "aggregates": {
    "workerCount": 1,
    "states": {
      "running": 1
    }
  }
}
```## Required Fields

### Top level

| Field | Type | Notes |
| --- | --- | --- |
| `schemaVersion` | string | MUST be exactly `ecc.session.v1` for this contract |
| `adapterId` | string | Stable adapter identifier such as `dmux-tmux` or `claude-history` |
| `session` | object | Canonical session metadata |
| `workers` | array | Canonical worker records; may be empty |
| `aggregates` | object | Derived worker counts |

### `session`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable identifier within the adapter domain |
| `kind` | string | High-level session family such as `orchestrated` or `history` |
| `state` | string | Canonical session state |
| `sourceTarget` | object | Provenance for the target that opened the session |

### `session.sourceTarget`

| Field | Type | Notes |
| --- | --- | --- |
| `type` | string | Lookup class such as `plan`, `session`, `claude-history`, `claude-alias`, or `session-file` |
| `value` | string | Raw target value or resolved path |

### `workers[]`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable worker identifier in adapter scope |
| `label` | string | Operator-facing label |
| `state` | string | Canonical worker state |
| `runtime` | object | Execution/runtime metadata |
| `intent` | object | Why this worker/session exists |
| `outputs` | object | Structured outcomes and checks |
| `artifacts` | object | Adapter-owned file/path references |

### `workers[].runtime`

| Field | Type | Notes |
| --- | --- | --- |
| `kind` | string | Runtime family such as `tmux-pane` or `claude-session` |
| `active` | boolean | Whether the runtime is active now |
| `dead` | boolean | Whether the runtime is known dead/finished |

### `workers[].intent`

| Field | Type | Notes |
| --- | --- | --- |
| `objective` | string | Primary objective or title |
| `seedPaths` | string[] | Seed or context paths associated with the worker/session |

### `workers[].outputs`

| Field | Type | Notes |
| --- | --- | --- |
| `summary` | string[] | Completed outputs or summary items |
| `validation` | string[] | Validation evidence or checks |
| `remainingRisks` | string[] | Open risks, follow-ups, or notes |

### `aggregates`

| Field | Type | Notes |
| --- | --- | --- |
| `workerCount` | integer | MUST equal `workers.length` |
| `states` | object | Count map derived from `workers[].state` |

## Optional Fields

Optional fields MAY be omitted, but if emitted they MUST preserve the documented
type:

| Field | Type | Notes |
| --- | --- | --- |
| `session.repoRoot` | `string \| null` | Repo/worktree root when known |
| `workers[].branch` | `string \| null` | Branch name when known |
| `workers[].worktree` | `string \| null` | Worktree path when known |
| `workers[].runtime.command` | `string \| null` | Active command when known |
| `workers[].runtime.pid` | `number \| null` | Process id when known |
| `workers[].artifacts.*` | adapter-defined | File paths or structured references owned by the adapter |

Adapter-specific optional fields belong inside `runtime`, `artifacts`, or other
documented nested objects. Adapters MUST NOT invent new top-level fields without
updating this contract.

## State Semantics

The contract intentionally keeps `session.state` and `workers[].state` flexible
enough for multiple harnesses, but current adapters use these values:

- `dmux-tmux`
  - session states: `active`, `completed`, `failed`, `idle`, `missing`
  - worker states: derived from worker status files, for example `running` or
    `completed`
- `claude-history`
  - session state: `recorded`
  - worker state: `recorded`

Consumers MUST treat unknown state strings as valid adapter-specific values and
degrade gracefully.

## Versioning Strategy

`schemaVersion` is the only compatibility gate. Consumers MUST branch on it.

### Allowed in `ecc.session.v1`

- adding new optional nested fields
- adding new adapter ids
- adding new state string values
- adding new artifact keys inside `workers[].artifacts`

### Requires a new schema version

- removing a required field
- renaming a field
- changing a field type
- changing the meaning of an existing field in a non-compatible way
- moving data from one field to another while keeping the same version string

If any of those happen, the producer MUST emit a new version string such as
`ecc.session.v2`.

## Adapter Compliance Requirements

Every ECC session adapter MUST:

1. Emit `schemaVersion: "ecc.session.v1"` exactly.
2. Return a snapshot that satisfies all required fields and types.
3. Use `null` for unknown optional scalar values and empty arrays for unknown
   list values.
4. Keep adapter-specific details nested under `runtime`, `artifacts`, or other
   documented nested objects.
5. Ensure `aggregates.workerCount === workers.length`.
6. Ensure `aggregates.states` matches the emitted worker states.
7. Produce plain JSON-serializable values only.
8. Validate the canonical shape before persistence or downstream use.
9. Persist the normalized canonical snapshot through the session recording shim.
   In this repo, that shim first attempts `scripts/lib/state-store` and falls
   back to a JSON recording file only when the state store module is not
   available yet.

## Consumer Expectations

Consumers SHOULD:

- rely only on documented fields for `ecc.session.v1`
- ignore unknown optional fields
- treat `adapterId`, `session.kind`, and `runtime.kind` as routing hints rather
  than exhaustive enums
- expect adapter-specific artifact keys inside `workers[].artifacts`

Consumers MUST NOT:

- infer harness-specific behavior from undocumented fields
- assume all adapters have tmux panes, git worktrees, or markdown coordination
  files
- reject snapshots only because a state string is unfamiliar

## Current Adapter Mappings

### `dmux-tmux`

- Source: `scripts/lib/orchestration-session.js`
- Session id: orchestration session name
- Session kind: `orchestrated`
- Session source target: plan path or session name
- Worker runtime kind: `tmux-pane`
- Artifacts: `statusFile`, `taskFile`, `handoffFile`

### `claude-history`

- Source: `scripts/lib/session-manager.js`
- Session id: Claude short id when present, otherwise session filename-derived id
- Session kind: `history`
- Session source target: explicit history target, alias, or `.tmp` session file
- Worker runtime kind: `claude-session`
- Intent seed paths: parsed from `### Context to Load`
- Artifacts: `sessionFile`, `context`

## Validation Reference

The repo implementation validates:

- required object structure
- required string fields
- boolean runtime flags
- string-array outputs and seed paths
- aggregate count consistency

Adapters should treat validation failures as contract bugs, not user input
errors.

## Recording Fallback Behavior

The JSON fallback recorder is a temporary compatibility shim for the period
before the dedicated state store lands. Its behavior is:

- latest snapshot is always replaced in-place
- history records only distinct snapshot bodies
- unchanged repeated reads do not append duplicate history entries

This keeps `session-inspect` and other polling-style reads from growing
unbounded history for the same unchanged session snapshot.