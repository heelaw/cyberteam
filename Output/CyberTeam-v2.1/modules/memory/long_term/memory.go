package long_term

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
	"time"

	"cyberteam/memory"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/sirupsen/logrus"
)

// Store pgvector 存储实现
type Store struct {
	pool          *pgxpool.Pool
	embeddingURL  string
	embeddingAPI  string
	apiKey        string
	similarityThresh float64
	maxResults    int
	cache         *sync.Map // 缓存
	logger        *logrus.Logger
}

// NewStore 创建新的向量存储
func NewStore(cfg memory.Config, logger *logrus.Logger) (*Store, error) {
	poolConfig, err := pgxpool.ParseConfig(cfg.VectorStoreURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse vector store config: %w", err)
	}

	pool, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create vector store pool: %w", err)
	}

	// 验证连接
	if err := pool.Ping(context.Background()); err != nil {
		return nil, fmt.Errorf("failed to ping vector store: %w", err)
	}

	s := &Store{
		pool:            pool,
		embeddingURL:    cfg.EmbeddingURL,
		embeddingAPI:    cfg.EmbeddingModel,
		apiKey:          cfg.APIKey,
		similarityThresh: cfg.SimilarityThreshold,
		maxResults:      cfg.MaxResults,
		cache:           new(sync.Map),
		logger:          logger,
	}

	// 初始化数据库表
	if err := s.initSchema(context.Background()); err != nil {
		return nil, fmt.Errorf("failed to initialize schema: %w", err)
	}

	return s, nil
}

// initSchema 初始化数据库表结构
func (s *Store) initSchema(ctx context.Context) error {
	schema := `
	CREATE EXTENSION IF NOT EXISTS vector;

	CREATE TABLE IF NOT EXISTS memory_documents (
		id TEXT PRIMARY KEY,
		content TEXT NOT NULL,
		embedding vector(1536),
		agent_type TEXT NOT NULL,
		skill_id TEXT,
		task_type TEXT,
		tags TEXT[],
		success_rate FLOAT DEFAULT 0,
		usage_count INT DEFAULT 0,
		metadata JSONB,
		created_at TIMESTAMP DEFAULT NOW(),
		updated_at TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_memory_agent_type ON memory_documents(agent_type);
	CREATE INDEX IF NOT EXISTS idx_memory_skill_id ON memory_documents(skill_id);
	CREATE INDEX IF NOT EXISTS idx_memory_task_type ON memory_documents(task_type);
	CREATE INDEX IF NOT EXISTS idx_memory_tags ON memory_documents USING GIN(tags);

	-- 向量索引 (HNSW)
	CREATE INDEX IF NOT EXISTS idx_memory_embedding ON memory_documents
		USING hnsw (embedding vector_cosine_ops)
		WITH (m = 16, ef_construction = 64);
	`

	_, err := s.pool.Exec(ctx, schema)
	return err
}

// generateID 生成文档 ID
func generateID(content string) string {
	hash := sha256.Sum256([]byte(content + time.Now().Format(time.RFC3339Nano)))
	return hex.EncodeToString(hash[:])[:16]
}

// generateEmbedding 生成向量嵌入
func (s *Store) generateEmbedding(ctx context.Context, text string) ([]float64, error) {
	// TODO: 实现实际的嵌入 API 调用
	// 这里使用简单的模拟实现
	// 在实际环境中，应该调用 OpenAI/MiniMax 等嵌入 API

	// 模拟生成固定大小的向量
	vector := make([]float64, 1536)
	hash := sha256.Sum256([]byte(text))
	for i, b := range hash {
		vector[i%1536] += float64(b) / 255.0
	}

	// 归一化
	var norm float64
	for _, v := range vector {
		norm += v * v
	}
	norm = 1 / (norm + 0.0001)
	for i := range vector {
		vector[i] *= norm
	}

	return vector, nil
}

