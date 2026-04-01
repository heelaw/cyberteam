# Django 验证循环

在 PR 之前、重大更改之后运行并预部署，以确保 Django 应用程序的质量和安全性。

## 何时激活

- 在为 Django 项目打开拉取请求之前
- 在重大模型更改、迁移更新或依赖项升级之后
- 预部署或生产验证
- 运行完整环境 → lint → 测试 → 安全性 → 部署准备管道
- 验证迁移安全性和测试覆盖率

## 第一阶段：环境检查```bash
# Verify Python version
python --version  # Should match project requirements

# Check virtual environment
which python
pip list --outdated

# Verify environment variables
python -c "import os; import environ; print('DJANGO_SECRET_KEY set' if os.environ.get('DJANGO_SECRET_KEY') else 'MISSING: DJANGO_SECRET_KEY')"
```如果环境配置错误，请停止并修复。

## 第 2 阶段：代码质量和格式```bash
# Type checking
mypy . --config-file pyproject.toml

# Linting with ruff
ruff check . --fix

# Formatting with black
black . --check
black .  # Auto-fix

# Import sorting
isort . --check-only
isort .  # Auto-fix

# Django-specific checks
python manage.py check --deploy
```常见问题：
- 缺少公共函数的类型提示
- PEP 8 格式违规
- 未分类的进口
- 生产配置中保留调试设置

## 第三阶段：迁移```bash
# Check for unapplied migrations
python manage.py showmigrations

# Create missing migrations
python manage.py makemigrations --check

# Dry-run migration application
python manage.py migrate --plan

# Apply migrations (test environment)
python manage.py migrate

# Check for migration conflicts
python manage.py makemigrations --merge  # Only if conflicts exist
```报告：
- 待处理的迁移数量
- 任何迁移冲突
- 无需迁移即可更改模型

## 第 4 阶段：测试 + 覆盖范围```bash
# Run all tests with pytest
pytest --cov=apps --cov-report=html --cov-report=term-missing --reuse-db

# Run specific app tests
pytest apps/users/tests/

# Run with markers
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests

# Coverage report
open htmlcov/index.html
```报告：
- 总测试：X 通过，Y 失败，Z 跳过
- 总体覆盖率：XX%
- 每个应用程序的覆盖范围细分

覆盖目标：

|组件|目标|
|------------|--------|
|型号| 90%+ |
|序列化器 | 85%+ |
|意见 | 80%+ |
|服务 | 90%+ |
|总体 | 80%+ |

## 第 5 阶段：安全扫描```bash
# Dependency vulnerabilities
pip-audit
safety check --full-report

# Django security checks
python manage.py check --deploy

# Bandit security linter
bandit -r . -f json -o bandit-report.json

# Secret scanning (if gitleaks is installed)
gitleaks detect --source . --verbose

# Environment variable check
python -c "from django.core.exceptions import ImproperlyConfigured; from django.conf import settings; settings.DEBUG"
```报告：
- 发现易受攻击的依赖项
- 安全配置问题
- 检测到硬编码秘密
- DEBUG 模式状态（在生产中应为 False）

## 第 6 阶段：Django 管理命令```bash
# Check for model issues
python manage.py check

# Collect static files
python manage.py collectstatic --noinput --clear

# Create superuser (if needed for tests)
echo "from apps.users.models import User; User.objects.create_superuser('admin@example.com', 'admin')" | python manage.py shell

# Database integrity
python manage.py check --database default

# Cache verification (if using Redis)
python -c "from django.core.cache import cache; cache.set('test', 'value', 10); print(cache.get('test'))"
```## 第 7 阶段：性能检查```bash
# Django Debug Toolbar output (check for N+1 queries)
# Run in dev mode with DEBUG=True and access a page
# Look for duplicate queries in SQL panel

# Query count analysis
django-admin debugsqlshell  # If django-debug-sqlshell installed

# Check for missing indexes
python manage.py shell << EOF
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT table_name, index_name FROM information_schema.statistics WHERE table_schema = 'public'")
    print(cursor.fetchall())
EOF
```报告：
- 每页查询数（典型页面应< 50）
- 缺少数据库索引
- 检测到重复查询

## 第 8 阶段：静态资产```bash
# Check for npm dependencies (if using npm)
npm audit
npm audit fix

# Build static files (if using webpack/vite)
npm run build

# Verify static files
ls -la staticfiles/
python manage.py findstatic css/style.css
```## 第 9 阶段：配置审查```python
# Run in Python shell to verify settings
python manage.py shell << EOF
from django.conf import settings
import os

# Critical checks
checks = {
    'DEBUG is False': not settings.DEBUG,
    'SECRET_KEY set': bool(settings.SECRET_KEY and len(settings.SECRET_KEY) > 30),
    'ALLOWED_HOSTS set': len(settings.ALLOWED_HOSTS) > 0,
    'HTTPS enabled': getattr(settings, 'SECURE_SSL_REDIRECT', False),
    'HSTS enabled': getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
    'Database configured': settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3',
}

for check, result in checks.items():
    status = '✓' if result else '✗'
    print(f"{status} {check}")
EOF
```## 第 10 阶段：日志记录配置```bash
# Test logging output
python manage.py shell << EOF
import logging
logger = logging.getLogger('django')
logger.warning('Test warning message')
logger.error('Test error message')
EOF

