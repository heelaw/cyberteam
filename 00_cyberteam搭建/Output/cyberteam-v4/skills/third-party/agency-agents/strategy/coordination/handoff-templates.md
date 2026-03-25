# NEXUS Handoff Templates

> Standardized templates for every agent-to-agent work transfer in the NEXUS pipeline. Consistent handoffs prevent context loss — the #1 cause of multi-agent coordination failure.

---

## 1. Standard Handoff Template

Used for any agent-to-agent work transfer.

```markdown
# NEXUS Handoff Document

## Metadata
| Field | Value |
|-------|-------|
| **From** | [Agent Name] ([Department]) |
| **To** | [Agent Name] ([Department]) |
| **Phase** | Phase [N] — [Phase Name] |
| **Task Reference** | [Task ID from Sprint Prioritizer backlog] |
| **Priority** | [Critical / High / Medium / Low] |
| **Timestamp** | [YYYY-MM-DDTHH:MM:SSZ] |

## Context
**Project**: [Project name]
**Current Status**: [What has been completed so far — be specific]
**Related Files**:
- [File/path 1] — [What it contains]
- [File/path 2] — [What it contains]
**Dependencies**: [What this work depends on being completed]
**Constraints**: [Technical, timeline, or resource constraints]

## Deliverable Request
**What is needed**: [Specific, measurable deliverable description]
**Acceptance Criteria**:
- [ ] [Criterion 1 — measurable]
- [ ] [Criterion 2 — measurable]
- [ ] [Criterion 3 — measurable]
**Reference Material**: [Links to specs, designs, prior work]

## Quality Expectations
**Must Pass**: [Specific quality standards for this deliverable]
**Required Evidence**: [What proof of completion looks like]
**Hand Off To**: [Who receives the output and what format they need]
```

---

## 2. QA Feedback Loop — Pass

Used when the Evidence Collector or other QA agent approves a task.

```markdown
# NEXUS QA Verdict: PASS

## Task
| Field | Value |
|-------|-------|
| **Task ID** | [ID] |
| **Task Description** | [Description] |
| **Developer Agent** | [Agent name] |
| **QA Agent** | [Agent name] |
| **Attempts** | [N] / 3 |
| **Timestamp** | [YYYY-MM-DDTHH:MM:SSZ] |

## Verdict: PASS

## Evidence
**Screenshots**:
- Desktop (1920x1080): [filename/path]
- Tablet (768x1024): [filename/path]
- Mobile (375x667): [filename/path]

**Functional Verification**:
- [x] [Acceptance criterion 1] — Verified
- [x] [Acceptance criterion 2] — Verified
- [x] [Acceptance criterion 3] — Verified

**Brand Consistency**: Verified — colors, fonts, spacing match design system
**Accessibility**: Verified — keyboard navigation, contrast, semantic HTML
**Performance**: [Measured load time] — within acceptable range

## Notes
[Any observations, small suggestions for future improvements, or positive feedback]

## Next Actions
→ Agent Orchestrator: Mark task complete, advance to next task in backlog
```

---

## 3. QA Feedback Loop — Fail

Used when the Evidence Collector or other QA agent rejects a task.

```markdown
# NEXUS QA Verdict: FAIL

## Task
| Field | Value |
|-------|-------|
| **Task ID** | [ID] |
| **Task Description** | [Description] |
| **Developer Agent** | [Agent name] |
| **QA Agent** | [Agent name] |
| **Attempts** | [N] / 3 |
| **Timestamp** | [YYYY-MM-DDTHH:MM:SSZ] |

## Verdict: FAIL

## Issues Found

### Issue 1: [Category] — [Severity: Critical/High/Medium/Low]
**Description**: [Exact description of the issue]
**Expected**: [What should happen according to acceptance criteria]
**Actual**: [What actually happened]
**Evidence**: [Screenshot filename or test output]
**Fix Instructions**: [Specific, actionable instructions to resolve this issue]
**Files to Modify**: [Exact file paths]

### Issue 2: [Category] — [Severity]
**Description**: [...]
**Expected**: [...]
**Actual**: [...]
**Evidence**: [...]
**Fix Instructions**: [...]
**Files to Modify**: [...]

[Continue listing all issues found]

## Acceptance Criteria Status
- [x] [Criterion 1] — Pass
- [ ] [Criterion 2] — Fail (see Issue 1)
- [ ] [Criterion 3] — Fail (see Issue 2)

## Retry Instructions
**For Developer Agent**:
1. Only fix the issues listed above
2. Do not introduce new features or changes
3. Resubmit for QA after resolving all issues
4. This is attempt [N] of maximum 3

**If 3rd attempt fails**: Task will be escalated to Agent Orchestrator
```

---

## 4. Escalation Report

Used when a task exceeds 3 retry attempts.