// Store 存储文档
func (s *Store) Store(ctx context.Context, doc memory.MemoryDocument) error {
	if doc.ID == "" {
		doc.ID = generateID(doc.Content)
	}
	doc.CreatedAt = time.Now()
	doc.UpdatedAt = time.Now()

	// 生成嵌入向量
	embedding, err := s.generateEmbedding(ctx, doc.Content)
	if err != nil {
		return fmt.Errorf("failed to generate embedding: %w", err)
	}
	doc.Embedding = embedding

	// 转换为 JSON
	tagsJSON, _ := json.Marshal(doc.Tags)
	metadataJSON, _ := json.Marshal(doc.Metadata)

	query := `
		INSERT INTO memory_documents
			(id, content, embedding, agent_type, skill_id, task_type, tags, success_rate, usage_count, metadata, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
		ON CONFLICT (id) DO UPDATE SET
			content = EXCLUDED.content,
			embedding = EXCLUDED.embedding,
			agent_type = EXCLUDED.agent_type,
			skill_id = EXCLUDED.skill_id,
			task_type = EXCLUDED.task_type,
			tags = EXCLUDED.tags,
			success_rate = EXCLUDED.success_rate,
			usage_count = EXCLUDED.usage_count,
			metadata = EXCLUDED.metadata,
			updated_at = EXCLUDED.updated_at
	`

	_, err = s.pool.Exec(ctx, query,
		doc.ID, doc.Content, doc.Embedding, doc.AgentType, doc.SkillID, doc.TaskType,
		tagsJSON, doc.SuccessRate, doc.UsageCount, metadataJSON, doc.CreatedAt, doc.UpdatedAt,
	)

	if err != nil {
		return fmt.Errorf("failed to store document: %w", err)
	}

	// 更新缓存
	s.cache.Store(doc.ID, doc)

	s.logger.WithFields(logrus.Fields{
		"id":         doc.ID,
		"agent_type": doc.AgentType,
		"skill_id":   doc.SkillID,
	}).Debug("document stored in long-term memory")

	return nil
}

// StoreBatch 批量存储文档
func (s *Store) StoreBatch(ctx context.Context, docs []memory.MemoryDocument) error {
	if len(docs) == 0 {
		return nil
	}

	now := time.Now()
	batch := make([][]interface{}, 0, len(docs))

	for i := range docs {
		if docs[i].ID == "" {
			docs[i].ID = generateID(docs[i].Content)
		}
		docs[i].CreatedAt = now
		docs[i].UpdatedAt = now

		// 生成嵌入向量
		embedding, err := s.generateEmbedding(ctx, docs[i].Content)
		if err != nil {
			s.logger.WithError(err).Warnf("failed to generate embedding for doc %d", i)
			continue
		}
		docs[i].Embedding = embedding

		tagsJSON, _ := json.Marshal(docs[i].Tags)
		metadataJSON, _ := json.Marshal(docs[i].Metadata)

		batch = append(batch, []interface{}{
			docs[i].ID, docs[i].Content, docs[i].Embedding, docs[i].AgentType,
			docs[i].SkillID, docs[i].TaskType, tagsJSON, docs[i].SuccessRate,
			docs[i].UsageCount, metadataJSON, docs[i].CreatedAt, docs[i].UpdatedAt,
		})

		// 更新缓存
		s.cache.Store(docs[i].ID, docs[i])
	}

	if len(batch) == 0 {
		return fmt.Errorf("no valid documents to store")
	}

	// 批量插入
	query := `
		INSERT INTO memory_documents
			(id, content, embedding, agent_type, skill_id, task_type, tags, success_rate, usage_count, metadata, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
		ON CONFLICT (id) DO UPDATE SET
			content = EXCLUDED.content,
			embedding = EXCLUDED.embedding,
			agent_type = EXCLUDED.agent_type,
			skill_id = EXCLUDED.skill_id,
			task_type = EXCLUDED.task_type,
			tags = EXCLUDED.tags,
			success_rate = EXCLUDED.success_rate,
			usage_count = EXCLUDED.usage_count,
			metadata = EXCLUDED.metadata,
			updated_at = EXCLUDED.updated_at
	`

	_, err := s.pool.CopyFrom(
		ctx,
		pgx.Identifier{"memory_documents"},
		[]string{"id", "content", "embedding", "agent_type", "skill_id", "task_type", "tags", "success_rate", "usage_count", "metadata", "created_at", "updated_at"},
		pgx.CopyFromRows(batch),
	)

	if err != nil {
		return fmt.Errorf("failed to batch store documents: %w", err)
	}

	s.logger.WithFields(logrus.Fields{
		"count": len(batch),
	}).Debug("batch stored documents in long-term memory")

	return nil
}