# Check log files (if configured)
tail -f /var/log/django/django.log
```## 第 11 阶段：API 文档（如果是 DRF）```bash
# Generate schema
python manage.py generateschema --format openapi-json > schema.json

# Validate schema
# Check if schema.json is valid JSON
python -c "import json; json.load(open('schema.json'))"

# Access Swagger UI (if using drf-yasg)
# Visit http://localhost:8000/swagger/ in browser
```## 第 12 阶段：差异审查```bash
# Show diff statistics
git diff --stat

# Show actual changes
git diff

# Show changed files
git diff --name-only

# Check for common issues
git diff | grep -i "todo\|fixme\|hack\|xxx"
git diff | grep "print("  # Debug statements
git diff | grep "DEBUG = True"  # Debug mode
git diff | grep "import pdb"  # Debugger
```清单：
- 无调试语句（print、pdb、breakpoint()）
- 关键代码中没有 TODO/FIXME 注释
- 没有硬编码的秘密或凭证
- 包括模型更改的数据库迁移
- 记录配置更改
- 外部调用的错误处理
- 需要时的交易管理

## 输出模板```
DJANGO VERIFICATION REPORT
==========================

Phase 1: Environment Check
  ✓ Python 3.11.5
  ✓ Virtual environment active
  ✓ All environment variables set

Phase 2: Code Quality
  ✓ mypy: No type errors
  ✗ ruff: 3 issues found (auto-fixed)
  ✓ black: No formatting issues
  ✓ isort: Imports properly sorted
  ✓ manage.py check: No issues

Phase 3: Migrations
  ✓ No unapplied migrations
  ✓ No migration conflicts
  ✓ All models have migrations

Phase 4: Tests + Coverage
  Tests: 247 passed, 0 failed, 5 skipped
  Coverage:
    Overall: 87%
    users: 92%
    products: 89%
    orders: 85%
    payments: 91%

Phase 5: Security Scan
  ✗ pip-audit: 2 vulnerabilities found (fix required)
  ✓ safety check: No issues
  ✓ bandit: No security issues
  ✓ No secrets detected
  ✓ DEBUG = False

Phase 6: Django Commands
  ✓ collectstatic completed
  ✓ Database integrity OK
  ✓ Cache backend reachable

Phase 7: Performance
  ✓ No N+1 queries detected
  ✓ Database indexes configured
  ✓ Query count acceptable

Phase 8: Static Assets
  ✓ npm audit: No vulnerabilities
  ✓ Assets built successfully
  ✓ Static files collected

Phase 9: Configuration
  ✓ DEBUG = False
  ✓ SECRET_KEY configured
  ✓ ALLOWED_HOSTS set
  ✓ HTTPS enabled
  ✓ HSTS enabled
  ✓ Database configured

Phase 10: Logging
  ✓ Logging configured
  ✓ Log files writable

Phase 11: API Documentation
  ✓ Schema generated
  ✓ Swagger UI accessible

Phase 12: Diff Review
  Files changed: 12
  +450, -120 lines
  ✓ No debug statements
  ✓ No hardcoded secrets
  ✓ Migrations included

RECOMMENDATION: ⚠️ Fix pip-audit vulnerabilities before deploying

NEXT STEPS:
1. Update vulnerable dependencies
2. Re-run security scan
3. Deploy to staging for final testing
```## 部署前检查表

- [ ] 所有测试均通过
- [ ] 覆盖率 ≥ 80%
- [ ] 无安全漏洞
- [ ] 没有未应用的迁移
- [ ] DEBUG = 生产设置中的 False
- [ ] SECRET_KEY 正确配置
- [ ] ALLOWED_HOSTS 设置正确
- [ ] 启用数据库备份
- [ ] 收集并提供静态文件
- [ ] 日志记录已配置并正在运行
- [ ] 配置错误监控（Sentry等）
- [ ] CDN 配置（如果适用）
- [ ] Redis/缓存后端已配置
- [ ] Celery 工人正在运行（如果适用）
- [ ] HTTPS/SSL 配置
- [ ] 记录环境变量

## 持续集成

### GitHub 操作示例```yaml
# .github/workflows/django-verification.yml
name: Django Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install ruff black mypy pytest pytest-django pytest-cov bandit safety pip-audit

      - name: Code quality checks
        run: |
          ruff check .
          black . --check
          isort . --check-only
          mypy .

      - name: Security scan
        run: |
          bandit -r . -f json -o bandit-report.json
          safety check --full-report
          pip-audit

      - name: Run tests
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
          DJANGO_SECRET_KEY: test-secret-key
        run: |
          pytest --cov=apps --cov-report=xml --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```## 快速参考

|检查 |命令 |
|--------|---------|
|环境 | `python --版本` |
|类型检查 | `mypy 。` |
|绒毛 | `领口格纹。` |
|格式化| `黑色。 --检查` |
|移民| `python manage.py makemigrations --check` |
|测试 | `pytest --cov=apps` |
|安全| `pip-audit && bandit -r .` |
|姜戈检查 | `python manage.py check --deploy` |
|收集静态| `python manage.pycollectstatic--noinput` |
|差异统计 | `git diff --stat` |

请记住：自动验证可以捕获常见问题，但不能取代临时环境中的手动代码审查和测试。