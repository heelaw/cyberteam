# Phase 2 Playbook — Foundation & Scaffolding

> **Duration**: 3-5 days | **Agents**: 6 | **Gate Keepers**: DevOps Automator + Evidence Collector

---

## Objective

Build the technical and operational foundation that all subsequent work depends on. Get the skeleton standing before adding muscle. After this phase, every developer has a working environment, a deployable pipeline, and a design system to build against.

## Prerequisites

- [ ] Phase 1 quality gate passed (architecture package approved)
- [ ] Phase 1 handoff package received
- [ ] All architecture documents finalized

## Agent Activation Sequence

### Workflow A: Infrastructure (Day 1-3, Parallel)

#### DevOps Automator — CI/CD Pipeline + Infrastructure

```
Activate the DevOps Automator for infrastructure setup on [project].

Input: Backend Architect system architecture + deployment requirements
Required Deliverables:
1. CI/CD pipeline (GitHub Actions / GitLab CI)
   - Security scanning stage
   - Automated testing stage
   - Build and containerization stage
   - Deployment stage (blue-green or canary)
   - Automated rollback capability
2. Infrastructure as Code
   - Environment configuration (dev, staging, production)
   - Container orchestration setup
   - Network and security configuration
3. Environment configuration
   - Secret management
   - Environment variable management
   - Multi-environment consistency

Files to create:
- .github/workflows/ci-cd.yml (or equivalent)
- infrastructure/ (Terraform/CDK templates)
- docker-compose.yml
- Dockerfile(s)

Format: Working CI/CD pipeline with IaC templates
Timeline: 3 days
```

#### Infrastructure Maintainer — Cloud Infrastructure + Monitoring

```
Activate the Infrastructure Maintainer for monitoring setup on [project].

Input: DevOps Automator infrastructure + Backend Architect architecture
Required Deliverables:
1. Cloud resource configuration
   - Compute, storage, network resources
   - Auto-scaling configuration
   - Load balancer setup
2. Monitoring stack
   - Application metrics (Prometheus/DataDog)
   - Infrastructure metrics
   - Custom dashboards (Grafana)
3. Logging and alerting
   - Centralized log aggregation
   - Alert rules for critical thresholds
   - On-call notification setup
4. Security hardening
   - Firewall rules
   - SSL/TLS configuration
   - Access control policies

Format: Infrastructure ready report with dashboard access
Timeline: 3 days
```

#### Studio Operations — Process Setup

```
Activate the Studio Operations for process setup on [project].

Input: Sprint Prioritizer plan + Project Shepherd coordination requirements
Required Deliverables:
1. Git workflow
   - Branching strategy (GitFlow / trunk-based)
   - PR review process
   - Merge strategy
2. Communication channels
   - Team channel setup
   - Notification routing
   - Status update rhythm
3. Documentation templates
   - PR templates
   - Issue templates
   - Decision log template
4. Collaboration tools
   - Project board setup
   - Sprint tracking configuration

Format: Operations runbook
Timeline: 2 days
```

### Workflow B: Application Foundation (Day 1-4, Parallel)

#### Frontend Developer — Project Scaffolding + Component Library

```
Activate the Frontend Developer for project scaffolding on [project].

Input: UX Architect CSS design system + Brand Guardian identity
Required Deliverables:
1. Project scaffolding
   - Framework setup (React/Vue/Angular per architecture)
   - TypeScript configuration
   - Build tools (Vite/Webpack/Next.js)
   - Testing framework (Jest/Vitest + Testing Library)
2. Design system implementation
   - CSS design tokens from UX Architect
   - Base component library (Button, Input, Card, Layout)
   - Theming system (light/dark/system toggle)
   - Responsive utilities
3. Application shell
   - Routing setup
   - Layout components (Header, Footer, Sidebar)
   - Error boundary implementation
   - Loading states

Files to create:
- src/ (application source code)
- src/components/ (component library)
- src/styles/ (design tokens)
- src/layouts/ (layout components)

Format: Working application skeleton with component library
Timeline: 3 days
```

#### Backend Architect — Database + API Foundation

