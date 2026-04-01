# Laravel 安全最佳实践

针对 Laravel 应用程序的全面安全指南，以防止常见漏洞。

## 何时激活

- 添加身份验证或授权
- 处理用户输入和文件上传
- 构建新的 API 端点
- 管理秘密和环境设置
- 强化生产部署

## 它是如何工作的

- 中间件提供基线保护（通过 `VerifyCsrfToken` 进行 CSRF，通过 `SecurityHeaders` 进行安全标头）。
- 守卫和策略强制执行访问控制（`auth:sanctum`、`$this->authorize`、策略中间件）。
- 表单请求在输入（“UploadInvoiceRequest”）到达服务之前对其进行验证和调整。
- 速率限制增加了滥用保护（`RateLimiter::for('login')`）以及身份验证控制。
- 数据安全来自加密转换、批量分配保护和签名路由（`URL::temporarySignedRoute` + `signed` 中间件）。

## 核心安全设置

- 生产中的“APP_DEBUG = false”
- 必须在妥协时设置和轮换“APP_KEY”
- 设置“SESSION_SECURE_COOKIE=true”和“SESSION_SAME_SITE=lax”（或针对敏感应用程序设置“strict”）
- 配置可信代理以进行正确的 HTTPS 检测

## 会话和 Cookie 强化

- 设置 `SESSION_HTTP_ONLY=true` 以阻止 JavaScript 访问
- 对高风险流程使用“SESSION_SAME_SITE=strict”
- 在登录和权限更改时重新生成会话

## 身份验证和令牌

- 使用 Laravel Sanctum 或 Passport 进行 API 身份验证
- 优先选择具有敏感数据刷新流程的短期令牌
- 撤销注销和受损帐户上的令牌

路由保护示例：```php
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::middleware('auth:sanctum')->get('/me', function (Request $request) {
    return $request->user();
});
```## 密码安全

- 使用“Hash::make()”对密码进行哈希处理，并且从不存储明文
- 使用 Laravel 的密码代理来重置流程```php
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rules\Password;

$validated = $request->validate([
    'password' => ['required', 'string', Password::min(12)->letters()->mixedCase()->numbers()->symbols()],
]);

$user->update(['password' => Hash::make($validated['password'])]);
```## 授权：政策和门槛

- 使用策略进行模型级授权
- 在控制器和服务中强制授权```php
$this->authorize('update', $project);
```使用策略中间件进行路由级实施：```php
use Illuminate\Support\Facades\Route;

Route::put('/projects/{project}', [ProjectController::class, 'update'])
    ->middleware(['auth:sanctum', 'can:update,project']);
```## 验证和数据清理

- 始终通过表单请求验证输入
- 使用严格的验证规则和类型检查
- 永远不要相信派生字段的请求有效负载

## 批量分配保护

- 使用 `$fillable` 或 `$guarded` 并避免 `Model::unguard()`
- 更喜欢 DTO 或显式属性映射

## SQL注入预防

- 使用 Eloquent 或查询构建器参数绑定
- 除非绝对必要，否则避免原始 SQL```php
DB::select('select * from users where email = ?', [$email]);
```## XSS 预防

- Blade 默认转义输出 (`{{ }}`)
- 使用`{!! !!}` 仅适用于受信任的、经过净化的 HTML
- 使用专用库清理富文本

## CSRF 保护

- 保持“VerifyCsrfToken”中间件启用
- 在表单中包含“@csrf”并发送 SPA 请求的 XSRF 令牌

对于 Sanctum 的 SPA 身份验证，请确保配置有状态请求：```php
// config/sanctum.php
'stateful' => explode(',', env('SANCTUM_STATEFUL_DOMAINS', 'localhost')),
```## 文件上传安全

- 验证文件大小、MIME 类型和扩展名
- 尽可能将上传内容存储在公共路径之外
- 如果需要，扫描文件中是否存在恶意软件```php
final class UploadInvoiceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return (bool) $this->user()?->can('upload-invoice');
    }

    public function rules(): array
    {
        return [
            'invoice' => ['required', 'file', 'mimes:pdf', 'max:5120'],
        ];
    }
}
``````php
$path = $request->file('invoice')->store(
    'invoices',
    config('filesystems.private_disk', 'local') // set this to a non-public disk
);
```## 速率限制

- 在身份验证上应用“throttle”中间件并写入端点
- 对登录、密码重置和 OTP 使用更严格的限制```php
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;

RateLimiter::for('login', function (Request $request) {
    return [
        Limit::perMinute(5)->by($request->ip()),
        Limit::perMinute(5)->by(strtolower((string) $request->input('email'))),
    ];
});
```## 秘密和凭证

- 切勿将秘密提交给源代码管理
- 使用环境变量和秘密管理器
- 暴露后旋转密钥并使会话无效

## 加密属性

对静态敏感列使用加密转换。```php
protected $casts = [
    'api_token' => 'encrypted',
];
```## 安全标头

- 在适当的情况下添加 CSP、HSTS 和框架保护
- 使用受信任的代理配置来强制执行 HTTPS 重定向

设置标头的中间件示例：```php
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

final class SecurityHeaders
{
    public function handle(Request $request, \Closure $next): Response
    {
        $response = $next($request);

        $response->headers->add([
            'Content-Security-Policy' => "default-src 'self'",
            'Strict-Transport-Security' => 'max-age=31536000', // add includeSubDomains/preload only when all subdomains are HTTPS
            'X-Frame-Options' => 'DENY',
            'X-Content-Type-Options' => 'nosniff',
            'Referrer-Policy' => 'no-referrer',
        ]);

        return $response;
    }
}
```## CORS 和 API 暴露

- 限制“config/cors.php”中的来源
- 避免经过身份验证的路由使用通配符来源```php
// config/cors.php
return [
    'paths' => ['api/*', 'sanctum/csrf-cookie'],
    'allowed_methods' => ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    'allowed_origins' => ['https://app.example.com'],
    'allowed_headers' => [
        'Content-Type',
        'Authorization',
        'X-Requested-With',
        'X-XSRF-TOKEN',
        'X-CSRF-TOKEN',
    ],
    'supports_credentials' => true,
];
```## 日志记录和 PII

- 切勿记录密码、令牌或完整卡数据
- 编辑结构化日志中的敏感字段```php
use Illuminate\Support\Facades\Log;

Log::info('User updated profile', [
    'user_id' => $user->id,
    'email' => '[REDACTED]',
    'token' => '[REDACTED]',
]);
```## 依赖安全

- 定期运行“作曲家审核”
- 谨慎固定依赖项并及时更新 CVE

## 签名 URL

使用签名路由作为临时的、防篡改的链接。```php
use Illuminate\Support\Facades\URL;

$url = URL::temporarySignedRoute(
    'downloads.invoice',
    now()->addMinutes(15),
    ['invoice' => $invoice->id]
);
``````php
use Illuminate\Support\Facades\Route;

Route::get('/invoices/{invoice}/download', [InvoiceController::class, 'download'])
    ->name('downloads.invoice')
    ->middleware('signed');
```