```markdown
# NEXUS Escalation Report

## Task
| Field | Value |
|-------|-------|
| **Task ID** | [ID] |
| **Task Description** | [Description] |
| **Developer Agent** | [Agent name] |
| **QA Agent** | [Agent name] |
| **Attempts** | 3/3 |
| **Escalated To** | [Agent Orchestrator / Studio Producer] |
| **Timestamp** | [YYYY-MM-DDTHH:MM:SSZ] |

## Failure History

### Attempt 1
- **Issues Found**: [Summary]
- **Fix Applied**: [What developer changed]
- **Result**: Fail — [Why it still failed]

### Attempt 2
- **Issues Found**: [Summary]
- **Fix Applied**: [What developer changed]
- **Result**: Fail — [Why it still failed]

### Attempt 3
- **Issues Found**: [Summary]
- **Fix Applied**: [What developer changed]
- **Result**: Fail — [Why it still failed]

## Root Cause Analysis
**Why the task keeps failing**: [Analysis of underlying problems]
**Systemic Issue**: [Is this a one-off or a pattern?]
**Complexity Assessment**: [Is the scope of the task appropriate?]

## Recommended Solutions
- [ ] **Reassign** to different developer agent ([recommended agent])
- [ ] **Decompose** into smaller subtasks ([proposed breakdown])
- [ ] **Revise approach** — requires architecture/design changes
- [ ] **Accept** current state and document limitations
- [ ] **Defer** to future sprint

## Impact Assessment
**Blocked**: [What other tasks are blocked by this]
**Timeline Impact**: [How this affects overall progress]
**Quality Impact**: [What quality compromises are we making if we accept current state]

## Decision Required
**Decision Maker**: [Agent Orchestrator / Studio Producer]
**Deadline**: [Date decision is needed to avoid further delay]
```

---

## 5. Phase Gate Handoff

Used when transitioning between NEXUS phases.

```markdown
# NEXUS Phase Gate Handoff

## Transition
| Field | Value |
|-------|-------|
| **From Phase** | Phase [N] — [Name] |
| **To Phase** | Phase [N+1] — [Name] |
| **Gate Keeper** | [Agent name] |
| **Gate Result** | [Pass / Fail] |
| **Timestamp** | [YYYY-MM-DDTHH:MM:SSZ] |

## Gate Criteria Results
| # | Criterion | Threshold | Result | Evidence |
|---|-----------|-----------|--------|----------|
| 1 | [Criterion] | [Threshold] | Pass / Fail | [Evidence reference] |
| 2 | [Criterion] | [Threshold] | Pass / Fail | [Evidence reference] |
| 3 | [Criterion] | [Threshold] | Pass / Fail | [Evidence reference] |

## Documents to Carry Forward
1. [Document name] — [Purpose for next phase]
2. [Document name] — [Purpose for next phase]
3. [Document name] — [Purpose for next phase]

## Key Constraints for Next Phase
- [Constraint 1 discovered in this phase]
- [Constraint 2 discovered in this phase]

## Agent Activation for Next Phase
| Agent | Role | Priority |
|-------|------|----------|
| [Agent 1] | [Role in next phase] | [Immediate / Day 2 / As needed] |
| [Agent 2] | [Role in next phase] | [Immediate / Day 2 / As needed] |

## Risks to Carry Forward
| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| [Risk] | [P0-P3] | [Mitigation plan] | [Agent] |
```

---

## 6. Sprint Handoff

Used at sprint boundaries.

```markdown
# NEXUS Sprint Handoff

## Sprint Summary
| Field | Value |
|-------|-------|
| **Sprint** | [Number] |
| **Duration** | [Start date] → [End date] |
| **Sprint Goal** | [Goal statement] |
| **Velocity** | [Planned] / [Actual] story points |

## Completion Status
| Task ID | Description | Status | QA Attempts | Notes |
|---------|-------------|--------|-------------|-------|
| [ID] | [Description] | Complete | [N] | [Notes] |
| [ID] | [Description] | Complete | [N] | [Notes] |
| [ID] | [Description] | Carried | [N] | [Reason] |

## Quality Metrics
- **First-pass QA rate**: [X]%
- **Average retry count**: [N]
- **Tasks completed**: [X/Y]
- **Story points delivered**: [N]

## Carryover to Next Sprint
| Task ID | Description | Reason | Priority |
|---------|-------------|--------|----------|
| [ID] | [Description] | [Why incomplete] | [RICE score] |

## Retrospective Insights
**What Went Well**: [Key successes]
**Needs Improvement**: [Key improvements]
**Action Items**: [Specific changes for next sprint]

## Next Sprint Preview
**Sprint Goal**: [Suggested goal]
**Key Tasks**: [Highest priority items]
**Dependencies**: [Cross-team dependencies]
```

---

## 7. Incident Handoff

Used during incident response.

```markdown
# NEXUS Incident Handoff

## Incident
| Field | Value |
|-------|-------|
| **Severity** | [P0 / P1 / P2 / P3] |
| **Detected By** | [Agent or system] |
| **Detection Time** | [Timestamp] |
| **Assigned To** | [Agent name] |
| **Status** | [Investigating / Mitigating / Resolved / Post-mortem] |

## Description
**What happened**: [Clear description of the incident]
**Impact**: [Who/what is affected and severity]
**Timeline**:
- [HH:MM] — [Event]
- [HH:MM] — [Event]
- [HH:MM] — [Event]

## Current Status
**Systems Affected**: [List]
**Workaround Available**: [Yes/No — if yes, describe]
**Estimated Resolution Time**: [Time estimate]

## Actions Taken
1. [Action taken and result]
2. [Action taken and result]

## Handoff Context
**For next responder**:
- [What has been tried]
- [What hasn't been tried yet]
- [Suspected root cause]
- [Relevant logs/metrics to check]

## Stakeholder Communication
**Last update sent**: [Timestamp]
**Next update by**: [Timestamp]
**Communication channel**: [Where updates are posted]
```

---

## Usage Guide

| Situation | Template to Use |
|------------|----------------|
| Assigning work to another agent | Standard Handoff (#1) |
| QA approves a task | QA Pass (#2) |
| QA rejects a task | QA Fail (#3) |
| Task exceeds 3 retries | Escalation Report (#4) |
| Moving between phases | Phase Gate Handoff (#5) |
| Sprint boundary | Sprint Handoff (#6) |
| System incident | Incident Handoff (#7) |
