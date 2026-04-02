/**
 * AddNodeModal - 新增节点弹窗
 *
 * 功能：
 * - 选择节点类型（讨论团队/执行部门/Agent）
 * - 输入节点名称
 * - 设置描述
 */
import React, { useState, useCallback, useEffect } from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import type { OrgNodeType, LayerType } from '@/types/organization'
import { NODE_ICONS, NODE_COLORS } from '@/types/organization'

// Props 接口
export interface AddNodeModalProps {
  open: boolean
  parentNodeType?: OrgNodeType
  defaultType?: OrgNodeType
  onAdd: (data: {
    name: string
    type: OrgNodeType
    description: string
  }) => void
  onCancel: () => void
}

// 节点类型配置
const NODE_TYPE_CONFIGS: Record<OrgNodeType, {
  label: string
  icon: string
  layer: LayerType
  color: string
}> = {
  ceo: { label: 'CEO', icon: '👑', layer: 'ceo', color: '#f59e0b' },
  discuss_group: { label: '讨论层分组', icon: '💭', layer: 'discuss', color: '#8b5cf6' },
  execute_group: { label: '执行层分组', icon: '⚙️', layer: 'execute', color: '#10b981' },
  discuss_team: { label: '讨论团队', icon: '💬', layer: 'discuss', color: '#8b5cf6' },
  execute_dept: { label: '执行部门', icon: '💻', layer: 'execute', color: '#10b981' },
  agent: { label: 'Agent', icon: '🤖', layer: 'execute', color: '#3b82f6' },
}

// 可选的节点类型（根据父节点类型决定）
function getAvailableTypes(parentType?: OrgNodeType): OrgNodeType[] {
  if (!parentType) {
    return ['discuss_team', 'execute_dept', 'agent']
  }

  switch (parentType) {
    case 'ceo':
      return ['discuss_group', 'execute_group', 'discuss_team', 'execute_dept']
    case 'discuss_group':
      return ['discuss_team']
    case 'execute_group':
      return ['execute_dept']
    case 'discuss_team':
      return ['agent']
    case 'execute_dept':
      return ['agent']
    case 'agent':
      return []
    default:
      return []
  }
}

// AddNodeModal 组件
export const AddNodeModal: React.FC<AddNodeModalProps> = ({
  open,
  parentNodeType,
  defaultType,
  onAdd,
  onCancel,
}) => {
  const [form] = Form.useForm()
  const [selectedType, setSelectedType] = useState<OrgNodeType>(defaultType || 'discuss_team')

  const availableTypes = getAvailableTypes(parentNodeType)

  // 重置表单
  useEffect(() => {
    if (open) {
      const defaultTypeValue = defaultType || availableTypes[0] || 'discuss_team'
      setSelectedType(defaultTypeValue)
      form.resetFields()
      form.setFieldsValue({
        type: defaultTypeValue,
        icon: NODE_ICONS[defaultTypeValue],
        color: NODE_COLORS[defaultTypeValue],
      })
    }
  }, [open, defaultType, availableTypes, form])

  // 类型变化时更新图标和颜色
  const handleTypeChange = useCallback((type: OrgNodeType) => {
    setSelectedType(type)
    form.setFieldsValue({
      icon: NODE_ICONS[type],
      color: NODE_COLORS[type],
    })
  }, [form])

  // 提交
  const handleSubmit = useCallback(async () => {
    try {
      const values = await form.validateFields()
      onAdd({
        name: values.name,
        type: values.type,
        description: values.description || '',
      })
      form.resetFields()
    } catch (error) {
      console.error('[AddNodeModal] 验证失败:', error)
    }
  }, [form, onAdd])

  // 取消
  const handleCancel = useCallback(() => {
    form.resetFields()
    onCancel()
  }, [form, onCancel])

  if (availableTypes.length === 0) {
    return null
  }

  return (
    <Modal
      title="新增节点"
      open={open}
      onOk={handleSubmit}
      onCancel={handleCancel}
      okText="创建"
      cancelText="取消"
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          type: selectedType,
          icon: NODE_ICONS[selectedType],
          color: NODE_COLORS[selectedType],
        }}
      >
        <Form.Item
          name="type"
          label="节点类型"
          rules={[{ required: true, message: '请选择节点类型' }]}
        >
          <Select
            placeholder="选择节点类型"
            onChange={handleTypeChange}
            options={availableTypes.map((type) => {
              const config = NODE_TYPE_CONFIGS[type]
              return {
                value: type,
                label: (
                  <span>
                    <span className="mr-2">{config.icon}</span>
                    <span>{config.label}</span>
                  </span>
                ),
              }
            })}
          />
        </Form.Item>

        <Form.Item
          name="name"
          label="节点名称"
          rules={[
            { required: true, message: '请输入节点名称' },
            { max: 50, message: '名称不能超过50个字符' },
          ]}
        >
          <Input
            placeholder={`请输入${NODE_TYPE_CONFIGS[selectedType]?.label || '节点'}名称`}
            showCount
            maxLength={50}
          />
        </Form.Item>

        <Form.Item
          name="description"
          label="描述（可选）"
        >
          <Input.TextArea
            placeholder="输入节点描述..."
            rows={3}
            maxLength={200}
            showCount
          />
        </Form.Item>

        {/* 预览 */}
        <div className="mt-4 p-3 bg-gray-50 rounded border border-gray-200">
          <div className="text-xs text-gray-500 mb-2">预览</div>
          <div className="flex items-center gap-2">
            <span className="text-xl">{NODE_ICONS[selectedType]}</span>
            <span className="font-medium">
              {form.getFieldValue('name') || NODE_TYPE_CONFIGS[selectedType]?.label}
            </span>
          </div>
        </div>
      </Form>
    </Modal>
  )
}

export default AddNodeModal
