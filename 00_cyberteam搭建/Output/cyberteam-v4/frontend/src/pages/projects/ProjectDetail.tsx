import { useParams } from 'react-router-dom'
import { Card, Steps, Typography, Tabs, List, Tag, Avatar, Timeline, Button, Space, Row, Col, Statistic } from 'antd'
import {
  RobotOutlined,
  FileTextOutlined,
  LineChartOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography

const projectSteps = [
  { name: 'CEO-COO对齐', status: 'completed', agent: 'CEO + COO' },
  { name: '策略讨论', status: 'completed', agent: '增长总监 + 产品总监 + 运营总监' },
  { name: '风险预案', status: 'running', agent: '质疑者 + 增长总监' },
  { name: 'CEO汇报', status: 'pending', agent: 'COO' },
  { name: '设计联动', status: 'pending', agent: '设计主管' },
  { name: '文案产出', status: 'pending', agent: '高级文案' },
  { name: 'CEO汇总', status: 'pending', agent: 'CEO' },
  { name: '复盘进化', status: 'pending', agent: '全团队' },
]

const agentDiscussions = [
  { agent: 'CEO', dept: '决策层', message: '任务分析完毕，这是一个品牌+市场+营销的综合任务。建议分配给增长部主导。', time: '14:30' },
  { agent: 'COO', dept: '决策层', message: '同意。执行计划已制定，建议先收集海岸城商圈的真实数据。', time: '14:32' },
  { agent: '质疑者', dept: '质量门禁', message: '⚠️ 等一下。目前所有数据都是假设的，需要先通过 Web Search 收集真实竞品信息。', time: '14:35' },
  { agent: '增长总监', dept: '协调层', message: '已执行搜索。海岸城日均客流约12万人次（来源：官方公众号），餐饮占比约35%。', time: '14:40' },
]

const documents = [
  { name: '市场分析报告', type: 'report', status: 'completed' },
  { name: '竞品对比分析', type: 'report', status: 'completed' },
  { name: '品牌定位策略', type: 'plan', status: 'in_progress' },
  { name: '小红书内容方案', type: 'copy', status: 'pending' },
  { name: '抖音推广方案', type: 'copy', status: 'pending' },
]

export default function ProjectDetail() {
  const { id } = useParams()

  return (
    <div className="p-6">
      <Title level={3}>西北发面包子品牌策划</Title>

      {/* 八节点步骤条 */}
      <Card className="mb-4">
        <Steps
          current={2}
          items={projectSteps.map((s) => ({
            title: s.name,
            description: <span className="text-xs">{s.agent}</span>,
          }))}
        />
      </Card>

      {/* 统计 */}
      <Row gutter={16} className="mb-4">
        <Col span={6}><Card><Statistic title="参与 Agent" value={6} prefix={<RobotOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="讨论消息" value={47} prefix={<ThunderboltOutlined />} valueStyle={{ color: '#3b82f6' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="产出文档" value={2} suffix="/ 5" prefix={<FileTextOutlined />} valueStyle={{ color: '#f59e0b' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="完成度" value={37} suffix="%" prefix={<LineChartOutlined />} valueStyle={{ color: '#10b981' }} /></Card></Col>
      </Row>

      {/* Tab 切换 */}
      <Card>
        <Tabs
          items={[
            {
              key: 'discussion',
              label: 'Agent 讨论',
              children: (
                <Timeline
                  items={agentDiscussions.map((d) => ({
                    color: d.dept === '决策层' ? 'gold' : d.dept === '质量门禁' ? 'red' : 'blue',
                    children: (
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Tag color={d.dept === '决策层' ? 'gold' : d.dept === '质量门禁' ? 'red' : 'blue'}>{d.agent}</Tag>
                          <Text type="secondary" className="text-xs">{d.time}</Text>
                        </div>
                        <Paragraph className="mb-0">{d.message}</Paragraph>
                      </div>
                    ),
                  }))}
                />
              ),
            },
            {
              key: 'documents',
              label: '文档产出',
              children: (
                <List
                  dataSource={documents}
                  renderItem={(doc) => (
                    <List.Item actions={[
                      <Tag color={doc.status === 'completed' ? 'success' : doc.status === 'in_progress' ? 'processing' : 'default'}>
                        {doc.status === 'completed' ? '已完成' : doc.status === 'in_progress' ? '进行中' : '待开始'}
                      </Tag>,
                    ]}>
                      <List.Item.Meta
                        avatar={<Avatar icon={<FileTextOutlined />} />}
                        title={doc.name}
                        description={doc.type === 'report' ? '分析报告' : doc.type === 'plan' ? '策略方案' : '文案产出'}
                      />
                    </List.Item>
                  )}
                />
              ),
            },
            {
              key: 'playground',
              label: 'Playground 看板',
              children: (
                <div className="text-center py-12 text-gray-400">
                  <LineChartOutlined className="text-6xl mb-4" />
                  <p>Playground 交互式看板将在 CEO 批准执行后生成</p>
                  <Button type="primary">生成 Playground</Button>
                </div>
              ),
            },
          ]}
        />
      </Card>
    </div>
  )
}
