# Laravel API — 项目 CLAUDE.md

> 使用 PostgreSQL、Redis 和队列的 Laravel API 的真实示例。
> 将其复制到您的项目根目录并针对您的服务进行自定义。

## 项目概述

**堆栈：** PHP 8.2+、Laravel 11.x、PostgreSQL、Redis、Horizon、PHPUnit/Pest、Docker Compose

**架构：** 模块化 Laravel 应用程序，包含控制器 -> 服务 -> 操作、Eloquent ORM、用于异步工作的队列、用于验证的表单请求以及用于一致 JSON 响应的 API 资源。

## 关键规则

### PHP 约定

- 所有 PHP 文件中的 `declare(strict_types=1)`
- 随处使用类型化属性和返回类型
- 更喜欢服务和操作的“最终”类
- 提交的代码中没有“dd()”或“dump()”
- 通过 Laravel Pint 格式化 (PSR-12)

### API 响应信封

所有 API 响应都使用一致的信封：```json
{
  "success": true,
  "data": {"...": "..."},
  "error": null,
  "meta": {"page": 1, "per_page": 25, "total": 120}
}
```### 数据库

- 迁移到 git
- 使用 Eloquent 或查询生成器（除非参数化，否则没有原始 SQL）
- 索引“where”或“orderBy”中使用的任何列
- 避免改变服务中的模型实例；更喜欢通过存储库或查询构建器创建/更新

### 身份验证

- 通过 Sanctum 进行 API 身份验证
- 使用策略进行模型级授权
- 在控制器和服务中强制执行身份验证

### 验证

- 使用表单请求进行验证
- 将输入转换为业务逻辑的 DTO
- 永远不要相信派生字段的请求有效负载

### 错误处理

- 在服务中抛出域异常
- 通过“withExceptions”将异常映射到“bootstrap/app.php”中的 HTTP 响应
- 永远不要向客户暴露内部错误

### 代码风格

- 代码或注释中没有表情符号
- 最大行长度：120 个字符
- 控制器很薄；服务和操作保存业务逻辑

## 文件结构```
app/
  Actions/
  Console/
  Events/
  Exceptions/
  Http/
    Controllers/
    Middleware/
    Requests/
    Resources/
  Jobs/
  Models/
  Policies/
  Providers/
  Services/
  Support/
config/
database/
  factories/
  migrations/
  seeders/
routes/
  api.php
  web.php
```## 关键模式

### 服务层```php
<?php

declare(strict_types=1);

final class CreateOrderAction
{
    public function __construct(private OrderRepository $orders) {}

    public function handle(CreateOrderData $data): Order
    {
        return $this->orders->create($data);
    }
}

final class OrderService
{
    public function __construct(private CreateOrderAction $createOrder) {}

    public function placeOrder(CreateOrderData $data): Order
    {
        return $this->createOrder->handle($data);
    }
}
```### 控制器模式```php
<?php

declare(strict_types=1);

final class OrdersController extends Controller
{
    public function __construct(private OrderService $service) {}

    public function store(StoreOrderRequest $request): JsonResponse
    {
        $order = $this->service->placeOrder($request->toDto());

        return response()->json([
            'success' => true,
            'data' => OrderResource::make($order),
            'error' => null,
            'meta' => null,
        ], 201);
    }
}
```### 政策模式```php
<?php

declare(strict_types=1);

use App\Models\Order;
use App\Models\User;

final class OrderPolicy
{
    public function view(User $user, Order $order): bool
    {
        return $order->user_id === $user->id;
    }
}
```### 表单请求 + DTO```php
<?php

declare(strict_types=1);

final class StoreOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return (bool) $this->user();
    }

    public function rules(): array
    {
        return [
            'items' => ['required', 'array', 'min:1'],
            'items.*.sku' => ['required', 'string'],
            'items.*.quantity' => ['required', 'integer', 'min:1'],
        ];
    }

    public function toDto(): CreateOrderData
    {
        return new CreateOrderData(
            userId: (int) $this->user()->id,
            items: $this->validated('items'),
        );
    }
}
```### API 资源```php
<?php

declare(strict_types=1);

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

final class OrderResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'status' => $this->status,
            'total' => $this->total,
            'created_at' => $this->created_at?->toIso8601String(),
        ];
    }
}
```### 队列作业```php
<?php

declare(strict_types=1);

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use App\Repositories\OrderRepository;
use App\Services\OrderMailer;

final class SendOrderConfirmation implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(private int $orderId) {}

    public function handle(OrderRepository $orders, OrderMailer $mailer): void
    {
        $order = $orders->findOrFail($this->orderId);
        $mailer->sendOrderConfirmation($order);
    }
}
```### 测试模式（Pest）```php
<?php

declare(strict_types=1);

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use function Pest\Laravel\actingAs;
use function Pest\Laravel\assertDatabaseHas;
use function Pest\Laravel\postJson;

uses(RefreshDatabase::class);

test('user can place order', function () {
    $user = User::factory()->create();

    actingAs($user);

    $response = postJson('/api/orders', [
        'items' => [['sku' => 'sku-1', 'quantity' => 2]],
    ]);

    $response->assertCreated();
    assertDatabaseHas('orders', ['user_id' => $user->id]);
});
```### 测试模式 (PHPUnit)```php
<?php

declare(strict_types=1);

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class OrdersControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_user_can_place_order(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->postJson('/api/orders', [
            'items' => [['sku' => 'sku-1', 'quantity' => 2]],
        ]);

        $response->assertCreated();
        $this->assertDatabaseHas('orders', ['user_id' => $user->id]);
    }
}
```