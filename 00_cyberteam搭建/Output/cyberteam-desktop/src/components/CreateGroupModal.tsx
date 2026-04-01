import React, { useState, useEffect } from "react"
import { mockAgents, groupAgentsByDepartment, type AgentData } from "../data/mock-agents"

interface CreateGroupModalProps {
  visible: boolean
  /** 初始选中的 Agent（从哪个 Agent 点击进来） */
  initialAgents?: AgentData[]
  /** 初始群名 */
  initialName?: string
  onConfirm: (name: string, selectedAgents: AgentData[]) => void
  onCancel: () => void
}

export const CreateGroupModal: React.FC<CreateGroupModalProps> = ({
  visible,
  initialAgents = [],
  initialName = "",
  onConfirm,
  onCancel,
}) => {
  const [groupName, setGroupName] = useState(initialName)
  const [selectedAgents, setSelectedAgents] = useState<AgentData[]>(initialAgents)

  useEffect(() => {
    setGroupName(initialName)
    setSelectedAgents(initialAgents)
  }, [initialName, initialAgents, visible])

  const groupedAgents = groupAgentsByDepartment(mockAgents)

  const toggleAgent = (agent: AgentData) => {
    setSelectedAgents(prev => {
      const isSelected = prev.some(a => a.id === agent.id)
      if (isSelected) {
        return prev.filter(a => a.id !== agent.id)
      } else {
        return [...prev, agent]
      }
    })
  }

  const selectAllInDept = (dept: string) => {
    const deptAgents = mockAgents.filter(a => a.department === dept && a.status !== "offline")
    setSelectedAgents(prev => {
      const newSelected = [...prev.filter(a => a.department !== dept)]
      deptAgents.forEach(agent => {
        if (!newSelected.some(a => a.id === agent.id)) {
          newSelected.push(agent)
        }
      })
      return newSelected
    })
  }

  if (!visible) return null

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
      }}
      onClick={e => {
        if (e.target === e.currentTarget) onCancel()
      }}
    >
      <div
        style={{
          width: "560px",
          maxHeight: "80vh",
          backgroundColor: "#111827",
          border: "1px solid #374151",
          borderRadius: "16px",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* 标题栏 */}
        <div
          style={{
            padding: "20px 24px",
            borderBottom: "1px solid #374151",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <h2 style={{ fontSize: "16px", fontWeight: 600, color: "#fff" }}>创建群聊</h2>
          <button
            onClick={onCancel}
            style={{
              background: "none",
              border: "none",
              color: "#9ca3af",
              fontSize: "20px",
              cursor: "pointer",
              padding: "4px",
            }}
          >
            ×
          </button>
        </div>

        {/* 群名输入 */}
        <div style={{ padding: "16px 24px", borderBottom: "1px solid #374151" }}>
          <label
            style={{ fontSize: "12px", color: "#9ca3af", display: "block", marginBottom: "8px" }}
          >
            群聊名称
          </label>
          <input
            type="text"
            value={groupName}
            onChange={e => setGroupName(e.target.value)}
            placeholder="输入群聊名称..."
            style={{
              width: "100%",
              padding: "10px 12px",
              backgroundColor: "#1f2937",
              border: "1px solid #374151",
              borderRadius: "8px",
              color: "#fff",
              fontSize: "14px",
              outline: "none",
            }}
            autoFocus
          />
        </div>

        {/* 已选成员 */}
        {selectedAgents.length > 0 && (
          <div
            style={{
              padding: "12px 24px",
              borderBottom: "1px solid #374151",
              backgroundColor: "#1f2937",
            }}
          >
            <div style={{ fontSize: "12px", color: "#9ca3af", marginBottom: "8px" }}>
              已选择 {selectedAgents.length} 人
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {selectedAgents.map(agent => (
                <div
                  key={agent.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    padding: "4px 8px",
                    backgroundColor: "#374151",
                    borderRadius: "16px",
                    fontSize: "12px",
                    color: "#fff",
                  }}
                >
                  <span>{agent.avatar}</span>
                  <span>{agent.name}</span>
                  <button
                    onClick={() => toggleAgent(agent)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#9ca3af",
                      cursor: "pointer",
                      fontSize: "14px",
                      padding: "0 2px",
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Agent 列表 */}
        <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
          {Object.entries(groupedAgents).map(([dept, agents]) => (
            <div key={dept}>
              {/* 部门标题 + 全选 */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "8px 24px",
                  backgroundColor: "#0f172a",
                }}
              >
                <span style={{ fontSize: "11px", color: "#64748b", fontWeight: 600 }}>
                  {dept}
                </span>
                <button
                  onClick={() => selectAllInDept(dept)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#3b82f6",
                    fontSize: "11px",
                    cursor: "pointer",
                  }}
                >
                  全选
                </button>
              </div>

              {/* Agent 列表 */}
              {agents.map(agent => {
                const isSelected = selectedAgents.some(a => a.id === agent.id)
                return (
                  <div
                    key={agent.id}
                    onClick={() => toggleAgent(agent)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "12px",
                      padding: "10px 24px",
                      cursor: "pointer",
                      backgroundColor: isSelected ? "#1e3a5f" : "transparent",
                      transition: "background-color 0.1s",
                    }}
                    onMouseEnter={e => {
                      if (!isSelected) {
                        ;(e.currentTarget as HTMLElement).style.backgroundColor = "#1f2937"
                      }
                    }}
                    onMouseLeave={e => {
                      if (!isSelected) {
                        ;(e.currentTarget as HTMLElement).style.backgroundColor = "transparent"
                      }
                    }}
                  >
                    {/* 头像 */}
                    <div style={{ position: "relative" }}>
                      <span style={{ fontSize: "24px" }}>{agent.avatar}</span>
                    </div>

                    {/* 信息 */}
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: "13px", fontWeight: 500, color: "#fff" }}>
                        {agent.name}
                      </div>
                      <div style={{ fontSize: "11px", color: "#6b7280" }}>{agent.role}</div>
                    </div>

                    {/* 选中状态 */}
                    <div
                      style={{
                        width: "20px",
                        height: "20px",
                        borderRadius: "50%",
                        border: `2px solid ${isSelected ? "#3b82f6" : "#4b5563"}`,
                        backgroundColor: isSelected ? "#3b82f6" : "transparent",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        transition: "all 0.15s",
                      }}
                    >
                      {isSelected && <span style={{ color: "#fff", fontSize: "12px" }}>✓</span>}
                    </div>
                  </div>
                )
              })}
            </div>
          ))}
        </div>

        {/* 底部按钮 */}
        <div
          style={{
            padding: "16px 24px",
            borderTop: "1px solid #374151",
            display: "flex",
            gap: "12px",
            justifyContent: "flex-end",
          }}
        >
          <button
            onClick={onCancel}
            style={{
              padding: "10px 20px",
              backgroundColor: "#374151",
              border: "none",
              borderRadius: "8px",
              color: "#fff",
              fontSize: "14px",
              cursor: "pointer",
            }}
          >
            取消
          </button>
          <button
            onClick={() => {
              const name = groupName.trim() || `群聊 (${selectedAgents.length}人)`
              onConfirm(name, selectedAgents)
            }}
            disabled={selectedAgents.length === 0}
            style={{
              padding: "10px 20px",
              backgroundColor: selectedAgents.length > 0 ? "#3b82f6" : "#374151",
              border: "none",
              borderRadius: "8px",
              color: "#fff",
              fontSize: "14px",
              cursor: selectedAgents.length > 0 ? "pointer" : "not-allowed",
              opacity: selectedAgents.length > 0 ? 1 : 0.5,
            }}
          >
            创建群聊 ({selectedAgents.length})
          </button>
        </div>
      </div>
    </div>
  )
}
