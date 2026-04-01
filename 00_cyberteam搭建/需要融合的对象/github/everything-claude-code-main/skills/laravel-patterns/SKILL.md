# Laravel 开发模式

用于可扩展、可维护应用程序的生产级 Laravel 架构模式。

## 何时使用

- 构建 Laravel Web 应用程序或 API
- 构建控制器、服务和域逻辑
- 使用 Eloquent 模型和关系
- 设计具有资源和分页的 API
- 添加队列、事件、缓存和后台作业

## 它是如何工作的

- 围绕清晰的边界构建应用程序（控制器 -> 服务/操作 -> 模型）。
- 使用显式绑定和作用域绑定来保持路由可预测；仍然强制执行访问控制授权。
- 支持类型化模型、类型转换和作用域，以保持领域逻辑的一致性。
- 将 IO 密集型工作保留在队列中并缓存昂贵的读取。
- 将配置集中在`config/*`中并保持环境明确。

## 示例

### 项目结构

使用具有清晰层边界的传统 Laravel 布局（HTTP、服务/操作、模型）。

### 推荐布局```
app/
├── Actions/            # Single-purpose use cases
├── Console/
├── Events/
├── Exceptions/
├── Http/
│   ├── Controllers/
│   ├── Middleware/
│   ├── Requests/       # Form request validation
│   └── Resources/      # API resources
├── Jobs/
├── Models/
├── Policies/
├── Providers/
├── Services/           # Coordinating domain services
└── Support/
config/
database/
├── factories/
├── migrations/
└── seeders/
resources/
├── views/
└── lang/
routes/
├── api.php
├── web.php
└── console.php
```### 控制器 -> 服务 -> 操作

保持控制器纤薄。将编排放入服务中，将单一用途逻辑放入操作中。```php
final class CreateOrderAction
{
    public function __construct(private OrderRepository $orders) {}

    public function handle(CreateOrderData $data): Order
    {
        return $this->orders->create($data);
    }
}

final class OrdersController extends Controller
{
    public function __construct(private CreateOrderAction $createOrder) {}

    public function store(StoreOrderRequest $request): JsonResponse
    {
        $order = $this->createOrder->handle($request->toDto());

        return response()->json([
            'success' => true,
            'data' => OrderResource::make($order),
            'error' => null,
            'meta' => null,
        ], 201);
    }
}
```### 路由和控制器

为了清晰起见，首选路由模型绑定和资源控制器。```php
use Illuminate\Support\Facades\Route;

Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('projects', ProjectController::class);
});
```### 路由模型绑定（范围）

使用作用域绑定来防止跨租户访问。```php
Route::scopeBindings()->group(function () {
    Route::get('/accounts/{account}/projects/{project}', [ProjectController::class, 'show']);
});
```### 嵌套路由和绑定名称

- 保持前缀和路径一致以避免双重嵌套（例如，“对话”与“对话”）。
- 使用与绑定模型匹配的单个参数名称（例如，“{conversation}”代表“Conversation”）。
- 嵌套时首选作用域绑定以强制执行父子关系。```php
use App\Http\Controllers\Api\ConversationController;
use App\Http\Controllers\Api\MessageController;
use Illuminate\Support\Facades\Route;

Route::middleware('auth:sanctum')->prefix('conversations')->group(function () {
    Route::post('/', [ConversationController::class, 'store'])->name('conversations.store');

    Route::scopeBindings()->group(function () {
        Route::get('/{conversation}', [ConversationController::class, 'show'])
            ->name('conversations.show');

        Route::post('/{conversation}/messages', [MessageController::class, 'store'])
            ->name('conversation-messages.store');

        Route::get('/{conversation}/messages/{message}', [MessageController::class, 'show'])
            ->name('conversation-messages.show');
    });
});
```如果您希望参数解析为不同的模型类，请定义显式绑定。对于自定义绑定逻辑，请使用“Route::bind()”或在模型上实现“resolveRouteBinding()”。```php
use App\Models\AiConversation;
use Illuminate\Support\Facades\Route;

