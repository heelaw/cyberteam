# 数据库迁移模式

生产系统的安全、可逆的数据库模式更改。

## 何时激活

- 创建或更改数据库表
- 添加/删除列或索引
- 运行数据迁移（回填、转换）
- 规划零停机架构更改
- 为新项目设置迁移工具

## 核心原则

1. **每次更改都是迁移** - 切勿手动更改生产数据库
2. **迁移在生产中是仅前向的** — 回滚使用新的前向迁移
3. **架构和数据迁移是分开的** — 切勿在一次迁移中混合 DDL 和 DML
4. **针对生产规模的数据测试迁移** — 适用于 100 行的迁移可能会锁定 10M
5. **迁移一旦部署就不可变** - 切勿编辑已在生产中运行的迁移

## 迁移安全检查表

在应用任何迁移之前：

- [ ] 迁移既有UP又有DOWN（或者明确标记为不可逆）
- [ ] 大表上没有全表锁（使用并发操作）
- [ ] 新列具有默认值或可为空（没有默认值时切勿添加 NOT NULL）
- [ ] 同时创建索引（不与现有表的 CREATE TABLE 内联）
- [ ] 数据回填是与架构更改分开的迁移
- [ ] 根据生产数据副本进行测试
- [ ] 记录回滚计划

## PostgreSQL 模式

### 安全添加列```sql
-- GOOD: Nullable column, no lock
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- GOOD: Column with default (Postgres 11+ is instant, no rewrite)
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- BAD: NOT NULL without default on existing table (requires full rewrite)
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
-- This locks the table and rewrites every row
```### 在不停机的情况下添加索引```sql
-- BAD: Blocks writes on large tables
CREATE INDEX idx_users_email ON users (email);

-- GOOD: Non-blocking, allows concurrent writes
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);

-- Note: CONCURRENTLY cannot run inside a transaction block
-- Most migration tools need special handling for this
```### 重命名列（零停机）

切勿在生产中直接重命名。使用扩展-收缩模式：```sql
-- Step 1: Add new column (migration 001)
ALTER TABLE users ADD COLUMN display_name TEXT;

-- Step 2: Backfill data (migration 002, data migration)
UPDATE users SET display_name = username WHERE display_name IS NULL;

-- Step 3: Update application code to read/write both columns
-- Deploy application changes

-- Step 4: Stop writing to old column, drop it (migration 003)
ALTER TABLE users DROP COLUMN username;
```### 安全移除色谱柱```sql
-- Step 1: Remove all application references to the column
-- Step 2: Deploy application without the column reference
-- Step 3: Drop column in next migration
ALTER TABLE orders DROP COLUMN legacy_status;

-- For Django: use SeparateDatabaseAndState to remove from model
-- without generating DROP COLUMN (then drop in next migration)
```### 大数据迁移```sql
-- BAD: Updates all rows in one transaction (locks table)
UPDATE users SET normalized_email = LOWER(email);

-- GOOD: Batch update with progress
DO $$
DECLARE
  batch_size INT := 10000;
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET normalized_email = LOWER(email)
    WHERE id IN (
      SELECT id FROM users
      WHERE normalized_email IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RAISE NOTICE 'Updated % rows', rows_updated;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```## Prisma (TypeScript/Node.js)

### 工作流程```bash
# Create migration from schema changes
npx prisma migrate dev --name add_user_avatar

# Apply pending migrations in production
npx prisma migrate deploy

# Reset database (dev only)
npx prisma migrate reset

# Generate client after schema changes
npx prisma generate
```### 架构示例```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  avatarUrl String?  @map("avatar_url")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  orders    Order[]

  @@map("users")
  @@index([email])
}
```### 自定义 SQL 迁移

对于 Prisma 无法表达的操作（并发索引、数据回填）：```bash
# Create empty migration, then edit the SQL manually
npx prisma migrate dev --create-only --name add_email_index
``````sql
-- migrations/20240115_add_email_index/migration.sql
-- Prisma cannot generate CONCURRENTLY, so we write it manually
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
```## 毛毛雨 (TypeScript/Node.js)

### 工作流程```bash
# Generate migration from schema changes
npx drizzle-kit generate

