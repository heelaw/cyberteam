/**
 * AgentStatusPanel.tsx - Agent 状态面板
 *
 * 显示：
 * - 当前 Agent 信息
 * - 执行进度
 * - Token 消耗
 * - 预算使用率
 * - 最近活动时间
 */
import { Card, Progress, Badge, Statistic, Row, Col, Timeline } from 'antd'
import {
  RobotOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'

interface AgentStatus {
  name: string
  department: string
  status: 'idle' | 'running' | 'completed' | 'error'
  tokensUsed: number
  budgetLimit: number
  lastActive: string
  currentTask?: string
}

const mockAgent: AgentStatus = {
  name: 'CEO',
  department: '决策层',
  status: 'idle',
  tokensUsed: 12400,
  budgetLimit: 100000,
  lastActive: new Date().toISOString(),
}

// 预算使用率
const budgetPercent = Math.round((mockAgent.tokensUsed / mockAgent.budgetLimit) * 100)

// 状态映射
const statusMap = {
  idle: { color: 'default', text: '空闲', icon: <ClockCircleOutlined /> },
  running: { color: 'processing', text: '执行中', icon: <ThunderboltOutlined spin /> },
  completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
  error: { color: 'error', text: '异常', icon: <ExclamationCircleOutlined /> },
}

export default function AgentStatusPanel() {
  const agent = mockAgent
  const st = statusMap[agent.status]

  return (
    <div className="p-3 overflow-y-auto h-full">
      <div className="flex items-center gap-2 mb-4">
        <RobotOutlined className="text-xl text-green-400" />
        <span className="text-gray-200 font-medium">Agent 状态</span>
      </div>

      {/* Agent 信息卡片 */}
      <Card size="small" className="mb-3 bg-gray-800 border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-100 font-semibold">{agent.name}</span>
          <Badge status={st.color as any} text={st.text} />
        </div>
        <div className="text-xs text-gray-400">{agent.department}</div>
        {agent.currentTask && (
          <div className="mt-2 text-xs text-gray-300">
            当前任务：{agent.currentTask}
          </div>
        )}
      </Card>

      {/* Token 消耗 */}
      <Card size="small" className="mb-3 bg-gray-800 border-gray-700">
        <Statistic
          title={<span className="text-gray-400 text-xs">Token 消耗</span>}
          value={agent.tokensUsed}
          suffix="/ 100,000"
          valueStyle={{ fontSize: '18px', color: '#fff' }}
        />
        <Progress
          percent={budgetPercent}
          size="small"
          strokeColor={budgetPercent > 80 ? '#ef4444' : budgetPercent > 50 ? '#eab308' : '#22c55e'}
          className="mt-2"
        />
      </Card>

      {/* 快捷统计 */}
      <Row gutter={8} className="mb-3">
        <Col span={12}>
          <Card size="small" className="bg-gray-800 border-gray-700">
            <Statistic
              title={<span className="text-gray-400 text-xs">对话数</span>}
              value={12}
              valueStyle={{ fontSize: '16px', color: '#fff' }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card size="small" className="bg-gray-800 border-gray-700">
            <Statistic
              title={<span className="text-gray-400 text-xs">执行任务</span>}
              value={28}
              valueStyle={{ fontSize: '16px', color: '#fff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 活动时间线 */}
      <Card
        size="small"
        title={<span className="text-gray-300 text-xs">最近活动</span>}
        className="bg-gray-800 border-gray-700"
      >
        <Timeline
          items={[
            { color: 'green', children: 'Agent 完成响应' },
            { color: 'blue', children: '接收用户消息' },
            { color: 'gray', children: '任务排队中' },
          ]}
        />
      </Card>

      {/* 部门状态总览 */}
      <div className="mt-4">
        <div className="text-gray-300 text-sm mb-2">部门状态</div>
        <div className="space-y-1">
          {['CEO', 'COO', 'PM', '运营部', '设计部', '技术部'].map((dept) => (
            <div key={dept} className="flex items-center justify-between text-xs">
              <span className="text-gray-400">{dept}</span>
              <Badge status="success" text={<span className="text-gray-500">就绪</span>} />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
