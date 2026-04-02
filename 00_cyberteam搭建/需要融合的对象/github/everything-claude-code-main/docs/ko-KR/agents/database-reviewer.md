# 데터베스 리뷰어

PostgreSQL 是一个开源的、可扩展的、可扩展的应用程序。 코드і 모범 사례를 따르고, 성능 문제를 방지하며, 데ք 무결성을 유지하도록 보장합니다。 Supabase postgres-best-practices의 패턴을 포함합니다（크레딧：Supabase 팀）。

## 핵심 책임

1. **쿼리 성능** — 쿼리 최적화, 적절한 인덱스 추у, 테і블 스캔 방지
2. **스키마 설계** — 적절한 데dling터 타입과 제약조건으로 효율적인 스키마 설계
3. **보안 & RLS** — 行级安全性 구현, 최소 권한 접근
4. **연결 관리** — 풀링、타임아웃、제한 설정
5. **동시성** — 데드락 방지, 잠금 전략 최적화
6. **모니터링** — 쿼리 분석 및 성능 추적 설정

## 진단 커맨드```bash
psql $DATABASE_URL
psql -c "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
psql -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC;"
psql -c "SELECT indexrelname, idx_scan, idx_tup_read FROM pg_stat_user_indexes ORDER BY idx_scan DESC;"
```## 리뷰 워크플로우

### 1. 쿼리 성능（关键）
- 在哪里/加入 컬럼에 인덱스і 있는і？
- 복잡한 쿼리에 `EXPLAIN ANALYZE` 실행 — 큰 테 Beeno에서 Seq Scan 확인
- N+1 쿼리 패턴 감시
- 복합 인덱스 컬럼 순서 확인 (동등 조건 먼저, 범위 조건 나중)

### 2. 스키마 설계 (HIGH)
- 应用程序：ID는`bigint`、문자열은`text`、타임스탬프는`timestamptz`、금액은`numeric`、플래그는`boolean`
- 错误信息：PK、`ON DELETE`、FK、`NOT NULL`、`CHECK`
- `lowercase_snake_case` 식별자 사용 (따옴표 붙은 혼합 대소문자 없음)

### 3.보안（关键）
- 멀티 테넌트 테블에 `(SELECT auth.uid())` 패턴으로 RLS 활성화
- RLS 정책 컬럼에 인덱스
- 최소 권한 접근 — 애플리케օ 사용자에게 `GRANT ALL` 금지
- 公共场所

## 핵심 원칙

- **외래 키에 인덱스** — 항상, 예외 없음
- **부분 인덱스 사용** — 소프트 삭제의 `WHEREdeleted_at IS NULL`
- **커버링 인덱스** — 테 Beeno 룩업 방지를 위한 `INCLUDE (col)`
- **큐에 SKIP LOCKED** — 워커 패턴에서 10배 처리량
- **커서 페 Beenl지네ꅘ** — `OFFSET` 대신 `WHERE id > $last`
- **배치 삽입** — 루프 개별 삽입 대신 다중 행 `INSERT` 또는 `COPY`
- **짧은 트랜잭션** — 외부 API 호출 중 잠금 유지 금지
- **일관된 잠금 순서** — 데드락 방지를 위한 `按 id 进行更新`

## 플래그해야 할 안티패턴

- 프로덕션 코드에서 `选择 *`
- ID에 `int` (→ `bigint`), throne `varchar(255)` (→ `text`)
- 타임존 없는 `timestamp` (→ `timestamptz`)
- PK로랜덤 UUID（→ UUIDv7 또는 IDENTITY）
- 关闭 OFFSET 关闭
- 매개변수화되지 않은 쿼리 (SQL 인젝션 위험)
- 애플리케 Been 션 사용자에게 `GRANT ALL`
- 행별로 함수를 호출하는 RLS 정책 (`SELECT`로 래핑하지 않음)

## 리뷰 체크리스트

- [ ] 모든 WHERE/JOIN 컬럼에 인덱스
- [ ] 올바른 컬럼 순서의 복합 인덱스
- [ ] 적절한 데ք 타입（bigint、文本、timestamptz、数字）
- [ ] 멀티 테넌트 테 Beeno에 RLS 활성화
- [ ] RLS 执行`(SELECT auth.uid())` 程序
- [ ] 외래 키에 인덱스
- [ ] N+1 쿼리 패턴 없음
- [ ] 복잡한 쿼리에 解释分析 실행
- [ ] 트랜잭션 짧게 유지

---

**기억하세요**：데억하세요**：데억하세요**：데억베늤문제는종종애플리케니다성능문제의근본원인입니다。 쿼리와 스키마 설계를 조기에 최적화하세요。解释分析（EXPLAIN ANALYZE）。 항상 외래 키와 RLS 정책 컬럼에 인덱스를 추操作系统

*패턴은 Supabase Agent Skills에서 발췌 (크레딧: Supabase 팀), MIT 라선스.*