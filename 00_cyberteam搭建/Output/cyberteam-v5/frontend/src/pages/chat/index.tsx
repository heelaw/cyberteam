import { useState, useEffect, useCallback } from 'react'
import { Input, Button, List, Avatar, Badge, Modal, Form, message } from 'antd'
import { MessageOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { fetchConversations, createConversation, deleteConversation } from '@/apis/modules/chat'
import type { Conversation } from '@/types'

export default Chat {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [form] = Form.useForm()

  const loadConversations = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchConversations()
      setConversations(data)
    } catch {
      // 后端未启动时显示空状态
      setConversations([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  const handleCreate = async (values: { title?: string }) => {
    setCreateLoading(true)
    try {
      const conv = await createConversation(values.title || '新对话')
      setConversations((prev) => [conv, ...prev])
      setCreateModalOpen(false)
      form.resetFields()
      navigate(`/chat/${conv.id}`)
    } catch {
      message.error('创建对话失败，请检查后端服务')
    } finally {
      setCreateLoading(false)
    }
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await deleteConversation(id)
      setConversations((prev) => prev.filter((c) => c.id !== id))
      message.success('已删除')
    } catch {
      message.error('删除失败')
    }
  }

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="flex h-full">
      {/* 左栏：会话列表 */}
      <div className="w-80 border-r bg-white flex flex-col">
        <div className="p-3 border-b">
          <Input
            placeholder="搜索对话..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            block
            className="mt-2"
            onClick={() => setCreateModalOpen(true)}
          >
            新建对话
          </Button>
        </div>
        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-400">加载中...</div>
          ) : filtered.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              {search ? '无匹配对话' : '暂无对话，点击上方按钮创建'}
            </div>
          ) : (
            <List
              loading={loading}
              dataSource={filtered}
              renderItem={(item) => (
                <List.Item
                  key={item.id}
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => navigate(`/chat/${item.id}`)}
                >
                  <List.Item.Meta
                    avatar={
                      <Badge count={0} size="small">
                        <Avatar icon={<MessageOutlined />} />
                      </Badge>
                    }
                    title={item.title}
                    description={new Date(item.created_at).toLocaleDateString()}
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      </div>

      {/* 右栏：空白提示 */}
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-400">
          <MessageOutlined className="text-4xl mb-2" />
          <p>选择一个对话或创建新对话</p>
        </div>
      </div>

      {/* 创建对话 Modal */}
      <Modal
        title="新建对话"
        open={createModalOpen}
        onCancel={() => {
          setCreateModalOpen(false)
          form.resetFields()
        }}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="title" label="对话标题">
            <Input placeholder="输入对话标题（可选）" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={createLoading} block>
              创建
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
