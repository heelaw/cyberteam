# PHP 测试

> 此文件使用 PHP 特定内容扩展了 [common/testing.md](../common/testing.md)。

## 框架

使用 **PHPUnit** 作为默认测试框架。如果项目中配置了 **Pest**，请优先使用 Pest 进行新测试并避免混合框架。

## 覆盖范围```bash
vendor/bin/phpunit --coverage-text
# or
vendor/bin/pest --coverage
```更喜欢 CI 中的 **pcov** 或 **Xdebug**，并将覆盖阈值保留在 CI 中，而不是作为部落知识。

## 测试组织

- 将快速单元测试与框架/数据库集成测试分开。
- 使用工厂/构建器来代替大型手写数组。
- 将 HTTP/控制器测试重点放在传输和验证上；将业务规则转移到服务级别测试中。

## 惯性

如果项目使用 Inertia.js，则更喜欢使用“assertInertia”和“AssertableInertia”来验证组件名称和属性，而不是原始 JSON 断言。

## 参考

请参阅技能：“tdd-workflow”，了解存储库范围内的 RED -> GREEN -> REFACTOR 循环。
请参阅技能：`laravel-tdd` 了解 Laravel 特定的测试模式（PHPUnit 和 Pest）。