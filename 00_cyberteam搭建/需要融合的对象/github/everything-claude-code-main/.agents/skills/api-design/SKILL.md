# API 设计模式

用于设计一致、开发人员友好的 REST API 的约定和最佳实践。

## 何时激活

- 设计新的API端点
- 审查现有的 API 合同
- 添加分页、过滤或排序
- 实现 API 的错误处理
- 规划API版本控制策略
- 构建公共或面向合作伙伴的 API

## 资源设计

### 网址结构```
# Resources are nouns, plural, lowercase, kebab-case
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PUT    /api/v1/users/:id
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id

# Sub-resources for relationships
GET    /api/v1/users/:id/orders
POST   /api/v1/users/:id/orders

# Actions that don't map to CRUD (use verbs sparingly)
POST   /api/v1/orders/:id/cancel
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
```### 命名规则```
# GOOD
/api/v1/team-members          # kebab-case for multi-word resources
/api/v1/orders?status=active  # query params for filtering
/api/v1/users/123/orders      # nested resources for ownership

# BAD
/api/v1/getUsers              # verb in URL
/api/v1/user                  # singular (use plural)
/api/v1/team_members          # snake_case in URLs
/api/v1/users/123/getOrders   # verb in nested resource
```## HTTP 方法和状态代码

### 方法语义

|方法|幂等|安全|用于 |
|--------|------------|------|---------|
|获取 |是的 |是的 |检索资源 |
|发布 |没有 |没有 |创建资源，触发操作 |
|放置|是的 |没有 |资源全面替换|
|补丁|否* |没有 |资源的部分更新 |
|删除 |是的 |没有 |删除资源 |

*通过正确的实施，PATCH 可以成为幂等的

### 状态代码参考```
# Success
200 OK                    — GET, PUT, PATCH (with response body)
201 Created               — POST (include Location header)
204 No Content            — DELETE, PUT (no response body)

# Client Errors
400 Bad Request           — Validation failure, malformed JSON
401 Unauthorized          — Missing or invalid authentication
403 Forbidden             — Authenticated but not authorized
404 Not Found             — Resource doesn't exist
409 Conflict              — Duplicate entry, state conflict
422 Unprocessable Entity  — Semantically invalid (valid JSON, bad data)
429 Too Many Requests     — Rate limit exceeded

# Server Errors
500 Internal Server Error — Unexpected failure (never expose details)
502 Bad Gateway           — Upstream service failed
503 Service Unavailable   — Temporary overload, include Retry-After
```### 常见错误```
# BAD: 200 for everything
{ "status": 200, "success": false, "error": "Not found" }

# GOOD: Use HTTP status codes semantically
HTTP/1.1 404 Not Found
{ "error": { "code": "not_found", "message": "User not found" } }

# BAD: 500 for validation errors
# GOOD: 400 or 422 with field-level details

# BAD: 200 for created resources
# GOOD: 201 with Location header
HTTP/1.1 201 Created
Location: /api/v1/users/abc-123
```## 响应格式

### 成功响应```json
{
  "data": {
    "id": "abc-123",
    "email": "alice@example.com",
    "name": "Alice",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```### 集合响应（带分页）```json
{
  "data": [
    { "id": "abc-123", "name": "Alice" },
    { "id": "def-456", "name": "Bob" }
  ],
  "meta": {
    "total": 142,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
  },
  "links": {
    "self": "/api/v1/users?page=1&per_page=20",
    "next": "/api/v1/users?page=2&per_page=20",
    "last": "/api/v1/users?page=8&per_page=20"
  }
}
```### 错误响应```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address",
        "code": "invalid_format"
      },
      {
        "field": "age",
        "message": "Must be between 0 and 150",
        "code": "out_of_range"
      }
    ]
  }
}
```### 响应信封变体```typescript
// Option A: Envelope with data wrapper (recommended for public APIs)
interface ApiResponse<T> {
  data: T;
  meta?: PaginationMeta;
  links?: PaginationLinks;
}

interface ApiError {
  error: {
    code: string;
    message: string;
    details?: FieldError[];
  };
}

// Option B: Flat response (simpler, common for internal APIs)
// Success: just return the resource directly
// Error: return error object
// Distinguish by HTTP status code
```## 分页

### 基于偏移（简单）```
GET /api/v1/users?page=2&per_page=20

# Implementation
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 20;
```**优点：** 易于实现，支持“跳转到N页”
**缺点：** 大偏移量 (OFFSET 100000) 时速度较慢，与并发插入不一致

### 基于游标（可扩展）```
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ&limit=20

# Implementation
SELECT * FROM users
WHERE id > :cursor_id
ORDER BY id ASC
LIMIT 21;  -- fetch one extra to determine has_next
``````json
{
  "data": [...],
  "meta": {
    "has_next": true,
    "next_cursor": "eyJpZCI6MTQzfQ"
  }
}
```**优点：** 无论位置如何，性能始终如一，并发插入时稳定
**缺点：** 无法跳转到任意页面，光标不透明

### 何时使用哪个

|使用案例|分页类型 |
|----------|----------------|
|管理仪表板、小型数据集 (<10K) |偏移|
|无限滚动、提要、大型数据集 |光标|
|公共 API |带偏移量（可选）的光标（默认）|
|搜索结果 |偏移量（用户期望页码）|

## 过滤、排序和搜索

### 过滤```
# Simple equality
GET /api/v1/orders?status=active&customer_id=abc-123

