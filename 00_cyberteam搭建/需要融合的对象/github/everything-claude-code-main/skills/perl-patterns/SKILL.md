# 现代 Perl 开发模式

用于构建健壮、可维护应用程序的惯用 Perl 5.36+ 模式和最佳实践。

## 何时激活

- 编写新的 Perl 代码或模块
- 审查 Perl 代码以确保习惯用法的合规性
- 将遗留 Perl 重构为现代标准
- 设计Perl模块架构
- 将 5.36 之前的代码迁移到现代 Perl

## 它是如何工作的

应用这些模式作为对现代 Perl 5.36+ 默认值的偏向：签名、显式模块、集中错误处理和可测试边界。下面的示例旨在作为起点进行复制，然后针对您面前的实际应用程序、依赖项堆栈和部署模型进行收紧。

## 核心原则

### 1. 使用 `v5.36` 指令

单个“use v5.36”取代了旧的样板，并启用严格、警告和子例程签名。```perl
# Good: Modern preamble
use v5.36;

sub greet($name) {
    say "Hello, $name!";
}

# Bad: Legacy boilerplate
use strict;
use warnings;
use feature 'say', 'signatures';
no warnings 'experimental::signatures';

sub greet {
    my ($name) = @_;
    say "Hello, $name!";
}
```### 2. 子程序签名

使用签名来保证清晰度和自动数量检查。```perl
use v5.36;

# Good: Signatures with defaults
sub connect_db($host, $port = 5432, $timeout = 30) {
    # $host is required, others have defaults
    return DBI->connect("dbi:Pg:host=$host;port=$port", undef, undef, {
        RaiseError => 1,
        PrintError => 0,
    });
}

# Good: Slurpy parameter for variable args
sub log_message($level, @details) {
    say "[$level] " . join(' ', @details);
}

# Bad: Manual argument unpacking
sub connect_db {
    my ($host, $port, $timeout) = @_;
    $port    //= 5432;
    $timeout //= 30;
    # ...
}
```### 3. 上下文敏感性

了解标量与列表上下文——一个核心 Perl 概念。```perl
use v5.36;

my @items = (1, 2, 3, 4, 5);

my @copy  = @items;            # List context: all elements
my $count = @items;            # Scalar context: count (5)
say "Items: " . scalar @items; # Force scalar context
```### 4. 后缀解除引用

使用后缀取消引用语法来提高嵌套结构的可读性。```perl
use v5.36;

my $data = {
    users => [
        { name => 'Alice', roles => ['admin', 'user'] },
        { name => 'Bob',   roles => ['user'] },
    ],
};

# Good: Postfix dereferencing
my @users = $data->{users}->@*;
my @roles = $data->{users}[0]{roles}->@*;
my %first = $data->{users}[0]->%*;

# Bad: Circumfix dereferencing (harder to read in chains)
my @users = @{ $data->{users} };
my @roles = @{ $data->{users}[0]{roles} };
```### 5. `isa` 运算符 (5.32+)

中缀类型检查 — 替换 `blessed($o) && $o->isa('X')`。```perl
use v5.36;
if ($obj isa 'My::Class') { $obj->do_something }
```## 错误处理

### 评估/模具模式```perl
use v5.36;

sub parse_config($path) {
    my $content = eval { path($path)->slurp_utf8 };
    die "Config error: $@" if $@;
    return decode_json($content);
}
```### Try::Tiny（可靠的异常处理）```perl
use v5.36;
use Try::Tiny;

sub fetch_user($id) {
    my $user = try {
        $db->resultset('User')->find($id)
            // die "User $id not found\n";
    }
    catch {
        warn "Failed to fetch user $id: $_";
        undef;
    };
    return $user;
}
```### 本机 try/catch (5.40+)```perl
use v5.40;

sub divide($x, $y) {
    try {
        die "Division by zero" if $y == 0;
        return $x / $y;
    }
    catch ($e) {
        warn "Error: $e";
        return;
    }
}
```## 现代面向对象与 Moo

更喜欢 Moo，因为它是轻量级的、现代的 OO。仅当需要 Moose 元协议时才使用 Moose。```perl
# Good: Moo class
package User;
use Moo;
use Types::Standard qw(Str Int ArrayRef);
use namespace::autoclean;

