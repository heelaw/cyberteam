import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'

interface Skill {
  id: string
  name: string
  description: string
  category: string
  enabled: boolean
}

const defaultSkills: Skill[] = [
  { id: '1', name: '信息收集', description: '从多渠道采集、整理和分析信息', category: '信息部', enabled: true },
  { id: '2', name: '市场分析', description: '市场趋势、竞品分析和机会识别', category: '策略部', enabled: true },
  { id: '3', name: '文案创作', description: '多渠道营销文案生成', category: '内容部', enabled: true },
  { id: '4', name: '图像生成', description: 'AI 图像和视觉内容创作', category: '设计部', enabled: true },
  { id: '5', name: '代码审查', description: '代码质量检查和安全审计', category: '工程部', enabled: false },
  { id: '6', name: '运营策划', description: '活动策划和运营策略制定', category: '运营部', enabled: true },
]

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>(defaultSkills)
  const [filter, setFilter] = useState<string>('全部')

  const categories = ['全部', '信息部', '策略部', '内容部', '设计部', '工程部', '运营部']

  const filteredSkills = filter === '全部'
    ? skills
    : skills.filter(s => s.category === filter)

  const toggleSkill = async (id: string) => {
    const updated = skills.map(s =>
      s.id === id ? { ...s, enabled: !s.enabled } : s
    )
    setSkills(updated)
    const skill = updated.find(s => s.id === id)
    if (skill) {
      try {
        await invoke('toggle_skill', { skillId: id, enabled: skill.enabled })
      } catch (e) {
        console.error('Failed to toggle skill:', e)
      }
    }
  }

  return (
    <div className="h-full overflow-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">技能管理</h2>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
            + 添加技能
          </button>
        </div>

        <div className="flex gap-2 mb-6 flex-wrap">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                filter === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="grid gap-4">
          {filteredSkills.map(skill => (
            <div
              key={skill.id}
              className="bg-slate-800 rounded-lg p-4 border border-slate-700 flex items-center justify-between"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="font-medium text-white">{skill.name}</h3>
                  <span className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300">
                    {skill.category}
                  </span>
                </div>
                <p className="text-sm text-slate-400 mt-1">{skill.description}</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={skill.enabled}
                  onChange={() => toggleSkill(skill.id)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
