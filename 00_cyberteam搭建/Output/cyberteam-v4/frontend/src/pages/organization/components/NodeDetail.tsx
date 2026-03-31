/**
 * NodeDetail - 右侧节点详情编辑面板
 *
 * 功能：
 * - 显示选中节点的完整信息
 * - 编辑节点属性（名称、描述、图标、颜色）
 * - 管理绑定的 Agent
 * - 添加子节点快捷操作
 */
import React, { useState, useEffect, useCallback } from 'react'
import {
  Card, Form, Input, Select, Button, Space, Divider, Tag, Typography,
  message, Empty, Popconfirm,
} from 'antd'
import {
  SaveOutlined, PlusOutlined, DeleteOutlined, CloseOutlined,
} from '@ant-design/icons'
import type { OrgNode, AvailableAgent, OrgNodeType, LayerType } from '@/types/organization'
import { NODE_ICONS, NODE_COLORS, canAddChildren, canBindAgent } from '@/types/organization'

const { Title, Text } = Typography

// Props 接口
export interface NodeDetailProps {
  node: OrgNode | null
  availableAgents: AvailableAgent[]
  onSave: (nodeId: string, updates: Partial<OrgNode>) => void
  onAddChild: (parentNode: OrgNode, type: OrgNodeType) => void
  onBindAgent: (nodeId: string, agentId: string) => void
  onUnbindAgent: (nodeId: string, agentId: string) => void
  onClose: () => void
}

// 节点类型选项
const NODE_TYPE_OPTIONS: { value: OrgNodeType; label: string; color: string }[] = [
  { value: 'ceo', label: 'CEO', color: '#f59e0b' },
  { value: 'discuss_group', label: '讨论层分组', color: '#8b5cf6' },
  { value: 'execute_group', label: '执行层分组', color: '#10b981' },
  { value: 'discuss_team', label: '讨论团队', color: '#8b5cf6' },
  { value: 'execute_dept', label: '执行部门', color: '#10b981' },
  { value: 'agent', label: 'Agent', color: '#3b82f6' },
]

// 层级选项
const LAYER_OPTIONS: { value: LayerType; label: string }[] = [
  { value: 'ceo', label: 'CEO' },
  { value: 'discuss', label: '讨论层' },
  { value: 'execute', label: '执行层' },
]

// 图标选项
const ICON_OPTIONS = [
  { value: '👑', label: '👑 CEO' },
  { value: '💭', label: '💭 思考' },
  { value: '💬', label: '💬 讨论' },
  { value: '⚙️', label: '⚙️ 执行' },
  { value: '💻', label: '💻 技术' },
  { value: '📢', label: '📢 运营' },
  { value: '🤖', label: '🤖 Agent' },
  { value: '🚀', label: '🚀 增长' },
  { value: '🎯', label: '🎯 策略' },
  { value: '📊', label: '📊 数据' },
  { value: '🎨', label: '🎨 设计' },
  { value: '✍️', label: '✍️ 内容' },
]

// 颜色选项
const COLOR_OPTIONS = [
  { value: '#f59e0b', label: '金色' },
  { value: '#8b5cf6', label: '紫色' },
  { value: '#10b981', label: '绿色' },
  { value: '#3b82f6', label: '蓝色' },
  { value: '#ef4444', label: '红色' },
  { value: '#ec4899', label: '粉色' },
  { value: '#f97316', label: '橙色' },
  { value: '#6b7280', label: '灰色' },
]

