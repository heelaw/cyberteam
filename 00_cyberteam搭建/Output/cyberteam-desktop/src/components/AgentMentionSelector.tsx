import React, { useState, useEffect, useRef, useCallback } from "react"
import { mockAgents, groupAgentsByDepartment, statusColorMap, type AgentData } from "../data/mock-agents"

interface AgentMentionSelectorProps {
  /** 是否显示选择器 */
  visible: boolean
  /** 触发位置（光标坐标） */
  position: { x: number; y: number }
  /** 搜索文本 */
  searchText: string
  /** 选中回调 */
  onSelect: (agent: AgentData) => void
  /** 关闭回调 */
  onClose: () => void
}

export const AgentMentionSelector: React.FC<AgentMentionSelectorProps> = ({
  visible,
  position,
  searchText,
  onSelect,
  onClose,
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)

  // 根据搜索文本过滤 Agent
  const filteredAgents = searchText
    ? mockAgents.filter(
        agent =>
          agent.name.toLowerCase().includes(searchText.toLowerCase()) ||
          agent.role.toLowerCase().includes(searchText.toLowerCase()) ||
          agent.department.toLowerCase().includes(searchText.toLowerCase())
      )
    : mockAgents.filter(a => a.status !== "offline")

  // 按部门分组
  const groupedAgents = groupAgentsByDepartment(filteredAgents)
  const flatAgents = filteredAgents

  // 重置选中索引
  useEffect(() => {
    setSelectedIndex(0)
  }, [searchText, visible])

  // 键盘导航
  useEffect(() => {
    if (!visible) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault()
          setSelectedIndex(prev => Math.min(prev + 1, flatAgents.length - 1))
          break
        case "ArrowUp":
          e.preventDefault()
          setSelectedIndex(prev => Math.max(prev - 1, 0))
          break
        case "Enter":
          e.preventDefault()
          if (flatAgents[selectedIndex]) {
            onSelect(flatAgents[selectedIndex])
          }
          break
        case "Escape":
          e.preventDefault()
          onClose()
          break
      }
    }

    document.addEventListener("keydown", handleKeyDown, true)
    return () => document.removeEventListener("keydown", handleKeyDown, true)
  }, [visible, selectedIndex, flatAgents, onSelect, onClose])

  // 点击外部关闭
  useEffect(() => {
    if (!visible) return

    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose()
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [visible, onClose])

  if (!visible) return null

  return (
    <div
      ref={containerRef}
      className="agent-mention-selector"
      style={{
        position: "fixed",
        left: `${position.x}px`,
        top: `${position.y}px`,
        zIndex: 9999,
        minWidth: "280px",
        maxWidth: "340px",
        maxHeight: "280px",
        overflowY: "auto",
        backgroundColor: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
      }}
    >
      {/* 标题 */}
      <div
        style={{
          padding: "8px 12px",
          borderBottom: "1px solid #f3f4f6",
          fontSize: "11px",
          color: "#9ca3af",
          fontWeight: 500,
        }}
      >
        提到 Agent
      </div>

      {/* Agent 列表 */}
      {flatAgents.length === 0 ? (
        <div style={{ padding: "16px", textAlign: "center", color: "#9ca3af", fontSize: "13px" }}>
          未找到匹配的 Agent
        </div>
      ) : (
        Object.entries(groupedAgents).map(([dept, agents]) => (
          <div key={dept}>
            {/* 部门标题 */}
            <div
              style={{
                padding: "6px 12px",
                fontSize: "11px",
                color: "#6b7280",
                backgroundColor: "#f9fafb",
                fontWeight: 600,
                position: "sticky",
                top: 0,
              }}
            >
              {dept}
            </div>

            {/* Agent 列表 */}
            {agents.map(agent => {
              const flatIndex = flatAgents.findIndex(a => a.id === agent.id)
              const isSelected = flatIndex === selectedIndex

              return (
                <div
                  key={agent.id}
                  onClick={() => onSelect(agent)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "8px 12px",
                    cursor: "pointer",
                    backgroundColor: isSelected ? "#eff6ff" : "transparent",
                    transition: "background-color 0.1s",
                  }}
                  onMouseEnter={e => {
                    if (!isSelected) {
                      (e.currentTarget as HTMLElement).style.backgroundColor = "#f9fafb"
                    }
                  }}
                  onMouseLeave={e => {
                    if (!isSelected) {
                      (e.currentTarget as HTMLElement).style.backgroundColor = "transparent"
                    }
                  }}
                >
                  {/* 头像 + 状态点 */}
                  <div style={{ position: "relative" }}>
                    <span style={{ fontSize: "22px" }}>{agent.avatar}</span>
                    <span
                      style={{
                        position: "absolute",
                        bottom: "-2px",
                        right: "-2px",
                        width: "10px",
                        height: "10px",
                        borderRadius: "50%",
                        backgroundColor: statusColorMap[agent.status],
                        border: "2px solid white",
                      }}
                    />
                  </div>

                  {/* 信息 */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: "13px", fontWeight: 500, color: "#111827" }}>
                      {agent.name}
                    </div>
                    <div style={{ fontSize: "11px", color: "#6b7280" }}>
                      {agent.role}
                    </div>
                  </div>

                  {/* 状态标签 */}
                  {agent.status === "busy" && (
                    <span
                      style={{
                        fontSize: "10px",
                        padding: "2px 6px",
                        backgroundColor: "#fef3c7",
                        color: "#d97706",
                        borderRadius: "4px",
                      }}
                    >
                      忙碌
                    </span>
                  )}
                  {agent.status === "thinking" && (
                    <span
                      style={{
                        fontSize: "10px",
                        padding: "2px 6px",
                        backgroundColor: "#dbeafe",
                        color: "#2563eb",
                        borderRadius: "4px",
                      }}
                    >
                      思考中
                    </span>
                  )}
                </div>
              )
            })}
          </div>
        ))
      )}

      {/* 底部提示 */}
      <div
        style={{
          padding: "6px 12px",
          borderTop: "1px solid #f3f4f6",
          fontSize: "10px",
          color: "#9ca3af",
          display: "flex",
          gap: "12px",
        }}
      >
        <span>↑↓ 选择</span>
        <span>Enter 确认</span>
        <span>Esc 关闭</span>
      </div>
    </div>
  )
}