# Comparison operators (use bracket notation)
GET /api/v1/products?price[gte]=10&price[lte]=100
GET /api/v1/orders?created_at[after]=2025-01-01

# Multiple values (comma-separated)
GET /api/v1/products?category=electronics,clothing

# Nested fields (dot notation)
GET /api/v1/orders?customer.country=US
```### 排序```
# Single field (prefix - for descending)
GET /api/v1/products?sort=-created_at

# Multiple fields (comma-separated)
GET /api/v1/products?sort=-featured,price,-created_at
```### 全文搜索```
# Search query parameter
GET /api/v1/products?q=wireless+headphones

# Field-specific search
GET /api/v1/users?email=alice
```### 稀疏字段集```
# Return only specified fields (reduces payload)
GET /api/v1/users?fields=id,name,email
GET /api/v1/orders?fields=id,total,status&include=customer.name
```## 身份验证和授权

### 基于令牌的身份验证```
# Bearer token in Authorization header
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# API key (for server-to-server)
GET /api/v1/data
X-API-Key: sk_live_abc123
```### 授权模式```typescript
// Resource-level: check ownership
app.get("/api/v1/orders/:id", async (req, res) => {
  const order = await Order.findById(req.params.id);
  if (!order) return res.status(404).json({ error: { code: "not_found" } });
  if (order.userId !== req.user.id) return res.status(403).json({ error: { code: "forbidden" } });
  return res.json({ data: order });
});

// Role-based: check permissions
app.delete("/api/v1/users/:id", requireRole("admin"), async (req, res) => {
  await User.delete(req.params.id);
  return res.status(204).send();
});
```## 速率限制

### 标题```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

# When exceeded
HTTP/1.1 429 Too Many Requests
Retry-After: 60
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```### 速率限制等级

|等级 |限制|窗口|使用案例|
|------|--------|--------|----------|
|匿名 | 30/分钟 |每个IP |公共端点 |
|已认证 | 100/分钟 |每个用户 |标准API访问|
|高级| 1000/分钟 |每个 API 密钥 |付费 API 计划 |
|内部| 10000/分钟 |每项服务 |服务到服务|

## 版本控制

### URL 路径版本控制（推荐）```
/api/v1/users
/api/v2/users
```**优点：** 显式、易于路由、可缓存
**缺点：** 版本之间的 URL 发生变化

### 标头版本控制```
GET /api/users
Accept: application/vnd.myapp.v2+json
```**优点：** 干净的 URL
**缺点：** 更难测试，容易忘记

### 版本控制策略```
1. Start with /api/v1/ — don't version until you need to
2. Maintain at most 2 active versions (current + previous)
3. Deprecation timeline:
   - Announce deprecation (6 months notice for public APIs)
   - Add Sunset header: Sunset: Sat, 01 Jan 2026 00:00:00 GMT
   - Return 410 Gone after sunset date
4. Non-breaking changes don't need a new version:
   - Adding new fields to responses
   - Adding new optional query parameters
   - Adding new endpoints
5. Breaking changes require a new version:
   - Removing or renaming fields
   - Changing field types
   - Changing URL structure
   - Changing authentication method
```## 实现模式

### TypeScript（Next.js API 路线）```typescript
import { z } from "zod";
import { NextRequest, NextResponse } from "next/server";

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = createUserSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({
      error: {
        code: "validation_error",
        message: "Request validation failed",
        details: parsed.error.issues.map(i => ({
          field: i.path.join("."),
          message: i.message,
          code: i.code,
        })),
      },
    }, { status: 422 });
  }

  const user = await createUser(parsed.data);

  return NextResponse.json(
    { data: user },
    {
      status: 201,
      headers: { Location: `/api/v1/users/${user.id}` },
    },
  );
}
```### Python（Django REST 框架）```python
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "created_at"]

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer

    def create(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.create(**serializer.validated_data)
        return Response(
            {"data": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
            headers={"Location": f"/api/v1/users/{user.id}"},
        )
```### 去 (net/http)```go
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid_json", "Invalid request body")
        return
    }

    if err := req.Validate(); err != nil {
        writeError(w, http.StatusUnprocessableEntity, "validation_error", err.Error())
        return
    }

    user, err := h.service.Create(r.Context(), req)
    if err != nil {
        switch {
        case errors.Is(err, domain.ErrEmailTaken):
            writeError(w, http.StatusConflict, "email_taken", "Email already registered")
        default:
            writeError(w, http.StatusInternalServerError, "internal_error", "Internal error")
        }
        return
    }

    w.Header().Set("Location", fmt.Sprintf("/api/v1/users/%s", user.ID))
    writeJSON(w, http.StatusCreated, map[string]any{"data": user})
}
```## API 设计清单

在交付新端点之前：

- [ ] 资源 URL 遵循命名约定（复数、短横线大小写、无动词）
- [ ] 使用正确的 HTTP 方法（GET 用于读取，POST 用于创建等）
- [ ] 返回适当的状态代码（不是所有情况都是 200）
- [ ] 使用模式验证输入（Zod、Pydantic、Bean 验证）
- [ ] 错误响应遵循带有代码和消息的标准格式
- [ ] 为列表端点（光标或偏移量）实现分页
- [ ] 需要身份验证（或明确标记为公共）
- [ ] 授权检查（用户只能访问自己的资源）
- [ ] 已配置速率限制
- [ ] 响应不会泄露内部细节（堆栈跟踪、SQL 错误）
- [ ] 与现有端点一致的命名（camelCase 与 Snake_case）
- [ ] 记录（OpenAPI/Swagger 规范已更新）