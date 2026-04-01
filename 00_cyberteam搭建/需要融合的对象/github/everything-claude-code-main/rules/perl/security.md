# Perl 安全

> 此文件使用 Perl 特定内容扩展了 [common/security.md](../common/security.md)。

## 污点模式

- 在所有 CGI/面向 Web 的脚本上使用“-T”标志
- 在任何外部命令之前清理`%ENV`（`$ENV{PATH}`、`$ENV{CDPATH}`等）

## 输入验证

- 使用允许列表正则表达式来消除污染 - 切勿使用“/(.*)/s”
- 使用显式模式验证所有用户输入：```perl
if ($input =~ /\A([a-zA-Z0-9_-]+)\z/) {
    my $clean = $1;
}
```## 文件输入/输出

- **仅打开三个参数** — 从不打开两个参数
- 使用 `Cwd::realpath` 防止路径遍历：```perl
use Cwd 'realpath';
my $safe_path = realpath($user_path);
die "Path traversal" unless $safe_path =~ m{\A/allowed/directory/};
```## 流程执行

- 使用 **列表形式 `system()`** — 绝不是单字符串形式
- 使用 **IPC::Run3** 捕获输出
- 切勿在变量插值中使用反引号```perl
system('grep', '-r', $pattern, $directory);  # safe
```## SQL注入预防

始终使用 DBI 占位符 — 切勿插入 SQL：```perl
my $sth = $dbh->prepare('SELECT * FROM users WHERE email = ?');
$sth->execute($email);
```## 安全扫描

使用严重性为 4+ 的安全主题运行 **perlcritic**：```bash
perlcritic --severity 4 --theme security lib/
```## 参考

请参阅技能：“perl-security”，了解全面的 Perl 安全模式、污染模式和安全 I/O。