has name  => (is => 'ro', isa => Str, required => 1);
has email => (is => 'ro', isa => Str, required => 1);
has age   => (is => 'ro', isa => Int, default  => sub { 0 });
has roles => (is => 'ro', isa => ArrayRef[Str], default => sub { [] });

sub is_admin($self) {
    return grep { $_ eq 'admin' } $self->roles->@*;
}

sub greet($self) {
    return "Hello, I'm " . $self->name;
}

1;

# Usage
my $user = User->new(
    name  => 'Alice',
    email => 'alice@example.com',
    roles => ['admin', 'user'],
);

# Bad: Blessed hashref (no validation, no accessors)
package User;
sub new {
    my ($class, %args) = @_;
    return bless \%args, $class;
}
sub name { return $_[0]->{name} }
1;
```### 哞角色```perl
package Role::Serializable;
use Moo::Role;
use JSON::MaybeXS qw(encode_json);
requires 'TO_HASH';
sub to_json($self) { encode_json($self->TO_HASH) }
1;

package User;
use Moo;
with 'Role::Serializable';
has name  => (is => 'ro', required => 1);
has email => (is => 'ro', required => 1);
sub TO_HASH($self) { { name => $self->name, email => $self->email } }
1;
```### 原生 `class` 关键字（5.38+，Corinna）```perl
use v5.38;
use feature 'class';
no warnings 'experimental::class';

class Point {
    field $x :param;
    field $y :param;
    method magnitude() { sqrt($x**2 + $y**2) }
}

my $p = Point->new(x => 3, y => 4);
say $p->magnitude;  # 5
```## 正则表达式

### 命名捕获和 `/x` 标志```perl
use v5.36;

# Good: Named captures with /x for readability
my $log_re = qr{
    ^ (?<timestamp> \d{4}-\d{2}-\d{2} \s \d{2}:\d{2}:\d{2} )
    \s+ \[ (?<level> \w+ ) \]
    \s+ (?<message> .+ ) $
}x;

if ($line =~ $log_re) {
    say "Time: $+{timestamp}, Level: $+{level}";
    say "Message: $+{message}";
}

# Bad: Positional captures (hard to maintain)
if ($line =~ /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.+)$/) {
    say "Time: $1, Level: $2";
}
```### 预编译模式```perl
use v5.36;

# Good: Compile once, use many
my $email_re = qr/^[A-Za-z0-9._%+-]+\@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

sub validate_emails(@emails) {
    return grep { $_ =~ $email_re } @emails;
}
```## 数据结构

### 参考和安全深度访问```perl
use v5.36;

# Hash and array references
my $config = {
    database => {
        host => 'localhost',
        port => 5432,
        options => ['utf8', 'sslmode=require'],
    },
};

# Safe deep access (returns undef if any level missing)
my $port = $config->{database}{port};           # 5432
my $missing = $config->{cache}{host};           # undef, no error

# Hash slices
my %subset;
@subset{qw(host port)} = @{$config->{database}}{qw(host port)};

# Array slices
my @first_two = $config->{database}{options}->@[0, 1];

# Multi-variable for loop (experimental in 5.36, stable in 5.40)
use feature 'for_list';
no warnings 'experimental::for_list';
for my ($key, $val) (%$config) {
    say "$key => $val";
}
```## 文件输入/输出

### 三参数开放```perl
use v5.36;

# Good: Three-arg open with autodie (core module, eliminates 'or die')
use autodie;

sub read_file($path) {
    open my $fh, '<:encoding(UTF-8)', $path;
    local $/;
    my $content = <$fh>;
    close $fh;
    return $content;
}

# Bad: Two-arg open (shell injection risk, see perl-security)
open FH, $path;            # NEVER do this
open FH, "< $path";        # Still bad — user data in mode string
```### Path::Tiny 用于文件操作```perl
use v5.36;
use Path::Tiny;

my $file = path('config', 'app.json');
my $content = $file->slurp_utf8;
$file->spew_utf8($new_content);

