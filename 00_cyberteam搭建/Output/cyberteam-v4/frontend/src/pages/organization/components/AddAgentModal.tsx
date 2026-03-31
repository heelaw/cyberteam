/**
 * AddAgentModal - 绑定 Agent 弹窗
 *
 * 功能：
 * - 从可用 Agent 列表中选择并绑定
 * - 按类型/层级筛选
 * - 搜索 Agent
 */
import React, { useState, useCallback, useMemo } from 'react'
import { Modal, Input, Select, Card, Tag, Typography, Empty, Spin } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import type { AvailableAgent, LayerType } from '@/types/organization'

const { Text } = Typography

// Props 接口
export interface AddAgentModalProps {
  open: boolean
  nodeId: string
  nodeName: string
  nodeLayer: LayerType
  availableAgents: AvailableAgent[]
  boundAgentIds: string[]
  loading?: boolean
  onAdd: (agentId: string) => void
  onCancel: () => void
}

// AddAgentModal 组件
export const AddAgentModal: React.FC<AddAgentModalProps> = ({
  open,
  nodeName,
  nodeLayer,
  availableAgents,
  boundAgentIds,
  loading = false,
  onAdd,
  onCancel,
}) => {
  const [searchText, setSearchText] = useState('')
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)
  const [filterLayer, setFilterLayer] = useState<LayerType | 'all'>('all')

  // 过滤后的 Agent 列表
  const filteredAgents = useMemo(() => {
    return availableAgents.filter((agent) => {
      // 排除已绑定的
      if (boundAgentIds.includes(agent.id)) {
        return false
      }

      // 按层级过滤
      if (filterLayer !== 'all' && agent.layer !== filterLayer) {
        // Agent 可以绑定到任何层，但讨论层节点只能绑定讨论层 Agent
        if (nodeLayer === 'discuss' && agent.layer !== 'discuss' && agent.layer !== 'ceo') {
          return false
        }
        if (nodeLayer === 'execute' && agent.layer !== 'execute') {
          return false
        }
      }

      // 按搜索文本过滤
      if (searchText) {
        const search = searchText.toLowerCase()
        return (
          agent.name.toLowerCase().includes(search) ||
          agent.code.toLowerCase().includes(search) ||
          agent.description?.toLowerCase().includes(search) ||
          agent.agentType.toLowerCase().includes(search)
        )
      }

      return true
    })
  }, [availableAgents, boundAgentIds, filterLayer, searchText, nodeLayer])

  // 层级颜色
  const getLayerColor = (layer: LayerType): string => {
    switch (layer) {
      case 'ceo': return 'gold'
      case 'discuss': return 'purple'
      case 'execute': return 'green'
      default: return 'default'
    }
  }

  // 层级名称
  const getLayerName = (layer: LayerType): string => {
    switch (layer) {
      case 'ceo': return 'CEO'
      case 'discuss': return '讨论层'
      case 'execute': return '执行层'
      default: return layer
    }
  }

  // 提交选择
  const handleSubmit = useCallback(() => {
    if (selectedAgentId) {
      onAdd(selectedAgentId)
      setSelectedAgentId(null)
      setSearchText('')
    }
  }, [selectedAgentId, onAdd])

  // 取消
  const handleCancel = useCallback(() => {
    setSelectedAgentId(null)
    setSearchText('')
    setFilterLayer('all')
    onCancel()
  }, [onCancel])

  return (
    <Modal
      title={
        <div>
          <div>绑定 Agent</div>
          <Text type="secondary" className="text-sm font-normal">
            选择要绑定到「{nodeName}」的 Agent
          </Text>
        </div>
      }
      open={open}
      onOk={handleSubmit}
      onCancel={handleCancel}
      okText="绑定"
      cancelText="取消"
      okButtonProps={{ disabled: !selectedAgentId }}
      width={600}
      destroyOnClose
    >
      {/* 搜索和筛选 */}
      <div className="mb-4 flex gap-3">
        <Input
          placeholder="搜索 Agent 名称、类型..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          className="flex-1"
        />
        <Select
          value={filterLayer}
          onChange={setFilterLayer}
          style={{ width: 120 }}
          options={[
            { value: 'all', label: '全部' },
            { value: 'ceo', label: 'CEO' },
            { value: 'discuss', label: '讨论层' },
            { value: 'execute', label: '执行层' },
          ]}
        />
      </div>

      {/* Agent 列表 */}
      <div className="max-h-[400px] overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Spin />
          </div>
        ) : filteredAgents.length === 0 ? (
          <Empty
            description={
              searchText
                ? '未找到匹配的 Agent'
                : boundAgentIds.length === availableAgents.length
                ? '所有 Agent 已绑定'
                : '暂无可绑定的 Agent'
            }
          />
        ) : (
          <div className="space-y-2">
            {filteredAgents.map((agent) => (
              <Card
                key={agent.id}
                size="small"
                className={`
                  cursor-pointer transition-all
                  ${selectedAgentId === agent.id
                    ? 'ring-2 ring-blue-500 bg-blue-50'
                    : 'hover:bg-gray-50'
                  }
                `}
                onClick={() => setSelectedAgentId(agent.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{agent.name}</span>
                      <Tag color={getLayerColor(agent.layer)} style={{ fontSize: 10 }}>
                        {getLayerName(agent.layer)}
                      </Tag>
                      <Tag color="blue" style={{ fontSize: 10 }}>
                        {agent.agentType}
                      </Tag>
                    </div>
                    <div className="text-xs text-gray-500">
                      <span className="mr-3">代码: {agent.code}</span>
                      {agent.skills.length > 0 && (
                        <span>技能: {agent.skills.slice(0, 3).join(', ')}</span>
                      )}
                    </div>
                    {agent.description && (
                      <Text type="secondary" className="text-xs block mt-1 truncate">
                        {agent.description}
                      </Text>
                    )}
                  </div>
                  <div className="text-xs text-gray-400">
                    {agent.status === 'active' ? (
                      <Tag color="success" style={{ fontSize: 10 }}>活跃</Tag>
                    ) : (
                      <Tag style={{ fontSize: 10 }}>空闲</Tag>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* 已绑定数量提示 */}
      <div className="mt-3 text-xs text-gray-500">
        已绑定 {boundAgentIds.length} 个 Agent，可选 {filteredAgents.length} 个
      </div>
    </Modal>
  )
}

export default AddAgentModal
