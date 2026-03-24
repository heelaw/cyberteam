package memory

import (
	"context"
	"time"
)

// ==================== Vector Store 接口定义 ====================

// VectorStore 向量存储通用接口
// 支持多种后端实现：pgvector、Chroma、Milvus、Qdrant 等
type VectorStore interface {
	// Store 存储向量文档
	Store(ctx context.Context, doc VectorDocument) error

	// StoreBatch 批量存储向量文档
	StoreBatch(ctx context.Context, docs []VectorDocument) error

	// Search 向量相似性搜索
	Search(ctx context.Context, query VectorQuery) ([]VectorResult, error)

	// Delete 删除向量文档
	Delete(ctx context.Context, id string) error

	// Update 更新向量文档
	Update(ctx context.Context, doc VectorDocument) error

	// GetByID 根据 ID 获取文档
	GetByID(ctx context.Context, id string) (*VectorDocument, error)

	// Close 关闭连接
	Close() error
}

// VectorDocument 向量文档
type VectorDocument struct {
	ID        string                 `json:"id"`         // 唯一标识
	Content   string                 `json:"content"`    // 原始文本内容
	Embedding []float64             `json:"-"`          // 向量嵌入 (内存中使用)
	VectorID  string                 `json:"vector_id"` // 外部向量 ID
	Metadata  map[string]interface{} `json:"metadata"`   // 元数据
	Score     float64               `json:"score"`      // 相似度分数 (搜索结果返回)
	CreatedAt time.Time              `json:"created_at"`
	UpdatedAt time.Time              `json:"updated_at"`
}

// VectorQuery 向量搜索查询
type VectorQuery struct {
	Text       string                 // 查询文本
	Embedding  []float64              // 预计算的查询向量
	Filter     map[string]interface{} // 过滤条件
	TopK       int                    // 返回结果数量
	Threshold  float64                // 相似度阈值
	IncludeRaw bool                   // 是否包含原始文本
}

// VectorResult 向量搜索结果
type VectorResult struct {
	Document VectorDocument `json:"document"`
	Score    float64        `json:"score"`
	Distance float64        `json:"distance"` // 余弦距离
}

// ==================== 向量存储实现类型 ====================

// VectorStoreType 向量存储后端类型
type VectorStoreType string

const (
	VectorStoreTypePGVector VectorStoreType = "pgvector" // PostgreSQL + pgvector
	VectorStoreTypeChroma   VectorStoreType = "chroma"   // Chroma
	VectorStoreTypeMilvus   VectorStoreType = "milvus"   // Milvus
	VectorStoreTypeQdrant   VectorStoreType = "qdrant"   // Qdrant
	VectorStoreTypeMemory   VectorStoreType = "memory"   // 内存实现
)

// VectorStoreConfig 向量存储配置
type VectorStoreConfig struct {
	Type          VectorStoreType      // 存储后端类型
	ConnectionURL string               // 连接地址
	APIKey        string               // API Key (用于云服务)
	Dimension     int                  // 向量维度
	Collection    string               // 集合名称
	Metadata      map[string]string   // 额外配置
}

// NewVectorStore 创建向量存储实例
func NewVectorStore(cfg VectorStoreConfig, logger interface{}) (VectorStore, error) {
	switch cfg.Type {
	case VectorStoreTypePGVector, "":
		return newPGVectorStore(cfg, logger)
	case VectorStoreTypeMemory:
		return newMemoryVectorStore(cfg), nil
	default:
		return nil, ErrUnsupportedVectorStore
	}
}

// ErrUnsupportedVectorStore 不支持的向量存储类型
var ErrUnsupportedVectorStore = &VectorError{
	Code:    "UNSUPPORTED_VECTOR_STORE",
	Message: "unsupported vector store type",
}

type VectorError struct {
	Code    string
	Message string
}

func (e *VectorError) Error() string {
	return e.Message
}

// ==================== 内存向量存储实现 (Fallback) ====================

// MemoryVectorStore 内存向量存储实现
// 用于测试或无外部存储时的后备方案
type MemoryVectorStore struct {
	documents map[string]VectorDocument
	dimension int
}