// GetByFilter 根据过滤条件获取文档
func (s *Store) GetByFilter(ctx context.Context, filter MemoryFilter) ([]memory.MemoryDocument, error) {
	filters := []string{"1=1"}
	args := []interface{}{}
	argNum := 1

	if len(filter.AgentTypes) > 0 {
		placeholders := make([]string, len(filter.AgentTypes))
		for i, at := range filter.AgentTypes {
			placeholders[i] = fmt.Sprintf("$%d", argNum)
			args = append(args, at)
			argNum++
		}
		filters = append(filters, fmt.Sprintf("agent_type IN (%s)", strings.Join(placeholders, ",")))
	}

	if len(filter.SkillIDs) > 0 {
		placeholders := make([]string, len(filter.SkillIDs))
		for i, sid := range filter.SkillIDs {
			placeholders[i] = fmt.Sprintf("$%d", argNum)
			args = append(args, sid)
			argNum++
		}
		filters = append(filters, fmt.Sprintf("skill_id IN (%s)", strings.Join(placeholders, ",")))
	}

	if filter.MinSuccessRate > 0 {
		filters = append(filters, fmt.Sprintf("success_rate >= $%d", argNum))
		args = append(args, filter.MinSuccessRate)
		argNum++
	}

	if !filter.CreatedAfter.IsZero() {
		filters = append(filters, fmt.Sprintf("created_at >= $%d", argNum))
		args = append(args, filter.CreatedAfter)
		argNum++
	}

	if !filter.CreatedBefore.IsZero() {
		filters = append(filters, fmt.Sprintf("created_at <= $%d", argNum))
		args = append(args, filter.CreatedBefore)
		argNum++
	}

	sql := fmt.Sprintf(`
		SELECT id, content, agent_type, skill_id, task_type, tags, success_rate, usage_count, metadata, created_at, updated_at
		FROM memory_documents
		WHERE %s
		ORDER BY success_rate DESC, usage_count DESC
		LIMIT $%d
	`, strings.Join(filters, " AND "), argNum)

	args = append(args, filter.Limit)

	rows, err := s.pool.Query(ctx, sql, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to get documents by filter: %w", err)
	}
	defer rows.Close()

	var docs []memory.MemoryDocument
	for rows.Next() {
		var doc memory.MemoryDocument
		var tagsJSON []byte
		var metadataJSON []byte

		err := rows.Scan(
			&doc.ID, &doc.Content, &doc.AgentType, &doc.SkillID, &doc.TaskType,
			&tagsJSON, &doc.SuccessRate, &doc.UsageCount, &metadataJSON,
			&doc.CreatedAt, &doc.UpdatedAt,
		)
		if err != nil {
			continue
		}

		json.Unmarshal(tagsJSON, &doc.Tags)
		json.Unmarshal(metadataJSON, &doc.Metadata)
		docs = append(docs, doc)
	}

	return docs, nil
}

// MemoryFilter 文档过滤条件
type MemoryFilter struct {
	AgentTypes      []string
	SkillIDs        []string
	Tags            []string
	TaskTypes       []string
	MinSuccessRate  float64
	MinUsageCount   int
	CreatedAfter    time.Time
	CreatedBefore   time.Time
	Limit           int
}

// Search 搜索文档
func (s *Store) Search(ctx context.Context, query memory.SearchQuery) ([]memory.SearchResult, error) {
	// 生成查询向量
	embedding, err := s.generateEmbedding(ctx, query.Query)
	if err != nil {
		return nil, fmt.Errorf("failed to generate query embedding: %w", err)
	}

	limit := query.Limit
	if limit <= 0 {
		limit = s.maxResults
	}

	threshold := query.Threshold
	if threshold <= 0 {
		threshold = s.similarityThresh
	}

	// 构建过滤条件
	filters := []string{"1=1"}
	args := []interface{}{embedding, threshold, limit}
	argNum := 4

	if query.AgentType != "" {
		filters = append(filters, fmt.Sprintf("agent_type = $%d", argNum))
		args = append(args, query.AgentType)
		argNum++
	}
	if query.SkillID != "" {
		filters = append(filters, fmt.Sprintf("skill_id = $%d", argNum))
		args = append(args, query.SkillID)
		argNum++
	}
	if query.TaskType != "" {
		filters = append(filters, fmt.Sprintf("task_type = $%d", argNum))
		args = append(args, query.TaskType)
		argNum++
	}

	// 首先尝试特定过滤器搜索
	sql := fmt.Sprintf(`
		SELECT id, content, agent_type, skill_id, task_type, tags, success_rate, usage_count, metadata, created_at, updated_at,
			   1 - (embedding <=> $1) as score
		FROM memory_documents
		WHERE %s AND (1 - (embedding <=> $1)) > $2
		ORDER BY embedding <=> $1
		LIMIT $%d
	`, strings.Join(filters, " AND "), argNum)

	rows, err := s.pool.Query(ctx, sql, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to search documents: %w", err)
	}
	defer rows.Close()

	var results []memory.SearchResult
	for rows.Next() {
		var doc memory.MemoryDocument
		var tagsJSON []byte
		var metadataJSON []byte

		err := rows.Scan(
			&doc.ID, &doc.Content, &doc.AgentType, &doc.SkillID, &doc.TaskType,
			&tagsJSON, &doc.SuccessRate, &doc.UsageCount, &metadataJSON,
			&doc.CreatedAt, &doc.UpdatedAt, &doc.Score,
		)
		if err != nil {
			s.logger.WithError(err).Warn("failed to scan row")
			continue
		}

		json.Unmarshal(tagsJSON, &doc.Tags)
		json.Unmarshal(metadataJSON, &doc.Metadata)

		results = append(results, memory.SearchResult{
			Document: doc,
			Score:    doc.Score,
		})
	}

	// Fallback: 如果特定过滤器无结果，尝试全局搜索
	if len(results) == 0 && !query.Global && (query.TaskID != "" || query.SkillID != "") {
		s.logger.Debug("fallback to global search")
		return s.Search(ctx, memory.SearchQuery{
			Query:      query.Query,
			AgentType:  query.AgentType,
			TaskType:   query.TaskType,
			Limit:      limit,
			Threshold:  threshold,
			Global:     true,
		})
	}

	s.logger.WithFields(logrus.Fields{
		"query":      query.Query,
		"results":    len(results),
		"threshold":  threshold,
	}).Debug("search completed in long-term memory")

	return results, nil
}

