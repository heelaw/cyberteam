import React, { useState } from 'react'
import { cn } from '@/utils/cn'
import type { Skill } from '@/types'
import {
  Sparkles,
  Zap,
  BookOpen,
  Code,
  Palette,
  Bot,
  Layers,
  Database,
  Shield,
  Globe,
  Search,
  PenTool,
  ToggleRight,
  X,
  Info,
} from 'lucide-react'

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Zap,
  BookOpen,
  Code,
  Palette,
  Bot,
  Layers,
  Database,
  Shield,
  Globe,
  Search,
  PenTool,
  Sparkles,
}

const MOCK_SKILLS: Skill[] = [
  { id: '1', name: '增长策略', description: '用户增长、留存策略、A/B测试设计', icon: 'Zap', enabled: true, category: 'builtin', triggerKeywords: ['增长', '用户', '留存'] },
  { id: '2', name: '内容运营', description: '内容策略、爆款分析、选题方法论', icon: 'PenTool', enabled: true, category: 'builtin', triggerKeywords: ['内容', '文案', '选题'] },
  { id: '3', name: '数据分析', description: 'SQL查询、数据可视化、趋势分析', icon: 'Database', enabled: true, category: 'builtin', triggerKeywords: ['分析', '数据', '报表'] },
  { id: '4', name: '市场调研', description: '竞品分析、用户访谈、市场洞察', icon: 'Search', enabled: true, category: 'builtin', triggerKeywords: ['调研', '竞品', '市场'] },
  { id: '5', name: '品牌设计', description: '视觉设计、品牌规范、UI/UX评审', icon: 'Palette', enabled: false, category: 'builtin', triggerKeywords: ['设计', '品牌', '视觉'] },
  { id: '6', name: '代码审查', description: 'Code Review、最佳实践、性能优化建议', icon: 'Code', enabled: true, category: 'builtin', triggerKeywords: ['代码', '审查', '重构'] },
  { id: '7', name: '风险管理', description: '风险识别、应急预案、预警机制', icon: 'Shield', enabled: true, category: 'builtin', triggerKeywords: ['风险', '预案', '预警'] },
  { id: '8', name: '小红书营销', description: '小红书平台运营、爆款笔记策略', icon: 'Layers', enabled: false, category: 'custom', triggerKeywords: ['小红书', '种草', '笔记'] },
  { id: '9', name: '抖音运营', description: '抖音短视频运营、直播策略', icon: 'Bot', enabled: false, category: 'custom', triggerKeywords: ['抖音', '短视频', '直播'] },
]