func newMemoryVectorStore(cfg VectorStoreConfig) *MemoryVectorStore {
	dim := cfg.Dimension
	if dim == 0 {
		dim = 1536 // 默认 OpenAI embedding 维度
	}
	return &MemoryVectorStore{
		documents: make(map[string]VectorDocument),
		dimension: dim,
	}
}

func (m *MemoryVectorStore) Store(ctx context.Context, doc VectorDocument) error {
	doc.CreatedAt = time.Now()
	doc.UpdatedAt = time.Now()
	m.documents[doc.ID] = doc
	return nil
}

func (m *MemoryVectorStore) StoreBatch(ctx context.Context, docs []VectorDocument) error {
	now := time.Now()
	for i := range docs {
		docs[i].CreatedAt = now
		docs[i].UpdatedAt = now
		m.documents[docs[i].ID] = docs[i]
	}
	return nil
}

func (m *MemoryVectorStore) Search(ctx context.Context, query.VectorQuery) ([]VectorResult, error) {
	// 简化实现：返回所有文档
	var results []VectorResult
	for _, doc := range m.documents {
		results = append(results, VectorResult{
			Document: doc,
			Score:    0.0,
		})
	}
	return results, nil
}

func (m *MemoryVectorStore) Delete(ctx context.Context, id string) error {
	delete(m.documents, id)
	return nil
}

func (m *MemoryVectorStore) Update(ctx context.Context, doc VectorDocument) error {
	doc.UpdatedAt = time.Now()
	m.documents[doc.ID] = doc
	return nil
}

func (m *MemoryVectorStore) GetByID(ctx context.Context, id string) (*VectorDocument, error) {
	if doc, ok := m.documents[id]; ok {
		return &doc, nil
	}
	return nil, nil
}

func (m *MemoryVectorStore) Close() error {
	m.documents = nil
	return nil
}

// ==================== pgvector 实现 ====================

// PGVectorStore pgvector 实现
type PGVectorStore struct {
	// TODO: 实现 pgvector 后端
	// 需要引入 github.com/jackc/pgx/v5
}

func newPGVectorStore(cfg VectorStoreConfig, logger interface{}) (*PGVectorStore, error) {
	// TODO: 实现 pgvector 连接和操作
	return &PGVectorStore{}, nil
}

func (p *PGVectorStore) Store(ctx context.Context, doc VectorDocument) error {
	// TODO: 实现存储
	return nil
}

func (p *PGVectorStore) StoreBatch(ctx context.Context, docs []VectorDocument) error {
	// TODO: 实现批量存储
	return nil
}

func (p *PGVectorStore) Search(ctx context.Context, query VectorQuery) ([]VectorResult, error) {
	// TODO: 实现向量搜索
	return nil, nil
}

func (p *PGVectorStore) Delete(ctx context.Context, id string) error {
	// TODO: 实现删除
	return nil
}

func (p *PGVectorStore) Update(ctx context.Context, doc VectorDocument) error {
	// TODO: 实现更新
	return nil
}

func (p *PGVectorStore) GetByID(ctx context.Context, id string) (*VectorDocument, error) {
	// TODO: 实现 ID 查询
	return nil, nil
}

func (p *PGVectorStore) Close() error {
	// TODO: 关闭连接
	return nil
}

// ==================== 嵌入生成器接口 ====================

// Embedder 嵌入生成器接口
type Embedder interface {
	// Embed 生成文本嵌入向量
	Embed(ctx context.Context, text string) ([]float64, error)

	// EmbedBatch 批量生成嵌入向量
	EmbedBatch(ctx context.Context, texts []string) ([][]float64, error)

	// Dimension 返回向量维度
	Dimension() int
}

// EmbedderType 嵌入模型类型
type EmbedderType string

const (
	EmbedderTypeOpenAI    EmbedderType = "openai"
	EmbedderTypeMiniMax   EmbedderType = "minimax"
	EmbedderTypeLocal     EmbedderType = "local"
	EmbedderTypeMock      EmbedderType = "mock"
)

