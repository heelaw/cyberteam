# Phase 0 Playbook — Intelligence & Discovery

> **Duration**: 3-7 days | **Agents**: 6 | **Gate Keeper**: Executive Summary Generator

---

## Objective

Validate the opportunity before committing resources. Do not build before understanding the problem, market, and regulatory environment.

## Prerequisites

- [ ] Project brief or initial concept exists
- [ ] Stakeholder sponsor identified
- [ ] Discovery phase budget approved

## Agent Activation Sequence

### First Wave: Parallel Launch (Day 1)

#### Trend Researcher — Market Intelligence Lead

```
Activate the Trend Researcher for market intelligence research on [project domain].

Required Deliverables:
1. Competitive landscape analysis (direct + indirect competitors)
2. Market size: TAM, SAM, SOM with methodology
3. Trend lifecycle mapping: Where is this market on the adoption curve?
4. 3-6 month trend forecast with confidence intervals
5. Investment and funding trends in the space

Sources: Minimum 15 unique verified sources
Format: Strategic report with executive summary
Timeline: 3 days
```

#### Feedback Synthesizer — User Needs Analysis

```
Activate the Feedback Synthesizer for user needs analysis on [project domain].

Required Deliverables:
1. Multi-channel feedback collection plan (surveys, interviews, reviews, social)
2. Sentiment analysis across existing user touchpoints
3. Pain point identification and prioritization (RICE scoring)
4. Feature request analysis with business value estimates
5. Churn risk indicators from feedback patterns

Format: Comprehensive feedback report with priority matrix
Timeline: 3 days
```

#### UX Researcher — User Behavior Analysis

```
Activate the UX Researcher for user behavior analysis on [project domain].

Required Deliverables:
1. User interview plan (5-10 target users)
2. User persona development (3-5 primary personas)
3. Journey mapping for key user flows
4. Usability heuristic evaluation of competitor products
5. Behavior insights with statistical validation

Format: Research findings report with personas and journey maps
Timeline: 5 days
```

### Second Wave: Parallel Launch (Day 1, independent of First Wave)

#### Analytics Reporter — Data Landscape Assessment

```
Activate the Analytics Reporter for data landscape assessment on [project domain].

Required Deliverables:
1. Existing data sources audit (what data is available?)
2. Signal identification (what can we measure?)
3. Baseline metrics establishment
4. Data quality assessment with completeness scoring
5. Analytics infrastructure recommendations

Format: Data audit report with signal map
Timeline: 2 days
```

#### Legal Compliance Checker — Regulatory Scan

```
Activate the Legal Compliance Checker for regulatory scan on [project domain].

Required Deliverables:
1. Applicable regulatory frameworks (GDPR, CCPA, HIPAA, etc.)
2. Data processing requirements and constraints
3. Jurisdictional mapping for target markets
4. Compliance risk assessment with severity ratings
5. Blocking vs. manageable compliance issues

Format: Compliance requirements matrix
Timeline: 3 days
```

#### Tool Evaluator — Technology Landscape

```
Activate the Tool Evaluator for technology landscape assessment on [project domain].

Required Deliverables:
1. Technology stack assessment for problem domain
2. Build vs. buy analysis for key components
3. Integration feasibility with existing systems
4. Open source vs. commercial evaluation
5. Technology risk assessment

Format: Technology stack assessment with recommendation matrix
Timeline: 2 days
```

## Convergence Point (Day 5-7)

Six agents have all delivered their reports. The Executive Summary Generator synthesizes:

```
Activate the Executive Summary Generator to synthesize Phase 0 findings.

Input Documents:
1. Trend Researcher → Market analysis report
2. Feedback Synthesizer → Comprehensive feedback report
3. UX Researcher → Research findings report
4. Analytics Reporter → Data audit report
5. Legal Compliance Checker → Compliance requirements matrix
6. Tool Evaluator → Technology stack assessment

Output: Executive summary (≤500 words, SCQA format)
Decision needed: Continue / Do Not Continue / Pivot

Include: Quantified market opportunity, validated user needs, regulatory path, technical feasibility
```

## Quality Gate Checklist

| # | Standard | Evidence Source | Status |
|---|-----------|----------------|--------|
| 1 | Market opportunity validated, TAM > minimum viable threshold | Trend Researcher report | ☐ |
| 2 | ≥3 validated user pain points with supporting data | Feedback Synthesizer + UX Researcher | ☐ |
| 3 | No blocking compliance issues found | Legal Compliance Checker matrix | ☐ |
| 4 | Key metrics and data sources identified | Analytics Reporter audit | ☐ |
| 5 | Technology stack viable and assessed | Tool Evaluator assessment | ☐ |
| 6 | Executive summary delivered with continue/no-go recommendation | Executive Summary Generator | ☐ |

## Gate Decision

- **Continue**: Proceed to Phase 1 — Strategy & Architecture
- **Do Not Continue**: Archive findings, record learnings, redirect resources
- **Pivot**: Modify scope/direction based on findings, rerun targeted discovery

## Handoff to Phase 1

```markdown
## Phase 0 → Phase 1 Handoff Package

### Documents to Carry Forward:
1. Market analysis report (Trend Researcher)
2. Comprehensive feedback report (Feedback Synthesizer)
3. User personas and journey maps (UX Researcher)
4. Data audit report (Analytics Reporter)
5. Compliance requirements matrix (Legal Compliance Checker)
6. Technology stack assessment (Tool Evaluator)
7. Executive summary with continue decision (Executive Summary Generator)

### Key Constraints Identified:
- [Regulatory constraints from Legal Compliance Checker]
- [Technical constraints from Tool Evaluator]
- [Market timing constraints from Trend Researcher]

### Priority User Needs (for Sprint Prioritizer):
1. [Pain point 1 — from Feedback Synthesizer]
2. [Pain point 2 — from UX Researcher]
3. [Pain point 3 — from Feedback Synthesizer]
```

---

*Phase 0 is complete when the Executive Summary Generator delivers the continue decision with supporting evidence from all six discovery agents.*
