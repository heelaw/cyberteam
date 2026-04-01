# Perl 安全模式

Perl 应用程序的全面安全指南，涵盖输入验证、注入预防和安全编码实践。

## 何时激活

- 处理 Perl 应用程序中的用户输入
- 构建 Perl Web 应用程序（CGI、Mojolicious、Dancer2、Catalyst）
- 检查 Perl 代码的安全漏洞
- 使用用户提供的路径执行文件操作
- 从 Perl 执行系统命令
- 编写DBI数据库查询

## 它是如何工作的

从污染感知输入边界开始，然后向外移动：验证和清除输入，保持文件系统和进程执行受限，并在各处使用参数化 DBI 查询。下面的示例显示了此技能希望您在发布涉及用户输入、shell 或网络的 Perl 代码之前应用的安全默认值。

## 污点模式

Perl 的污点模式 (`-T`) 跟踪来自外部源的数据，并防止在没有显式验证的情况下将其用于不安全的操作。

### 启用污点模式```perl
#!/usr/bin/perl -T
use v5.36;

# Tainted: anything from outside the program
my $input    = $ARGV[0];        # Tainted
my $env_path = $ENV{PATH};      # Tainted
my $form     = <STDIN>;         # Tainted
my $query    = $ENV{QUERY_STRING}; # Tainted

# Sanitize PATH early (required in taint mode)
$ENV{PATH} = '/usr/local/bin:/usr/bin:/bin';
delete @ENV{qw(IFS CDPATH ENV BASH_ENV)};
```### 净化模式```perl
use v5.36;

# Good: Validate and untaint with a specific regex
sub untaint_username($input) {
    if ($input =~ /^([a-zA-Z0-9_]{3,30})$/) {
        return $1;  # $1 is untainted
    }
    die "Invalid username: must be 3-30 alphanumeric characters\n";
}

# Good: Validate and untaint a file path
sub untaint_filename($input) {
    if ($input =~ m{^([a-zA-Z0-9._-]+)$}) {
        return $1;
    }
    die "Invalid filename: contains unsafe characters\n";
}

# Bad: Overly permissive untainting (defeats the purpose)
sub bad_untaint($input) {
    $input =~ /^(.*)$/s;
    return $1;  # Accepts ANYTHING — pointless
}
```## 输入验证

### 允许列表优先于阻止列表```perl
use v5.36;

# Good: Allowlist — define exactly what's permitted
sub validate_sort_field($field) {
    my %allowed = map { $_ => 1 } qw(name email created_at updated_at);
    die "Invalid sort field: $field\n" unless $allowed{$field};
    return $field;
}

