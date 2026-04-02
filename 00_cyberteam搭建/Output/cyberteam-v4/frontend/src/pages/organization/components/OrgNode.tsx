/**
 * OrgNode - 组织树形节点组件
 *
 * 支持功能：
 * - 点击选中
 * - 双击内联编辑
 * - 拖拽排序
 * - 展开/折叠
 * - 右键上下文菜单
 */
import React, { useState, useRef, useCallback, memo } from 'react'
import { Button, Input, Dropdown, Tag } from 'antd'
import type { MenuProps } from 'antd'
import {
  ExpandOutlined,
  NodeCollapseOutlined,
  PlusOutlined,
  DeleteOutlined,
  CopyOutlined,
  EditOutlined,
} from '@ant-design/icons'
import type { OrgNode as OrgNodeType, OrgNodeType as NodeType } from '@/types/organization'
import { isLeafNode, isGroupNode, NODE_COLOR_CLASS } from '@/types/organization'

// Props 接口
export interface OrgNodeProps {
  node: OrgNodeType
  level: number
  selectedId: string | null
  onSelect: (node: OrgNodeType) => void
  onToggle: (nodeId: string) => void
  onDoubleClick?: (node: OrgNodeType) => void
  onAddChild: (parentNode: OrgNodeType, type: NodeType) => void
  onDelete: (nodeId: string) => void
  onCopy?: (node: OrgNodeType) => void
  onInlineEdit?: (nodeId: string, newName: string) => void
  onDragStart?: (e: React.DragEvent, node: OrgNodeType) => void
  onDragOver?: (e: React.DragEvent) => void
  onDrop?: (e: React.DragEvent, targetNode: OrgNodeType) => void
}

