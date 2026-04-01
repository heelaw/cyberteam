# PostgreSQL 模式

PostgreSQL 最佳实践的快速参考。如需详细指导，请使用“database-reviewer”代理。

## 何时激活

- 编写 SQL 查询或迁移
- 设计数据库模式
- 解决查询速度慢的问题
- 实施行级安全性
- 设置连接池

## 快速参考

### 索引备忘单

|查询模式 |指数类型 |示例|
|--------------|------------|---------|
| `WHERE col = 值` | B 树（默认）| `在 t (col) 上创建索引 idx` |
| `WHERE col > 值` | B 树 | `在 t (col) 上创建索引 idx` |
| `其中 a = x 且 b > y` |复合| `在 t (a, b) 上创建索引 idx` |
| `哪里 jsonb @> '{}'` |杜松子酒 | `使用 gin (col) 在 t 上创建索引 idx` |
| `WHERE tsv @@ 查询` |杜松子酒 | `使用 gin (col) 在 t 上创建索引 idx` |
|时间序列范围 |布林 | `使用 brin (col) 在 t 上创建索引 idx` |

### 数据类型快速参考

|使用案例|正确类型 |避免 |
|----------|-------------|--------|
|身份证 | `bigint` | `int`，随机 UUID |
|字符串| `文本` | `varchar(255)` |
|时间戳 | `时间戳` | `时间戳` |
|钱| `数字(10,2)` | `浮动` |
|旗帜| `布尔值` | `varchar`、`int` |

### 常见模式

**综合指数顺序：**```sql
-- Equality columns first, then range columns
CREATE INDEX idx ON orders (status, created_at);
-- Works for: WHERE status = 'pending' AND created_at > '2024-01-01'
```**覆盖指数：**```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- Avoids table lookup for SELECT email, name, created_at
```**部分索引：**```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- Smaller index, only includes active users
```**RLS 策略（优化）：**```sql
CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);  -- Wrap in SELECT!
```**更新插入：**```sql
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```**光标分页：**```sql
SELECT * FROM products WHERE id > $last_id ORDER BY id LIMIT 20;
-- O(1) vs OFFSET which is O(n)
```**队列处理：**```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```### 反模式检测```sql
-- Find unindexed foreign keys
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- Check table bloat
SELECT relname, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```### 配置模板```sql
-- Connection limits (adjust for RAM)
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- Timeouts
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';

-- Monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Security defaults
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```## 相关

- 代理：`database-reviewer` - 完整的数据库审核工作流程
- 技能：`clickhouse-io` - ClickHouse 分析模式
- 技能：`后端模式` - API 和后端模式

---

*基于 Supabase 代理技能（来源：Supabase 团队）（麻省理工学院许可证）*