# Good: Validate with specific patterns
sub validate_email($email) {
    if ($email =~ /^([a-zA-Z0-9._%+-]+\@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/) {
        return $1;
    }
    die "Invalid email address\n";
}

sub validate_integer($input) {
    if ($input =~ /^(-?\d{1,10})$/) {
        return $1 + 0;  # Coerce to number
    }
    die "Invalid integer\n";
}

# Bad: Blocklist — always incomplete
sub bad_validate($input) {
    die "Invalid" if $input =~ /[<>"';&|]/;  # Misses encoded attacks
    return $input;
}
```### 长度限制```perl
use v5.36;

sub validate_comment($text) {
    die "Comment is required\n"        unless length($text) > 0;
    die "Comment exceeds 10000 chars\n" if length($text) > 10_000;
    return $text;
}
```## 安全正则表达式

### 重做攻击预防

重叠模式上的嵌套量词会发生灾难性回溯。```perl
use v5.36;

# Bad: Vulnerable to ReDoS (exponential backtracking)
my $bad_re = qr/^(a+)+$/;           # Nested quantifiers
my $bad_re2 = qr/^([a-zA-Z]+)*$/;   # Nested quantifiers on class
my $bad_re3 = qr/^(.*?,){10,}$/;    # Repeated greedy/lazy combo

# Good: Rewrite without nesting
my $good_re = qr/^a+$/;             # Single quantifier
my $good_re2 = qr/^[a-zA-Z]+$/;     # Single quantifier on class

# Good: Use possessive quantifiers or atomic groups to prevent backtracking
my $safe_re = qr/^[a-zA-Z]++$/;             # Possessive (5.10+)
my $safe_re2 = qr/^(?>a+)$/;                # Atomic group

# Good: Enforce timeout on untrusted patterns
use POSIX qw(alarm);
sub safe_match($string, $pattern, $timeout = 2) {
    my $matched;
    eval {
        local $SIG{ALRM} = sub { die "Regex timeout\n" };
        alarm($timeout);
        $matched = $string =~ $pattern;
        alarm(0);
    };
    alarm(0);
    die $@ if $@;
    return $matched;
}
```## 安全文件操作

### 三参数开放```perl
use v5.36;

# Good: Three-arg open, lexical filehandle, check return
sub read_file($path) {
    open my $fh, '<:encoding(UTF-8)', $path
        or die "Cannot open '$path': $!\n";
    local $/;
    my $content = <$fh>;
    close $fh;
    return $content;
}

# Bad: Two-arg open with user data (command injection)
sub bad_read($path) {
    open my $fh, $path;        # If $path = "|rm -rf /", runs command!
    open my $fh, "< $path";   # Shell metacharacter injection
}
```### TOCTOU预防和路径遍历```perl
use v5.36;
use Fcntl qw(:DEFAULT :flock);
use File::Spec;
use Cwd qw(realpath);

# Atomic file creation
sub create_file_safe($path) {
    sysopen(my $fh, $path, O_WRONLY | O_CREAT | O_EXCL, 0600)
        or die "Cannot create '$path': $!\n";
    return $fh;
}

# Validate path stays within allowed directory
sub safe_path($base_dir, $user_path) {
    my $real = realpath(File::Spec->catfile($base_dir, $user_path))
        // die "Path does not exist\n";
    my $base_real = realpath($base_dir)
        // die "Base dir does not exist\n";
    die "Path traversal blocked\n" unless $real =~ /^\Q$base_real\E(?:\/|\z)/;
    return $real;
}
```使用 `File::Temp` 作为临时文件 (`tempfile(UNLINK => 1)`) 和 `flock(LOCK_EX)` 来防止竞争条件。

## 安全流程执行

### 列表表单系统和执行```perl
use v5.36;

# Good: List form — no shell interpolation
sub run_command(@cmd) {
    system(@cmd) == 0
        or die "Command failed: @cmd\n";
}

run_command('grep', '-r', $user_pattern, '/var/log/app/');

# Good: Capture output safely with IPC::Run3
use IPC::Run3;
sub capture_output(@cmd) {
    my ($stdout, $stderr);
    run3(\@cmd, \undef, \$stdout, \$stderr);
    if ($?) {
        die "Command failed (exit $?): $stderr\n";
    }
    return $stdout;
}

# Bad: String form — shell injection!
sub bad_search($pattern) {
    system("grep -r '$pattern' /var/log/app/");  # If $pattern = "'; rm -rf / #"
}

# Bad: Backticks with interpolation
my $output = `ls $user_dir`;   # Shell injection risk
```还可以使用“Capture::Tiny”从外部命令安全地捕获 stdout/stderr。

## SQL注入预防

### DBI 占位符```perl
use v5.36;
use DBI;

my $dbh = DBI->connect($dsn, $user, $pass, {
    RaiseError => 1,
    PrintError => 0,
    AutoCommit => 1,
});

# Good: Parameterized queries — always use placeholders
sub find_user($dbh, $email) {
    my $sth = $dbh->prepare('SELECT * FROM users WHERE email = ?');
    $sth->execute($email);
    return $sth->fetchrow_hashref;
}

sub search_users($dbh, $name, $status) {
    my $sth = $dbh->prepare(
        'SELECT * FROM users WHERE name LIKE ? AND status = ? ORDER BY name'
    );
    $sth->execute("%$name%", $status);
    return $sth->fetchall_arrayref({});
}

# Bad: String interpolation in SQL (SQLi vulnerability!)
sub bad_find($dbh, $email) {
    my $sth = $dbh->prepare("SELECT * FROM users WHERE email = '$email'");
    # If $email = "' OR 1=1 --", returns all users
    $sth->execute;
    return $sth->fetchrow_hashref;
}
```### 动态列白名单```perl
use v5.36;

# Good: Validate column names against an allowlist
sub order_by($dbh, $column, $direction) {
    my %allowed_cols = map { $_ => 1 } qw(name email created_at);
    my %allowed_dirs = map { $_ => 1 } qw(ASC DESC);

    die "Invalid column: $column\n"    unless $allowed_cols{$column};
    die "Invalid direction: $direction\n" unless $allowed_dirs{uc $direction};

    my $sth = $dbh->prepare("SELECT * FROM users ORDER BY $column $direction");
    $sth->execute;
    return $sth->fetchall_arrayref({});
}

# Bad: Directly interpolating user-chosen column
sub bad_order($dbh, $column) {
    $dbh->prepare("SELECT * FROM users ORDER BY $column");  # SQLi!
}
```### DBIx::Class（ORM 安全）```perl
use v5.36;

# DBIx::Class generates safe parameterized queries
my @users = $schema->resultset('User')->search({
    status => 'active',
    email  => { -like => '%@example.com' },
}, {
    order_by => { -asc => 'name' },
    rows     => 50,
});
```## 网络安全

### XSS预防```perl
use v5.36;
use HTML::Entities qw(encode_entities);
use URI::Escape qw(uri_escape_utf8);

# Good: Encode output for HTML context
sub safe_html($user_input) {
    return encode_entities($user_input);
}

# Good: Encode for URL context
sub safe_url_param($value) {
    return uri_escape_utf8($value);
}

# Good: Encode for JSON context
use JSON::MaybeXS qw(encode_json);
sub safe_json($data) {
    return encode_json($data);  # Handles escaping
}

# Template auto-escaping (Mojolicious)
# <%= $user_input %>   — auto-escaped (safe)
# <%== $raw_html %>    — raw output (dangerous, use only for trusted content)

# Template auto-escaping (Template Toolkit)
# [% user_input | html %]  — explicit HTML encoding

# Bad: Raw output in HTML
sub bad_html($input) {
    print "<div>$input</div>";  # XSS if $input contains <script>
}
```### CSRF 保护```perl
use v5.36;
use Crypt::URandom qw(urandom);
use MIME::Base64 qw(encode_base64url);

sub generate_csrf_token() {
    return encode_base64url(urandom(32));
}
```验证令牌时使用常量时间比较。大多数 Web 框架（Mojolicious、Dancer2、Catalyst）都提供内置的 CSRF 保护 - 与手动解决方案相比，人们更喜欢这些框架。

### 会话和标头安全```perl
use v5.36;

# Mojolicious session + headers
$app->secrets(['long-random-secret-rotated-regularly']);
$app->sessions->secure(1);          # HTTPS only
$app->sessions->samesite('Lax');

$app->hook(after_dispatch => sub ($c) {
    $c->res->headers->header('X-Content-Type-Options' => 'nosniff');
    $c->res->headers->header('X-Frame-Options'        => 'DENY');
    $c->res->headers->header('Content-Security-Policy' => "default-src 'self'");
    $c->res->headers->header('Strict-Transport-Security' => 'max-age=31536000; includeSubDomains');
});
```## 输出编码

始终对其上下文编码输出：“HTML::Entities::encode_entities()”（对于 HTML）、“URI::Escape::uri_escape_utf8()”（对于 URL）、“JSON::MaybeXS::encode_json()”（对于 JSON）。

## CPAN 模块安全

- cpanfile 中的 **Pin 版本**：`需要 'DBI'，'== 1.643'；`
- **首选维护模块**：检查 MetaCPAN 的最新版本
- **最小化依赖关系**：每个依赖关系都是一个攻击面

## 安全工具

### perlcritic 安全策略```ini
# .perlcriticrc — security-focused configuration
severity = 3
theme = security + core

# Require three-arg open
[InputOutput::RequireThreeArgOpen]
severity = 5

# Require checked system calls
[InputOutput::RequireCheckedSyscalls]
functions = :builtins
severity = 4

# Prohibit string eval
[BuiltinFunctions::ProhibitStringyEval]
severity = 5

# Prohibit backtick operators
[InputOutput::ProhibitBacktickOperators]
severity = 4

# Require taint checking in CGI
[Modules::RequireTaintChecking]
severity = 5

# Prohibit two-arg open
[InputOutput::ProhibitTwoArgOpen]
severity = 5

# Prohibit bare-word filehandles
[InputOutput::ProhibitBarewordFileHandles]
severity = 5
```### 运行 perlcritic```bash
# Check a file
perlcritic --severity 3 --theme security lib/MyApp/Handler.pm

# Check entire project
perlcritic --severity 3 --theme security lib/

# CI integration
perlcritic --severity 4 --theme security --quiet lib/ || exit 1
```## 快速安全检查表

|检查 |验证什么 |
|---|---|
|污染模式 | CGI/Web 脚本上的“-T”标志 |
|输入验证 |许可名单模式、长度限制 |
|文件操作 |三参数开放，路径遍历检查 |
|流程执行 |列表形式系统，无外壳插值 |
| SQL 查询 | DBI 占位符，从不插值 |
| HTML 输出 | `encode_entities()`，模板自动转义 |
| CSRF 代币 |根据状态更改请求生成并验证 |
|会话配置 |安全、HttpOnly、SameSite cookies |
| HTTP 标头 | CSP、X 框架选项、HSTS |
|依赖关系 |固定版本、审核模块 |
|正则表达式安全 |没有嵌套量词、锚定模式 |
|错误信息 |没有堆栈跟踪或路径泄露给用户 |

## 反模式```perl
# 1. Two-arg open with user data (command injection)
open my $fh, $user_input;               # CRITICAL vulnerability

# 2. String-form system (shell injection)
system("convert $user_file output.png"); # CRITICAL vulnerability

# 3. SQL string interpolation
$dbh->do("DELETE FROM users WHERE id = $id");  # SQLi

# 4. eval with user input (code injection)
eval $user_code;                         # Remote code execution

# 5. Trusting $ENV without sanitizing
my $path = $ENV{UPLOAD_DIR};             # Could be manipulated
system("ls $path");                      # Double vulnerability

# 6. Disabling taint without validation
($input) = $input =~ /(.*)/s;           # Lazy untaint — defeats purpose

# 7. Raw user data in HTML
print "<div>Welcome, $username!</div>";  # XSS

# 8. Unvalidated redirects
print $cgi->redirect($user_url);         # Open redirect
```**记住**：Perl 的灵活性非常强大，但需要纪律。对面向 Web 的代码使用污点模式，使用允许列表验证所有输入，对每个查询使用 DBI 占位符，并针对其上下文对所有输出进行编码。纵深防御——永远不要依赖单层防御。