```
Activate the Backend Architect for API foundation setup on [project].

Input: System architecture spec + database schema design
Required Deliverables:
1. Database setup
   - Schema deployment (migrations)
   - Index creation
   - Seed data for development
   - Connection pool configuration
2. API scaffolding
   - Framework setup (Express/FastAPI/etc.)
   - Route structure matching architecture
   - Middleware stack (auth, validation, error handling, CORS)
   - Health check endpoint
3. Authentication system
   - Authentication provider integration
   - JWT/session management
   - Role-based access control scaffolding
4. Service communication
   - API versioning setup
   - Request/response serialization
   - Error response standardization

Files to create:
- api/ or server/ (backend source code)
- migrations/ (database migrations)
- docs/api-spec.yaml (OpenAPI spec)

Format: Working API scaffold with database and authentication
Timeline: 4 days
```

#### UX Architect — CSS System Implementation

```
Activate the UX Architect for CSS system implementation on [project].

Input: Brand Guardian identity + own Phase 1 CSS design system spec
Required Deliverables:
1. Design token implementation
   - CSS custom properties (colors, typography, spacing)
   - Brand palette with semantic naming
   - Font scale with responsive adjustments
2. Layout system
   - Container system (responsive breakpoints)
   - Grid patterns (2-col, 3-col, sidebar)
   - Flexbox utilities
3. Theming system
   - Light theme variables
   - Dark theme variables
   - System preference detection
   - Theme toggle component
   - Smooth transitions between themes

Files to create/update:
- css/design-system.css (or equivalent in framework)
- css/layout.css
- css/components.css
- js/theme-manager.js

Format: Implemented CSS design system with theme switching
Timeline: 2 days
```

## Verification Checkpoints (Day 4-5)

### Evidence Collector Verification

```
Activate the Evidence Collector for Phase 2 foundation verification.

Verify the following with screenshot evidence:
1. CI/CD pipeline executes successfully (show pipeline logs)
2. Application skeleton loads in browser (desktop screenshot)
3. Application skeleton loads on mobile (mobile screenshot)
4. Theme switching works (light + dark screenshots)
5. API health check responds (curl output)
6. Database is accessible (migration status)
7. Monitoring dashboard is active (dashboard screenshot)
8. Component library renders (component demo page)

Format: Evidence package with screenshots
Decision: Pass / Fail with specific issues
```

## Quality Gate Checklist

| # | Standard | Evidence Source | Status |
|---|-----------|----------------|--------|
| 1 | CI/CD pipeline builds, tests, and deploys | Pipeline execution logs | ☐ |
| 2 | Database schema deployed, all tables/indexes | Migration success output | ☐ |
| 3 | API scaffold responds on health check | curl response evidence | ☐ |
| 4 | Frontend skeleton renders in browser | Evidence Collector screenshots | ☐ |
| 5 | Monitoring dashboard shows metrics | Dashboard screenshot | ☐ |
| 6 | Design system tokens implemented | Component library demo | ☐ |
| 7 | Theme switching functional (light/dark/system) | Before/after screenshots | ☐ |
| 8 | Git workflow and processes documented | Studio Operations runbook | ☐ |

## Gate Decision

**Requires dual sign-off**: DevOps Automator (infrastructure) + Evidence Collector (visual)

- **Pass**: Working skeleton with full DevOps pipeline → Activate Phase 3
- **Fail**: Specific infrastructure or application issues → Fix and re-verify

## Handoff to Phase 3

```markdown
## Phase 2 → Phase 3 Handoff Package

### For all developer agents:
- Working CI/CD pipeline (auto-deploys on merge)
- Design system tokens and component library
- API scaffold with authentication and health checks
- Database with schema and seed data
- Git workflow and PR process

### For Evidence Collector (ongoing QA):
- Application URLs (dev, staging)
- Screenshot capture methodology
- Component library reference
- Brand guidelines for visual verification

### For Agent Orchestrator (Dev↔QA loop management):
- Sprint Prioritizer backlog (from Phase 1)
- Task list with acceptance criteria (from Phase 1)
- Agent assignment matrix (from NEXUS strategy)
- Quality thresholds per task type

### Environment access:
- Development environment: [URL]
- Staging environment: [URL]
- Monitoring dashboard: [URL]
- CI/CD pipeline: [URL]
- API documentation: [URL]
```

---

*Phase 2 is complete when the skeleton application runs, CI/CD pipeline operates, and the Evidence Collector has verified all foundation elements with screenshots.*
