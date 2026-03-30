/**
 * 技能管理页面
 */
import { useState, useEffect, useCallback } from 'react'
import { Table, Card, Tag, Space, Button, message, Modal, Input, Select, Tabs } from 'antd'
import { PlayCircleOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { fetchSkills, executeWithSkill, Skill } from '@/apis/modules/skills'

const { TextArea } = Input

export default function SkillManagement() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(false)
  const [executing, setExecuting] = useState(false)
  const [executeModalOpen, setExecuteModalOpen] = useState(false)
  const [taskInput, setTaskInput] = useState('')
  const [result, setResult] = useState('')
  const [selectedSkill, setSelectedSkill] = useState<string | undefined>()

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchSkills()
      setSkills(data)
    } catch (error) {
      message.error('加载技能失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleExecute = async () => {
    if (!taskInput.trim()) {
      message.warning('请输入任务')
      return
    }

    setExecuting(true)
    setResult('')

    try {
      const res = await executeWithSkill(taskInput, selectedSkill)
      setResult(res.result)
    } catch (error: any) {
      message.error(error.message || '执行失败')
    } finally {
      setExecuting(false)
    }
  }

  const columns = [
    {
      title: '技能名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Skill) => (
        <Space>
          <ThunderboltOutlined className="text-yellow-500" />
          <span className="font-medium">{text}</span>
        </Space>
      )
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      render: (cat: string) => {
        const colorMap: Record<string, string> = {
          analysis: 'blue',
          writing: 'green',
          research: 'purple',
          execution: 'orange'
        }
        return <Tag color={colorMap[cat] || 'default'}>{cat}</Tag>
      }
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (kws: string[]) => (
        <Space wrap>
          {kws.slice(0, 5).map(k => <Tag key={k}>{k}</Tag>)}
        </Space>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Skill) => (
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          size="small"
          onClick={() => {
            setSelectedSkill(record.id)
            setExecuteModalOpen(true)
          }}
        >
          执行
        </Button>
      )
    }
  ]

  const categoryStats = (skills || []).reduce((acc, skill) => {
    acc[skill.category] = (acc[skill.category] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="p-4">
      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-bold">技能中心</h2>
        <Button type="primary" icon={<PlayCircleOutlined />} onClick={() => setExecuteModalOpen(true)}>
          执行任务
        </Button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-4 mb-4">
        {Object.entries(categoryStats).map(([cat, count]) => (
          <Card key={cat} size="small">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-500">{count}</div>
              <div className="text-gray-500">{cat}</div>
            </div>
          </Card>
        ))}
      </div>

      <Table
        columns={columns}
        dataSource={skills}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      {/* 执行 Modal */}
      <Modal
        title="执行任务"
        open={executeModalOpen}
        onCancel={() => {
          setExecuteModalOpen(false)
          setTaskInput('')
          setResult('')
        }}
        footer={[
          <Button key="close" onClick={() => setExecuteModalOpen(false)}>
            关闭
          </Button>
        ]}
        width={700}
      >
        <div className="space-y-4">
          <div>
            <label className="block mb-2 font-medium">选择技能（可选）</label>
            <Select
              placeholder="自动匹配最佳技能"
              allowClear
              style={{ width: '100%' }}
              value={selectedSkill}
              onChange={setSelectedSkill}
            >
              {skills.map(s => (
                <Select.Option key={s.id} value={s.id}>{s.name} - {s.category}</Select.Option>
              ))}
            </Select>
          </div>

          <div>
            <label className="block mb-2 font-medium">任务描述</label>
            <TextArea
              rows={4}
              placeholder="描述你要完成的任务..."
              value={taskInput}
              onChange={e => setTaskInput(e.target.value)}
            />
          </div>

          <Button
            type="primary"
            block
            loading={executing}
            onClick={handleExecute}
          >
            执行
          </Button>

          {result && (
            <div>
              <label className="block mb-2 font-medium">执行结果</label>
              <div className="p-4 bg-gray-50 rounded-lg whitespace-pre-wrap">
                {result}
              </div>
            </div>
          )}
        </div>
      </Modal>
    </div>
  )
}