type TabType = 'all' | 'builtin' | 'custom'

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>(MOCK_SKILLS)
  const [activeTab, setActiveTab] = useState<TabType>('all')
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredSkills = skills.filter((skill) => {
    const matchesTab = activeTab === 'all' || skill.category === activeTab
    const matchesSearch = skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesTab && matchesSearch
  })

  const toggleSkill = (id: string) => {
    setSkills((prev) =>
      prev.map((skill) =>
        skill.id === id ? { ...skill, enabled: !skill.enabled } : skill
      )
    )
  }

  const tabs: { key: TabType; label: string; count: number }[] = [
    { key: 'all', label: '全部', count: skills.length },
    { key: 'builtin', label: '内置', count: skills.filter((s) => s.category === 'builtin').length },
    { key: 'custom', label: '自定义', count: skills.filter((s) => s.category === 'custom').length },
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-[var(--color-border)]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[var(--color-bg-tertiary)]">
              <Sparkles className="w-5 h-5 text-[var(--color-accent)]" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-[var(--color-text-primary)]">技能中心</h1>
              <p className="text-sm text-[var(--color-text-secondary)]">
                管理内置技能和自定义技能
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-1 p-1 bg-[var(--color-bg-secondary)] rounded-lg w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={cn(
                'px-4 py-1.5 rounded-md text-sm font-medium transition-all',
                activeTab === tab.key
                  ? 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-primary)]'
                  : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
              )}
            >
              {tab.label}
              <span className="ml-1.5 text-xs opacity-60">({tab.count})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Search */}
      <div className="px-6 py-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索技能..."
            className="w-full pl-10 pr-4 py-2 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent)] transition-colors"
          />
        </div>
      </div>

      {/* Skills Grid */}
      <div className="flex-1 overflow-auto px-6 pb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((skill) => {
            const Icon = ICON_MAP[skill.icon] || Sparkles
            return (
              <div
                key={skill.id}
                className="group relative bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border)] p-5 hover:border-[var(--color-accent)] transition-all cursor-pointer"
                onClick={() => setSelectedSkill(skill)}
              >
                {/* Category Badge */}
                <div className="absolute top-3 right-3">
                  <span
                    className={cn(
                      'px-2 py-0.5 rounded text-xs font-medium',
                      skill.category === 'builtin'
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'bg-purple-500/20 text-purple-400'
                    )}
                  >
                    {skill.category === 'builtin' ? '内置' : '自定义'}
                  </span>
                </div>

                {/* Icon */}
                <div
                  className={cn(
                    'w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-colors',
                    skill.enabled
                      ? 'bg-[var(--color-accent)]/20 text-[var(--color-accent)]'
                      : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)]'
                  )}
                >
                  <Icon className="w-6 h-6" />
                </div>

                {/* Content */}
                <h3 className="text-base font-medium text-[var(--color-text-primary)] mb-1">
                  {skill.name}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] line-clamp-2">
                  {skill.description}
                </p>

                {/* Keywords */}
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {skill.triggerKeywords.slice(0, 3).map((keyword) => (
                    <span
                      key={keyword}
                      className="px-2 py-0.5 bg-[var(--color-bg-tertiary)] rounded text-xs text-[var(--color-text-muted)]"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>

                {/* Toggle Switch */}
                <div className="absolute bottom-5 right-5" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => toggleSkill(skill.id)}
                    className={cn(
                      'relative w-10 h-5 rounded-full transition-colors',
                      skill.enabled ? 'bg-[var(--color-accent)]' : 'bg-[var(--color-border)]'
                    )}
                  >
                    <div
                      className={cn(
                        'absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform',
                        skill.enabled ? 'translate-x-5' : 'translate-x-0.5'
                      )}
                    />
                  </button>
                </div>

                {/* Info Icon */}
                <div className="absolute top-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Info className="w-4 h-4 text-[var(--color-text-muted)]" />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Detail Modal */}
      {selectedSkill && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
          onClick={() => setSelectedSkill(null)}
        >
          <div
            className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border)] w-full max-w-md mx-4 overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-5 border-b border-[var(--color-border)]">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    selectedSkill.enabled
                      ? 'bg-[var(--color-accent)]/20 text-[var(--color-accent)]'
                      : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)]'
                  )}
                >
                  {(() => {
                    const Icon = ICON_MAP[selectedSkill.icon] || Sparkles
                    return <Icon className="w-5 h-5" />
                  })()}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
                    {selectedSkill.name}
                  </h3>
                  <span
                    className={cn(
                      'text-xs',
                      selectedSkill.category === 'builtin'
                        ? 'text-blue-400'
                        : 'text-purple-400'
                    )}
                  >
                    {selectedSkill.category === 'builtin' ? '内置技能' : '自定义技能'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedSkill(null)}
                className="p-1.5 rounded-lg hover:bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-5 space-y-4">
              <div>
                <label className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">
                  描述
                </label>
                <p className="mt-1.5 text-sm text-[var(--color-text-secondary)]">
                  {selectedSkill.description}
                </p>
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">
                  触发关键词
                </label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedSkill.triggerKeywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="px-3 py-1 bg-[var(--color-bg-tertiary)] rounded-lg text-sm text-[var(--color-text-secondary)]"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-[var(--color-border)]">
                <div className="flex items-center gap-2">
                  <ToggleRight className="w-4 h-4 text-[var(--color-text-muted)]" />
                  <span className="text-sm text-[var(--color-text-secondary)]">启用状态</span>
                </div>
                <button
                  onClick={() => {
                    toggleSkill(selectedSkill.id)
                    setSelectedSkill({ ...selectedSkill, enabled: !selectedSkill.enabled })
                  }}
                  className={cn(
                    'relative w-11 h-6 rounded-full transition-colors',
                    selectedSkill.enabled
                      ? 'bg-[var(--color-accent)]'
                      : 'bg-[var(--color-border)]'
                  )}
                >
                  <div
                    className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
                      selectedSkill.enabled ? 'translate-x-5' : 'translate-x-0.5'
                    )}
                  />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
