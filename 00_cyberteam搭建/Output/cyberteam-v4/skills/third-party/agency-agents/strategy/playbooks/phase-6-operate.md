# Phase 6 Playbook — Operate & Evolve

> **Duration**: Ongoing | **Agents**: 12+ (rotating) | **Governance**: Studio Producer

---

## Objective

Ongoing operations and continuous improvement. The product is live — now make it thrive. This phase has no end date; it runs as long as the product runs in the market.

## Prerequisites

- [ ] Phase 5 quality gate passed (stable launch)
- [ ] Phase 5 handoff package received
- [ ] Operational rhythm established
- [ ] Baseline metrics recorded

## Operational Rhythm

### Continuous (Always Active)

| Agent | Responsibility | SLA |
|-------|---------------|-----|
| **Infrastructure Maintainer** | Uptime, performance, security | 99.9% uptime, < 30 min MTTR |
| **Support Responder** | Customer support, issue resolution | < 4 hour first response |
| **DevOps Automator** | Deployment pipeline, hotfixes | Multiple deployments per day capability |

### Daily

| Agent | Activity | Output |
|-------|----------|--------|
| **Analytics Reporter** | KPI dashboard update | Daily metrics snapshot |
| **Support Responder** | Issue triage and resolution | Support ticket summary |
| **Infrastructure Maintainer** | System health check | Health status report |

### Weekly

| Agent | Activity | Output |
|-------|----------|--------|
| **Analytics Reporter** | Weekly performance analysis | Weekly analytics report |
| **Feedback Synthesizer** | User feedback synthesis | Weekly feedback summary |
| **Sprint Prioritizer** | Backlog grooming + Sprint planning | Sprint plan |
| **Growth Hacker** | Growth channel optimization | Growth metrics report |
| **Project Shepherd** | Cross-team coordination | Weekly status update |

### Bi-Weekly

| Agent | Activity | Output |
|-------|----------|--------|
| **Feedback Synthesizer** | Deep feedback analysis | Bi-weekly insights report |
| **Experiment Tracker** | A/B test analysis | Experiment results summary |
| **Content Creator** | Content calendar execution | Published content report |

### Monthly

| Agent | Activity | Output |
|-------|----------|--------|
| **Executive Summary Generator** | C-suite reporting | Monthly executive summary |
| **Finance Tracker** | Financial performance review | Monthly financial report |
| **Legal Compliance Checker** | Regulatory monitoring | Compliance status report |
| **Trend Researcher** | Market intelligence update | Monthly market brief |
| **Brand Guardian** | Brand consistency audit | Brand health report |

### Quarterly

| Agent | Activity | Output |
|-------|----------|--------|
| **Studio Producer** | Strategic portfolio review | Quarterly strategic review |
| **Workflow Optimizer** | Process efficiency audit | Optimization report |
| **Performance Benchmarker** | Performance regression testing | Quarterly performance report |
| **Tool Evaluator** | Technology stack review | Technical debt assessment |

## Continuous Improvement Loop

```
Measure (Analytics Reporter)
    │
    ▼
Analyze (Feedback Synthesizer + Data Analytics Reporter)
    │
    ▼
Plan (Sprint Prioritizer + Studio Producer)
    │
    ▼
Build (Phase 3 Dev↔QA loop — mini-loop)
    │
    ▼
Verify (Evidence Collector + Reality Checker)
    │
    ▼
Deploy (DevOps Automator)
    │
    ▼
Measure (return to start)
```

### Feature Development in Phase 6

New features follow a compressed NEXUS cycle:

```
1. Sprint Prioritizer selects feature from backlog
2. Appropriate developer agent implements
3. Evidence Collector verifies (Dev↔QA loop)
4. DevOps Automator deploys (feature flag or direct)
5. Experiment Tracker monitors (A/B testing if applicable)
6. Analytics Reporter measures impact
7. Feedback Synthesizer collects user response
```

## Incident Response Protocol

### Severity Levels

| Level | Definition | Response Time | Decision Authority |
|-------|-----------|---------------|-------------------|
| **P0 — Critical** | Service outage, data loss, security breach | Immediate | Studio Producer |
| **P1 — High** | Major feature broken, significant degradation | < 1 hour | Project Shepherd |
| **P2 — Medium** | Minor feature issues, workaround available | < 4 hours | Agent Orchestrator |
| **P3 — Low** | Cosmetic issues, minor inconveniences | Next sprint | Sprint Prioritizer |

### Incident Response Sequence

```
Detect (Infrastructure Maintainer or Support Responder)
    │
    ▼
Classify (Agent Orchestrator)
    ├── Classify severity level (P0-P3)
    ├── Assign response team
    └── Notify stakeholders
    │
    ▼
Respond
    ├── P0: Infrastructure Maintainer + DevOps Automator + Backend Architect
    ├── P1: Relevant developer agent + DevOps Automator
    ├── P2: Relevant developer agent
    └── P3: Add to sprint backlog
    │
    ▼
Resolve
    ├── Fix implemented and deployed
    ├── Evidence Collector verifies fix
    └── Infrastructure Maintainer confirms stability
    │
    ▼
Post-Mortem
    ├── Workflow Optimizer leads retrospective
    ├── Document root cause analysis
    ├── Identify preventive measures
    └── Implement process improvements
```