Route::model('conversation', AiConversation::class);
```### 服务容器绑定

将接口绑定到服务提供者中的实现，以实现清晰的依赖关系连接。```php
use App\Repositories\EloquentOrderRepository;
use App\Repositories\OrderRepository;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind(OrderRepository::class, EloquentOrderRepository::class);
    }
}
```### Eloquent 模型模式

### 模型配置```php
final class Project extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'owner_id', 'status'];

    protected $casts = [
        'status' => ProjectStatus::class,
        'archived_at' => 'datetime',
    ];

    public function owner(): BelongsTo
    {
        return $this->belongsTo(User::class, 'owner_id');
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->whereNull('archived_at');
    }
}
```### 自定义转换和值对象

使用枚举或值对象进行严格类型化。```php
use Illuminate\Database\Eloquent\Casts\Attribute;

protected $casts = [
    'status' => ProjectStatus::class,
];
``````php
protected function budgetCents(): Attribute
{
    return Attribute::make(
        get: fn (int $value) => Money::fromCents($value),
        set: fn (Money $money) => $money->toCents(),
    );
}
```### 急切加载以避免 N+1```php
$orders = Order::query()
    ->with(['customer', 'items.product'])
    ->latest()
    ->paginate(25);
```### 复杂过滤器的查询对象```php
final class ProjectQuery
{
    public function __construct(private Builder $query) {}

    public function ownedBy(int $userId): self
    {
        $query = clone $this->query;

        return new self($query->where('owner_id', $userId));
    }

    public function active(): self
    {
        $query = clone $this->query;

        return new self($query->whereNull('archived_at'));
    }

    public function builder(): Builder
    {
        return $this->query;
    }
}
```### 全局范围和软删除

使用全局范围进行默认过滤，使用“SoftDeletes”进行可恢复记录。
对同一过滤器使用全局作用域或命名作用域，而不是同时使用两者，除非您打算分层行为。```php
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Builder;

final class Project extends Model
{
    use SoftDeletes;

    protected static function booted(): void
    {
        static::addGlobalScope('active', function (Builder $builder): void {
            $builder->whereNull('archived_at');
        });
    }
}
```### 可重用过滤器的查询范围```php
use Illuminate\Database\Eloquent\Builder;

final class Project extends Model
{
    public function scopeOwnedBy(Builder $query, int $userId): Builder
    {
        return $query->where('owner_id', $userId);
    }
}

// In service, repository etc.
$projects = Project::ownedBy($user->id)->get();
```### 多步更新事务```php
use Illuminate\Support\Facades\DB;

DB::transaction(function (): void {
    $order->update(['status' => 'paid']);
    $order->items()->update(['paid_at' => now()]);
});
```### 迁移

### 命名约定

- 文件名使用时间戳：`YYYY_MM_DD_HHMMSS_create_users_table.php`
- 迁移使用匿名类（无命名类）；文件名传达意图
- 表名默认为 `snake_case` 和复数

### 迁移示例```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('customer_id')->constrained()->cascadeOnDelete();
            $table->string('status', 32)->index();
            $table->unsignedInteger('total_cents');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
```### 表单请求和验证

在表单请求中保留验证并将输入转换为 DTO。```php
use App\Models\Order;

final class StoreOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()?->can('create', Order::class) ?? false;
    }

    public function rules(): array
    {
        return [
            'customer_id' => ['required', 'integer', 'exists:customers,id'],
            'items' => ['required', 'array', 'min:1'],
            'items.*.sku' => ['required', 'string'],
            'items.*.quantity' => ['required', 'integer', 'min:1'],
        ];
    }

    public function toDto(): CreateOrderData
    {
        return new CreateOrderData(
            customerId: (int) $this->validated('customer_id'),
            items: $this->validated('items'),
        );
    }
}
```### API 资源

保持 API 响应与资源和分页一致。```php
$projects = Project::query()->active()->paginate(25);

return response()->json([
    'success' => true,
    'data' => ProjectResource::collection($projects->items()),
    'error' => null,
    'meta' => [
        'page' => $projects->currentPage(),
        'per_page' => $projects->perPage(),
        'total' => $projects->total(),
    ],
]);
```### 事件、作业和队列

- 发出域事件以产生副作用（电子邮件、分析）
- 使用排队作业来处理缓慢的工作（报告、导出、webhooks）
- 更喜欢具有重试和退避功能的幂等处理程序

### 缓存

- 缓存读取繁重的端点和昂贵的查询
- 使模型事件的缓存无效（创建/更新/删除）
- 缓存相关数据时使用标签，方便失效

### 配置和环境

- 在`.env`中保存秘密，在`config/*.php`中保存配置
- 在生产中使用每个环境的配置覆盖和`config:cache`