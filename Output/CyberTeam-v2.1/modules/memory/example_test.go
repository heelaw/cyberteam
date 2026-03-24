package memory

import (
	"context"
	"fmt"
	"time"

	"cyberteam/memory"
)

// ExampleLongTermMemory 长期记忆示例
func ExampleLongTermMemory() {
	// 配置
	cfg := memory.Config{
		VectorStoreURL:  "postgres://user:pass@localhost:5432/cyberteam",
		EmbeddingModel:  "text-embedding-3-small",
		SimilarityThreshold: 0.7,
		MaxResults:     5,
	}

	// 创建系统
	sys, err := memory.NewSystem(cfg, nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	defer sys.Close()

	ctx := context.Background()

	// 存储经验
	err = sys.LongTerm().Store(ctx, memory.MemoryDocument{
		AgentType:   "eng-agent",
		SkillID:    "frontend-developer",
		TaskType:   "web-development",
		Content:    "使用 React + TypeScript + TailwindCSS 构建现代 Web 应用",
		Tags:        []string{"react", "typescript", "web", "frontend"},
		SuccessRate: 0.85,
	})
	if err != nil {
		fmt.Printf("Store error: %v\n", err)
		return
	}

	// 搜索经验
	results, err := sys.LongTerm().Search(ctx, memory.SearchQuery{
		Query:     "如何构建 React 组件",
		AgentType: "eng-agent",
		Limit:     3,
		Threshold: 0.7,
	})
	if err != nil {
		fmt.Printf("Search error: %v\n", err)
		return
	}

	fmt.Printf("Found %d results\n", len(results))
	for _, r := range results {
		fmt.Printf("  - Score: %.2f, Content: %s\n", r.Score, r.Document.Content)
	}
}

// ExampleWorkingMemory 工作记忆示例
func ExampleWorkingMemory() {
	cfg := memory.Config{
		VectorStoreURL: "postgres://user:pass@localhost:5432/cyberteam",
		RedisURL:       "redis://localhost:6379",
	}

	sys, _ := memory.NewSystem(cfg, nil)
	defer sys.Close()

	ctx := context.Background()

	// 创建任务上下文
	err := sys.Working().CreateContext(ctx, memory.TaskContext{
		TaskID:     "task-001",
		AgentType:  "gsd-planner",
		Status:     memory.TaskStatusRunning,
		Input:      map[string]interface{}{"goal": "构建 Web 应用"},
		TempData:   make(map[string]interface{}),
		History:    []memory.AgentAction{},
	})
	if err != nil {
		fmt.Printf("Create error: %v\n", err)
		return
	}

	// 添加操作记录
	err = sys.Working().AddAction(ctx, "task-001", memory.AgentAction{
		ActionType: "create-plan",
		AgentType:  "gsd-planner",
		Input:      map[string]interface{}{"spec": " PRD v1.0"},
		Output:     map[string]interface{}{"plan": "3 phases"},
		Duration:   time.Second * 5,
		Success:    true,
	})
	if err != nil {
		fmt.Printf("AddAction error: %v\n", err)
		return
	}

	// 获取上下文
	tc, err := sys.Working().GetContext(ctx, "task-001")
	if err != nil || tc == nil {
		fmt.Println("Context not found")
		return
	}

	fmt.Printf("Task: %s, Status: %s, Actions: %d\n",
		tc.TaskID, tc.Status, len(tc.History))
}

// ExampleEpisodicMemory 情景记忆示例
func ExampleEpisodicMemory() {
	cfg := memory.Config{
		VectorStoreURL: "postgres://user:pass@localhost:5432/cyberteam",
	}

	sys, _ := memory.NewSystem(cfg, nil)
	defer sys.Close()

	ctx := context.Background()

	// 记录成功案例
	err := sys.Episodic().Record(ctx, memory.SuccessEpisode{
		TaskType:   "web-development",
		Solution:   "使用 Next.js + TailwindCSS",
		Duration:   time.Hour * 2,
		AgentType:  "gsd-executor",
		Skills:     []string{"frontend-developer", "design-ux"},
		Outcome:    memory.EpisodeOutcomeSuccess,
		Tags:       []string{"nextjs", "tailwind", "modern"},
		Steps: []memory.ActionStep{
			{
				StepNumber: 1,
				Action:     "创建项目结构",
				AgentType:  "gsd-planner",
				Success:    true,
				Duration:   time.Minute * 10,
			},
			{
				StepNumber: 2,
				Action:     "实现 UI 组件",
				AgentType:  "eng-agent",
				Success:    true,
				Duration:   time.Hour,
			},
		},
	})
	if err != nil {
		fmt.Printf("Record error: %v\n", err)
		return
	}

	// 获取统计
	stats, err := sys.Episodic().GetStats(ctx)
	if err != nil {
		fmt.Printf("Stats error: %v\n", err)
		return
	}

	fmt.Printf("Total: %d, Success Rate: %.2f%%\n",
		stats.TotalEpisodes, stats.SuccessRate*100)
}

// ExampleSmartSearch 智能搜索示例
func ExampleSmartSearch() {
	cfg := memory.Config{
		VectorStoreURL: "postgres://user:pass@localhost:5432/cyberteam",
	}

	sys, _ := memory.NewSystem(cfg, nil)
	defer sys.Close()

	ctx := context.Background()

	// 综合搜索
	result, err := sys.SmartSearch(ctx, memory.SmartSearchQuery{
		Query:          "构建 React Web 应用",
		AgentType:      "eng-agent",
		TaskType:       "web-development",
		Threshold:      0.7,
		EnableLongTerm: true,
		EnableWorking:  true,
		EnableEpisodic: true,
	})
	if err != nil {
		fmt.Printf("Search error: %v\n", err)
		return
	}

	fmt.Printf("Long-term: %d, Working: %d, Episodic: %d, Score: %.2f\n",
		len(result.LongTerm), len(result.Working), len(result.Episodic), result.Score)
}