# Iterate directory
for my $child (path('src')->children(qr/\.pl$/)) {
    say $child->basename;
}
```## 模块组织

### 标准项目布局```text
MyApp/
├── lib/
│   └── MyApp/
│       ├── App.pm           # Main module
│       ├── Config.pm        # Configuration
│       ├── DB.pm            # Database layer
│       └── Util.pm          # Utilities
├── bin/
│   └── myapp                # Entry-point script
├── t/
│   ├── 00-load.t            # Compilation tests
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── cpanfile                 # Dependencies
├── Makefile.PL              # Build system
└── .perlcriticrc            # Linting config
```### 导出器模式```perl
package MyApp::Util;
use v5.36;
use Exporter 'import';

our @EXPORT_OK   = qw(trim);
our %EXPORT_TAGS = (all => \@EXPORT_OK);

sub trim($str) { $str =~ s/^\s+|\s+$//gr }

1;
```## 工具

### perltidy 配置 (.perltidyrc)```text
-i=4        # 4-space indent
-l=100      # 100-char line length
-ci=4       # continuation indent
-ce         # cuddled else
-bar        # opening brace on same line
-nolq       # don't outdent long quoted strings
```### perlcritic 配置 (.perlcriticrc)```ini
severity = 3
theme = core + pbp + security

[InputOutput::RequireCheckedSyscalls]
functions = :builtins
exclude_functions = say print

[Subroutines::ProhibitExplicitReturnUndef]
severity = 4

[ValuesAndExpressions::ProhibitMagicNumbers]
allowed_values = 0 1 2 -1
```### 依赖管理（cpanfile + carton）```bash
cpanm App::cpanminus Carton   # Install tools
carton install                 # Install deps from cpanfile
carton exec -- perl bin/myapp  # Run with local deps
``````perl
# cpanfile
requires 'Moo', '>= 2.005';
requires 'Path::Tiny';
requires 'JSON::MaybeXS';
requires 'Try::Tiny';

on test => sub {
    requires 'Test2::V0';
    requires 'Test::MockModule';
};
```## 快速参考：现代 Perl 习惯用法

|传统模式|现代更换 |
|---|---|
| `使用严格；使用警告；` | `使用 v5.36;` |
| `我的($x, $y) = @_;` | `sub foo($x, $y) { ... }` |
| `@{ $ref }` | `$ref->@*` |
| `%{ $ref }` | `$ref->%*` |
| `打开 FH，"< $file"` | `打开我的 $fh, '<:encoding(UTF-8)', $file` |
| `有福的 hashref` |具有类型的 `Moo` 类 |
| `$1, $2, $3` | `$+{name}` （命名捕获）|
| `评估{}；如果 ($@)` | `Try::Tiny` 或原生 `try/catch` (5.40+) |
| `BEGIN { 需要导出器； }` | `使用导出器'导入'；` |
|手动文件操作 | `路径::小` |
| `有福($o) && $o->isa('X')` | `$o 是 'X'` (5.32+) |
| `内置::true / false` | `使用内置'true'、'false';`（5.36+，实验性）|

## 反模式```perl
# 1. Two-arg open (security risk)
open FH, $filename;                     # NEVER

# 2. Indirect object syntax (ambiguous parsing)
my $obj = new Foo(bar => 1);            # Bad
my $obj = Foo->new(bar => 1);           # Good

# 3. Excessive reliance on $_
map { process($_) } grep { validate($_) } @items;  # Hard to follow
my @valid = grep { validate($_) } @items;           # Better: break it up
my @results = map { process($_) } @valid;

# 4. Disabling strict refs
no strict 'refs';                        # Almost always wrong
${"My::Package::$var"} = $value;         # Use a hash instead

# 5. Global variables as configuration
our $TIMEOUT = 30;                       # Bad: mutable global
use constant TIMEOUT => 30;              # Better: constant
# Best: Moo attribute with default

# 6. String eval for module loading
eval "require $module";                  # Bad: code injection risk
eval "use $module";                      # Bad
use Module::Runtime 'require_module';    # Good: safe module loading
require_module($module);
```**记住**：现代 Perl 干净、可读且安全。让“use v5.36”处理样板文件，使用 Moo 处理对象，并且更喜欢 CPAN 的经过实战检验的模块而不是手动解决方案。