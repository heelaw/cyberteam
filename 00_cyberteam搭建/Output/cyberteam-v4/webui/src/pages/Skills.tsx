import { useEffect, useState } from 'react';

const API = '/api';

interface Skill {
  id?: string; skill_id?: string; name: string; category: string; description: string;
  triggerConditions?: string; trigger?: string; usageGuide?: string;
  source_path?: string; difficulty?: string; estimated_time?: string; version?: string;
  author?: string; tags?: string[]; success_metrics?: Record<string, string>;
  references?: Array<{ name: string; path: string; type: string }>;
  assess?: Array<{ name: string; path: string }>; content?: string; file_path?: string;
}
interface SkillsResponse { skills: Skill[]; total: number; categories: string[]; }

async function api(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    ...(opts.body ? { body: JSON.stringify(opts.body) } : {}),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

const CATEGORY_STYLES: Record<string, { label: string; color: string; gradient: string }> = {
  growth:     { label: '增长',   color: 'text-emerald-400',  gradient: 'from-emerald-500 to-teal-500' },
  content:    { label: '内容',   color: 'text-blue-400',     gradient: 'from-blue-500 to-cyan-500' },
  analytics:  { label: '分析',   color: 'text-purple-400',   gradient: 'from-purple-500 to-violet-500' },
  social:     { label: '社交',   color: 'text-pink-400',     gradient: 'from-pink-500 to-rose-500' },
  event:      { label: '活动',   color: 'text-orange-400',   gradient: 'from-orange-500 to-amber-500' },
  brand:      { label: '品牌',   color: 'text-indigo-400',   gradient: 'from-indigo-500 to-blue-500' },
  tech:       { label: '技术',   color: 'text-slate-400',    gradient: 'from-slate-500 to-gray-500' },
  design:     { label: '设计',   color: 'text-rose-400',     gradient: 'from-rose-500 to-pink-500' },
  finance:    { label: '财务',   color: 'text-yellow-400',   gradient: 'from-yellow-500 to-amber-500' },
  hr:         { label: '人力',   color: 'text-cyan-400',     gradient: 'from-cyan-500 to-teal-500' },
  product:    { label: '产品',   color: 'text-teal-400',     gradient: 'from-teal-500 to-emerald-500' },
  ops:        { label: '运营',   color: 'text-green-400',    gradient: 'from-green-500 to-emerald-500' },
  marketing:  { label: '营销',   color: 'text-red-400',      gradient: 'from-red-500 to-rose-500' },
  management: { label: '管理',   color: 'text-slate-300',    gradient: 'from-slate-500 to-zinc-500' },
  writing:    { label: '写作',   color: 'text-amber-400',    gradient: 'from-amber-500 to-orange-500' },
  cyberteam:  { label: 'CyberTeam', color: 'text-violet-400', gradient: 'from-violet-500 to-purple-500' },
  'third-party':       { label: '第三方',   color: 'text-gray-400',   gradient: 'from-gray-500 to-slate-500' },
  'third-party/baoyu': { label: 'Baoyu',    color: 'text-orange-400', gradient: 'from-orange-500 to-amber-500' },
  'third-party/pua':   { label: 'PUA',      color: 'text-red-400',    gradient: 'from-red-500 to-rose-500' },
};

const DIFFICULTY_STYLES: Record<string, { label: string; gradient: string }> = {
  high:   { label: '高难', gradient: 'from-rose-500 to-red-500' },
  medium: { label: '中等', gradient: 'from-amber-500 to-yellow-500' },
  low:    { label: '简单', gradient: 'from-emerald-500 to-green-500' },
};

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [show, setShow] = useState(false);
  const [detail, setDetail] = useState<Skill | null>(null);
  const [edit, setEdit] = useState<Skill | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{msg: string; type: 'success'|'error'} | null>(null);
  const [filterCat, setFilterCat] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<'basic' | 'content' | 'advanced'>('basic');
  const [form, setForm] = useState({
    name: '', category: 'growth', description: '', triggerConditions: '', usageGuide: '',
    difficulty: 'medium', version: 'v1.0.0', author: 'CyberTeam',
    references: '', successMetrics: '', assess: '',
  });

  const showToast = (msg: string, type: 'success'|'error') => {
    setToast({msg, type});
    setTimeout(() => setToast(null), 3000);
  };

  const fetchSkills = async () => {
    try {
      setLoading(true);
      const data: SkillsResponse | Skill[] = await api('/skills');
      const skillsList = Array.isArray(data) ? data : (data.skills || []);
      setSkills(skillsList.map((s: Skill) => ({
        ...s, id: s.skill_id || s.id,
        triggerConditions: s.triggerConditions || s.trigger || '',
      })));
    } catch (e) { showToast('加载技能失败', 'error'); } finally { setLoading(false); }
  };

  useEffect(() => { fetchSkills(); }, []);

  const handleSave = async () => {
    if (!form.name.trim()) { showToast('请输入技能名称', 'error'); return; }
    try {
      if (edit) {
        const skillId = edit.id || edit.skill_id;
        await api(`/skills/${edit.category}/${skillId}`, {
          method: 'PUT',
          body: { name: form.name, description: form.description, trigger: form.triggerConditions,
            usageGuide: form.usageGuide, difficulty: form.difficulty, version: form.version, author: form.author, tags: [edit.category] }
        });
        showToast('技能更新成功', 'success');
      } else {
        await api('/skills', {
          method: 'POST',
          body: { name: form.name, category: form.category, description: form.description, trigger: form.triggerConditions,
            usageGuide: form.usageGuide, difficulty: form.difficulty, version: form.version, author: form.author }
        });
        showToast('技能创建成功', 'success');
      }
      setShow(false); setEdit(null);
      setForm({ name: '', category: 'growth', description: '', triggerConditions: '', usageGuide: '', difficulty: 'medium', version: 'v1.0.0', author: 'CyberTeam', references: '', successMetrics: '', assess: '' });
      fetchSkills();
    } catch (e) { showToast('保存失败', 'error'); }
  };

  const handleDelete = async (skill: Skill) => {
    if (!confirm('确定删除此技能？')) return;
    try {
      await api(`/skills/${skill.category}/${skill.id || skill.skill_id}`, { method: 'DELETE' });
      showToast('删除成功', 'success'); fetchSkills();
    } catch (e) { showToast('删除失败', 'error'); }
  };

  const openEdit = (skill: Skill) => {
    setActiveTab('basic'); setEdit(skill);
    const refs = skill.references?.map((r: any) => `${r.name}, ${r.path || ''}, ${r.type || 'doc'}`).join('\n') || '';
    const metrics = skill.success_metrics ? Object.entries(skill.success_metrics).map(([k, v]) => `${k}: ${v}`).join('\n') : '';
    setForm({
      name: skill.name, category: skill.category, description: skill.description || '',
      triggerConditions: skill.triggerConditions || '', usageGuide: skill.usageGuide || skill.content || '',
      difficulty: skill.difficulty || 'medium', version: skill.version || 'v1.0.0', author: skill.author || 'CyberTeam',
      references: refs, successMetrics: metrics, assess: skill.assess?.map((a: any) => a.name || a).join('\n') || '',
    });
    setShow(true);
  };

  const openAdd = () => {
    setActiveTab('basic'); setEdit(null);
    setForm({ name: '', category: 'growth', description: '', triggerConditions: '', usageGuide: '', difficulty: 'medium', version: 'v1.0.0', author: 'CyberTeam', references: '', successMetrics: '', assess: '' });
    setShow(true);
  };

  const grouped: Record<string, Skill[]> = {};
  skills.forEach((s) => { const cat = s.category || 'other'; if (!grouped[cat]) grouped[cat] = []; grouped[cat].push(s); });
  const filtered = filterCat === 'all' ? grouped : { [filterCat]: grouped[filterCat] || [] };

  return (
    <div className="p-8 min-h-full relative">
      {toast && (
        <div className={`fixed top-6 right-6 px-5 py-3 rounded-2xl z-50 backdrop-blur-xl border-l-[3px] animate-slide-in ${
          toast.type === 'success' ? 'bg-emerald-500/10 border-l-emerald-400 text-emerald-300' : 'bg-rose-500/10 border-l-rose-400 text-rose-300'
        }`}>{toast.msg}</div>
      )}

      {loading && (
        <div className="absolute inset-0 bg-[#06080f]/80 backdrop-blur-sm flex items-center justify-center z-40">
          <div className="text-slate-400 text-sm animate-pulse">加载中...</div>
        </div>
      )}

      {/* 详情弹窗 */}
      {detail && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass p-8 w-full max-w-2xl max-h-[90vh] overflow-auto animate-slide-up shadow-glass">
            <div className="flex justify-between items-start mb-5">
              <div>
                <h2 className="text-xl font-bold text-white">{detail.name}</h2>
                {detail.source_path && <p className="text-slate-600 text-xs mt-1">{detail.source_path}</p>}
              </div>
              <button onClick={() => setDetail(null)} className="text-slate-500 hover:text-white transition-colors p-1">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>

            <div className="flex flex-wrap gap-2 mb-5">
              <span className={`text-xs px-3 py-1 rounded-lg bg-gradient-to-r ${CATEGORY_STYLES[detail.category]?.gradient || 'from-slate-500 to-slate-600'} text-white font-medium`}>
                {CATEGORY_STYLES[detail.category]?.label || detail.category}
              </span>
              {detail.difficulty && (
                <span className={`text-xs px-3 py-1 rounded-lg bg-gradient-to-r ${DIFFICULTY_STYLES[detail.difficulty]?.gradient || 'from-slate-500 to-slate-600'} text-white`}>
                  {DIFFICULTY_STYLES[detail.difficulty]?.label || detail.difficulty}
                </span>
              )}
              {detail.version && <span className="tag">{detail.version}</span>}
              {detail.author && <span className="tag">{detail.author}</span>}
            </div>

            <p className="text-slate-300 mb-5 leading-relaxed">{detail.description || '暂无描述'}</p>

            {detail.tags && detail.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-5">
                {detail.tags.map((tag, i) => <span key={i} className="tag">{tag}</span>)}
              </div>
            )}

            {(detail.triggerConditions || detail.trigger) && (
              <div className="mb-5 p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2">触发条件</h4>
                <p className="text-slate-300 text-sm">{detail.triggerConditions || detail.trigger}</p>
              </div>
            )}

            {detail.success_metrics && Object.keys(detail.success_metrics).length > 0 && (
              <div className="mb-5 p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-3">成功指标</h4>
                <div className="space-y-2">
                  {Object.entries(detail.success_metrics).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-slate-400">{key}</span>
                      <span className="text-emerald-400 font-medium">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {detail.content && (
              <div className="mb-5 p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2">完整内容</h4>
                <div className="max-h-64 overflow-auto">
                  <pre className="text-slate-300 text-sm whitespace-pre-wrap font-mono">{detail.content}</pre>
                </div>
              </div>
            )}

            {!detail.content && detail.usageGuide && (
              <div className="mb-5 p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
                <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2">使用指南</h4>
                <p className="text-slate-300 text-sm">{detail.usageGuide}</p>
              </div>
            )}

            {detail.references && detail.references.length > 0 && (
              <div className="mb-5">
                <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2">参考文档</h4>
                <div className="grid grid-cols-2 gap-2">
                  {detail.references.map((ref, i) => (
                    <div key={i} className="p-3 bg-white/[0.02] rounded-xl border border-white/[0.05] text-sm text-slate-300">
                      {ref.name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-4 mt-6 pt-4 border-t border-white/[0.06]">
              <button onClick={() => { setDetail(null); openEdit(detail); }} className="btn-aurora flex-1 py-2.5">编辑</button>
              <button onClick={() => setDetail(null)} className="btn-ghost flex-1 py-2.5">关闭</button>
            </div>
          </div>
        </div>
      )}

      {/* 头部 */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">技能管理</h1>
          <p className="text-slate-500 text-sm mt-1">查看和配置所有 Agent 技能</p>
        </div>
        <button onClick={openAdd} className="btn-aurora flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加技能
        </button>
      </div>

      {/* 提示 */}
      <div className="bg-indigo-500/[0.06] border border-indigo-500/15 rounded-2xl p-4 mb-8 animate-fade-in">
        <p className="text-indigo-300/80 text-sm">
          技能是 Agent 的核心能力。每个 Agent 可以配置多个技能。点击技能卡片查看详情。
        </p>
      </div>

      {/* 分类筛选 */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button onClick={() => setFilterCat('all')}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            filterCat === 'all' ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-glow-sm' : 'btn-ghost'
          }`}>
          全部 ({skills.length})
        </button>
        {Object.entries(CATEGORY_STYLES).map(([k, v]) => (
          <button key={k} onClick={() => setFilterCat(k)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              filterCat === k ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white' : 'btn-ghost'
            }`}>
            {v.label} ({grouped[k]?.length || 0})
          </button>
        ))}
      </div>

      {/* 技能分组 */}
      {Object.entries(filtered).map(([cat, catSkills]) => {
        const cs = CATEGORY_STYLES[cat] || { label: cat, gradient: 'from-slate-500 to-slate-600' };
        return (
          <div key={cat} className="mb-10 animate-fade-in">
            <h2 className="text-base font-semibold text-slate-300 mb-4 flex items-center gap-3">
              <span className={`w-2 h-2 rounded-full bg-gradient-to-r ${cs.gradient}`} />
              {cs.label} ({catSkills.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {catSkills.map((s) => {
                const diffStyle = DIFFICULTY_STYLES[s.difficulty || 'medium'] || DIFFICULTY_STYLES.medium;
                return (
                  <div key={s.id} className="glass aurora-glow p-5 cursor-pointer animate-slide-up"
                    onClick={() => setDetail(s)}>
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-white font-semibold">{s.name}</h3>
                      <div className="flex flex-col items-end gap-1.5">
                        <span className={`text-[10px] px-2 py-0.5 rounded-md bg-gradient-to-r ${cs.gradient} text-white`}>
                          {cs.label}
                        </span>
                        {s.difficulty && (
                          <span className={`text-[10px] px-2 py-0.5 rounded-md bg-gradient-to-r ${diffStyle.gradient} text-white`}>
                            {diffStyle.label}
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-slate-400 text-sm mb-3 line-clamp-2 leading-relaxed">{s.description || '暂无描述'}</p>
                    {(s.triggerConditions || s.trigger) && (
                      <p className="text-slate-600 text-xs mb-2 line-clamp-1">{s.triggerConditions || s.trigger}</p>
                    )}
                    {s.tags && s.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {s.tags.slice(0, 3).map((tag, i) => <span key={i} className="tag">{tag}</span>)}
                        {s.tags.length > 3 && <span className="text-xs text-slate-600">+{s.tags.length - 3}</span>}
                      </div>
                    )}
                    <div className="flex gap-3 pt-3 border-t border-white/[0.06]" onClick={e => e.stopPropagation()}>
                      <button onClick={() => openEdit(s)} className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">编辑</button>
                      <button onClick={() => handleDelete(s)} className="text-sm text-rose-400/60 hover:text-rose-400 transition-colors">删除</button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {Object.keys(filtered).length === 0 && !loading && (
        <div className="text-center py-20 animate-fade-in">
          <p className="text-slate-500 mb-4">暂无技能</p>
          <button onClick={openAdd} className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">点击添加第一个技能</button>
        </div>
      )}

      {/* 编辑弹窗 */}
      {show && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-start justify-center z-50 overflow-auto py-8">
          <div className="glass p-8 w-full max-w-4xl mb-8 animate-slide-up shadow-glass">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">{edit ? '编辑技能' : '添加新技能'}</h2>
              <button onClick={() => setShow(false)} className="text-slate-500 hover:text-white transition-colors">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 mb-6 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06]">
              {(['basic', 'content', 'advanced'] as const).map(tab => (
                <button key={tab} onClick={() => setActiveTab(tab)}
                  className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    activeTab === tab ? 'bg-white/[0.08] text-white' : 'text-slate-500 hover:text-slate-300'
                  }`}>
                  {tab === 'basic' ? '基本信息' : tab === 'content' ? '完整内容' : '高级设置'}
                </button>
              ))}
            </div>

            <div className="space-y-5">
              {/* Basic */}
              <div className={`space-y-4 ${activeTab !== 'basic' ? 'hidden' : ''}`}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">技能名称 <span className="text-indigo-400">*</span></label>
                    <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                      className="input-glass text-lg py-3" placeholder="如：增长黑客" />
                  </div>
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">技能分类</label>
                    <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}
                      className="input-glass py-3">
                      {Object.entries(CATEGORY_STYLES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-slate-400 text-sm mb-2">技能描述</label>
                  <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                    rows={3} className="input-glass resize-none" placeholder="简洁描述这个技能的核心能力和价值" />
                </div>
                <div>
                  <label className="block text-slate-400 text-sm mb-2">触发条件</label>
                  <input value={form.triggerConditions} onChange={(e) => setForm({ ...form, triggerConditions: e.target.value })}
                    className="input-glass" placeholder="如：用户请求增长策略时" />
                </div>
                <div>
                  <label className="block text-slate-400 text-sm mb-2">使用指南</label>
                  <textarea value={form.usageGuide} onChange={(e) => setForm({ ...form, usageGuide: e.target.value })}
                    rows={10} className="input-glass resize-none font-mono text-sm" placeholder="详细说明如何使用这个技能..." />
                </div>
              </div>

              {/* Content */}
              <div className={`space-y-4 ${activeTab !== 'content' ? 'hidden' : ''}`}>
                <div className="p-4 bg-white/[0.02] rounded-2xl border border-white/[0.06]">
                  <label className="text-slate-300 text-sm font-medium mb-3 block">完整 SKILL.md 内容</label>
                  <textarea value={form.usageGuide || ''} onChange={(e) => setForm({ ...form, usageGuide: e.target.value })}
                    rows={25} className="input-glass resize-none font-mono text-sm leading-relaxed"
                    placeholder="# 技能名称\n\n## 核心职责\n描述技能的核心职责和工作范围\n\n## 工作流程\n1. 步骤一：...\n2. 步骤二：..." />
                </div>
              </div>

              {/* Advanced */}
              <div className={`space-y-4 ${activeTab !== 'advanced' ? 'hidden' : ''}`}>
                <div className="p-4 bg-white/[0.02] rounded-2xl border border-white/[0.06]">
                  <h4 className="text-slate-300 text-sm font-medium mb-4">元数据设置</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-slate-500 text-xs mb-1">难度</label>
                      <select value={form.difficulty || 'medium'} onChange={(e) => setForm({ ...form, difficulty: e.target.value })} className="input-glass">
                        <option value="low">简单</option><option value="medium">中等</option><option value="high">困难</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-slate-500 text-xs mb-1">版本</label>
                      <input value={form.version || 'v1.0.0'} onChange={(e) => setForm({ ...form, version: e.target.value })} className="input-glass" />
                    </div>
                    <div>
                      <label className="block text-slate-500 text-xs mb-1">作者</label>
                      <input value={form.author || 'CyberTeam'} onChange={(e) => setForm({ ...form, author: e.target.value })} className="input-glass" />
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-white/[0.02] rounded-2xl border border-white/[0.06]">
                  <h4 className="text-slate-300 text-sm font-medium mb-3">参考文档</h4>
                  <textarea value={form.references || ''} onChange={(e) => setForm({ ...form, references: e.target.value })}
                    rows={4} className="input-glass resize-none font-mono text-sm" placeholder="每行一个：名称, 路径, 类型" />
                </div>
                <div className="p-4 bg-white/[0.02] rounded-2xl border border-white/[0.06]">
                  <h4 className="text-slate-300 text-sm font-medium mb-3">成功指标</h4>
                  <textarea value={form.successMetrics || ''} onChange={(e) => setForm({ ...form, successMetrics: e.target.value })}
                    rows={4} className="input-glass resize-none font-mono text-sm" placeholder="每行一个：指标名称: 期望值" />
                </div>
                <div className="p-4 bg-white/[0.02] rounded-2xl border border-white/[0.06]">
                  <h4 className="text-slate-300 text-sm font-medium mb-3">评估清单</h4>
                  <textarea value={form.assess || ''} onChange={(e) => setForm({ ...form, assess: e.target.value })}
                    rows={4} className="input-glass resize-none font-mono text-sm" placeholder="每行一个评估项" />
                </div>
              </div>
            </div>

            <div className="flex gap-4 mt-8 pt-6 border-t border-white/[0.06]">
              <button onClick={handleSave} className="btn-aurora flex-1 py-3 text-base">{edit ? '保存修改' : '创建技能'}</button>
              <button onClick={() => setShow(false)} className="btn-ghost flex-1 py-3">取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
