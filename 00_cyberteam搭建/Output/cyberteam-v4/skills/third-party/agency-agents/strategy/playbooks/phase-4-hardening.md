# Phase 4 Playbook — Quality & Hardening

> **Duration**: 3-7 days | **Agents**: 8 | **Gate Keeper**: Reality Checker (sole authority)

---

## Objective

The final quality inspection. Reality Checker's default verdict is "needs work" — you must prove production readiness with overwhelming evidence. This phase exists because first implementations typically need 2-3 revision cycles, and that's healthy.

## Prerequisites

- [ ] Phase 3 quality gate passed (all tasks QA'd)
- [ ] Phase 3 handoff package received
- [ ] All features implemented and individually verified

## Key Mindset

> **Reality Checker's default verdict is needs work.**

> This isn't pessimism — it's realism. Production readiness requires:
> - Complete user journeys working end-to-end
> - Cross-device consistency (desktop, tablet, mobile)
> - Performance under load (not just happy path)
> - Security verification (not just "we added authentication")
> - Spec compliance (every requirement, not just most)

> First-pass B/B+ ratings are normal and expected.

## Agent Activation Sequence

### Step 1: Evidence Collection (Day 1-2, All Parallel)

#### Evidence Collector — Comprehensive Visual Evidence

```
Activate the Evidence Collector for comprehensive system evidence collection on [project].

Required Deliverables:
1. Complete screenshot suite:
   - Desktop (1920x1080) — every page/view
   - Tablet (768x1024) — every page/view
   - Mobile (375x667) — every page/view
2. Interaction evidence:
   - Navigation flows (before/after clicks)
   - Form interactions (empty, filled, submitted, error states)
   - Modal/dialog interactions
   - Accordion/expandable content
3. Theme evidence:
   - Light mode — all pages
   - Dark mode — all pages
   - System preference detection
4. Error state evidence:
   - 404 pages
   - Form validation errors
   - Network error handling
   - Empty states

Format: Screenshot evidence package with test-results.json
Timeline: 2 days
```

#### API Tester — Complete API Regression

```
Activate the API Tester for complete API regression on [project].

Required Deliverables:
1. Endpoint regression suite:
   - All endpoints tested (GET, POST, PUT, DELETE)
   - Authentication/authorization verification
   - Input validation testing
   - Error response verification
2. Integration tests:
   - Cross-service communication
   - Database operation verification
   - External API integrations
3. Edge case testing:
   - Rate limiting behavior
   - Large payload handling
   - Concurrent request handling
   - Malformed input handling

Format: API test report with pass/fail per endpoint
Timeline: 2 days
```

#### Performance Benchmarker — Load Testing

```
Activate the Performance Benchmarker for load testing on [project].

Required Deliverables:
1. Load test at 10x expected traffic:
   - Response time distribution (P50, P95, P99)
   - Throughput under load
   - Error rate under load
   - Resource utilization (CPU, memory, network)
2. Core Web Vitals measurement:
   - LCP (Largest Contentful Paint) < 2.5s
   - FID (First Input Delay) < 100ms
   - CLS (Cumulative Layout Shift) < 0.1
3. Database performance:
   - Query execution times
   - Connection pool utilization
   - Index effectiveness
4. Stress test results:
   - Breakpoint identification
   - Graceful degradation behavior
   - Recovery time after overload

Format: Performance certification report
Timeline: 2 days
```

#### Legal Compliance Checker — Final Compliance Audit

```
Activate the Legal Compliance Checker for final compliance audit on [project].

Required Deliverables:
1. Privacy compliance verification:
   - Privacy policy accuracy
   - Consent management functionality
   - Data subject rights implementation
   - Cookie consent implementation
2. Security compliance:
   - Data encryption (at rest and in transit)
   - Authentication security
   - Input sanitization
   - OWASP Top 10 check
3. Regulatory compliance:
   - GDPR requirements (if applicable)
   - CCPA requirements (if applicable)
   - Industry-specific requirements
4. Accessibility compliance:
   - WCAG 2.1 AA verification
   - Screen reader compatibility
   - Keyboard navigation

Format: Compliance certification report
Timeline: 2 days
```

### Step 2: Analysis (Day 3-4, Parallel after Step 1)

#### Test Results Analyzer — Quality Metrics Aggregation

```
Activate the Test Results Analyzer for quality metrics aggregation on [project].

Input: All Step 1 reports
Required Deliverables:
1. Aggregated quality dashboard:
   - Overall quality score
   - Category breakdown (visual, functional, performance, security, compliance)
   - Issue severity distribution
   - Trend analysis (if multiple test cycles)
2. Issue prioritization:
   - Critical issues (must fix before production)
   - High priority issues (should fix before production)
   - Medium priority issues (next sprint)
   - Low priority issues (backlog)
3. Risk assessment:
   - Production readiness probability
   - Remaining risk areas
   - Recommended mitigations

Format: Quality metrics dashboard
Timeline: 1 day
```

#### Workflow Optimizer — Process Efficiency Review

```
Activate the Workflow Optimizer for process efficiency review on [project].

Input: Phase 3 execution data + Step 1 findings
Required Deliverables:
1. Process efficiency analysis:
   - Dev↔QA loop efficiency (first-pass rate, avg retry count)
   - Bottleneck identification
   - Resolution time by issue type
2. Improvement recommendations:
   - Process changes for Phase 6 operations
   - Automation opportunities
   - Quality improvement suggestions

Format: Optimization recommendations report
Timeline: 1 day
```

#### Infrastructure Maintainer — Production Readiness Check

```
Activate the Infrastructure Maintainer for production readiness check on [project].

Required Deliverables:
1. Production environment verification:
   - All services healthy and responding
   - Auto-scaling configured and tested
   - Load balancer configuration verified
   - SSL/TLS certificates valid
2. Monitoring verification:
   - All critical metrics being collected
   - Alert rules configured and tested
   - Dashboard access verified
   - Log aggregation working
3. Disaster recovery verification:
   - Backup systems running
   - Recovery procedures documented and tested
   - Failover mechanisms verified
4. Security verification:
   - Firewall rules reviewed
   - Access controls verified
   - Key management confirmed
   - Vulnerability scan clean

Format: Infrastructure readiness report
Timeline: 1 day
```

### Step 3: Final Verdict (Day 5-7, Sequential)

#### Reality Checker — Final Verdict

```
Activate the Reality Checker for final integration testing on [project].

Mandatory process — do not skip:

Step 1: Reality Check Command
- Verify what was actually built (ls, grep claimed functionality)
- Cross-check claimed functionality against specs
- Run comprehensive screenshot capture
- Review all evidence from Step 1 and Step 2

Step 2: QA Cross-Validation
- Review Evidence Collector findings
- Cross-reference with API Tester results
- Verify Performance Benchmarker data
- Confirm Legal Compliance Checker findings

Step 3: End-to-End System Verification
- Test complete user journeys (not individual features)
- Verify responsive behavior across all devices
- Check interaction flows end-to-end
- Review actual performance data

Step 4: Spec Reality Check
- Quote exact text from original specs
- Compare against actual implementation evidence
- Document every gap between spec and reality
- Make no assumptions — only evidence

Verdict options:
- Ready: Overwhelming evidence of production readiness (rare first-pass)
- Needs Work: Specific issues identified with fix list (expected)
- Not Ready: Major architecture issues requiring return to Phase 1/2

Format: Reality-based integration report
Default: Needs work unless proven otherwise
```

## Quality Gate — Final Gate

| # | Standard | Threshold | Required Evidence |
|---|-----------|-----------|-------------------|
| 1 | User journey complete | All critical paths work end-to-end | Reality Checker screenshots |
| 2 | Cross-device consistency | Desktop + tablet + mobile all work | Responsive screenshots |
| 3 | Performance certification | P95 < 200ms, LCP < 2.5s, uptime > 99.9% | Performance Benchmarker report |
| 4 | Security verified | Zero critical vulnerabilities | Security scan + compliance report |
| 5 | Compliance certified | All regulatory requirements met | Legal Compliance Checker report |
| 6 | Spec compliance | 100% of spec requirements implemented | Point-by-point verification |
| 7 | Infrastructure ready | Production environment verified | Infrastructure Maintainer report |

## Gate Decision

**Sole Authority**: Reality Checker

### If Ready (Proceed to Phase 5):

```markdown
## Phase 4 → Phase 5 Handoff Package

### For launch team:
- Reality Checker certification report
- Performance certification
- Compliance certification
- Infrastructure readiness report
- Known limitations (if any)

### For Growth Hacker:
- Product ready for users
- Feature list for marketing messaging
- Performance data for credibility

### For DevOps Automator:
- Production deployment approved
- Blue-green deployment plan
- Rollback procedures confirmed
```

### If Needs Work (Return to Phase 3):

```markdown
## Phase 4 → Phase 3 Return Package

### Fix list (from Reality Checker):
1. [Critical issue 1]: [Description + evidence + fix instructions]
2. [Critical issue 2]: [Description + evidence + fix instructions]
3. [High priority issue 1]: [Description + evidence + fix instructions]
...

### Process:
- Issues enter Dev↔QA loop (Phase 3 mechanism)
- Each fix must pass Evidence Collector QA
- When all fixes complete → Return to Phase 4 Step 3
- Reality Checker re-evaluates with updated evidence

### Expected: 2-3 revision cycles are normal
```

### If Not Ready (Return to Phase 1/2):

```markdown
## Phase 4 → Phase 1/2 Return Package

### Identified architecture issues:
1. [Fundamental issue]: [Why it can't be fixed in Phase 3]
2. [Structural issue]: [What needs to change at architecture level]

### Recommended actions:
- [ ] Revise system architecture (Phase 1)
- [ ] Rebuild foundation (Phase 2)
- [ ] Scope down and redefine (Phase 1)

### Requires Studio Producer decision
```

---

*Phase 4 is complete when the Reality Checker issues a "Ready" verdict with overwhelming evidence. "Needs work" is the expected first-pass result — it means the system is working but needs polish.*
