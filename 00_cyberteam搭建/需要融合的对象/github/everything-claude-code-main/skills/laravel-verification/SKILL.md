# Laravel 验证循环

在 PR 之前、重大更改之后运行以及预部署。

## 何时使用

- 在为 Laravel 项目打开拉取请求之前
- 重大重构或依赖升级之后
- 预部署或生产验证
- 运行完整的 lint -> 测试 -> 安全性 -> 部署准备管道

## 它是如何工作的

- 从环境检查到部署准备，按顺序运行各个阶段，以便每一层都建立在最后一层的基础上。
- 环境和作曲家检查其他一切；如果失败，请立即停止。
- 在运行完整的测试和覆盖之前，应该清理/静态分析。
- 安全和迁移审查在测试后进行，因此您可以在数据或发布步骤之前验证行为。
- 构建/部署准备情况和队列/调度程序检查是最后的关卡；任何故障都会阻止释放。

## 第一阶段：环境检查```bash
php -v
composer --version
php artisan --version
```- 验证 `.env` 是否存在以及所需的密钥是否存在
- 确认生产环境的“APP_DEBUG=false”
- 确认“APP_ENV”与目标部署匹配（“生产”、“暂存”）

如果本地使用 Laravel Sail：```bash
./vendor/bin/sail php -v
./vendor/bin/sail artisan --version
```## 阶段 1.5：Composer 和自动加载```bash
composer validate
composer dump-autoload -o
```## 第 2 阶段：Linting 和静态分析```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
```如果您的项目使用 Psalm 而不是 PHPStan：```bash
vendor/bin/psalm
```## 第 3 阶段：测试和覆盖率```bash
php artisan test
```覆盖范围（CI）：```bash
XDEBUG_MODE=coverage php artisan test --coverage
```CI 示例（格式 -> 静态分析 -> 测试）：```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
XDEBUG_MODE=coverage php artisan test --coverage
```## 第 4 阶段：安全性和依赖性检查```bash
composer audit
```## 第 5 阶段：数据库和迁移```bash
php artisan migrate --pretend
php artisan migrate:status
```- 仔细审查破坏性迁移
- 确保迁移文件名遵循“Y_m_d_His_*”（例如“2025_03_14_154210_create_orders_table.php”）并清楚地描述更改
- 确保回滚是可能的
- 验证“down()”方法并避免在没有显式备份的情况下发生不可逆转的数据丢失

## 第 6 阶段：构建和部署准备```bash
php artisan optimize:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache
```- 确保缓存预热在生产配置中成功
- 验证队列工作人员和调度程序是否已配置
- 确认 `storage/` 和 `bootstrap/cache/` 在目标环境中可写

## 第 7 阶段：队列和调度程序检查```bash
php artisan schedule:list
php artisan queue:failed
```如果使用 Horizo​​n：```bash
php artisan horizon:status
```如果“queue:monitor”可用，请使用它来检查积压而不处理作业：```bash
php artisan queue:monitor default --max=100
```主动验证（仅登台）：将无操作作业分派到专用队列并运行单个工作程序来处理它（确保配置了非“同步”队列连接）。```bash
php artisan tinker --execute="dispatch((new App\\Jobs\\QueueHealthcheck())->onQueue('healthcheck'))"
php artisan queue:work --once --queue=healthcheck
```验证作业产生了预期的副作用（日志条目、运行状况检查表行或指标）。

仅在处理测试作业是安全的非生产环境中运行此操作。

## 示例

最小流量：```bash
php -v
composer --version
php artisan --version
composer validate
vendor/bin/pint --test
vendor/bin/phpstan analyse
php artisan test
composer audit
php artisan migrate --pretend
php artisan config:cache
php artisan queue:failed
```CI 风格的管道：```bash
composer validate
composer dump-autoload -o
vendor/bin/pint --test
vendor/bin/phpstan analyse
XDEBUG_MODE=coverage php artisan test --coverage
composer audit
php artisan migrate --pretend
php artisan optimize:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan schedule:list
```