// OrgNode 组件
export const OrgNodeComponent: React.FC<OrgNodeProps> = memo(({
  node,
  level,
  selectedId,
  onSelect,
  onToggle,
  onDoubleClick,
  onAddChild,
  onDelete,
  onCopy,
  onInlineEdit,
  onDragStart,
  onDragOver,
  onDrop,
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(node.name)
  const inputRef = useRef<any>(null)

  const hasChildren = node.children && node.children.length > 0
  const isSelected = selectedId === node.id
  const indent = level * 24

  // 获取节点图标
  const getNodeIcon = () => node.icon || '🤖'

  // 获取节点颜色类
  const getColorClass = () => NODE_COLOR_CLASS[node.type] || NODE_COLOR_CLASS.agent

  // 获取节点类型标签颜色
  const getTypeTagColor = (): string => {
    switch (node.type) {
      case 'ceo': return 'gold'
      case 'discuss_group': return 'purple'
      case 'execute_group': return 'green'
      case 'discuss_team': return 'purple'
      case 'execute_dept': return 'green'
      case 'agent': return 'blue'
      default: return 'default'
    }
  }

  // 获取节点类型中文名
  const getTypeName = (): string => {
    switch (node.type) {
      case 'ceo': return 'CEO'
      case 'discuss_group': return '讨论层'
      case 'execute_group': return '执行层'
      case 'discuss_team': return '讨论团队'
      case 'execute_dept': return '执行部门'
      case 'agent': return 'Agent'
      default: return node.type
    }
  }

  // 处理点击
  const handleClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onSelect(node)
  }, [node, onSelect])

  // 处理双击（内联编辑）
  const handleDoubleClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    if (node.editable !== false) {
      setIsEditing(true)
      setEditValue(node.name)
      setTimeout(() => inputRef.current?.focus(), 0)
    }
  }, [node])

  // 处理编辑完成
  const handleEditComplete = useCallback(() => {
    const trimmed = editValue.trim()
    if (trimmed && trimmed !== node.name && onInlineEdit) {
      onInlineEdit(node.id, trimmed)
    }
    setIsEditing(false)
  }, [editValue, node.id, node.name, onInlineEdit])

  // 处理编辑取消
  const handleEditCancel = useCallback(() => {
    setIsEditing(false)
    setEditValue(node.name)
  }, [node.name])

  // 处理键盘事件
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleEditComplete()
    } else if (e.key === 'Escape') {
      handleEditCancel()
    }
  }, [handleEditComplete, handleEditCancel])

  // 右键菜单
  const contextMenuItems: MenuProps['items'] = [
    ...(node.type !== 'agent' ? [{
      key: 'add_child',
      icon: <PlusOutlined />,
      label: '添加子节点',
      children: [
        ...(node.type === 'ceo' || node.type === 'discuss_group' ? [
          { key: 'add_discuss_team', label: '添加讨论团队', onClick: () => onAddChild(node, 'discuss_team') },
        ] : []),
        ...(node.type === 'ceo' || node.type === 'execute_group' ? [
          { key: 'add_execute_dept', label: '添加执行部门', onClick: () => onAddChild(node, 'execute_dept') },
        ] : []),
        ...(node.type === 'discuss_team' || node.type === 'execute_dept' ? [
          { key: 'add_agent', label: '添加 Agent', onClick: () => onAddChild(node, 'agent') },
        ] : []),
      ],
    }] : []),
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: '重命名',
      disabled: node.editable === false,
      onClick: () => {
        setIsEditing(true)
        setEditValue(node.name)
        setTimeout(() => inputRef.current?.focus(), 0)
      },
    },
    ...(onCopy ? [{
      key: 'copy',
      icon: <CopyOutlined />,
      label: '复制节点',
      onClick: () => onCopy(node),
    }] : []),
    ...(node.deletable !== false ? [{
      type: 'divider' as const,
    }, {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除节点',
      danger: true,
      onClick: () => onDelete(node.id),
    }] : []),
  ]

  return (
    <div style={{ marginLeft: indent }}>
      <Dropdown menu={{ items: contextMenuItems }} trigger={['contextMenu']}>
        <div
          className={`
            flex items-center gap-2 p-2 mb-1 rounded border cursor-pointer transition-all
            hover:shadow-sm
            ${getColorClass()}
            ${isSelected ? 'ring-2 ring-blue-500 shadow-sm' : ''}
            ${node.deletable === false ? 'opacity-75' : ''}
          `}
          onClick={handleClick}
          onDoubleClick={handleDoubleClick}
          draggable={!isEditing && node.type !== 'ceo'}
          onDragStart={(e) => onDragStart?.(e, node)}
          onDragOver={(e) => onDragOver?.(e)}
          onDrop={(e) => onDrop?.(e, node)}
        >
          {/* 展开/折叠按钮 */}
          {isGroupNode(node) && (
            <Button
              type="text"
              size="small"
              icon={node.expanded ? <NodeCollapseOutlined /> : <ExpandOutlined />}
              onClick={(e) => {
                e.stopPropagation()
                onToggle(node.id)
              }}
              className="w-6 h-6 min-w-6 p-0 flex items-center justify-center"
            />
          )}
          {!isGroupNode(node) && <span className="w-6" />}

          {/* 节点图标 */}
          <span className="text-lg">{getNodeIcon()}</span>

          {/* 节点名称 */}
          <div className="flex-1 min-w-0">
            {isEditing ? (
              <Input
                ref={inputRef}
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onBlur={handleEditComplete}
                onKeyDown={handleKeyDown}
                onClick={(e) => e.stopPropagation()}
                size="small"
                className="max-w-[200px]"
              />
            ) : (
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm truncate">{node.name}</span>
                <Tag color={getTypeTagColor()} style={{ fontSize: 10 }}>
                  {getTypeName()}
                </Tag>
              </div>
            )}
          </div>

          {/* 子节点数量 */}
          <div className="text-xs text-gray-400 mr-2">
            {node.type === 'agent' && node.boundAgents.length > 0 && (
              <span>{node.boundAgents.length} Agent</span>
            )}
            {node.type !== 'agent' && hasChildren && (
              <span>{node.children.length} 子节点</span>
            )}
          </div>
        </div>
      </Dropdown>

      {/* 递归渲染子节点 */}
      {node.expanded && hasChildren && (
        <div className="border-l-2 border-gray-200 ml-3">
          {node.children.map((child) => (
            <OrgNodeComponent
              key={child.id}
              node={child}
              level={0}
              selectedId={selectedId}
              onSelect={onSelect}
              onToggle={onToggle}
              onDoubleClick={onDoubleClick}
              onAddChild={onAddChild}
              onDelete={onDelete}
              onCopy={onCopy}
              onInlineEdit={onInlineEdit}
              onDragStart={onDragStart}
              onDragOver={onDragOver}
              onDrop={onDrop}
            />
          ))}
        </div>
      )}
    </div>
  )
})

OrgNodeComponent.displayName = 'OrgNodeComponent'

export default OrgNodeComponent
