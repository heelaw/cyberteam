# CyberTeam V4 - Security Policy

## Branch Protection Rules

### Main Branch
- **Require pull request reviews before merging**: 2 approvals required
- **Require status checks to pass before merging**: All CI checks must pass
- **Require branches to be up to date before merging**
- **Do not allow bypassing the above settings**

### Develop Branch
- **Require pull request reviews before merging**: 1 approval required
- **Require status checks to pass before merging**: CI tests and linting must pass

## Secret Management

### Required Secrets
Configure these secrets in your GitHub repository settings:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SECRET_KEY` | Application secret key | Generate with `openssl rand -hex 32` |
| `DB_PASSWORD` | Database password | Secure random string |
| `REDIS_PASSWORD` | Redis password | Secure random string |
| `GITHUB_TOKEN` | GitHub token for registry | Automatically provided |
| `KUBE_CONFIG_STAGING` | Kubeconfig for staging | Base64 encoded kubeconfig |
| `KUBE_CONFIG_PROD` | Kubeconfig for production | Base64 encoded kubeconfig |
| `SLACK_WEBHOOK` | Slack notifications (optional) | Slack webhook URL |

### Secret Generation
```bash
# Generate secret key
openssl rand -hex 32

# Generate database password
openssl rand -base64 32

# Encode kubeconfig
cat ~/.kube/config | base64 -w 0
```

## Security Scanning

### Automated Scans
The CI pipeline includes:
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **TruffleHog**: Secret detection

### Manual Security Audits
Run before major releases:
```bash
# Bandit scan
bandit -r CYBERTEAM/ cyberteam/ -f json -o security-report.json

# Safety check
pip install safety
safety check --json

# Dependency check
pip-audit
```

## Access Control

### Kubernetes RBAC
Define role-based access control:

```yaml
# Developer role - can deploy to staging only
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cyberteam-developer
  namespace: cyberteam-staging
rules:
- apiGroups: ["apps", ""]
  resources: ["deployments", "pods", "services"]
  verbs: ["get", "list", "create", "update", "patch"]
```

### GitHub Teams
| Team | Permissions | Scope |
|------|-------------|-------|
| `cyberteam-admins` | Admin | All |
| `cyberteam-developers` | Write | Staging only |
| `cyberteam-ops` | Write | All environments |
| `cyberteam-readonly` | Read | All |

## Network Policies

### Default Deny All
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: cyberteam
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Allow Specific Traffic
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web
  namespace: cyberteam
spec:
  podSelector:
    matchLabels:
      app: cyberteam
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

## Compliance & Auditing

### Audit Logging
Enable audit logging in Kubernetes:
```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  namespaces: ["cyberteam"]
  verbs: ["create", "update", "delete"]
```

### Change Log
Maintain deployment change log:
- Date and time
- Deployer name
- Version deployed
- Environment
- Rollback status

## Incident Response

### Security Incident Steps
1. **Isolate**: Scale down affected deployments
2. **Assess**: Review logs and metrics
3. **Remediate**: Apply patches or rollback
4. **Document**: Create incident report

### Rollback Procedure
```bash
# Kubernetes rollback
kubectl rollout undo deployment/cyberteam -n cyberteam-prod

# Force specific version
kubectl rollout undo deployment/cyberteam --to-revision=42 -n cyberteam-prod
```

## Compliance Checklist

- [ ] All secrets stored in GitHub Secrets (never in code)
- [ ] Branch protection rules enabled
- [ ] Required PR reviews configured
- [ ] CI security scans passing
- [ ] TLS/SSL enabled for all endpoints
- [ ] Network policies configured
- [ ] RBAC roles defined
- [ ] Audit logging enabled
- [ ] Backup and recovery tested
- [ ] Incident response procedure documented
