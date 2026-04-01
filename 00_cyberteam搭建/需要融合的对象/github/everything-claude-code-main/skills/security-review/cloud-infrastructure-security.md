|名称 |描述 |
|------|-------------|
|云基础设施安全 |在部署到云平台、配置基础设施、管理 IAM 策略、设置日志记录/监控或实施 CI/CD 管道时使用此技能。提供符合最佳实践的云安全检查表。 |

# 云和基础设施安全技能

此技能可确保云基础设施、CI/CD 管道和部署配置遵循安全最佳实践并符合行业标准。

## 何时激活

- 将应用程序部署到云平台（AWS、Vercel、Railway、Cloudflare）
- 配置IAM角色和权限
- 设置 CI/CD 管道
- 实施基础设施即代码（Terraform、CloudFormation）
- 配置日志记录和监控
- 管理云环境中的机密
- 设置 CDN 和边缘安全
- 实施灾难恢复和备份策略

## 云安全检查表

### 1. IAM 和访问控制

#### 最小特权原则```yaml
# ✅ CORRECT: Minimal permissions
iam_role:
  permissions:
    - s3:GetObject  # Only read access
    - s3:ListBucket
  resources:
    - arn:aws:s3:::my-bucket/*  # Specific bucket only

# ❌ WRONG: Overly broad permissions
iam_role:
  permissions:
    - s3:*  # All S3 actions
  resources:
    - "*"  # All resources
```#### 多重身份验证 (MFA)```bash
# ALWAYS enable MFA for root/admin accounts
aws iam enable-mfa-device \
  --user-name admin \
  --serial-number arn:aws:iam::123456789:mfa/admin \
  --authentication-code1 123456 \
  --authentication-code2 789012
```#### 验证步骤

- [ ] 生产中不使用 root 帐户
- [ ] 为所有特权帐户启用 MFA
- [ ] 服务帐户使用角色，而不是长期凭据
- [ ] IAM 策略遵循最小权限
- [ ] 定期进行访问审查
- [ ] 轮换或删除未使用的凭据

### 2. 秘密管理

#### 云秘密管理器```typescript
// ✅ CORRECT: Use cloud secrets manager
import { SecretsManager } from '@aws-sdk/client-secrets-manager';

const client = new SecretsManager({ region: 'us-east-1' });
const secret = await client.getSecretValue({ SecretId: 'prod/api-key' });
const apiKey = JSON.parse(secret.SecretString).key;

// ❌ WRONG: Hardcoded or in environment variables only
const apiKey = process.env.API_KEY; // Not rotated, not audited
```#### 秘密轮换```bash
# Set up automatic rotation for database credentials
aws secretsmanager rotate-secret \
  --secret-id prod/db-password \
  --rotation-lambda-arn arn:aws:lambda:region:account:function:rotate \
  --rotation-rules AutomaticallyAfterDays=30
```#### 验证步骤

- [ ] 存储在云机密管理器（AWS Secrets Manager、Vercel Secrets）中的所有机密
- [ ] 为数据库凭据启用自动轮换
- [ ] API 密钥至少每季度轮换一次
- [ ] 代码、日志或错误消息中没有秘密
- [ ] 为秘密访问启用审核日志记录

### 3.网络安全

#### VPC 和防火墙配置```terraform
# ✅ CORRECT: Restricted security group
resource "aws_security_group" "app" {
  name = "app-sg"
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # Internal VPC only
  }
  
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Only HTTPS outbound
  }
}

# ❌ WRONG: Open to the internet
resource "aws_security_group" "bad" {
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # All ports, all IPs!
  }
}
```#### 验证步骤

- [ ] 数据库不可公开访问
- [ ] SSH/RDP 端口仅限 VPN/堡垒
- [ ] 安全组遵循最小权限
- [ ] 网络 ACL 已配置
- [ ] VPC 流日志已启用

### 4. 日志记录和监控

#### CloudWatch/日志记录配置```typescript
// ✅ CORRECT: Comprehensive logging
import { CloudWatchLogsClient, CreateLogStreamCommand } from '@aws-sdk/client-cloudwatch-logs';

const logSecurityEvent = async (event: SecurityEvent) => {
  await cloudwatch.putLogEvents({
    logGroupName: '/aws/security/events',
    logStreamName: 'authentication',
    logEvents: [{
      timestamp: Date.now(),
      message: JSON.stringify({
        type: event.type,
        userId: event.userId,
        ip: event.ip,
        result: event.result,
        // Never log sensitive data
      })
    }]
  });
};
```#### 验证步骤

- [ ] 为所有服务启用 CloudWatch/日志记录
- [ ] 记录失败的身份验证尝试
- [ ] 管理员操作已审核
- [ ] 配置日志保留（合规性超过 90 天）
- [ ] 针对可疑活动配置警报
- [ ] 日志集中、防篡改

### 5. CI/CD 管道安全

#### 安全管道配置```yaml
# ✅ CORRECT: Secure GitHub Actions workflow
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read  # Minimal permissions
      
    steps:
      - uses: actions/checkout@v4
      
      # Scan for secrets
      - name: Secret scanning
        uses: trufflesecurity/trufflehog@main
        
      # Dependency audit
      - name: Audit dependencies
        run: npm audit --audit-level=high
        
      # Use OIDC, not long-lived tokens
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
          aws-region: us-east-1
```#### 供应链安全```json
// package.json - Use lock files and integrity checks
{
  "scripts": {
    "install": "npm ci",  // Use ci for reproducible builds
    "audit": "npm audit --audit-level=moderate",
    "check": "npm outdated"
  }
}
```#### 验证步骤

- [ ] 使用 OIDC 代替长期凭证
- [ ] 管道中的秘密扫描
- [ ] 依赖漏洞扫描
- [ ] 容器图像扫描（如果适用）
- [ ] 执行分支保护规则
- [ ] 合并前需要进行代码审查
- [ ] 强制执行签名提交

### 6.Cloudflare 和 CDN 安全

#### Cloudflare 安全配置```typescript
// ✅ CORRECT: Cloudflare Workers with security headers
export default {
  async fetch(request: Request): Promise<Response> {
    const response = await fetch(request);
    
    // Add security headers
    const headers = new Headers(response.headers);
    headers.set('X-Frame-Options', 'DENY');
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    headers.set('Permissions-Policy', 'geolocation=(), microphone=()');
    
    return new Response(response.body, {
      status: response.status,
      headers
    });
  }
};
```#### WAF 规则```bash
# Enable Cloudflare WAF managed rules
# - OWASP Core Ruleset
# - Cloudflare Managed Ruleset
# - Rate limiting rules
# - Bot protection
```#### 验证步骤

- [ ] 使用 OWASP 规则启用 WAF
- [ ] 已配置速率限制
- [ ] 机器人防护已激活
- [ ] DDoS 防护已启用
- [ ] 配置安全标头
- [ ] SSL/TLS 严格模式已启用

### 7. 备份和灾难恢复

#### 自动备份```terraform
# ✅ CORRECT: Automated RDS backups
resource "aws_db_instance" "main" {
  allocated_storage     = 20
  engine               = "postgres"
  
  backup_retention_period = 30  # 30 days retention
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  deletion_protection = true  # Prevent accidental deletion
}
```#### 验证步骤

- [ ] 配置自动每日备份
- [ ] 备份保留满足合规性要求
- [ ] 启用时间点恢复
- [ ] 每季度进行一次备份测试
- [ ] 记录灾难恢复计划
- [ ] RPO 和 RTO 定义和测试

## 部署前云安全检查表

在任何生产云部署之前：

- [ ] **IAM**：未使用根帐户、启用 MFA、最小权限策略
- [ ] **秘密**：云秘密管理器中的所有秘密，可轮换
- [ ] **网络**：安全组受限，无公共数据库
- [ ] **日志记录**：启用并保留 CloudWatch/日志记录
- [ ] **监控**：针对异常配置的警报
- [ ] **CI/CD**：OIDC 身份验证、机密扫描、依赖性审计
- [ ] **CDN/WAF**：使用 OWASP 规则启用 Cloudflare WAF
- [ ] **加密**：静态和传输中加密的数据
- [ ] **备份**：具有经过测试恢复的自动备份
- [ ] **合规性**：满足 GDPR/HIPAA 要求（如果适用）
- [ ] **文档**：记录基础架构，创建操作手册
- [ ] **事件响应**：安全事件计划到位

## 常见的云安全配置错误

### S3桶曝光```bash
# ❌ WRONG: Public bucket
aws s3api put-bucket-acl --bucket my-bucket --acl public-read

# ✅ CORRECT: Private bucket with specific access
aws s3api put-bucket-acl --bucket my-bucket --acl private
aws s3api put-bucket-policy --bucket my-bucket --policy file://policy.json
```### RDS 公共访问```terraform
# ❌ WRONG
resource "aws_db_instance" "bad" {
  publicly_accessible = true  # NEVER do this!
}

# ✅ CORRECT
resource "aws_db_instance" "good" {
  publicly_accessible = false
  vpc_security_group_ids = [aws_security_group.db.id]
}
```## 资源

- [AWS 安全最佳实践](https://aws.amazon.com/security/best-practices/)
- [CIS AWS 基金会基准](https://www.cisecurity.org/benchmark/amazon_web_services)
- [Cloudflare 安全文档](https://developers.cloudflare.com/security/)
- [OWASP 云安全](https://owasp.org/www-project-cloud-security/)
- [Terraform 安全最佳实践](https://www.terraform.io/docs/cloud/guides/recommended-practices/)

**记住**：云配置错误是数据泄露的主要原因。单个暴露的 S3 存储桶或过于宽松的 IAM 策略可能会危及您的整个基础设施。始终遵循最小特权和纵深防御原则。