# Apply migrations
npx drizzle-kit migrate

# Push schema directly (dev only, no migration file)
npx drizzle-kit push
```### 架构示例```typescript
import { pgTable, text, timestamp, uuid, boolean } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name"),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});
```## 姜戈（Python）

### 工作流程```bash
# Generate migration from model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Generate empty migration for custom SQL
python manage.py makemigrations --empty app_name -n description
```### 数据迁移```python
from django.db import migrations

def backfill_display_names(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    batch_size = 5000
    users = User.objects.filter(display_name="")
    while users.exists():
        batch = list(users[:batch_size])
        for user in batch:
            user.display_name = user.username
        User.objects.bulk_update(batch, ["display_name"], batch_size=batch_size)

def reverse_backfill(apps, schema_editor):
    pass  # Data migration, no reverse needed

class Migration(migrations.Migration):
    dependencies = [("accounts", "0015_add_display_name")]

    operations = [
        migrations.RunPython(backfill_display_names, reverse_backfill),
    ]
```### 分离数据库和状态

从 Django 模型中删除一列，而不立即将其从数据库中删除：```python
class Migration(migrations.Migration):
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name="user", name="legacy_field"),
            ],
            database_operations=[],  # Don't touch the DB yet
        ),
    ]
```## golang-迁移（Go）

### 工作流程```bash
# Create migration pair
migrate create -ext sql -dir migrations -seq add_user_avatar

# Apply all pending migrations
migrate -path migrations -database "$DATABASE_URL" up

# Rollback last migration
migrate -path migrations -database "$DATABASE_URL" down 1

# Force version (fix dirty state)
migrate -path migrations -database "$DATABASE_URL" force VERSION
```### 迁移文件```sql
-- migrations/000003_add_user_avatar.up.sql
ALTER TABLE users ADD COLUMN avatar_url TEXT;
CREATE INDEX CONCURRENTLY idx_users_avatar ON users (avatar_url) WHERE avatar_url IS NOT NULL;

-- migrations/000003_add_user_avatar.down.sql
DROP INDEX IF EXISTS idx_users_avatar;
ALTER TABLE users DROP COLUMN IF EXISTS avatar_url;
```## 零停机迁移策略

对于关键的生产变更，请遵循扩展合同模式：```
Phase 1: EXPAND
  - Add new column/table (nullable or with default)
  - Deploy: app writes to BOTH old and new
  - Backfill existing data

Phase 2: MIGRATE
  - Deploy: app reads from NEW, writes to BOTH
  - Verify data consistency

Phase 3: CONTRACT
  - Deploy: app only uses NEW
  - Drop old column/table in separate migration
```### 时间轴示例```
Day 1: Migration adds new_status column (nullable)
Day 1: Deploy app v2 — writes to both status and new_status
Day 2: Run backfill migration for existing rows
Day 3: Deploy app v3 — reads from new_status only
Day 7: Migration drops old status column
```## 反模式

|反模式 |为什么失败 |更好的方法|
|----------|-------------|-----------------|
|生产中的手动 SQL |无审计追踪，不可重复|始终使用迁移文件 |
|编辑已部署的迁移 |导致环境之间的漂移 |相反，创建新的迁移 |
|不带默认值的 NOT NULL |锁定表，重写所有行 |添加可为空，回填，然后添加约束 |
|大表上的内联索引 |构建期间阻止写入 |同时创建索引 |
|架构 + 数据一次迁移 |难以回滚、事务长 |单独迁移 |
|在删除代码之前删除列 |缺少列的应用程序错误 |首先删除代码，然后删除列部署 |