# PHP 测试

> 该文件使用 PHP 特定内容扩展了通用测试规则。

## 框架

使用 **PHPUnit** 作为默认测试框架。 **Pest** 当项目已经使用它时也是可以接受的。

## 覆盖范围```bash
vendor/bin/phpunit --coverage-text
# or
vendor/bin/pest --coverage
```## 测试组织

- 将快速单元测试与框架/数据库集成测试分开。
- 使用工厂/构建器来代替大型手写数组。
- 将 HTTP/控制器测试重点放在传输和验证上；将业务规则转移到服务级别测试中。