// EmbedderConfig 嵌入模型配置
type EmbedderConfig struct {
	Type       EmbedderType
	APIKey     string
	Endpoint   string
	Model      string
	Dimension  int
	BatchSize  int
}

// NewEmbedder 创建嵌入生成器
func NewEmbedder(cfg EmbedderConfig) (Embedder, error) {
	switch cfg.Type {
	case EmbedderTypeOpenAI:
		return newOpenAIEmbedder(cfg)
	case EmbedderTypeMiniMax:
		return newMiniMaxEmbedder(cfg)
	case EmbedderTypeMock, "":
		return newMockEmbedder(cfg), nil
	default:
		return nil, ErrUnsupportedEmbedder
	}
}

// ErrUnsupportedEmbedder 不支持的嵌入模型
var ErrUnsupportedEmbedder = &VectorError{
	Code:    "UNSUPPORTED_EMBEDDER",
	Message: "unsupported embedder type",
}

// MockEmbedder 模拟嵌入生成器
type MockEmbedder struct {
	dimension int
}

func newMockEmbedder(cfg EmbedderConfig) *MockEmbedder {
	dim := cfg.Dimension
	if dim == 0 {
		dim = 1536
	}
	return &MockEmbedder{dimension: dim}
}

func (m *MockEmbedder) Embed(ctx context.Context, text string) ([]float64, error) {
	// 生成确定性伪随机向量
	vector := make([]float64, m.dimension)
	hash := 0
	for _, c := range text {
		hash ^= int(c)
	}
	seed := hash
	for i := 0; i < m.dimension; i++ {
		// 简单伪随机
		seed = seed*1103515245 + 12345
		vector[i] = float64(seed%1000) / 1000.0
	}
	// 归一化
	sum := 0.0
	for _, v := range vector {
		sum += v * v
	}
	sum = 1.0 / (sum + 0.0001)
	for i := range vector {
		vector[i] *= sum
	}
	return vector, nil
}

func (m *MockEmbedder) EmbedBatch(ctx context.Context, texts []string) ([][]float64, error) {
	results := make([][]float64, len(texts))
	for i, text := range texts {
		emb, err := m.Embed(ctx, text)
		if err != nil {
			return nil, err
		}
		results[i] = emb
	}
	return results, nil
}

func (m *MockEmbedder) Dimension() int {
	return m.dimension
}

// OpenAIEmbedder OpenAI 嵌入实现
type OpenAIEmbedder struct {
	config EmbedderConfig
}

func newOpenAIEmbedder(cfg EmbedderConfig) (*OpenAIEmbedder, error) {
	// TODO: 实现 OpenAI 嵌入 API 调用
	return &OpenAIEmbedder{config: cfg}, nil
}

func (o *OpenAIEmbedder) Embed(ctx context.Context, text string) ([]float64, error) {
	// TODO: 调用 OpenAI Embedding API
	return nil, nil
}

func (o *OpenAIEmbedder) EmbedBatch(ctx context.Context, texts []string) ([][]float64, error) {
	// TODO: 批量调用
	return nil, nil
}

func (o *OpenAIEmbedder) Dimension() int {
	return o.config.Dimension
}

// MiniMaxEmbedder MiniMax 嵌入实现
type MiniMaxEmbedder struct {
	config EmbedderConfig
}

func newMiniMaxEmbedder(cfg EmbedderConfig) (*MiniMaxEmbedder, error) {
	// TODO: 实现 MiniMax 嵌入 API 调用
	return &MiniMaxEmbedder{config: cfg}, nil
}

func (m *MiniMaxEmbedder) Embed(ctx context.Context, text string) ([]float64, error) {
	// TODO: 调用 MiniMax Embedding API
	return nil, nil
}

func (m *MiniMaxEmbedder) EmbedBatch(ctx context.Context, texts []string) ([][]float64, error) {
	// TODO: 批量调用
	return nil, nil
}

func (m *MiniMaxEmbedder) Dimension() int {
	return m.config.Dimension
}
