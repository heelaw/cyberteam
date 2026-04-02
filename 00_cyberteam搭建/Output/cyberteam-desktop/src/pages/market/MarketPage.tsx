import { useState, useEffect } from "react"
import { CreateGroupModal } from "../../components/CreateGroupModal"
import { mockAgents, type AgentData } from "../../data/mock-agents"

interface CrewMember {
  agent_id: string
  role: string
}

interface CrewTemplate {
  id: string
  name: string
  description: string
  members: string // JSON string of CrewMember[]
  departments: string // JSON string of {department_id}[]
  is_preset: number
}

interface Department {
  id: string
  name: string
  icon: string
  description: string
  sort_order: number
}

export default function MarketPage() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [crewTemplates, setCrewTemplates] = useState<CrewTemplate[]>([])
  const [selectedDept, setSelectedDept] = useState<Department | null>(null)
  const [searchKeyword, setSearchKeyword] = useState("")
  const [showGroupModal, setShowGroupModal] = useState(false)
  const [groupName, setGroupName] = useState("")
  const [selectedAgents, setSelectedAgents] = useState<AgentData[]>([])
  const [creatingCrew, setCreatingCrew] = useState<string | null>(null)
  const [notification, setNotification] = useState<string | null>(null)

  // 预设在市场的 Agent 模板（未安装的）
  const marketAgents = [
    {
      id: "market-seo",
      name: "SEO 专家",
      avatar: "🔍",
      role: "增长部 - SEO 专家",
      department: "增长部",
      description: "搜索引擎优化专家，提升自然搜索流量",
      capabilities: ["关键词研究", "技术SEO", "外链建设"],
    },
    {
      id: "market-copywriter",
      name: "资深文案",
      avatar: "✍️",
      role: "内容部 - 文案专家",
      department: "增长部",
      description: "专业文案撰写，擅长各类营销内容创作",
      capabilities: ["品牌文案", "种草笔记", "产品介绍"],
    },
    {
      id: "market-data",
      name: "数据分析师",
      avatar: "📊",
      role: "增长部 - 数据专家",
      department: "增长部",
      description: "数据驱动决策，深度用户行为分析",
      capabilities: ["数据建模", "用户分析", "AB测试"],
    },
    {
      id: "market-designer",
      name: "视觉设计师",
      avatar: "🎨",
      role: "产品部 - 设计专家",
      department: "产品部",
      description: "UI/UX 设计专家，打造优秀产品体验",
      capabilities: ["UI设计", "品牌视觉", "动效设计"],
    },
    {
      id: "market-pm",
      name: "高级产品经理",
      avatar: "🎯",
      role: "产品部 - 产品专家",
      department: "产品部",
      description: "产品规划与设计，需求优先级管理",
      capabilities: ["PRD撰写", "需求管理", "项目管理"],
    },
    {
      id: "market-sre",
      name: "SRE 工程师",
      avatar: "🛡️",
      role: "技术部 - 稳定性专家",
      department: "技术部",
      description: "系统可靠性工程，保障服务稳定运行",
      capabilities: ["监控告警", "容量规划", "故障响应"],
    },
  ]

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const api = window.electronAPI
      if (!api || !api.departments) {
        console.warn("electronAPI not ready, retrying...")
        setTimeout(loadData, 500)
        return
      }
      const [deptList, crewList] = await Promise.all([
        api.departments.list(),
        api.crewTemplates.list(),
      ])
      const safeDepts = deptList || []
      const safeCrews = crewList || []
      setDepartments(safeDepts)
      setCrewTemplates(safeCrews)
      if (safeDepts.length > 0) {
        setSelectedDept(safeDepts[0])
      }
    } catch (err) {
      console.error("Failed to load data:", err)
    }
  }

  // 按模板创建团队
  async function createCrewFromTemplate(template: CrewTemplate) {
    setCreatingCrew(template.id)
    try {
      const members: CrewMember[] = JSON.parse(template.members)

      // 为每个成员创建 Agent
      for (const member of members) {
        // 检查是否已存在
        const existingAgents = (await window.electronAPI.agents.list()) || []
        if (existingAgents.some(a => a.id === member.agent_id)) {
          continue // 已存在，跳过
        }

        // 从 mockAgents 查找预设数据
        const mockAgent = mockAgents.find(a => a.id === member.agent_id)
        if (!mockAgent) continue

        await window.electronAPI.agents.create({
          name: mockAgent.name,
          avatar: mockAgent.avatar,
          role: mockAgent.role === "ceo" || mockAgent.role === "manager" ? mockAgent.role : "expert",
          department_id: member.department_id || mockAgent.departmentId,
          description: mockAgent.description,
          soul_content: mockAgent.capabilities.join("、"),
        })
      }

      showNotification(`✅ ${template.name} 创建成功！`)
    } catch (err) {
      console.error("Failed to create crew:", err)
      showNotification("❌ 创建失败，请重试")
    } finally {
      setCreatingCrew(null)
    }
  }

  // 手动创建群聊
  async function handleCreateGroup(name: string, agents: AgentData[]) {
    setShowGroupModal(false)
    setCreatingCrew("custom")
    try {
      // 为每个成员创建 Agent
      for (const agent of agents) {
        const existingAgents = (await window.electronAPI.agents.list()) || []
        if (existingAgents.some(a => a.id === agent.id)) {
          continue
        }

        await window.electronAPI.agents.create({
          name: agent.name,
          avatar: agent.avatar,
          role: "expert",
          department_id: agent.departmentId,
          description: agent.description,
          soul_content: agent.capabilities.join("、"),
        })
      }

      showNotification(`✅ 群聊 "${name}" 创建成功！`)
    } catch (err) {
      console.error("Failed to create group:", err)
      showNotification("❌ 创建失败，请重试")
    } finally {
      setCreatingCrew(null)
    }
  }

  // 聘用单个 Agent
  async function hireAgent(agentId: string, deptId: string) {
    try {
      const marketAgent = marketAgents.find(a => a.id === agentId)
      if (!marketAgent) return

      // 检查是否已在该部门
      const existingAgents = (await window.electronAPI.agents.list()) || []
      if (existingAgents.some(a => a.name === marketAgent.name && a.department_id === deptId)) {
        showNotification("⚠️ 该 Agent 已在当前部门")
        return
      }

      await window.electronAPI.agents.create({
        name: marketAgent.name,
        avatar: marketAgent.avatar,
        role: "expert",
        department_id: deptId,
        description: marketAgent.description,
        soul_content: marketAgent.capabilities.join("、"),
      })

      showNotification(`✅ ${marketAgent.name} 已聘用至部门`)
      await loadData() // 刷新列表
    } catch (err) {
      console.error("Failed to hire agent:", err)
    }
  }

  function showNotification(msg: string) {
    setNotification(msg)
    setTimeout(() => setNotification(null), 3000)
  }

  // 过滤市场 Agent
  const filteredMarketAgents = searchKeyword
    ? marketAgents.filter(
        a =>
          a.name.toLowerCase().includes(searchKeyword.toLowerCase()) ||
          a.description.toLowerCase().includes(searchKeyword.toLowerCase()) ||
          a.capabilities.some(c => c.includes(searchKeyword))
      )
    : marketAgents

  // 已安装的 Agent（按部门）
  const installedAgents = (departments || []).flatMap(dept =>
    (crewTemplates || []).flatMap(crew => {
      try {
        const members: CrewMember[] = JSON.parse(crew.members)
        return members
          .filter(m => m.agent_id)
          .map(m => ({
            ...m,
            agent_name: mockAgents.find(a => a.id === m.agent_id)?.name || m.agent_id,
            agent_avatar: mockAgents.find(a => a.id === m.agent_id)?.avatar || "🤖",
          }))
      } catch {
        return []
      }
    })
  )

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        backgroundColor: "#0a0a0f",
        color: "#fff",
      }}
    >
      {/* 通知 */}
      {notification && (
        <div
          style={{
            position: "fixed",
            top: "24px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 99999,
            padding: "12px 24px",
            backgroundColor: "#111827",
            border: "1px solid #374151",
            borderRadius: "12px",
            fontSize: "14px",
            color: "#fff",
            boxShadow: "0 8px 30px rgba(0,0,0,0.3)",
          }}
        >
          {notification}
        </div>
      )}

      {/* 左侧边栏 */}
      <div
        style={{
          width: "240px",
          backgroundColor: "#111827",
          borderRight: "1px solid #1f2937",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: "20px 16px",
            borderBottom: "1px solid #1f2937",
            fontSize: "14px",
            fontWeight: 600,
            color: "#fff",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span style={{ fontSize: "20px" }}>🛒</span>
          <span>Agent 市场</span>
        </div>

        {/* 部门列表 */}
        <div style={{ flex: 1, overflowY: "auto" }}>
          <div
            style={{
              padding: "8px 16px",
              fontSize: "10px",
              color: "#6b7280",
              fontWeight: 600,
              textTransform: "uppercase",
            }}
          >
            部门
          </div>
          {departments.map(dept => (
            <div
              key={dept.id}
              onClick={() => setSelectedDept(dept)}
              style={{
                padding: "10px 16px",
                cursor: "pointer",
                backgroundColor:
                  selectedDept?.id === dept.id ? "#1f2937" : "transparent",
                borderLeft:
                  selectedDept?.id === dept.id ? "3px solid #3b82f6" : "3px solid transparent",
                color: "#fff",
                fontSize: "13px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span>{dept.icon}</span>
              <span>{dept.name}</span>
            </div>
          ))}
        </div>

        {/* 新建群聊按钮 */}
        <div style={{ padding: "12px", borderTop: "1px solid #1f2937" }}>
          <button
            onClick={() => {
              setGroupName("")
              setSelectedAgents([])
              setShowGroupModal(true)
            }}
            style={{
              width: "100%",
              padding: "10px",
              backgroundColor: "#3b82f6",
              border: "none",
              borderRadius: "8px",
              color: "#fff",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "6px",
            }}
          >
            <span>+</span> 新建群聊
          </button>
        </div>
      </div>

      {/* 右侧主内容 */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {/* 顶部搜索 */}
        <div
          style={{
            padding: "20px 24px",
            borderBottom: "1px solid #1f2937",
            backgroundColor: "#111827",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "16px",
              marginBottom: "12px",
            }}
          >
            <div style={{ fontSize: "28px" }}>🛒</div>
            <div>
              <h2 style={{ fontSize: "18px", fontWeight: 600 }}>
                {selectedDept ? `${selectedDept.icon} ${selectedDept.name} Agent 市场` : "Agent 市场"}
              </h2>
              {selectedDept && (
                <p style={{ fontSize: "12px", color: "#6b7280", marginTop: "4px" }}>
                  {selectedDept.description || "从市场聘用 Agent 加入团队"}
                </p>
              )}
            </div>
          </div>

          {/* 搜索框 */}
          <div style={{ position: "relative" }}>
            <input
              type="text"
              value={searchKeyword}
              onChange={e => setSearchKeyword(e.target.value)}
              placeholder="搜索 Agent 名称、技能..."
              style={{
                width: "100%",
                padding: "10px 16px",
                paddingLeft: "40px",
                backgroundColor: "#1f2937",
                border: "1px solid #374151",
                borderRadius: "8px",
                color: "#fff",
                fontSize: "14px",
                outline: "none",
              }}
            />
            <span
              style={{
                position: "absolute",
                left: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                color: "#6b7280",
                fontSize: "16px",
              }}
            >
              🔍
            </span>
          </div>
        </div>

        <div style={{ padding: "24px" }}>
          {/* 团队模板 */}
          <div style={{ marginBottom: "32px" }}>
            <h3
              style={{
                fontSize: "14px",
                fontWeight: 600,
                color: "#9ca3af",
                marginBottom: "16px",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              ⚡ 快速团队模板
            </h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                gap: "12px",
              }}
            >
              {crewTemplates.map(template => {
                let members: CrewMember[] = []
                try {
                  members = JSON.parse(template.members)
                } catch {}

                return (
                  <div
                    key={template.id}
                    style={{
                      padding: "16px",
                      backgroundColor: "#111827",
                      border: "1px solid #1f2937",
                      borderRadius: "12px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "flex-start", gap: "12px", marginBottom: "12px" }}>
                      <div
                        style={{
                          fontSize: "32px",
                          lineHeight: 1,
                        }}
                      >
                        {template.id === "crew-growth"
                          ? "📈"
                          : template.id === "crew-product"
                          ? "🎯"
                          : template.id === "crew-tech"
                          ? "💻"
                          : template.id === "crew-ops"
                          ? "🚀"
                          : "🏢"}
                      </div>
                      <div style={{ flex: 1 }}>
                        <h4 style={{ fontSize: "14px", fontWeight: 600, color: "#fff", marginBottom: "4px" }}>
                          {template.name}
                        </h4>
                        <p style={{ fontSize: "12px", color: "#6b7280", lineHeight: 1.5 }}>
                          {template.description}
                        </p>
                      </div>
                    </div>

                    {/* 成员预览 */}
                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "4px",
                        marginBottom: "12px",
                      }}
                    >
                      {members.slice(0, 5).map((member, i) => {
                        const agent = mockAgents.find(a => a.id === member.agent_id)
                        return (
                          <span
                            key={i}
                            style={{
                              fontSize: "11px",
                              padding: "2px 8px",
                              backgroundColor: "#1f2937",
                              borderRadius: "12px",
                              color: "#9ca3af",
                            }}
                          >
                            {agent?.avatar} {agent?.name || member.agent_id}
                          </span>
                        )
                      })}
                      {members.length > 5 && (
                        <span
                          style={{
                            fontSize: "11px",
                            padding: "2px 8px",
                            color: "#6b7280",
                          }}
                        >
                          +{members.length - 5}
                        </span>
                      )}
                    </div>

                    <button
                      onClick={() => createCrewFromTemplate(template)}
                      disabled={creatingCrew === template.id}
                      style={{
                        width: "100%",
                        padding: "8px",
                        backgroundColor: creatingCrew === template.id ? "#374151" : "#3b82f6",
                        border: "none",
                        borderRadius: "6px",
                        color: "#fff",
                        fontSize: "12px",
                        fontWeight: 500,
                        cursor: creatingCrew === template.id ? "wait" : "pointer",
                        opacity: creatingCrew === template.id ? 0.7 : 1,
                      }}
                    >
                      {creatingCrew === template.id ? "⏳ 创建中..." : "⚡ 一键创建"}
                    </button>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Agent 市场网格 */}
          <div>
            <h3
              style={{
                fontSize: "14px",
                fontWeight: 600,
                color: "#9ca3af",
                marginBottom: "16px",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              🤖 可聘用 Agent
            </h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
                gap: "12px",
              }}
            >
              {filteredMarketAgents.length === 0 ? (
                <div
                  style={{
                    gridColumn: "1/-1",
                    padding: "40px",
                    textAlign: "center",
                    color: "#6b7280",
                  }}
                >
                  未找到匹配的 Agent
                </div>
              ) : (
                filteredMarketAgents.map(agent => (
                  <div
                    key={agent.id}
                    style={{
                      padding: "16px",
                      backgroundColor: "#111827",
                      border: "1px solid #1f2937",
                      borderRadius: "12px",
                      transition: "border-color 0.15s",
                    }}
                    onMouseEnter={e => {
                      ;(e.currentTarget as HTMLElement).style.borderColor = "#3b82f6"
                    }}
                    onMouseLeave={e => {
                      ;(e.currentTarget as HTMLElement).style.borderColor = "#1f2937"
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "flex-start", gap: "12px", marginBottom: "12px" }}>
                      <div style={{ fontSize: "32px", lineHeight: 1 }}>{agent.avatar}</div>
                      <div style={{ flex: 1 }}>
                        <h4 style={{ fontSize: "14px", fontWeight: 600, color: "#fff", marginBottom: "2px" }}>
                          {agent.name}
                        </h4>
                        <p style={{ fontSize: "11px", color: "#6b7280" }}>{agent.role}</p>
                      </div>
                    </div>

                    <p
                      style={{
                        fontSize: "12px",
                        color: "#9ca3af",
                        lineHeight: 1.5,
                        marginBottom: "12px",
                      }}
                    >
                      {agent.description}
                    </p>

                    {/* 能力标签 */}
                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "4px",
                        marginBottom: "12px",
                      }}
                    >
                      {agent.capabilities.slice(0, 3).map((cap, i) => (
                        <span
                          key={i}
                          style={{
                            fontSize: "10px",
                            padding: "2px 6px",
                            backgroundColor: "#1f2937",
                            borderRadius: "4px",
                            color: "#60a5fa",
                          }}
                        >
                          {cap}
                        </span>
                      ))}
                    </div>

                    <button
                      onClick={() => selectedDept && hireAgent(agent.id, selectedDept.id)}
                      disabled={!selectedDept}
                      style={{
                        width: "100%",
                        padding: "8px",
                        backgroundColor: selectedDept ? "#3b82f6" : "#374151",
                        border: "none",
                        borderRadius: "6px",
                        color: "#fff",
                        fontSize: "12px",
                        fontWeight: 500,
                        cursor: selectedDept ? "pointer" : "not-allowed",
                        opacity: selectedDept ? 1 : 0.5,
                      }}
                    >
                      {selectedDept ? `+ 聘用至 ${selectedDept.name}` : "请先选择部门"}
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 创建群聊模态框 */}
      <CreateGroupModal
        visible={showGroupModal}
        initialName={groupName}
        initialAgents={selectedAgents}
        onConfirm={handleCreateGroup}
        onCancel={() => setShowGroupModal(false)}
      />
    </div>
  )
}
