# NEXUS Quick Start Guide

> **From zero to coordinated multi-agent pipeline in 5 minutes.**

---

## What is NEXUS?

**NEXUS** (Network of Experts, Unified Strategy) transforms your agency's AI experts into a coordinated pipeline. Instead of activating one agent at a time and hoping they work together, NEXUS precisely defines who does what at what time, and how to verify quality at every step.

## Choose Your Mode

| I want to... | Use | Agents | Time |
|-------------|-----|--------|------|
| Build a complete product from scratch | **NEXUS-Full** | All | 12-24 weeks |
| Build a feature or MVP | **NEXUS-Sprint** | 15-25 | 2-6 weeks |
| Do a specific task (bug fix, campaign, audit) | **NEXUS-Micro** | 5-10 | 1-5 days |

---

## NEXUS-Full: Launch a Complete Project

**Copy this prompt to activate the full pipeline:**

```
Activate the Agent Orchestrator in NEXUS-Full mode.

Project: [Your project name]
Spec: [Describe your project or link to spec]

Execute the full NEXUS pipeline:
- Phase 0: Discovery (Trend Researcher, Feedback Synthesizer, UX Researcher, Analytics Reporter, Legal Compliance Checker, Tool Evaluator)
- Phase 1: Strategy (Studio Producer, Senior Project Manager, Sprint Prioritizer, UX Architect, Brand Guardian, Backend Architect, Finance Tracker)
- Phase 2: Foundation (DevOps Automator, Frontend Developer, Backend Architect, UX Architect, Infrastructure Maintainer)
- Phase 3: Build (Dev↔QA Loop — all engineering + Evidence Collector)
- Phase 4: Hardening (Reality Checker, Performance Benchmarker, API Tester, Legal Compliance Checker)
- Phase 5: Launch (Growth Hacker, Content Creator, all marketing agents, DevOps Automator)
- Phase 6: Operate (Analytics Reporter, Infrastructure Maintainer, Support Responder, ongoing)

Quality gates between every phase. All assessments require evidence.
Max 3 retries per task, then escalate.
```

---

## NEXUS-Sprint: Build a Feature or MVP

**Copy this prompt:**

```
Activate the Agent Orchestrator in NEXUS-Sprint mode.

Feature/MVP: [Describe what you want to build]
Timeline: [Target number of weeks]
Skip Phase 0 (market is validated).

Sprint Team:
- PM: Senior Project Manager, Sprint Prioritizer
- Design: UX Architect, Brand Guardian
- Engineering: Frontend Developer, Backend Architect, DevOps Automator
- QA: Evidence Collector, Reality Checker, API Tester
- Support: Analytics Reporter

Start with Phase 1 architecture and Sprint planning.
Run Dev↔QA loop for all implementation tasks.
Reality Checker approval required before launch.
```

---

## NEXUS-Micro: Execute Specific Tasks

**Choose your scenario and copy the prompt:**

### Fix a Bug
```
Activate the Backend Architect to investigate and fix [bug description].
After fix, activate the API Tester to verify the fix.
Then activate the Evidence Collector to confirm no visual regressions.
```

### Run a Marketing Campaign
```
Activate the Social Media Strategist as campaign lead for [campaign description].
Team: Content Creator, Twitter Interactor, Instagram Curator, Reddit Community Builder.
Brand Guardian reviews all content before posting.
Analytics Reporter tracks performance daily.
Growth Hacker optimizes channels weekly.
```

### Conduct a Compliance Audit
```
Activate the Legal Compliance Checker for a full compliance audit.
Scope: [GDPR / CCPA / HIPAA / All]
After audit, activate the Executive Summary Generator to create stakeholder report.
```

### Investigate Performance Issues
```
Activate the Performance Benchmarker to diagnose performance issues.
Scope: [API response time / Page load / Database queries / All]
After diagnosis, activate the Infrastructure Maintainer for optimization.
DevOps Automator deploys any infrastructure changes.
```

### Market Research
```
Activate the Trend Researcher for market intelligence research on [domain].
Deliverables: Competitive landscape, market size, trend forecasting.
After research, activate the Executive Summary Generator to create executive brief.
```

