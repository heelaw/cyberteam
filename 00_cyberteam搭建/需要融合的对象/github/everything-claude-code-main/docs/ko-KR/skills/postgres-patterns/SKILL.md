# PostgreSQL 中文版

PostgreSQL 是免费的。数据库审阅者是数据库审阅者。

## 활성화 시점

- SQL 语句
- 스키마를 설계할 때
- 느린 쿼리를 문제 해결할 때
- 行级安全를 구현할 때
- 커넥션 풀링을 설정할 때

## 빠른 참조

### 인덱스 치트 시트

| 쿼리 패턴 | 인덱스 유형 | 예시 |
|--------------|------------|---------|
| `WHERE col = 值` | B 树 (기본값) | `在 t (col) 上创建索引 idx` |
| `WHERE col > 值` | B 树 | `在 t (col) 上创建索引 idx` |
| `其中 a = x 且 b > y` |复合| `在 t (a, b) 上创建索引 idx` |
| `哪里 jsonb @> '{}'` |杜松子酒 | `使用 gin (col) 在 t 上创建索引 idx` |
| `WHERE tsv @@ 查询` |杜松子酒 | `使用 gin (col) 在 t 上创建索引 idx` |
| 시계열 범위 |布林 | `使用 brin (col) 在 t 上创建索引 idx` |

### 타입 빠른 참조

| 사용 사례 | 올바른 타입 | 지양 |
|----------|-------------|--------|
|身份证 | `bigint` | `int`，随机 UUID |
| 문자열 | `文本` | `varchar(255)` |
| 타임스탬프 | `时间戳` | `时间戳` |
| 금액 | `数字(10,2)` | `浮动` |
| 플래그 | `布尔值` | `varchar`、`int` |

### 일반 패턴

**效果:**```sql
-- Equality columns first, then range columns
CREATE INDEX idx ON orders (status, created_at);
-- Works for: WHERE status = 'pending' AND created_at > '2024-01-01'
```**效果:**```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- Avoids table lookup for SELECT email, name, created_at
```**效果:**```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- Smaller index, only includes active users
```**RLS 정책 (최적화):**```sql
CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);  -- Wrap in SELECT!
```**更新插入：**```sql
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```**应用程序:**```sql
SELECT * FROM products WHERE id > $last_id ORDER BY id LIMIT 20;
-- O(1) vs OFFSET which is O(n)
```** 처리:**```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```### 안티패턴 감지```sql
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
```### 구성 템플릿```sql
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
```## 관련 항목

- 에이전트: `database-reviewer` - 전체 데이터베이스 리뷰 워크플로우
- 스킬: `clickhouse-io` - ClickHouse 분석 패턴
- 스킬: `backend-patterns` - API 및 백엔드 패턴

---

*Supabase Agent Skills 기반 (크레딧: Supabase 팀) (MIT License)*