## Growth Operations

### Monthly Growth Review (led by Growth Hacker)

```
1. Channel Performance Analysis
   - Acquisition by channel (organic, paid, referral, social)
   - CAC by channel
   - Conversion rates by funnel stage
   - LTV:CAC ratio trends

2. Experiment Results
   - Completed A/B tests and results
   - Statistical significance verification
   - Winner implementation status
   - New experiment pipeline

3. Retention Analysis
   - Cohort retention curves
   - Churn risk identification
   - Re-engagement campaign results
   - Feature adoption metrics

4. Growth Roadmap Update
   - Next month's growth experiments
   - Channel budget reallocation
   - New channel exploration
   - Viral coefficient optimization
```

### Content Operations (Content Creator + Social Media Strategist)

```
Weekly:
- Content calendar execution
- Social media engagement
- Community management
- Performance tracking

Monthly:
- Content performance review
- Editorial calendar planning
- Platform algorithm updates
- Content strategy refinement

Platform-specific:
- Twitter Interactor → Daily engagement, weekly thread
- Instagram Curator → 3-5 posts/week, daily stories
- TikTok Strategist → 3-5 videos/week
- Reddit Community Builder → Daily authentic engagement
```

## Finance Operations

### Monthly Financial Review (Finance Tracker)

```
1. Revenue Analysis
   - MRR/ARR tracking
   - Revenue by segment/plan
   - Expansion revenue
   - Churn revenue impact

2. Cost Analysis
   - Infrastructure costs
   - Marketing spend by channel
   - Team/resource costs
   - Tool and service costs

3. Unit Economics
   - CAC trends
   - LTV trends
   - LTV:CAC ratio
   - Payback period

4. Forecasting
   - Revenue forecast (3-month rolling)
   - Cost forecast
   - Cash flow forecast
   - Budget variance analysis
```

## Compliance Operations

### Monthly Compliance Check (Legal Compliance Checker)

```
1. Regulatory Monitoring
   - New regulations affecting product
   - Changes to existing regulations
   - Industry enforcement actions
   - Compliance deadline tracking

2. Privacy Compliance
   - Data subject request processing
   - Consent management effectiveness
   - Data retention policy adherence
   - Cross-border transfer compliance

3. Security Compliance
   - Vulnerability scan results
   - Patch management status
   - Access control review
   - Event log review

4. Audit Preparation
   - Documentation currency
   - Evidence collection status
   - Training completion rates
   - Policy acknowledgment tracking
```

## Strategic Evolution

### Quarterly Strategic Review (Studio Producer)

```
1. Market Position Assessment
   - Competitive landscape changes (Trend Researcher input)
   - Market share evolution
   - Brand perception (Brand Guardian input)
   - Customer satisfaction trends (Feedback Synthesizer input)

2. Product Strategy
   - Feature roadmap review
   - Technical debt assessment (Tool Evaluator input)
   - Platform expansion opportunities
   - Partnership evaluation

3. Growth Strategy
   - Channel effectiveness review
   - New market opportunities
   - Pricing strategy evaluation
   - Expansion planning

4. Organizational Health
   - Process efficiency (Workflow Optimizer input)
   - Team performance metrics
   - Resource allocation optimization
   - Capability development needs

Output: Quarterly strategic review → Updated roadmap and priorities
```

## Phase 6 Success Metrics

| Category | Metric | Target | Owner |
|----------|--------|--------|-------|
| **Reliability** | System uptime | > 99.9% | Infrastructure Maintainer |
| **Reliability** | MTTR | < 30 min | Infrastructure Maintainer |
| **Growth** | MoM user growth | > 20% | Growth Hacker |
| **Growth** | Activation rate | > 60% | Analytics Reporter |
| **Retention** | Day 7 retention | > 40% | Analytics Reporter |
| **Retention** | Day 30 retention | > 20% | Analytics Reporter |
| **Finance** | LTV:CAC ratio | > 3:1 | Finance Tracker |
| **Finance** | Portfolio ROI | > 25% | Studio Producer |
| **Quality** | NPS score | > 50 | Feedback Synthesizer |
| **Quality** | Support resolution time | < 4 hours | Support Responder |
| **Compliance** | Regulatory adherence | > 98% | Legal Compliance Checker |
| **Efficiency** | Deployment frequency | Multiple per day | DevOps Automator |
| **Efficiency** | Process improvement | 20% per quarter | Workflow Optimizer |

---

*Phase 6 has no end date. It runs as long as the product runs in the market, with the continuous improvement loop driving the product forward. For major new features or pivots, the NEXUS pipeline can be reactivated (NEXUS-Sprint or NEXUS-Micro).*