### UX Improvements
```
Activate the UX Researcher to identify usability issues in [feature/product].
After research, activate the UX Architect to design improvements.
Frontend Developer implements the changes.
Evidence Collector verifies the improvements.
```

---

## Strategy Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Main Strategy** | Complete NEXUS principles | `strategy/nexus-strategy.md` |
| **Phase 0 Playbook** | Discovery and intelligence | `strategy/playbooks/phase-0-discovery.md` |
| **Phase 1 Playbook** | Strategy and architecture | `strategy/playbooks/phase-1-strategy.md` |
| **Phase 2 Playbook** | Foundation and scaffolding | `strategy/playbooks/phase-2-foundation.md` |
| **Phase 3 Playbook** | Build and iterate | `strategy/playbooks/phase-3-build.md` |
| **Phase 4 Playbook** | Quality and hardening | `strategy/playbooks/phase-4-hardening.md` |
| **Phase 5 Playbook** | Launch and growth | `strategy/playbooks/phase-5-launch.md` |
| **Phase 6 Playbook** | Operate and evolve | `strategy/playbooks/phase-6-operate.md` |
| **Activation Prompts** | Ready-to-use agent prompts | `strategy/coordination/agent-activation-prompts.md` |
| **Handoff Templates** | Standardized handoff formats | `strategy/coordination/handoff-templates.md` |
| **Startup MVP Runbook** | 4-6 week MVP build | `strategy/runbooks/scenario-startup-mvp.md` |
| **Enterprise Feature Runbook** | Enterprise feature development | `strategy/runbooks/scenario-enterprise-feature.md` |
| **Marketing Campaign Runbook** | Multi-channel campaigns | `strategy/runbooks/scenario-marketing-campaign.md` |
| **Incident Response Runbook** | Production incident handling | `strategy/runbooks/scenario-incident-response.md` |

---

## 30-Second Key Concepts

1. **Quality Gates** — No phase advances without evidence-based approval
2. **Dev↔QA Loop** — Every task is built then tested; pass to continue, fail to retry (max 3 times)
3. **Handoffs** — Structured context transfer between agents (never cold start)
4. **Reality Checker** — Final quality authority; default "needs work" posture
5. **Agent Orchestrator** — Pipeline controller that manages the entire process
6. **Evidence Over Claims** — Screenshots, test results, and data — not assertions

---

## Agent Overview

```
Engineering                 │ Design                │ Marketing
Frontend Developer          │ UI Designer           │ Growth Hacker
Backend Architect          │ UX Researcher         │ Content Creator
Mobile App Builder         │ UX Architect          │ Twitter Interactor
AI Engineer               │ Brand Guardian        │ TikTok Strategist
DevOps Automator          │ Visual Storyteller   │ Instagram Curator
Rapid Prototyper          │ Whimsy Injector      │ Reddit Community Builder
Senior Developer          │ Image Prompt Engineer │ App Store Optimizer
                           │                      │ Social Media Strategist
───────────────────────────┼───────────────────────┼──────────────────────
Product                    │ Project Management    │ Testing
Sprint Prioritizer        │ Studio Producer       │ Evidence Collector
Trend Researcher          │ Project Shepherd      │ Reality Checker
Feedback Synthesizer      │ Studio Operations     │ Test Results Analyzer
                           │ Experiment Tracker   │ Performance Benchmarker
                           │ Senior PM            │ API Tester
                           │                      │ Tool Evaluator
                           │                      │ Workflow Optimizer
───────────────────────────┼───────────────────────┼──────────────────────
Support                    │ Spatial Computing     │ Specialized
Support Responder          │ XR Interface Architect│ Agent Orchestrator
Analytics Reporter        │ macOS Spatial/Metal Engineer │ Data Analytics Reporter
Finance Tracker           │ XR Immersive Developer│ LSP/Index Engineer
Infrastructure Maintainer │ XR Cockpit Expert    │ Sales Data Extraction
Legal Compliance          │ visionOS Spatial Engineer│ Data Consolidation
Executive Summary Generator│ Terminal Integration │ Report Distribution
```

---

<div align="center">

**Start with one mode. Follow the playbook. Trust the pipeline.**

`strategy/nexus-strategy.md` — Complete principles

</div>
