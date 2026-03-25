# Phase 3 Playbook — Build & Iterate

> **Duration**: 2-12 weeks (varies by scope) | **Agents**: 15-30+ | **Gate Keeper**: Agent Orchestrator

---

## Objective

Implement all features through continuous Dev↔QA loops. Every task is verified before moving to the next. This is where most of the work happens — and where NEXUS's orchestration delivers the most value.

## Prerequisites

- [ ] Phase 2 quality gate passed (foundation verified)
- [ ] Sprint Prioritizer backlog available with RICE scores calculated
- [ ] CI/CD pipeline operational
- [ ] Design system and component library ready
- [ ] API scaffold with authentication system ready

## The Dev↔QA Loop — Core Mechanism

The Agent Orchestrator manages every task through this loop:

```
For each task in sprint_backlog (sorted by RICE score):

  1. Assign task to appropriate developer agent (see assignment matrix)
  2. Developer implements the task
  3. Evidence Collector tests the task
     - Visual screenshots (desktop, tablet, mobile)
     - Functional verification against acceptance criteria
     - Brand consistency check
  4. If verdict == pass:
       Mark task complete
       Move to next task
     Else if verdict == fail AND attempts < 3:
       Send QA feedback to developer
       Developer fixes specific issues
       Return to step 3
     Else if attempts >= 3:
       Escalate to Agent Orchestrator
       Orchestrator decides: reassign, decompose, defer, or accept
  5. Update pipeline status report
```

## Agent Assignment Matrix

### Primary Developer Assignments

| Task Category | Primary Agent | Backup Agent | QA Agent |
|--------------|--------------|-------------|----------|
| **React/Vue/Angular UI** | Frontend Developer | Rapid Prototyper | Evidence Collector |
| **REST/GraphQL API** | Backend Architect | Senior Developer | API Tester |
| **Database Operations** | Backend Architect | — | API Tester |
| **Mobile (iOS/Android)** | Mobile App Builder | — | Evidence Collector |
| **ML Models/Pipelines** | AI Engineer | — | Test Results Analyzer |
| **CI/CD/Infrastructure** | DevOps Automator | Infrastructure Maintainer | Performance Benchmarker |
| **Advanced/Complex Features** | Senior Developer | Backend Architect | Evidence Collector |
| **Rapid Prototype/POC** | Rapid Prototyper | Frontend Developer | Evidence Collector |
| **WebXR/Immersive** | XR Immersive Developer | — | Evidence Collector |
| **visionOS** | visionOS Spatial Engineer | macOS Spatial/Metal Engineer | Evidence Collector |
| **Cockpit Controls** | XR Cockpit Interaction Specialist | XR Interface Architect | Evidence Collector |
| **CLI/Terminal Tools** | Terminal Integration Specialist | — | API Tester |
| **Code Intelligence** | LSP/Index Engineer | — | Test Results Analyzer |
| **Performance Optimization** | Performance Benchmarker | Infrastructure Maintainer | Performance Benchmarker |

### Expert Support (Activated As Needed)

| Expert | When to Activate | Trigger |
|-----------|-----------------|---------|
| UI Designer | Component needs visual improvement | Developer requests design guidance |
| Whimsy Injector | Feature needs delight/personality | UX review finds opportunities |
| Visual Storyteller | Visual content needs visual narrative | Content needs visual assets |
| Brand Guardian | Brand consistency concern | QA finds brand deviation |
| XR Interface Architect | Spatial interaction design needed | XR feature needs UX guidance |
| Data Analytics Reporter | Deep data analysis needed | Feature needs analytics integration |

## Parallel Build Tracks

For NEXUS-Full deployments, four tracks run simultaneously:

### Track A: Core Product Development

```
Manager: Agent Orchestrator (Dev↔QA loops)
Agents: Frontend Developer, Backend Architect, AI Engineer,
        Mobile App Builder, Senior Developer
QA: Evidence Collector, API Tester, Test Results Analyzer

Sprint rhythm: 2-week sprints
Daily: Task implementation + QA verification
Sprint end: Sprint review + retrospective
```

### Track B: Growth & Marketing Prep

```
Manager: Project Shepherd
Agents: Growth Hacker, Content Creator, Social Media Strategist,
        App Store Optimizer

Rhythm: Aligned with Track A milestones
Activities:
- Growth Hacker → Design viral loops and referral mechanisms
- Content Creator → Build launch content pipeline
- Social Media Strategist → Plan cross-platform campaigns
- App Store Optimizer → Prepare store listings (if mobile)
```

### Track C: Quality & Operations

