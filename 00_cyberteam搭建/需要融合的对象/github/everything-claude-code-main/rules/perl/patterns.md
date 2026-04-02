# Perl 模式

> 此文件使用 Perl 特定内容扩展了 [common/patterns.md](../common/patterns.md)。

## 存储库模式

在接口后面使用 **DBI** 或 **DBIx::Class**：```perl
package MyApp::Repo::User;
use Moo;

has dbh => (is => 'ro', required => 1);

sub find_by_id ($self, $id) {
    my $sth = $self->dbh->prepare('SELECT * FROM users WHERE id = ?');
    $sth->execute($id);
    return $sth->fetchrow_hashref;
}
```## DTO / 值对象

将 **Moo** 类与 **Types::Standard** 一起使用（相当于 Python 数据类）：```perl
package MyApp::DTO::User;
use Moo;
use Types::Standard qw(Str Int);

has name  => (is => 'ro', isa => Str, required => 1);
has email => (is => 'ro', isa => Str, required => 1);
has age   => (is => 'ro', isa => Int);
```## 资源管理

- 始终使用 **三参数打开** 和 `autodie`
- 使用 **Path::Tiny** 进行文件操作```perl
use autodie;
use Path::Tiny;

my $content = path('config.json')->slurp_utf8;
```## 模块接口

将“Exporter 'import'”与“@EXPORT_OK”一起使用——切勿使用“@EXPORT”：```perl
use Exporter 'import';
our @EXPORT_OK = qw(parse_config validate_input);
```## 依赖管理

使用 **cpanfile** + **carton** 进行可重复安装：```bash
carton install
carton exec prove -lr t/
```## 参考

请参阅技能：“perl-patterns”，了解全面的现代 Perl 模式和习惯用法。