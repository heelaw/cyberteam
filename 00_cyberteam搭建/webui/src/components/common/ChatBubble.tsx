import { Avatar, Tooltip } from 'antd'
import ReactMarkdown from 'react-markdown'
import { UserOutlined, RobotOutlined, SyncOutlined } from '@ant-design/icons'
import type { Message } from '../../stores/chatStore'

interface ChatBubbleProps {
  message: Message
  isStreaming?: boolean
}

export default function ChatBubble({ message, isStreaming }: ChatBubbleProps) {
  const isUser = message.sender_type === 'user'
  const isAgent = message.sender_type === 'agent'
  const isSystem = message.sender_type === 'system'

  const getAvatar = () => {
    if (isUser) return <Avatar icon={<UserOutlined />} className="bg-neon-cyan" />
    if (isAgent) return <Avatar icon={<RobotOutlined />} className="bg-neon-purple" />
    return <Avatar icon={<SyncOutlined spin />} className="bg-slate-500" />
  }

  const getBubbleClass = () => {
    if (isUser) return 'bg-neon-cyan/10 border-neon-cyan/30 ml-auto'
    if (isAgent) return 'bg-neon-purple/10 border-neon-purple/30'
    return 'bg-slate-800/50 border-slate-600/30 text-slate-400 text-center text-sm'
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} ${isSystem ? 'justify-center' : ''}`}>
      {isSystem ? null : getAvatar()}

      <div className={`max-w-[70%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        <div className="text-xs text-slate-500 px-2">
          {isUser ? '你' : message.sender_id}
          {message.metadata?.tokens_used && (
            <span className="ml-2 text-neon-green/60">
              {message.metadata.tokens_used} tokens
            </span>
          )}
        </div>

        <div
          className={`px-4 py-2 rounded-lg border ${getBubbleClass()} ${
            isStreaming ? 'animate-pulse' : ''
          }`}
        >
          {message.metadata?.tools_used && message.metadata.tools_used.length > 0 && (
            <div className="mb-2 pb-2 border-b border-current/20">
              <Tooltip title={message.metadata.tools_used.join(', ')}>
                <span className="text-xs opacity-60">
                  调用工具: {message.metadata.tools_used.length}个
                </span>
              </Tooltip>
            </div>
          )}

          <div className="prose prose-sm prose-invert max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-neon-cyan ml-1 animate-pulse" />
          )}
        </div>
      </div>
    </div>
  )
}