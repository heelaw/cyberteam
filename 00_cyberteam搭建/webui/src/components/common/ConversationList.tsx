import { Input, Button, Dropdown, Empty } from 'antd'
import { PlusOutlined, SearchOutlined, MoreOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons'
import type { MenuProps } from 'antd'
import { format } from 'date-fns'
import type { Conversation } from '../../stores/chatStore'

interface ConversationListProps {
  conversations: Conversation[]
  currentConversation: Conversation | null
  searchValue: string
  onSearchChange: (value: string) => void
  onSelect: (conv: Conversation) => void
  onNew: () => void
  onDelete: (id: string) => void
}

export default function ConversationList({
  conversations,
  currentConversation,
  searchValue,
  onSearchChange,
  onSelect,
  onNew,
  onDelete
}: ConversationListProps) {
  const getConversationMenu = (conv: Conversation): MenuProps['items'] => [
    {
      key: 'rename',
      icon: <EditOutlined />,
      label: '重命名'
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除',
      danger: true,
      onClick: () => onDelete(conv.id)
    }
  ]

  const formatTime = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'MM-dd HH:mm')
    } catch {
      return dateStr
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b border-neon-cyan/10">
        <div className="text-[10px] text-slate-600 font-mono tracking-widest uppercase mb-2 px-2">
          对话
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onNew}
          block
          size="small"
          className="bg-neon-cyan border-neon-cyan hover:bg-neon-cyan/80"
        >
          新建对话
        </Button>
      </div>

      {/* Search */}
      <div className="p-3">
        <Input
          prefix={<SearchOutlined className="text-slate-500" />}
          placeholder="搜索对话..."
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          className="bg-cyber-dark border-neon-cyan/20 text-white"
          size="small"
        />
      </div>

      {/* List */}
      <div className="flex-1 overflow-auto px-2">
        {conversations.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={<span className="text-slate-500 text-xs">暂无对话</span>}
            className="py-8"
          />
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => onSelect(conv)}
              className={`group flex items-center justify-between p-3 mb-1 rounded-lg cursor-pointer transition-all ${
                currentConversation?.id === conv.id
                  ? 'bg-neon-cyan/10 border border-neon-cyan/30'
                  : 'hover:bg-cyber-dark/50 border border-transparent'
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm text-white truncate">{conv.title || '新对话'}</div>
                <div className="text-xs text-slate-500 mt-1">
                  {formatTime(conv.updated_at)}
                </div>
              </div>

              <Dropdown
                menu={{ items: getConversationMenu(conv) }}
                trigger={['click']}
                placement="bottomRight"
              >
                <Button
                  type="text"
                  size="small"
                  icon={<MoreOutlined />}
                  className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-white"
                  onClick={(e) => e.stopPropagation()}
                />
              </Dropdown>
            </div>
          ))
        )}
      </div>
    </div>
  )
}