// Delete 删除文档
func (s *Store) Delete(ctx context.Context, id string) error {
	_, err := s.pool.Exec(ctx, "DELETE FROM memory_documents WHERE id = $1", id)
	if err != nil {
		return fmt.Errorf("failed to delete document: %w", err)
	}

	s.cache.Delete(id)
	return nil
}

// Update 更新文档
func (s *Store) Update(ctx context.Context, doc memory.MemoryDocument) error {
	doc.UpdatedAt = time.Now()

	tagsJSON, _ := json.Marshal(doc.Tags)
	metadataJSON, _ := json.Marshal(doc.Metadata)

	// 重新生成嵌入
	embedding, err := s.generateEmbedding(ctx, doc.Content)
	if err != nil {
		return fmt.Errorf("failed to generate embedding: %w", err)
	}

	query := `
		UPDATE memory_documents SET
			content = $2, embedding = $3, agent_type = $4, skill_id = $5,
			task_type = $6, tags = $7, success_rate = $8, usage_count = $9,
			metadata = $10, updated_at = $11
		WHERE id = $1
	`

	_, err = s.pool.Exec(ctx, query,
		doc.ID, doc.Content, embedding, doc.AgentType, doc.SkillID, doc.TaskType,
		tagsJSON, doc.SuccessRate, doc.UsageCount, metadataJSON, doc.UpdatedAt,
	)

	if err != nil {
		return fmt.Errorf("failed to update document: %w", err)
	}

	s.cache.Store(doc.ID, doc)
	return nil
}

// GetByID 根据 ID 获取文档
func (s *Store) GetByID(ctx context.Context, id string) (*memory.MemoryDocument, error) {
	// 先检查缓存
	if cached, ok := s.cache.Load(id); ok {
		doc := cached.(memory.MemoryDocument)
		return &doc, nil
	}

	var doc memory.MemoryDocument
	var tagsJSON []byte
	var metadataJSON []byte

	err := s.pool.QueryRow(ctx, `
		SELECT id, content, agent_type, skill_id, task_type, tags, success_rate, usage_count, metadata, created_at, updated_at
		FROM memory_documents WHERE id = $1
	`, id).Scan(
		&doc.ID, &doc.Content, &doc.AgentType, &doc.SkillID, &doc.TaskType,
		&tagsJSON, &doc.SuccessRate, &doc.UsageCount, &metadataJSON,
		&doc.CreatedAt, &doc.UpdatedAt,
	)

	if err == pgx.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get document: %w", err)
	}

	json.Unmarshal(tagsJSON, &doc.Tags)
	json.Unmarshal(metadataJSON, &doc.Metadata)

	s.cache.Store(id, doc)
	return &doc, nil
}

// GetByTag 根据标签获取文档
func (s *Store) GetByTag(ctx context.Context, tag string) ([]memory.MemoryDocument, error) {
	rows, err := s.pool.Query(ctx, `
		SELECT id, content, agent_type, skill_id, task_type, tags, success_rate, usage_count, metadata, created_at, updated_at
		FROM memory_documents WHERE $1 = ANY(tags)
	`, tag)
	if err != nil {
		return nil, fmt.Errorf("failed to get documents by tag: %w", err)
	}
	defer rows.Close()

	var docs []memory.MemoryDocument
	for rows.Next() {
		var doc memory.MemoryDocument
		var tagsJSON []byte
		var metadataJSON []byte

		err := rows.Scan(
			&doc.ID, &doc.Content, &doc.AgentType, &doc.SkillID, &doc.TaskType,
			&tagsJSON, &doc.SuccessRate, &doc.UsageCount, &metadataJSON,
			&doc.CreatedAt, &doc.UpdatedAt,
		)
		if err != nil {
			continue
		}

		json.Unmarshal(tagsJSON, &doc.Tags)
		json.Unmarshal(metadataJSON, &doc.Metadata)
		docs = append(docs, doc)
	}

	return docs, nil
}

// Close 关闭连接
func (s *Store) Close() {
	if s.pool != nil {
		s.pool.Close()
	}
}
