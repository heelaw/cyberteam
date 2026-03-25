# Django REST API — 项目 CLAUDE.md

> 使用 PostgreSQL 和 Celery 的 Django REST Framework API 的真实示例。
> 将其复制到您的项目根目录并针对您的服务进行自定义。

## 项目概述

**堆栈：** Python 3.12+、Django 5.x、Django REST Framework、PostgreSQL、Celery + Redis、pytest、Docker Compose

**架构：** 领域驱动设计，每个业务领域都有应用程序。 DRF 用于 API 层，Celery 用于异步任务，pytest 用于测试。所有端点都返回 JSON — 无模板渲染。

## 关键规则

### Python 约定

- 所有函数签名的类型提示 — 使用“from __future__ import comments”
- 没有 `print()` 语句 — 使用 `logging.getLogger(__name__)`
- 用于字符串格式化的 f 字符串，绝不是 `%` 或 `.format()`
- 使用 `pathlib.Path` 而不是 `os.path` 进行文件操作
- 使用 isort 排序的导入：stdlib、第三方、本地（由 ruff 强制执行）

### 数据库

- 所有查询都使用 Django ORM - 仅使用“.raw()”和参数化查询的原始 SQL
- 迁移致力于 git — 切勿在生产中使用 `--fake`
- 使用`select_lated()`和`prefetch_lated()`来防止N+1查询
- 所有模型必须具有“created_at”和“updated_at”自动字段
- “filter()”、“order_by()”或“WHERE”子句中使用的任何字段的索引```python
# BAD: N+1 query
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)  # hits DB for each order

# GOOD: Single query with join
orders = Order.objects.select_related("customer").all()
```### 身份验证

- JWT 通过 `djangorestframework-simplejwt` — 访问令牌（15 分钟）+ 刷新令牌（7 天）
- 每个视图上的权限类别 - 永远不要依赖默认值
- 使用“IsAuthenticated”作为基础，添加对象级访问的自定义权限
- 为注销启用令牌黑名单

### 序列化器

- 使用“ModelSerializer”进行简单的 CRUD，使用“Serializer”进行复杂的验证
- 当输入/输出形状不同时，单独的读写串行器
- 在序列化器级别验证，而不是在视图中验证 - 视图应该很薄```python
class CreateOrderSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, active=True).exists():
            raise serializers.ValidationError("Product not found or inactive")
        return value

class OrderDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "product", "quantity", "total", "status", "created_at"]
```### 错误处理

- 使用 DRF 异常处理程序来实现一致的错误响应
- “core/exceptions.py”中业务逻辑的自定义异常
- 切勿向客户公开内部错误详细信息```python
# core/exceptions.py
from rest_framework.exceptions import APIException

class InsufficientStockError(APIException):
    status_code = 409
    default_detail = "Insufficient stock for this order"
    default_code = "insufficient_stock"
```### 代码风格

- 代码或注释中没有表情符号
- 最大行长度：120 个字符（由 ruff 强制执行）
- 类：PascalCase，函数/变量：snake_case，常量：UPPER_SNAKE_CASE
- 视图很薄——业务逻辑存在于服务功能或模型方法中

## 文件结构```
config/
  settings/
    base.py              # Shared settings
    local.py             # Dev overrides (DEBUG=True)
    production.py        # Production settings
  urls.py                # Root URL config
  celery.py              # Celery app configuration
apps/
  accounts/              # User auth, registration, profile
    models.py
    serializers.py
    views.py
    services.py          # Business logic
    tests/
      test_views.py
      test_services.py
      factories.py       # Factory Boy factories
  orders/                # Order management
    models.py
    serializers.py
    views.py
    services.py
    tasks.py             # Celery tasks
    tests/
  products/              # Product catalog
    models.py
    serializers.py
    views.py
    tests/
core/
  exceptions.py          # Custom API exceptions
  permissions.py         # Shared permission classes
  pagination.py          # Custom pagination
  middleware.py          # Request logging, timing
  tests/
```## 关键模式

### 服务层```python
# apps/orders/services.py
from django.db import transaction

def create_order(*, customer, product_id: uuid.UUID, quantity: int) -> Order:
    """Create an order with stock validation and payment hold."""
    product = Product.objects.select_for_update().get(id=product_id)

    if product.stock < quantity:
        raise InsufficientStockError()

    with transaction.atomic():
        order = Order.objects.create(
            customer=customer,
            product=product,
            quantity=quantity,
            total=product.price * quantity,
        )
        product.stock -= quantity
        product.save(update_fields=["stock", "updated_at"])

    # Async: send confirmation email
    send_order_confirmation.delay(order.id)
    return order
```### 查看模式```python
# apps/orders/views.py
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrderSerializer
        return OrderDetailSerializer

    def get_queryset(self):
        return (
            Order.objects
            .filter(customer=self.request.user)
            .select_related("product", "customer")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        order = create_order(
            customer=self.request.user,
            product_id=serializer.validated_data["product_id"],
            quantity=serializer.validated_data["quantity"],
        )
        serializer.instance = order
```### 测试模式（pytest + Factory Boy）```python
# apps/orders/tests/factories.py
import factory
from apps.accounts.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "orders.Order"

    customer = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory, stock=100)
    quantity = 1
    total = factory.LazyAttribute(lambda o: o.product.price * o.quantity)

# apps/orders/tests/test_views.py
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestCreateOrder:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_order_success(self):
        product = ProductFactory(price=29_99, stock=10)
        response = self.client.post("/api/orders/", {
            "product_id": str(product.id),
            "quantity": 2,
        })
        assert response.status_code == 201
        assert response.data["total"] == 59_98

    def test_create_order_insufficient_stock(self):
        product = ProductFactory(stock=0)
        response = self.client.post("/api/orders/", {
            "product_id": str(product.id),
            "quantity": 1,
        })
        assert response.status_code == 409

    def test_create_order_unauthenticated(self):
        self.client.force_authenticate(None)
        response = self.client.post("/api/orders/", {})
        assert response.status_code == 401
```## 环境变量```bash
# Django
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=api.example.com

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/myapp

# Redis (Celery broker + cache)
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15       # minutes
JWT_REFRESH_TOKEN_LIFETIME=10080   # minutes (7 days)

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
```## 测试策略```bash
# Run all tests
pytest --cov=apps --cov-report=term-missing

# Run specific app tests
pytest apps/orders/tests/ -v

# Run with parallel execution
pytest -n auto

# Only failing tests from last run
pytest --lf
```## ECC 工作流程```bash
# Planning
/plan "Add order refund system with Stripe integration"

# Development with TDD
/tdd                    # pytest-based TDD workflow

# Review
/python-review          # Python-specific code review
/security-scan          # Django security audit
/code-review            # General quality check

# Verification
/verify                 # Build, lint, test, security scan
```## Git 工作流程

- `feat:` 新功能、`fix:` 错误修复、`refactor:` 代码更改
- 来自“main”的功能分支，需要 PR
- CI：ruff（lint + 格式）、mypy（类型）、pytest（测试）、安全性（dep 检查）
- 部署：Docker 镜像，通过 Kubernetes 或 Railway 管理