```
Manager: Agent Orchestrator
Agents: Evidence Collector, API Tester, Performance Benchmarker,
        Workflow Optimizer, Experiment Tracker

Continuous activities:
- Evidence Collector → Screenshot QA for every task
- API Tester → Endpoint verification for every API task
- Performance Benchmarker → Periodic load testing
- Workflow Optimizer → Process improvement identification
- Experiment Tracker → A/B test setup for validated features
```

### Track D: Brand & Experience Polish

```
Manager: Brand Guardian
Agents: UI Designer, Brand Guardian, Visual Storyteller,
        Whimsy Injector

Triggered activities:
- UI Designer → Component improvements when QA finds visual issues
- Brand Guardian → Periodic brand consistency audits
- Visual Storyteller → Visual narrative assets when features complete
- Whimsy Injector → Micro-interactions and delight moments
```

## Sprint Execution Template

### Sprint Planning (Day 1)

```
Sprint Prioritizer activation:
1. Review updated RICE-scored backlog
2. Select sprint tasks based on team velocity
3. Assign tasks to developer agents
4. Identify dependencies and ordering
5. Set sprint goals and success criteria

Output: Sprint plan with task assignments
```

### Daily Execution (Day 2 to Day N-1)

```
Agent Orchestrator manages:
1. Current task status check
2. Dev↔QA loop execution
3. Blocker identification and resolution
4. Progress tracking and reporting

Status report format:
- Tasks completed today: [list]
- Tasks in QA: [list]
- Tasks in development: [list]
- Tasks blocked: [list and reason]
- QA pass rate: [X/Y]
```

### Sprint Review (Day N)

```
Project Shepherd facilitates:
1. Demo of completed features
2. Review QA evidence for each task
3. Collect stakeholder feedback
4. Update backlog based on learnings

Participants: All active agents + stakeholders
Output: Sprint review summary
```

### Sprint Retrospective

```
Workflow Optimizer facilitates:
1. What went well?
2. What can we improve?
3. What will we change next sprint?
4. Process efficiency metrics

Output: Retrospective action items
```

## Orchestrator Decision Logic

### Task Failure Handling

```
When a task fails QA:
  If attempt == 1:
    → Send specific QA feedback to developer
    → Developer fixes only identified issues
    → Resubmit for QA

  If attempt == 2:
    → Send cumulative QA feedback
    → Consider: Is the developer agent appropriate?
    → Developer fixes with additional context
    → Resubmit for QA

  If attempt == 3:
    → Escalate
    → Options:
      a) Reassign to different developer agent
      b) Decompose task into smaller subtasks
      c) Revise approach/architecture
      d) Accept known limitation (document)
      e) Defer to future sprint
    → Document decision and rationale
```

### Parallel Task Management

```
When multiple tasks have no dependencies:
  → Assign simultaneously to different developer agents
  → Each runs independent Dev↔QA loop
  → Orchestrator tracks all loops simultaneously
  → Merge completed tasks in dependency order

When tasks have dependencies:
  → Wait for dependency to pass QA
  → Then assign dependent task
  → Include dependency context in handoff
```

## Quality Gate Checklist

| # | Standard | Evidence Source | Status |
|---|-----------|----------------|--------|
| 1 | All sprint tasks pass QA (100% complete) | Evidence Collector screenshots per task | ☐ |
| 2 | All API endpoints verified | API Tester regression report | ☐ |
| 3 | Performance baseline met (P95 < 200ms) | Performance Benchmarker report | ☐ |
| 4 | Brand consistency verified (95%+ adherence) | Brand Guardian audit | ☐ |
| 5 | No critical bugs (zero P0/P1 open) | Test Results Analyzer summary | ☐ |
| 6 | All acceptance criteria met | Per-task verification | ☐ |
| 7 | All PRs have completed code review | Git history evidence | ☐ |

## Gate Decision

**Gate Keeper**: Agent Orchestrator

- **Pass**: Feature-complete application → Activate Phase 4
- **Continue**: Need more sprints → Continue Phase 3
- **Escalate**: Systemic issues → Studio Producer intervention

## Handoff to Phase 4

```markdown
## Phase 3 → Phase 4 Handoff Package

### For Reality Checker:
- Complete application (all features implemented)
- All QA evidence from Dev↔QA loops
- API Tester regression results
- Performance Benchmarker baseline data
- Brand Guardian consistency audit
- List of known issues (if accepted limitations exist)

### For Legal Compliance Checker:
- Data processing implementation details
- Privacy policy implementation
- Consent management implementation
- Security measures implemented

### For Performance Benchmarker:
- Application URL for load testing
- Expected traffic patterns
- Performance budget in architecture

### For Infrastructure Maintainer:
- Production environment requirements
- Scaling configuration needs
- Monitoring alert thresholds
```

---

*Phase 3 is complete when all sprint tasks pass QA, all API endpoints verified, performance baselines met, and no critical bugs are open.*
