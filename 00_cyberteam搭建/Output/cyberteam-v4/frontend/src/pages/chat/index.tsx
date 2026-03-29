import { useState } from 'react'
import { Input, Button, List, Avatar, Badge } from 'antd'
import { MessageOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const mockConversations = [
  { id: '1', title: '西北发面包子品牌策划', status: 'active' as const, updatedAt: '10分钟前' },
  { id: '2', title: '新品上市全渠道推广方案', status: 'active' as const, updatedAt: '1小时前' },
  { id: '3', title: '618大促活动策略讨论', status: 'active' as const, updatedAt: '昨天' },
  { id: '4', title: '用户增长策略分析', status: 'archived' as const, updatedAt: '3天前' },
]

export default function Chat() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')

  const filtered = mockConversations.filter((c) =>
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
          <Button type="primary" icon={<PlusOutlined />} block className="mt-2">
            新建对话
          </Button>
        </div>
        <div className="flex-1 overflow-auto">
          <List
            dataSource={filtered}
            renderItem={(item) => (
              <List.Item
                className="cursor-pointer hover:bg-gray-50 px-3"
                onClick={() => navigate(`/chat/${item.id}`)}
              >
                <List.Item.Meta
                  avatar={
                    <Badge status={item.status === 'active' ? 'processing' : 'default'}>
                      <Avatar icon={<MessageOutlined />} />
                    </Badge>
                  }
                  title={item.title}
                  description={item.updatedAt}
                />
              </List.Item>
            )}
          />
        </div>
      </div>

      {/* 中栏：欢迎页 */}
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-400">
          <MessageOutlined className="text-6xl mb-4" />
          <h2 className="text-xl">选择一个对话开始</h2>
          <p>或创建新对话启动 CyberTeam 任务</p>
        </div>
      </div>
    </div>
  )
}
