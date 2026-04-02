# 去测试

> 此文件使用 Go 特定内容扩展了 [common/testing.md](../common/testing.md)。

## 框架

将标准“go test”与**表驱动测试**结合使用。

## 种族检测

始终使用“-race”标志运行：```bash
go test -race ./...
```## 覆盖范围```bash
go test -cover ./...
```## 参考

有关详细的 Go 测试模式和帮助程序，请参阅技能：“golang-testing”。