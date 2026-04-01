import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useStore } from '../stores'
import { api } from '../api/client'
import { Users, Building2, Network, FileText, Wrench, MessageSquare, Clock } from 'lucide-react'
import type { Conversation } from '../types'

export default function Dashboard() {
  const { departments, agents, teams, templates, skills, fetchDepartments, fetchAgents, fetchTeams, fetchTemplates, fetchSkills } = useStore()
  const [stats, setStats] = useState({ agentCount: 0, deptCount: 0, teamCount: 0, templateCount: 0, skillCount: 0 })
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [convLoading, setConvLoading] = useState(true)

  useEffect(() => {
    fetchDepartments()
    fetchAgents()
    fetchTeams()
    fetchTemplates()
    fetchSkills()

    // 加载最近会话
    api.getConversations()
      .then((data: Conversation[]) => {
        setConversations(Array.isArray(data) ? data.slice(0, 8) : [])
      })
      .catch(() => setConversations([]))
      .finally(() => setConvLoading(false))
  }, [])

  useEffect(() => {
    setStats({
      agentCount: agents.length,
      deptCount: departments.length,
      teamCount: teams.length,
      templateCount: templates.length,
      skillCount: skills.length,
    })
  }, [agents, departments, teams, templates, skills])

  const cards = [
    { title: '部门数量', value: stats.deptCount, icon: Building2, color: 'blue' },
    { title: 'Agent数量', value: stats.agentCount, icon: Users, color: 'green' },
    { title: '团队数量', value: stats.teamCount, icon: Network, color: 'purple' },
    { title: '模板数量', value: stats.templateCount, icon: FileText, color: 'orange' },
    { title: '技能数量', value: stats.skillCount, icon: Wrench, color: 'pink' },
  ]

  const colorMap: any = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    pink: 'bg-pink-500',
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">CyberTeam Studio 控制台</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {cards.map((card) => {
          const Icon = card.icon
          return (
            <div key={card.title} className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <span className="text-slate-400 text-sm">{card.title}</span>
                <div className={`${colorMap[card.color]} p-2 rounded-lg`}>
                  <Icon size={18} className="text-white" />
                </div>
              </div>
              <p className="text-3xl font-bold text-white">{card.value}</p>
            </div>
          )
        })}
      </div>

      {/* Department Tree */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Building2 size={20} />
          组织架构
        </h2>
        <div className="space-y-2">
          {departments.map((dept) => (
            <div key={dept.id} className="flex items-center gap-2 text-slate-300">
              <div className={`w-2 h-2 rounded-full ${dept.parentId ? 'bg-slate-500' : 'bg-blue-500'}`} />
              <span className={dept.parentId ? 'ml-4 text-sm' : 'font-medium text-white'}>
                {dept.name}
              </span>
              {dept.parentId && (
                <span className="text-xs text-slate-500 ml-2">
                  → {departments.find((d) => d.id === dept.parentId)?.name}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Agents */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Users size={20} />
          最近 Agent
        </h2>
        {agents.length === 0 ? (
          <p className="text-slate-500 text-sm">暂无 Agent 数据</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {agents.slice(0, 6).map((agent) => (
              <div key={agent.id} className="bg-slate-700 rounded-lg p-3">
                <div className="font-medium text-white">{agent.name}</div>
                <div className="text-xs text-slate-400">{agent.role} · {agent.level}</div>
                {agent.skills && agent.skills.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {agent.skills.slice(0, 2).map((skill: string) => (
                      <span key={skill} className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Conversations */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <MessageSquare size={20} />
          最近会话
        </h2>
        {convLoading ? (
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Clock size={14} className="animate-spin" />
            加载中...
          </div>
        ) : conversations.length === 0 ? (
          <p className="text-slate-500 text-sm">暂无会话记录</p>
        ) : (
          <div className="space-y-2">
            {conversations.map((conv) => {
              const statusColors: Record<string, string> = {
                active: 'bg-green-500',
                completed: 'bg-blue-500',
                archived: 'bg-slate-500',
              }
              const statusLabels: Record<string, string> = {
                active: '进行中',
                completed: '已完成',
                archived: '已归档',
              }
              return (
                <Link
                  key={conv.id}
                  to={`/chat/${conv.id}`}
                  className="flex items-center justify-between p-3 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={`w-2 h-2 rounded-full shrink-0 ${statusColors[conv.status] || 'bg-slate-400'}`} />
                    <span className="text-white truncate">{conv.title || '未命名会话'}</span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 ml-3">
                    <span className="text-xs text-slate-400">{statusLabels[conv.status] || conv.status}</span>
                    <span className="text-xs text-slate-500">
                      {new Date(conv.updated_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
