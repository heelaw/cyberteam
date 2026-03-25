# Laravel TDD 工作流程

使用 PHPUnit 和 Pest 进行 Laravel 应用程序的测试驱动开发，覆盖率超过 80%（单元 + 功能）。

## 何时使用

- Laravel 中的新功能或端点
- 错误修复或重构
- 测试 Eloquent 模型、策略、作业和通知
- 首选 Pest 进行新测试，除非该项目已经在 PHPUnit 上标准化

## 它是如何工作的

### 红-绿-重构循环

1）编写一个失败的测试
2）实施最小的改变以通过
3）重构同时保持测试绿色

### 测试层

- **单元**：纯 PHP 类、值对象、服务
- **功能**：HTTP 端点、身份验证、验证、策略
- **集成**：数据库+队列+外部边界

根据范围选择图层：

- 对纯业务逻辑和服务使用**单元**测试。
- 使用 HTTP、身份验证、验证和响应形状的 **功能** 测试。
- 一起验证数据库/队列/外部服务时使用**集成**测试。

### 数据库策略

- 用于大多数功能/集成测试的“RefreshDatabase”（每次测试运行运行一次迁移，然后在支持时将每个测试包装在事务中；内存数据库可能会在每次测试时重新迁移）
- 当模式已经迁移并且您只需要按测试回滚时“DatabaseTransactions”
- “DatabaseMigrations”，当您需要为每个测试进行完全迁移/刷新并且可以承受成本时

使用“RefreshDatabase”作为涉及数据库的测试的默认设置：对于具有事务支持的数据库，它在每次测试运行时运行一次迁移（通过静态标志）并将每个测试包装在事务中；对于`:memory:` SQLite 或没有事务的连接，它会在每次测试之前迁移。当架构已经迁移并且您只需要按测试回滚时，请使用“DatabaseTransactions”。

### 测试框架选择

- 新测试可用时默认为 **Pest**。
- 仅当项目已标准化或需要 PHPUnit 特定工具时才使用 **PHPUnit**。

## 示例

### PHPUnit 示例```php
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class ProjectControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_owner_can_create_project(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->postJson('/api/projects', [
            'name' => 'New Project',
        ]);

        $response->assertCreated();
        $this->assertDatabaseHas('projects', ['name' => 'New Project']);
    }
}
```### 功能测试示例（HTTP 层）```php
use App\Models\Project;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class ProjectIndexTest extends TestCase
{
    use RefreshDatabase;

    public function test_projects_index_returns_paginated_results(): void
    {
        $user = User::factory()->create();
        Project::factory()->count(3)->for($user)->create();

        $response = $this->actingAs($user)->getJson('/api/projects');

        $response->assertOk();
        $response->assertJsonStructure(['success', 'data', 'error', 'meta']);
    }
}
```### 害虫示例```php
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;

use function Pest\Laravel\actingAs;
use function Pest\Laravel\assertDatabaseHas;

uses(RefreshDatabase::class);

test('owner can create project', function () {
    $user = User::factory()->create();

    $response = actingAs($user)->postJson('/api/projects', [
        'name' => 'New Project',
    ]);

    $response->assertCreated();
    assertDatabaseHas('projects', ['name' => 'New Project']);
});
```### 功能测试 Pest 示例（HTTP 层）```php
use App\Models\Project;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;

use function Pest\Laravel\actingAs;

uses(RefreshDatabase::class);

test('projects index returns paginated results', function () {
    $user = User::factory()->create();
    Project::factory()->count(3)->for($user)->create();

    $response = actingAs($user)->getJson('/api/projects');

    $response->assertOk();
    $response->assertJsonStructure(['success', 'data', 'error', 'meta']);
});
```### 工厂和状态

- 使用工厂来获取测试数据
- 定义边缘情况的状态（存档、管理、试用）```php
$user = User::factory()->state(['role' => 'admin'])->create();
```### 数据库测试

- 使用“RefreshDatabase”来保持干净状态
- 保持测试的隔离性和确定性
- 优先选择“assertDatabaseHas”而不是手动查询

### 持久性测试示例```php
use App\Models\Project;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class ProjectRepositoryTest extends TestCase
{
    use RefreshDatabase;

    public function test_project_can_be_retrieved_by_slug(): void
    {
        $project = Project::factory()->create(['slug' => 'alpha']);

        $found = Project::query()->where('slug', 'alpha')->firstOrFail();

        $this->assertSame($project->id, $found->id);
    }
}
```### 假货的副作用

- 用于工作的“Bus::fake()”
- 用于排队工作的“Queue::fake()”
- 用于通知的“Mail::fake()”和“Notification::fake()”
- 用于领域事件的“Event::fake()”```php
use Illuminate\Support\Facades\Queue;

Queue::fake();

dispatch(new SendOrderConfirmation($order->id));

Queue::assertPushed(SendOrderConfirmation::class);
``````php
use Illuminate\Support\Facades\Notification;

Notification::fake();

$user->notify(new InvoiceReady($invoice));

Notification::assertSentTo($user, InvoiceReady::class);
```### 身份验证测试（Sanctum）```php
use Laravel\Sanctum\Sanctum;

Sanctum::actingAs($user);

$response = $this->getJson('/api/projects');
$response->assertOk();
```### HTTP 和外部服务

- 使用 `Http::fake()` 来隔离外部 API
- 使用“Http::assertSent()”断言出站有效负载

### 覆盖目标

- 对单元+功能测试执行 80% 以上的覆盖率
- 在 CI 中使用 `pcov` 或 `XDEBUG_MODE=coverage`

### 测试命令

- `php artisan 测试`
- `供应商/bin/phpunit`
- `供应商/垃圾箱/害虫`

### 测试配置

- 使用`phpunit.xml`设置`DB_CONNECTION=sqlite`和`DB_DATABASE=:memory:`进行快速测试
- 为测试保留单独的环境以避免触及开发/生产数据

### 授权测试```php
use Illuminate\Support\Facades\Gate;

$this->assertTrue(Gate::forUser($user)->allows('update', $project));
$this->assertFalse(Gate::forUser($otherUser)->allows('update', $project));
```### 惯性特征测试

使用 Inertia.js 时，使用 Inertia 测试助手对组件名称和 props 进行断言。```php
use App\Models\User;
use Inertia\Testing\AssertableInertia;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class DashboardInertiaTest extends TestCase
{
    use RefreshDatabase;

    public function test_dashboard_inertia_props(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->get('/dashboard');

        $response->assertOk();
        $response->assertInertia(fn (AssertableInertia $page) => $page
            ->component('Dashboard')
            ->where('user.id', $user->id)
            ->has('projects')
        );
    }
}
```优先使用“assertInertia”而不是原始 JSON 断言，以使测试与 Inertia 响应保持一致。