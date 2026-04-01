# Perl 测试

> 此文件使用 Perl 特定内容扩展了 [common/testing.md](../common/testing.md)。

## 框架

对新项目使用 **Test2::V0** （不是 Test::More）：```perl
use Test2::V0;

is($result, 42, 'answer is correct');

done_testing;
```## 跑步者```bash
prove -l t/              # adds lib/ to @INC
prove -lr -j8 t/         # recursive, 8 parallel jobs
```始终使用“-l”来确保“lib/”位于“@INC”上。

## 覆盖范围

使用 **Devel::Cover** — 目标 80%+：```bash
cover -test
```## 嘲笑

- **Test::MockModule** — 现有模块上的模拟方法
- **Test::MockObject** — 从头开始创建测试替身

## 陷阱

- 始终以“done_testing”结束测试文件
- 永远不要忘记带有“prove”的“-l”标志

## 参考

请参阅技能：“perl-testing”，了解带有 Test2::V0、prove 和 Devel::Cover 的详细 Perl TDD 模式。