// NodeDetail 组件
export const NodeDetail: React.FC<NodeDetailProps> = ({
  node,
  availableAgents,
  onSave,
  onAddChild,
  onBindAgent,
  onUnbindAgent,
  onClose,
}) => {
  const [form] = Form.useForm()
  const [hasChanges, setHasChanges] = useState(false)
  const [boundAgents, setBoundAgents] = useState<AvailableAgent[]>([])

  // 当节点变化时，重置表单
  useEffect(() => {
    if (node) {
      form.setFieldsValue({
        name: node.name,
        type: node.type,
        layer: node.layer,
        icon: node.icon || NODE_ICONS[node.type],
        color: node.color || NODE_COLORS[node.type],
        description: node.description || '',
      })
      setHasChanges(false)

      // 获取已绑定的 Agent
      const bound = availableAgents.filter((a) => node.boundAgents.includes(a.id))
      setBoundAgents(bound)
    }
  }, [node, form, availableAgents])

  // 表单值变化时标记有更改
  const handleValuesChange = useCallback(() => {
    setHasChanges(true)
  }, [])

  // 保存更改
  const handleSave = useCallback(async () => {
    if (!node) return

    try {
      const values = await form.validateFields()
      onSave(node.id, {
        name: values.name,
        type: values.type,
        layer: values.layer,
        icon: values.icon,
        color: values.color,
        description: values.description,
      })
      message.success('保存成功')
      setHasChanges(false)
    } catch (error) {
      console.error('[NodeDetail] 保存失败:', error)
    }
  }, [node, form, onSave])

  // 解绑 Agent
  const handleUnbindAgent = useCallback((agentId: string) => {
    if (!node) return
    onUnbindAgent(node.id, agentId)
    setBoundAgents((prev) => prev.filter((a) => a.id !== agentId))
    message.success('已解绑 Agent')
  }, [node, onUnbindAgent])

  if (!node) {
    return (
      <Card className="h-full">
        <Empty
          description="选择左侧节点查看详情"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    )
  }

  return (
    <Card
      className="h-full"
      title={
        <div className="flex items-center gap-2">
          <span className="text-xl">{node.icon}</span>
          <span className="font-medium">节点详情</span>
        </div>
      }
      extra={
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={onClose}
        />
      }
      actions={[
        <div key="actions" className="px-4 flex gap-2">
          {hasChanges && (
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
            >
              保存
            </Button>
          )}
          <Button onClick={() => form.resetFields()}>
            重置
          </Button>
        </div>,
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleValuesChange}
        disabled={node.deletable === false && node.type === 'ceo'}
      >
        <Form.Item
          name="name"
          label="名称"
          rules={[{ required: true, message: '请输入名称' }]}
        >
          <Input placeholder="节点名称" />
        </Form.Item>

        <div className="grid grid-cols-2 gap-4">
          <Form.Item name="type" label="类型">
            <Select
              placeholder="选择类型"
              options={NODE_TYPE_OPTIONS.map((opt) => ({
                value: opt.value,
                label: (
                  <span>
                    <span style={{ color: opt.color }}>{opt.label}</span>
                  </span>
                ),
              }))}
            />
          </Form.Item>

          <Form.Item name="layer" label="层级">
            <Select
              placeholder="选择层级"
              options={LAYER_OPTIONS}
            />
          </Form.Item>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Form.Item name="icon" label="图标">
            <Select
              placeholder="选择图标"
              options={ICON_OPTIONS}
              showSearch
              filterOption={(input, option) =>
                (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
              }
            />
          </Form.Item>

          <Form.Item name="color" label="颜色">
            <Select
              placeholder="选择颜色"
              options={COLOR_OPTIONS.map((opt) => ({
                value: opt.value,
                label: (
                  <span>
                    <span
                      style={{
                        display: 'inline-block',
                        width: 12,
                        height: 12,
                        borderRadius: 2,
                        backgroundColor: opt.value,
                        marginRight: 8,
                      }}
                    />
                    {opt.label}
                  </span>
                ),
              }))}
            />
          </Form.Item>
        </div>

        <Form.Item name="description" label="描述">
          <Input.TextArea
            placeholder="节点描述..."
            rows={3}
          />
        </Form.Item>

        {/* 节点属性标签 */}
        <div className="flex flex-wrap gap-2 mb-4">
          <Tag color={node.type === 'ceo' ? 'gold' : node.layer === 'discuss' ? 'purple' : 'green'}>
            {node.layer === 'ceo' ? 'CEO' : node.layer === 'discuss' ? '讨论层' : '执行层'}
          </Tag>
          {node.editable === false && <Tag>不可编辑</Tag>}
          {node.deletable === false && <Tag>不可删除</Tag>}
        </div>

        <Divider />

        {/* 绑定 Agent 区域 */}
        {canBindAgent(node) ? (
          <div>
            <div className="flex items-center justify-between mb-3">
              <Title level={5} className="m-0">绑定的 Agent</Title>
              <Button
                type="link"
                size="small"
                icon={<PlusOutlined />}
                onClick={() => onAddChild(node, 'agent')}
              >
                添加 Agent
              </Button>
            </div>

            {boundAgents.length > 0 ? (
              <div className="space-y-2">
                {boundAgents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between p-2 bg-blue-50 rounded border border-blue-100"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{agent.name}</span>
                        <Tag color="blue" style={{ fontSize: 10 }}>{agent.agentType}</Tag>
                      </div>
                      {agent.description && (
                        <Text type="secondary" className="text-xs block">
                          {agent.description}
                        </Text>
                      )}
                    </div>
                    <Popconfirm
                      title="确认解绑"
                      description="确定要解绑此 Agent 吗？"
                      onConfirm={() => handleUnbindAgent(agent.id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                      />
                    </Popconfirm>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-400">
                <Text type="secondary">暂未绑定 Agent</Text>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-4 text-gray-400">
            <Text type="secondary">
              {node.type === 'ceo' && 'CEO 节点为根节点'}
              {node.type === 'discuss_group' && '分组节点，可添加讨论团队'}
              {node.type === 'execute_group' && '分组节点，可添加执行部门'}
            </Text>
          </div>
        )}

        <Divider />

        {/* 快捷操作 */}
        <div>
          <Title level={5} className="m-0 mb-3">快捷操作</Title>
          <Space wrap>
            {canAddChildren(node) && (
              <>
                {(node.type === 'ceo' || node.type === 'discuss_group') && (
                  <Button
                    size="small"
                    icon={<PlusOutlined />}
                    onClick={() => onAddChild(node, 'discuss_team')}
                  >
                    添加讨论团队
                  </Button>
                )}
                {(node.type === 'ceo' || node.type === 'execute_group') && (
                  <Button
                    size="small"
                    icon={<PlusOutlined />}
                    onClick={() => onAddChild(node, 'execute_dept')}
                  >
                    添加执行部门
                  </Button>
                )}
                {(node.type === 'discuss_team' || node.type === 'execute_dept') && (
                  <Button
                    size="small"
                    icon={<PlusOutlined />}
                    onClick={() => onAddChild(node, 'agent')}
                  >
                    添加 Agent
                  </Button>
                )}
              </>
            )}
          </Space>
        </div>

        {/* 子节点数量 */}
        {node.children && node.children.length > 0 && (
          <>
            <Divider />
            <div>
              <Text type="secondary">
                包含 {node.children.length} 个子节点
              </Text>
            </div>
          </>
        )}
      </Form>
    </Card>
  )
}

export default NodeDetail
