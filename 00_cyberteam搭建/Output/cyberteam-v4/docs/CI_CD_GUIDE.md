# CyberTeam V4 - CI/CD Guide

## Overview

This document provides a comprehensive guide to the CI/CD pipeline for CyberTeam V4, including workflows, deployment procedures, and troubleshooting.

## Table of Contents

1. [Pipeline Architecture](#pipeline-architecture)
2. [CI Workflow](#ci-workflow)
3. [CD Workflow](#cd-workflow)
4. [Local Development](#local-development)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Repository                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Push/PR → CI Workflow                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Lint (Black, Ruff, mypy)                          │    │
│  │ 2. Security Scan (Bandit, Safety, TruffleHog)        │    │
│  │ 3. Test (pytest, coverage)                           │    │
│  │ 4. Docker Build Test                                 │    │
│  │ 5. Structure Validation                              │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  All checks pass → Merge to main                             │
│                          ↓                                   │
│  CD Workflow                                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Build & Push Docker Image                        │    │
│  │ 2. Deploy to Staging                                │    │
│  │ 3. Run Smoke Tests                                  │    │
│  │ 4. (Manual) Deploy to Production                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  Kubernetes Cluster (Staging/Production)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## CI Workflow

### Triggers
- Push to `main`, `develop`, or `feature/**` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### Jobs

#### 1. Lint Python Code
```yaml
Job: lint-python
Tools: Black, Ruff, mypy
Timeout: 10 minutes
```

**Checks performed:**
- Code formatting (Black)
- Linting (Ruff)
- Type checking (mypy)

#### 2. Security Scan
```yaml
Job: security-scan
Tools: Bandit, Safety, TruffleHog
Timeout: 15 minutes
```

**Checks performed:**
- Security linter (Bandit)
- Dependency vulnerabilities (Safety)
- Secret detection (TruffleHog)

#### 3. Python Tests
```yaml
Job: test-python
Matrix: Python 3.9, 3.10, 3.11
Timeout: 20 minutes
```

**Tests performed:**
- Unit tests
- Integration tests
- Coverage reporting

#### 4. Docker Build Test
```yaml
Job: test-docker-build
Timeout: 20 minutes
```

**Validates:**
- Dockerfile syntax
- Image build success
- Import verification

#### 5. Structure Validation
```yaml
Job: validate-structure
Timeout: 10 minutes
```

**Validates:**
- Required directories exist
- Python imports work
- Configuration files present

---

## CD Workflow

### Triggers
- Push to `main` branch
- Manual workflow dispatch with environment selection

### Environments

#### Staging (Automatic)
- Deployed on every merge to `main`
- URL: `https://staging.cyberteam.example.com`
- Rollback: Automatic on health check failure

#### Production (Manual)
- Requires manual approval
- URL: `https://cyberteam.example.com`
- Rollback: Manual or automatic on failure

### Jobs

#### 1. Build & Push
```yaml
Job: build-and-push
Registry: ghcr.io
Image: cyberteam
Tags: latest, version, sha
```

#### 2. Deploy Staging
```yaml
Job: deploy-staging
Namespace: cyberteam-staging
Health Check: /health endpoint
```

#### 3. Deploy Production
```yaml
Job: deploy-production
Namespace: cyberteam-prod
Backup: Automatic before deployment
```

---

## Local Development

### Prerequisites
```bash
# Install dependencies
brew install docker kubectl helm

# Or use Homebrew on macOS
brew install --cask docker
```

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f cyberteam

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Service URLs (Local)
| Service | URL | Credentials |
|---------|-----|-------------|
| CyberTeam API | http://localhost:8000 | - |
| API Documentation | http://localhost:8000/docs | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9091 | - |
| pgAdmin | http://localhost:5050 | admin@cyberteam.local / admin |
| Redis Commander | http://localhost:8081 | - |

---

## Deployment

### Manual Deployment

#### Using the deploy script
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy specific version
./scripts/deploy.sh staging v4.0.0

# Deploy to production
./scripts/deploy.sh production v4.0.0
```

#### Using kubectl directly
```bash
# Set context
kubectl config use-context staging-cluster

# Apply manifests
kubectl apply -f k8s/ -n cyberteam-staging

# Update image
kubectl set image deployment/cyberteam \
  cyberteam=ghcr.io/your-org/cyberteam:v4.0.0 \
  -n cyberteam-staging

# Check rollout status
kubectl rollout status deployment/cyberteam -n cyberteam-staging
```

### Rollback

#### Automatic rollback
The CD pipeline automatically rolls back if:
- Health checks fail
- Pod readiness timeout
- Critical errors detected

#### Manual rollback
```bash
# Undo last deployment
kubectl rollout undo deployment/cyberteam -n cyberteam-prod

# Rollback to specific revision
kubectl rollout undo deployment/cyberteam \
  --to-revision=42 -n cyberteam-prod
```

---

## Monitoring

### Metrics (Prometheus)
- **URL**: http://localhost:9091 (local) or cluster URL (prod)
- **Key metrics**:
  - `cyberteam_requests_total` - Request count
  - `cyberteam_request_duration_seconds` - Request latency
  - `cyberteam_active_agents` - Active agent count
  - `cyberteam_errors_total` - Error count

### Logs (Loki/Grafana)
- **URL**: http://localhost:3000 (local)
- **Log queries**:
  - `{job="cyberteam"}` - All application logs
  - `{level="error"}` - Error logs only
  - `{container_name="cyberteam-app"}` - Container logs

### Alerts
Configure alerts in Grafana:
- High error rate (> 1%)
- High latency (> 1s)
- Pod crashes
- Database connection failures

---

## Troubleshooting

### CI Failures

#### Lint failures
```bash
# Run locally
black --check CYBERTEAM/ cyberteam/
ruff check CYBERTEAM/ cyberteam/

# Auto-fix
black CYBERTEAM/ cyberteam/
ruff check --fix CYBERTEAM/ cyberteam/
```

#### Test failures
```bash
# Run tests locally
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=CYBERTEAM --cov-report=term-missing
```

### Deployment Failures

#### Pod not starting
```bash
# Check pod status
kubectl get pods -n cyberteam-staging

# Describe pod
kubectl describe pod <pod-name> -n cyberteam-staging

# View logs
kubectl logs <pod-name> -n cyberteam-staging

# Check events
kubectl get events -n cyberteam-staging --sort-by='.lastTimestamp'
```

#### Image pull errors
```bash
# Verify image exists
docker pull ghcr.io/your-org/cyberteam:latest

# Check registry credentials
kubectl get secret cyberteam-secret -n cyberteam-staging -o yaml
```

#### Health check failures
```bash
# Port-forward to local
kubectl port-forward svc/cyberteam 8000:80 -n cyberteam-staging

# Test health endpoint
curl http://localhost:8000/health
```

### Performance Issues

#### High memory usage
```bash
# Check resource usage
kubectl top pods -n cyberteam-staging

# Increase limits in deployment.yaml
resources:
  limits:
    memory: "2Gi"
```

#### Slow startup
```bash
# Check startup time
kubectl describe pod <pod-name> -n cyberteam-staging | grep Started

# Increase initialDelaySeconds
livenessProbe:
  initialDelaySeconds: 60
```

---

## Best Practices

1. **Always test locally before pushing**
2. **Use feature branches for development**
3. **Review PR comments before merging**
4. **Monitor deployments closely**
5. **Keep secrets secure**
6. **Document all changes**
7. **Test rollback procedures**

---

## Support

For issues or questions:
- GitHub Issues: [Create issue](https://github.com/your-org/cyberteam/issues)
- Documentation: [CyberTeam Docs](https://docs.cyberteam.example.com)
- Slack: #cyberteam-devops
