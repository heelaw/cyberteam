import { useEffect, useState } from 'react'
import { Card, Tag, Avatar, Spin, Empty, Tooltip, Badge, Tabs, Button, Form, Input, Select, message } from 'antd'
import { RobotOutlined, ToolOutlined, TeamOutlined, ThunderboltOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { api } from '../api/client'

interface AgentInfo {
  name: string
  llm: string
  tools: string[]
  skills: string[]
  departments: string[]
  version: string
  description: string
}

interface CustomAgentInfo extends AgentInfo {
  id: string
  is_active: boolean
  created_at: string
  system_prompt?: string
}

const AVAILABLE_TOOLS = ['bash', 'read', 'write', 'edit', 'grep', 'glob', 'web_search', 'browser', 'database', 'api']
const AVAILABLE_SKILLS = ['代码审查', '架构设计', '产品规划', '市场分析', '用户研究', '数据可视化', '文案撰写', '运营策划', '财务管理', '人力资源']
const AVAILABLE_LLMS = ['claude', 'claude-opus-4-6', 'claude-sonnet-4-6', 'claude-haiku-4-5', 'glm-4', 'qwen', 'deepseek']

export default function Agents() {
  const [builtinAgents, setBuiltinAgents] = useState<AgentInfo[]>([])
  const [customAgents, setCustomAgents] = useState<CustomAgentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<CustomAgentInfo | null>(null)
  const [editAgent, setEditAgent] = useState<CustomAgentInfo | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [form] = Form.useForm()

  const loadAgents = async () => {
    setLoading(true)
    try {
      const [builtin, custom] = await Promise.all([
        api.getAgents() as Promise<AgentInfo[]>,
        api.getCustomAgents() as Promise<CustomAgentInfo[]>
      ])
      setBuiltinAgents(builtin || [])
      setCustomAgents(custom || [])
    } catch {
      message.error('加载 Agent 失败')
    }
    setLoading(false)
  }

  useEffect(() => {
    loadAgents()
  }, [])

  const llmColor: Record<string, string> = {
    'claude-opus-4-6': 'gold',
    'claude-sonnet-4-6': 'blue',
    'claude-haiku-4-5': 'green',
    'glm-5.1': 'cyan',
  }

  const getLlmColor = (llm: string) => {
    for (const [key, color] of Object.entries(llmColor)) {
      if (llm.includes(key)) return color
    }
    return 'purple'
  }

  const handleCreate = async (values: Record<string, unknown>) => {
    try {
      await api.createCustomAgent(values)
      message.success('创建成功')
      setShowCreate(false)
      form.resetFields()
      loadAgents()
    } catch {
      message.error('创建失败')
    }
  }

  const handleUpdate = async (values: Record<string, unknown>) => {
    if (!editAgent) return
    try {
      await api.updateCustomAgent(editAgent.id, values)
      message.success('更新成功')
      setEditAgent(null)
      loadAgents()
    } catch {
      message.error('更新失败')
    }
  }

  const handleDelete = async (agent: CustomAgentInfo) => {
    try {
      await api.deleteCustomAgent(agent.id)
      message.success('删除成功')
      loadAgents()
    } catch {
      message.error('删除失败')
    }
  }

  const AgentCard = ({ agent, showActions = false }: { agent: CustomAgentInfo; showActions?: boolean }) => (
    <Card
      hoverable
      className="bg-cyber-panel border-neon-cyan/20 cursor-pointer transition-all hover:border-neon-cyan/50 hover:shadow-lg hover:shadow-neon-cyan/10"
      onClick={() => setSelectedAgent(agent)}
      styles={{ body: { padding: '16px' } }}
    >
      <div className="flex items-start gap-3 mb-3">
        <Avatar size={44} icon={<RobotOutlined />} className="bg-neon-cyan/20 text-neon-cyan text-lg" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-white font-semibold text-base truncate">{agent.name}</span>
            {agent.is_active === false && <Tag color="red">禁用</Tag>}
          </div>
          <Tag color={getLlmColor(agent.llm)} className="text-xs mt-1">{agent.llm || 'unknown'}</Tag>
        </div>
      </div>
      <p className="text-slate-400 text-xs line-clamp-2 mb-3 min-h-[32px]">{agent.description || '暂无描述'}</p>
      {agent.departments?.length > 0 && (
        <div className="flex items-center gap-1 mb-2">
          <TeamOutlined className="text-slate-500 text-xs" />
          <div className="flex flex-wrap gap-1">
            {agent.departments.slice(0, 2).map((dept) => (
              <Tag key={dept} className="text-xs bg-slate-700 border-slate-600 text-slate-300">{dept}</Tag>
            ))}
          </div>
        </div>
      )}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span><ToolOutlined /> {agent.tools?.length || 0}</span>
          <span><ThunderboltOutlined /> {agent.skills?.length || 0}</span>
        </div>
        {showActions && (
          <div className="flex gap-2">
            <Button size="small" icon={<EditOutlined />} onClick={(e) => { e.stopPropagation(); setEditAgent(agent) }} />
            <Button size="small" danger icon={<DeleteOutlined />} onClick={(e) => { e.stopPropagation(); handleDelete(agent) }} />
          </div>
        )}
      </div>
      {agent.skills?.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {agent.skills.slice(0, 3).map((skill) => (
            <span key={skill} className="text-xs px-2 py-0.5 bg-neon-cyan/10 text-neon-cyan rounded border border-neon-cyan/20">{skill}</span>
          ))}
        </div>
      )}
    </Card>
  )

  const BuiltinCard = ({ agent }: { agent: AgentInfo }) => (
    <Card
      hoverable
      className="bg-cyber-panel border-slate-600/30 hover:border-slate-500/50"
      styles={{ body: { padding: '16px' } }}
    >
      <div className="flex items-start gap-3 mb-3">
        <Avatar size={44} icon={<RobotOutlined />} className="bg-slate-600/30 text-slate-400 text-lg" />
        <div className="flex-1 min-w-0">
          <span className="text-white font-semibold text-base truncate">{agent.name}</span>
          <Tag color={getLlmColor(agent.llm)} className="text-xs mt-1">{agent.llm || 'unknown'}</Tag>
        </div>
        <Tag color="default">内置</Tag>
      </div>
      <p className="text-slate-400 text-xs line-clamp-2 mb-3">{agent.description || '暂无描述'}</p>
      <div className="flex items-center gap-3 text-xs text-slate-500">
        <span><ToolOutlined /> {agent.tools?.length || 0}</span>
        <span><ThunderboltOutlined /> {agent.skills?.length || 0}</span>
      </div>
    </Card>
  )

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Spin size="large" /></div>
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">数字员工</h1>
          <p className="text-slate-400 text-sm">{builtinAgents.length} 个内置 Agent · {customAgents.length} 个自定义 Agent</p>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowCreate(true)} className="bg-neon-cyan">
          创建自定义 Agent
        </Button>
      </div>

      <Tabs defaultActiveKey="custom" items={[
        {
          key: 'custom',
          label: `自定义 Agent (${customAgents.length})`,
          children: (
            <div>
              {customAgents.length === 0 ? (
                <Empty description="暂无自定义 Agent，点击上方按钮创建" className="text-slate-400 mt-20" />
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {customAgents.map((agent) => (
                    <AgentCard key={agent.id} agent={agent} showActions />
                  ))}
                </div>
              )}
            </div>
          ),
        },
        {
          key: 'builtin',
          label: `内置 Agent (${builtinAgents.length})`,
          children: (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {builtinAgents.map((agent) => (
                <BuiltinCard key={agent.name} agent={agent} />
              ))}
            </div>
          ),
        },
      ]} />

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowCreate(false)}>
          <div className="bg-cyber-panel border border-neon-cyan/30 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-xl font-bold text-white mb-4">创建自定义 Agent</h2>
            <Form form={form} layout="vertical" onFinish={handleCreate}>
              <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
                <Input placeholder="例如：我的助手" />
              </Form.Item>
              <Form.Item name="llm" label="语言模型" initialValue="claude">
                <Select options={AVAILABLE_LLMS.map(l => ({ value: l, label: l }))} />
              </Form.Item>
              <Form.Item name="description" label="描述">
                <Input.TextArea placeholder="描述这个 Agent 的用途..." rows={2} />
              </Form.Item>
              <Form.Item name="system_prompt" label="系统提示词">
                <Input.TextArea placeholder="定义 Agent 的角色和行为..." rows={3} />
              </Form.Item>
              <Form.Item name="tools" label="工具">
                <Select mode="multiple" placeholder="选择工具" options={AVAILABLE_TOOLS.map(t => ({ value: t, label: t }))} />
              </Form.Item>
              <Form.Item name="skills" label="技能">
                <Select mode="multiple" placeholder="选择技能" options={AVAILABLE_SKILLS.map(s => ({ value: s, label: s }))} />
              </Form.Item>
              <Form.Item name="departments" label="部门">
                <Select mode="tags" placeholder="选择部门" />
              </Form.Item>
              <div className="flex gap-3 mt-6">
                <Button type="primary" htmlType="submit" className="bg-neon-cyan">创建</Button>
                <Button onClick={() => setShowCreate(false)}>取消</Button>
              </div>
            </Form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editAgent && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setEditAgent(null)}>
          <div className="bg-cyber-panel border border-neon-cyan/30 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-xl font-bold text-white mb-4">编辑 Agent: {editAgent.name}</h2>
            <Form layout="vertical" onFinish={handleUpdate} initialValues={editAgent}>
              <Form.Item name="llm" label="语言模型">
                <Select options={AVAILABLE_LLMS.map(l => ({ value: l, label: l }))} />
              </Form.Item>
              <Form.Item name="description" label="描述">
                <Input.TextArea rows={2} />
              </Form.Item>
              <Form.Item name="system_prompt" label="系统提示词">
                <Input.TextArea rows={3} />
              </Form.Item>
              <Form.Item name="tools" label="工具">
                <Select mode="multiple" options={AVAILABLE_TOOLS.map(t => ({ value: t, label: t }))} />
              </Form.Item>
              <Form.Item name="skills" label="技能">
                <Select mode="multiple" options={AVAILABLE_SKILLS.map(s => ({ value: s, label: s }))} />
              </Form.Item>
              <Form.Item name="departments" label="部门">
                <Select mode="tags" />
              </Form.Item>
              <Form.Item name="is_active" label="状态" valuePropName="checked">
                <input type="checkbox" />
              </Form.Item>
              <div className="flex gap-3 mt-6">
                <Button type="primary" htmlType="submit" className="bg-neon-cyan">保存</Button>
                <Button onClick={() => setEditAgent(null)}>取消</Button>
              </div>
            </Form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setSelectedAgent(null)}>
          <div className="bg-cyber-panel border border-neon-cyan/30 rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start gap-4 mb-4">
              <Avatar size={56} icon={<RobotOutlined />} className="bg-neon-cyan/20 text-neon-cyan" />
              <div className="flex-1">
                <h2 className="text-xl font-bold text-white">{selectedAgent.name}</h2>
                <Tag color={getLlmColor(selectedAgent.llm)} className="mt-1">{selectedAgent.llm}</Tag>
              </div>
              <button onClick={() => setSelectedAgent(null)} className="text-slate-500 hover:text-white text-xl">×</button>
            </div>
            {selectedAgent.description && <p className="text-slate-300 text-sm mb-4">{selectedAgent.description}</p>}
            {selectedAgent.system_prompt && (
              <div className="mb-4">
                <h3 className="text-slate-400 text-xs uppercase tracking-wider mb-2">系统提示词</h3>
                <pre className="bg-slate-800 p-3 rounded text-slate-300 text-xs whitespace-pre-wrap">{selectedAgent.system_prompt}</pre>
              </div>
            )}
            {selectedAgent.departments?.length > 0 && (
              <div className="mb-4">
                <h3 className="text-slate-400 text-xs uppercase tracking-wider mb-2">部门</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedAgent.departments.map((d) => <Tag key={d} icon={<TeamOutlined />}>{d}</Tag>)}
                </div>
              </div>
            )}
            {selectedAgent.tools?.length > 0 && (
              <div className="mb-4">
                <h3 className="text-slate-400 text-xs uppercase tracking-wider mb-2">工具</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedAgent.tools.map((t) => <Tag key={t} icon={<ToolOutlined />}>{t}</Tag>)}
                </div>
              </div>
            )}
            {selectedAgent.skills?.length > 0 && (
              <div className="mb-4">
                <h3 className="text-slate-400 text-xs uppercase tracking-wider mb-2">技能</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedAgent.skills.map((s) => <Tag key={s} color="cyan">{s}</Tag>)}
                </div>
              </div>
            )}
            <div className="flex gap-3 mt-6">
              <Button type="primary" onClick={() => { setSelectedAgent(null); setEditAgent(selectedAgent) }} icon={<EditOutlined />}>编辑</Button>
              <Button onClick={() => setSelectedAgent(null)}>关闭</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}