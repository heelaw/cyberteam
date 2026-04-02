# Perl 编码风格

> 此文件使用 Perl 特定内容扩展了 [common/coding-style.md](../common/coding-style.md)。

## 标准

- 始终“使用 v5.36”（启用“strict”、“warnings”、“say”、子例程签名）
- 使用子例程签名 - 切勿手动解压`@_`
- 更喜欢带有显式换行符的“say”而不是“print”

## 不变性

- 对所有属性使用 **Moo** 和 `is => 'ro'` 和 `Types::Standard`
- 切勿直接使用受祝福的哈希引用 - 始终使用 Moo/Moose 访问器
- **OO 覆盖注释**：带有“builder”或“default”的 Moo“has”属性对于计算的只读值是可接受的

## 格式化

使用 **perltidy** 进行以下设置：```
-i=4    # 4-space indent
-l=100  # 100 char line length
-ce     # cuddled else
-bar    # opening brace always right
```## 代码检查

使用严重性为 3 的 **perlcritic** 和主题：“core”、“pbp”、“security”。```bash
perlcritic --severity 3 --theme 'core || pbp || security' lib/
```## 参考

请参阅技能：“perl-patterns”，了解全面的现代 Perl 习惯用法和最佳实践。