# Runbook: Incident Response

> **Mode**: NEXUS-Micro | **Duration**: Minutes to hours | **Agents**: 3-8

---

## Scenario

An issue has occurred in the production environment. Users are affected. Response speed matters, but so does getting it right. This runbook covers the full spectrum from detection to post-mortem.

## Severity Classification

| Level | Definition | Examples | Response Time |
|-------|-----------|----------|---------------|
| **P0 — Critical** | Complete service outage, data loss, security breach | Database corruption, DDoS attack, authentication system failure | Immediate (all hands) |
| **P1 — High** | Major feature broken, significant performance degradation | Payment processing down, 50%+ error rate, 10x latency | < 1 hour |
| **P2 — Medium** | Minor feature broken, workaround available | Search not working, non-critical API errors | < 4 hours |
| **P3 — Low** | Cosmetic issues, minor inconveniences | Style bugs, typos, minor UI glitches | Next sprint |

## Response Teams by Severity

### P0 — Critical Response Team

| Agent | Role | Actions |
|-------|------|--------|
| **Infrastructure Maintainer** | Incident Commander | Assess scope, coordinate response |
| **DevOps Automator** | Deployment/Rollback | Execute rollback if needed |
| **Backend Architect** | Root Cause Investigation | Diagnose system issues |
| **Frontend Developer** | Client Investigation | Diagnose client issues |
| **Support Responder** | User Communication | Status page updates, user notifications |
| **Executive Summary Generator** | Stakeholder Communication | Real-time executive updates |

### P1 — High Response Team

| Agent | Role |
|-------|------|
| **Infrastructure Maintainer** | Incident Commander |
| **DevOps Automator** | Deployment Support |
| **Relevant Developer Agent** | Fix Implementation |
| **Support Responder** | User Communication |

### P2 — Medium Response

| Agent | Role |
|-------|------|
| **Relevant Developer Agent** | Fix Implementation |
| **Evidence Collector** | Verify Fix |

### P3 — Low Response

| Agent | Role |
|-------|------|
| **Sprint Prioritizer** | Add to backlog |

## Incident Response Sequence

### Step 1: Detection and Classification (0-5 minutes)

```
Trigger: Monitoring alert / User report / Agent detection

Infrastructure Maintainer:
1. Confirm the alert
2. Assess scope and impact
   - How many users affected?
   - Which services affected?
   - Is data at risk?
3. Classify severity level (P0/P1/P2/P3)
4. Activate appropriate response team
5. Create incident channel/thread

Output: Incident classification + Response team activated
```

### Step 2: Investigation (5-30 minutes)

```
Parallel investigation:

Infrastructure Maintainer:
├── Check system metrics (CPU, memory, network, disk)
├── Review error logs
├── Check recent deployments
└── Verify external dependencies

Backend Architect (if P0/P1):
├── Check database health
├── Review API error rates
├── Check service communication
└── Identify failing component

DevOps Automator:
├── Review recent deployment history
├── Check CI/CD pipeline status
├── Prepare rollback (if needed)
└── Verify infrastructure state

Output: Root cause identified (or narrowed to component)
```

### Step 3: Mitigation (15-60 minutes)

```
Decision tree:

If caused by recent deployment:
  → DevOps Automator: Execute rollback
  → Infrastructure Maintainer: Verify recovery
  → Evidence Collector: Confirm fix

If caused by infrastructure issue:
  → Infrastructure Maintainer: Scale/restart/failover
  → DevOps Automator: Support infrastructure changes
  → Verify recovery

If caused by code bug:
  → Relevant Developer Agent: Implement hotfix
  → Evidence Collector: Verify fix
  → DevOps Automator: Deploy hotfix
  → Infrastructure Maintainer: Monitor recovery

If caused by external dependency:
  → Infrastructure Maintainer: Activate backup/cache
  → Support Responder: Communicate to users
  → Monitor external recovery

Throughout:
  → Support Responder: Update status page every 15 minutes
  → Executive Summary Generator: Brief executives (P0 only)
```

### Step 4: Resolution Verification (after fix)

```
Evidence Collector:
1. Verify the fix resolved the issue
2. Screenshot evidence of working state
3. Confirm no new issues introduced

Infrastructure Maintainer:
1. Verify all metrics return to normal
2. Confirm no cascading failures
3. Monitor for 30 minutes after fix

API Tester (if API-related):
1. Run regression on affected endpoints
2. Verify response times return to normal
3. Confirm error rates at baseline

Output: Incident resolved confirmation
```

### Step 5: Post-Mortem (within 48 hours)

```
Workflow Optimizer leads post-mortem:

1. Timeline Reconstruction
   - When was the problem introduced?
   - When was it detected?
   - When was it resolved?
   - Total user impact duration

2. Root Cause Analysis
   - What failed?
   - Why did it fail?
   - Why wasn't it caught earlier?
   - 5 Whys analysis

3. Impact Assessment
   - Users affected
   - Revenue impact
   - Reputation impact
   - Data impact

4. Preventive Measures
   - What monitoring would have caught this faster?
   - What testing would have prevented this?
   - What process changes are needed?
   - What infrastructure changes are needed?

5. Action Items
   - [Action] → [Owner] → [Due Date]
   - [Action] → [Owner] → [Due Date]
   - [Action] → [Owner] → [Due Date]

Output: Post-mortem report → Sprint Prioritizer adds prevention tasks to backlog
```

## Communication Templates

### Status Page Update (Support Responder)

```
[Timestamp] — [Service Name] Incident

Status: [Investigating / Identified / Monitoring / Resolved]
Impact: [Description of user impact]
Current Action: [What we are doing]
Next Update: [Expected time of next update]
```

### Executive Update (Executive Summary Generator — P0 only)

```
Incident Briefing — [Timestamp]

Situation: [Service] [down/degraded] affecting [N users/% traffic]
Cause: [Known/Under investigation] — [Brief description if known]
Action: [What is being done] — ETA [Time estimate]
Impact: [Business impact — revenue, users, reputation]
Next Update: [Timestamp]
```

## Escalation Matrix

| Condition | Escalate To | Action |
|-----------|------------|--------|
| P0 not resolved within 30 minutes | Studio Producer | Additional resources, vendor escalation |
| P1 not resolved within 2 hours | Project Shepherd | Resource reallocation |
| Suspected data breach | Legal Compliance Checker | Regulatory notification assessment |
| User data affected | Legal Compliance Checker + Executive Summary Generator | GDPR/CCPA notification |
| Revenue impact > $X | Finance Tracker + Studio Producer | Business impact assessment |
