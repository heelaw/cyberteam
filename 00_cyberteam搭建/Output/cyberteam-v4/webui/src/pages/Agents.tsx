import { useEffect, useState } from 'react';

const API = '/api';

interface Skill {
  id?: string;
  skill_id?: string;
  name: string;
  category: string;
  description: string;
  trigger?: string;
  triggerConditions?: string;
}
interface Agent {
  id: string; name: string; role: string; departmentId: string; level: number | string;
  skills: Skill[]; upstreamAgents: string[]; downstreamAgents: string[];
  knowledge: string; outputStyle: string;
}
interface Dept { id: string; name: string; parentId: string | null; }

async function api(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    ...(opts.body ? { body: JSON.stringify(opts.body) } : {}),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// 级别颜色映射 - 极光渐变色条
const levelStyles: Record<number, { gradient: string; text: string; label: string }> = {
  1: { gradient: 'from-indigo-500 to-blue-500', text: 'text-indigo-300', label: 'CEO' },
  2: { gradient: 'from-purple-500 to-indigo-500', text: 'text-purple-300', label: '总监' },
  3: { gradient: 'from-pink-500 to-purple-500', text: 'text-pink-300', label: '专家' },
  4: { gradient: 'from-orange-500 to-amber-500', text: 'text-amber-300', label: '专员' },
};

// SVG 图标组件
const IconPlus = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
    <path d="M8 3v10M3 8h10" />
  </svg>
);

const IconEdit = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11.5 1.5a2.121 2.121 0 013 3L5 14l-4 1 1-4 9.5-9.5z" />
  </svg>
);

const IconTrash = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 4h12M5.333 4V2.667a1.333 1.333 0 011.334-1.334h2.666a1.333 1.333 0 011.334 1.334V4m2 0v9.333a1.333 1.333 0 01-1.334 1.334H4.667a1.333 1.333 0 01-1.334-1.334V4h9.334z" />
  </svg>
);

const IconCheck = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 8.5l3.5 3.5L13 4" />
  </svg>
);

const IconAlert = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
    <circle cx="8" cy="8" r="6.5" />
    <path d="M8 5v3.5M8 10.5v.5" />
  </svg>
);

const IconAgents = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="10" cy="6" r="3.5" />
    <path d="M3 18c0-3.314 3.134-6 7-6s7 2.686 7 6" />
  </svg>
);

const IconArrowUp = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9V3M3 5l3-3 3 3" />
  </svg>
);

const IconArrowDown = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 3v6M3 7l3 3 3-3" />
  </svg>
);

const IconEmpty = () => (
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
    <rect x="8" y="4" width="32" height="40" rx="4" />
    <path d="M16 14h16M16 20h12M16 26h16M16 32h8" />
    <circle cx="36" cy="36" r="8" fill="#06080f" />
    <path d="M33 36h6M36 33v6" stroke="currentColor" strokeWidth="1.5" />
  </svg>
);

const IconSparkle = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
    <path d="M8 0l1.5 5.5L15 7l-5.5 1.5L8 14l-1.5-5.5L1 7l5.5-1.5z" opacity="0.6" />
  </svg>
);

export default function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [depts, setDepts] = useState<Dept[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [show, setShow] = useState(false);
  const [edit, setEdit] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{msg: string; type: 'success'|'error'} | null>(null);
  const [form, setForm] = useState({
    name: '', role: '', departmentId: '', level: 3,
    selectedSkills: [] as string[],
    upstreamAgents: [] as string[],
    downstreamAgents: [] as string[],
    knowledge: '', outputStyle: '',
  });

  const showToast = (msg: string, type: 'success'|'error') => {
    setToast({msg, type});
    setTimeout(() => setToast(null), 3000);
  };

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [a, d, sResp] = await Promise.all([
        api('/agents'),
        api('/departments'),
        api('/skills'),
      ]);
      const agentList = (a.agents || a || []).map((ag: any) => ({
        ...ag,
        id: ag.agent_id || ag.id,
        departmentId: ag.department_id || ag.departmentId,
        level: typeof ag.level === 'string' ? parseInt(ag.level.replace('L', '')) || 3 : (ag.level || 3),
      }));
      setAgents(agentList);
      const deptList = (d.departments || d || []).map((dept: any) => ({
        ...dept,
        id: dept.department_id || dept.id,
      }));
      setDepts(deptList);
      const skillsList = Array.isArray(sResp) ? sResp : (sResp.skills || []);
      const mappedSkills = skillsList.map((sk: Skill) => ({
        ...sk,
        id: sk.skill_id || sk.id,
        triggerConditions: sk.triggerConditions || sk.trigger || '',
      }));
      setSkills(mappedSkills);
    } catch (e) {
      showToast('加载数据失败', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleSave = async () => {
    if (!form.name.trim()) { showToast('请输入名称', 'error'); return; }
    if (!form.departmentId) { showToast('请选择部门', 'error'); return; }
    try {
      const id = edit?.id || `agent-${Date.now()}`;
      const payload = {
        id, name: form.name, role: form.role, departmentId: form.departmentId,
        level: typeof form.level === 'string' ? parseInt(form.level) || 3 : form.level,
        skills: form.selectedSkills,
        upstreamAgents: form.upstreamAgents, downstreamAgents: form.downstreamAgents,
        knowledge: form.knowledge, outputStyle: form.outputStyle,
      };
      if (edit) {
        await api(`/agents/${id}`, { method: 'PUT', body: payload });
        showToast('Agent 更新成功', 'success');
      } else {
        await api('/agents', { method: 'POST', body: payload });
        showToast('Agent 创建成功', 'success');
      }
      setShow(false);
      setEdit(null);
      fetchAll();
    } catch (e) {
      showToast('保存失败：' + String(e), 'error');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除此 Agent？删除后无法恢复！')) return;
    try {
      await api(`/agents/${id}`, { method: 'DELETE' });
      showToast('删除成功', 'success');
      fetchAll();
    } catch (e) {
      showToast('删除失败', 'error');
    }
  };

  const openEdit = (a: Agent) => {
    setEdit(a);
    const levelValue = typeof a.level === 'string' ? parseInt(a.level.replace('L', '')) || 3 : (a.level || 3);
    setForm({
      name: a.name, role: a.role || '', departmentId: a.departmentId || '',
      level: levelValue,
      selectedSkills: (a.skills || []).map((s: any) => s.id || s),
      upstreamAgents: a.upstreamAgents || [],
      downstreamAgents: a.downstreamAgents || [],
      knowledge: a.knowledge || '', outputStyle: a.outputStyle || '',
    });
    setShow(true);
  };

  const openAdd = () => {
    setEdit(null);
    setForm({ name: '', role: '', departmentId: '', level: 3, selectedSkills: [], upstreamAgents: [], downstreamAgents: [], knowledge: '', outputStyle: '' });
    setShow(true);
  };

  const toggleSkill = (skillId: string) => {
    const sel = form.selectedSkills.includes(skillId)
      ? form.selectedSkills.filter((s) => s !== skillId)
      : [...form.selectedSkills, skillId];
    setForm({ ...form, selectedSkills: sel });
  };

  const toggleUpstream = (agentId: string) => {
    const sel = form.upstreamAgents.includes(agentId)
      ? form.upstreamAgents.filter(id => id !== agentId)
      : [...form.upstreamAgents, agentId];
    setForm({ ...form, upstreamAgents: sel });
  };

  const toggleDownstream = (agentId: string) => {
    const sel = form.downstreamAgents.includes(agentId)
      ? form.downstreamAgents.filter(id => id !== agentId)
      : [...form.downstreamAgents, agentId];
    setForm({ ...form, downstreamAgents: sel });
  };

  const getDeptName = (id: string) => depts.find((d) => d.id === id)?.name || '未知部门';
  const getAgentName = (id: string) => agents.find((a) => a.id === id)?.name || id;
  const getSkillName = (id: string) => skills.find((s) => s.id === id)?.name || id;

  // 按部门分组
  const grouped: Record<string, Agent[]> = {};
  agents.forEach((a) => {
    const key = a.departmentId || 'other';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(a);
  });

  return (
    <div className="p-6 lg:p-8 min-h-full relative overflow-auto">
      {/* 星空背景光效 */}
      <div className="fixed inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(168,85,247,0.06) 0%, transparent 50%), radial-gradient(ellipse at 60% 80%, rgba(236,72,153,0.04) 0%, transparent 50%)' }} />

      {/* Toast 提示 - 极光风格 */}
      {toast && (
        <div className={`fixed top-5 right-5 px-5 py-3 rounded-xl z-50 backdrop-blur-xl border animate-fade-in flex items-center gap-2.5 ${
          toast.type === 'success'
            ? 'bg-white/[0.06] border-white/[0.1] text-emerald-300'
            : 'bg-white/[0.06] border-white/[0.1] text-amber-300'
        }`}>
          {toast.type === 'success' ? <IconCheck /> : <IconAlert />}
          <span className="text-sm text-slate-200">{toast.msg}</span>
        </div>
      )}

      {/* 加载状态 - 极光脉动 */}
      {loading && (
        <div className="absolute inset-0 bg-[#06080f]/90 backdrop-blur-sm flex items-center justify-center z-40">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin" />
            <span className="text-slate-500 text-sm">加载中...</span>
          </div>
        </div>
      )}

      {/* 页面标题区 */}
      <div className="relative z-10 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1.5">
            <div className="p-2 rounded-xl bg-aurora-subtle">
              <span className="text-indigo-400"><IconAgents /></span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-bold text-white tracking-tight">Agent 管理</h1>
          </div>
          <p className="text-slate-500 text-sm ml-[52px]">管理所有 Agent 角色、技能配置和上下游协作关系</p>
        </div>
        <button
          onClick={openAdd}
          className="btn-aurora flex items-center gap-2 shrink-0"
        >
          <IconPlus /> 添加 Agent
        </button>
      </div>

      {/* 使用说明 */}
      <div className="relative z-10 glass-accent rounded-xl p-4 mb-8 animate-fade-in">
        <p className="text-slate-400 text-sm leading-relaxed">
          点击 Agent 卡片进入编辑模式。每个 Agent 可配置多项技能，并通过上下游关系定义组织架构中的汇报路线。
        </p>
      </div>

      {/* 部门分组 */}
      <div className="relative z-10 space-y-10">
        {Object.entries(grouped).map(([deptId, deptAgents]) => (
          <div key={deptId} className="animate-fade-in">
            {/* 部门标题 - 左侧极光渐变色条 */}
            <div className="flex items-center gap-3 mb-5">
              <div className="w-1 h-6 rounded-full bg-aurora-gradient" />
              <h2 className="text-sm font-semibold text-slate-300 tracking-wide uppercase">
                {getDeptName(deptId)}
              </h2>
              <span className="tag">{deptAgents.length} 个 Agent</span>
            </div>

            {/* Agent 卡片网格 */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {deptAgents.map((a, idx) => {
                const levelNum = typeof a.level === 'string' ? parseInt(a.level.replace('L', '')) || 3 : (a.level || 3);
                const lvStyle = levelStyles[levelNum] || levelStyles[3];
                const levelLabel = typeof a.level === 'string' ? a.level : `L${a.level}`;

                return (
                  <div
                    key={a.id}
                    className="glass aurora-glow group cursor-pointer animate-slide-up"
                    style={{ animationDelay: `${idx * 60}ms`, animationFillMode: 'both' }}
                    onClick={() => openEdit(a)}
                  >
                    <div className="p-5">
                      {/* 头部：名称 + 级别 */}
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-white font-semibold text-base truncate">{a.name}</h3>
                          <p className="text-xs text-slate-500 mt-1 truncate">{a.role || '未设置角色'}</p>
                        </div>
                        <span className={`shrink-0 ml-3 text-xs font-medium px-2.5 py-1 rounded-md bg-gradient-to-r ${lvStyle.gradient} text-white/90`}>
                          {levelLabel}
                        </span>
                      </div>

                      {/* 已配置的 Skills */}
                      <div className="mb-4">
                        <p className="text-[11px] text-slate-600 uppercase tracking-wider mb-2 font-medium">已配置技能</p>
                        <div className="flex flex-wrap gap-1.5">
                          {(a.skills || []).slice(0, 4).map((s: any) => (
                            <span key={s.id} className="tag">
                              <IconSparkle /> {s.name || s.id}
                            </span>
                          ))}
                          {(a.skills?.length || 0) > 4 && (
                            <span className="tag text-slate-600">
                              +{a.skills.length - 4}
                            </span>
                          )}
                          {(!a.skills || a.skills.length === 0) && (
                            <span className="text-xs text-slate-600 italic">暂无技能</span>
                          )}
                        </div>
                      </div>

                      {/* 上下游关系 */}
                      {(a.upstreamAgents?.length > 0 || a.downstreamAgents?.length > 0) && (
                        <div className="mb-4 space-y-1.5">
                          {a.upstreamAgents?.length > 0 && (
                            <div className="flex items-center gap-1.5 text-xs text-slate-500">
                              <span className="text-indigo-400/70"><IconArrowUp /></span>
                              <span>上游: {a.upstreamAgents.slice(0, 2).map(id => getAgentName(id)).join(', ')}</span>
                            </div>
                          )}
                          {a.downstreamAgents?.length > 0 && (
                            <div className="flex items-center gap-1.5 text-xs text-slate-500">
                              <span className="text-pink-400/70"><IconArrowDown /></span>
                              <span>下游: {a.downstreamAgents.slice(0, 2).map(id => getAgentName(id)).join(', ')}</span>
                            </div>
                          )}
                        </div>
                      )}

                      {/* 底部操作栏 */}
                      <div className="flex gap-3 pt-3 border-t border-white/[0.06]" onClick={e => e.stopPropagation()}>
                        <button
                          onClick={() => openEdit(a)}
                          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-indigo-400 transition-colors"
                        >
                          <IconEdit /> 编辑
                        </button>
                        <button
                          onClick={() => handleDelete(a.id)}
                          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-red-400 transition-colors"
                        >
                          <IconTrash /> 删除
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* 空状态 - 柔和极光风格 */}
      {agents.length === 0 && !loading && (
        <div className="relative z-10 flex flex-col items-center justify-center py-24 animate-fade-in">
          <div className="text-slate-600 mb-5">
            <IconEmpty />
          </div>
          <p className="text-slate-500 text-sm mb-2">暂无 Agent 数据</p>
          <p className="text-slate-600 text-xs mb-6">创建第一个 Agent 来开始组建你的 AI 团队</p>
          <button
            onClick={openAdd}
            className="btn-aurora flex items-center gap-2"
          >
            <IconPlus /> 创建第一个 Agent
          </button>
        </div>
      )}

      {/* 弹窗表单 - 毛玻璃背景 */}
      {show && (
        <div className="fixed inset-0 bg-[#06080f]/80 backdrop-blur-md flex items-center justify-center z-50 overflow-auto animate-fade-in">
          <div className="glass w-full max-w-2xl mx-4 max-h-[90vh] overflow-auto shadow-glass animate-slide-up">
            <div className="p-6 lg:p-8">
              {/* 弹窗标题 */}
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-xl font-semibold text-white">
                  {edit ? '编辑 Agent' : '添加新 Agent'}
                </h2>
                <button
                  onClick={() => setShow(false)}
                  className="p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/[0.05] transition-colors"
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                    <path d="M4 4l8 8M12 4l-8 8" />
                  </svg>
                </button>
              </div>

              <div className="space-y-6">
                {/* 名称和角色 */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">
                      名称 <span className="text-indigo-400/60">*</span>
                    </label>
                    <input
                      value={form.name}
                      onChange={(e) => setForm({ ...form, name: e.target.value })}
                      className="input-glass"
                      placeholder="如：张三"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">
                      角色
                    </label>
                    <input
                      value={form.role}
                      onChange={(e) => setForm({ ...form, role: e.target.value })}
                      className="input-glass"
                      placeholder="如：增长专家"
                    />
                  </div>
                </div>

                {/* 部门和级别 */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">
                      所属部门 <span className="text-indigo-400/60">*</span>
                    </label>
                    <select
                      value={form.departmentId}
                      onChange={(e) => setForm({ ...form, departmentId: e.target.value })}
                      className="input-glass"
                    >
                      <option value="">选择部门</option>
                      {depts.map((d) => (
                        <option key={d.id} value={d.id}>{d.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 text-sm mb-2">
                      级别
                    </label>
                    <select
                      value={form.level}
                      onChange={(e) => setForm({ ...form, level: parseInt(e.target.value) })}
                      className="input-glass"
                    >
                      <option value="1">L1 - CEO</option>
                      <option value="2">L2 - 总监</option>
                      <option value="3">L3 - 专家</option>
                      <option value="4">L4 - 专员</option>
                    </select>
                  </div>
                </div>

                {/* 技能选择 */}
                <div>
                  <label className="block text-slate-400 text-sm mb-2">
                    配置技能
                  </label>
                  <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto p-3 bg-white/[0.02] rounded-xl border border-white/[0.06]">
                    {skills.map((s) => (
                      <button
                        key={s.id}
                        onClick={() => toggleSkill(s.id)}
                        className={`tag transition-all duration-200 ${
                          form.selectedSkills.includes(s.id)
                            ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300 !border-indigo-500/30'
                            : 'hover:bg-white/[0.06] hover:border-white/[0.1]'
                        }`}
                      >
                        {s.name}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-slate-600 mt-2">
                    已选 <span className="text-indigo-400">{form.selectedSkills.length}</span> 个技能
                  </p>
                </div>

                {/* 上游 Agent */}
                <div>
                  <label className="flex items-center gap-1.5 text-slate-400 text-sm mb-2">
                    <span className="text-indigo-400/70"><IconArrowUp /></span>
                    上游 Agent（向谁汇报）
                  </label>
                  <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-3 bg-white/[0.02] rounded-xl border border-white/[0.06]">
                    {agents.filter(a => a.id !== edit?.id).map((a) => (
                      <button
                        key={a.id}
                        onClick={() => toggleUpstream(a.id)}
                        className={`tag transition-all duration-200 ${
                          form.upstreamAgents.includes(a.id)
                            ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300 !border-indigo-500/30'
                            : 'hover:bg-white/[0.06] hover:border-white/[0.1]'
                        }`}
                      >
                        {a.name}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-slate-600 mt-2">
                    已选 <span className="text-indigo-400">{form.upstreamAgents.length}</span> 个上游
                  </p>
                </div>

                {/* 下游 Agent */}
                <div>
                  <label className="flex items-center gap-1.5 text-slate-400 text-sm mb-2">
                    <span className="text-pink-400/70"><IconArrowDown /></span>
                    下游 Agent（谁向你汇报）
                  </label>
                  <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-3 bg-white/[0.02] rounded-xl border border-white/[0.06]">
                    {agents.filter(a => a.id !== edit?.id).map((a) => (
                      <button
                        key={a.id}
                        onClick={() => toggleDownstream(a.id)}
                        className={`tag transition-all duration-200 ${
                          form.downstreamAgents.includes(a.id)
                            ? 'bg-pink-500/20 border-pink-500/40 text-pink-300 !border-pink-500/30'
                            : 'hover:bg-white/[0.06] hover:border-white/[0.1]'
                        }`}
                      >
                        {a.name}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-slate-600 mt-2">
                    已选 <span className="text-pink-400">{form.downstreamAgents.length}</span> 个下游
                  </p>
                </div>

                {/* 知识领域 */}
                <div>
                  <label className="block text-slate-400 text-sm mb-2">
                    知识领域
                  </label>
                  <input
                    value={form.knowledge}
                    onChange={(e) => setForm({ ...form, knowledge: e.target.value })}
                    className="input-glass"
                    placeholder="如：电商、金融、教育（用逗号分隔）"
                  />
                </div>

                {/* 输出风格 */}
                <div>
                  <label className="block text-slate-400 text-sm mb-2">
                    输出风格
                  </label>
                  <input
                    value={form.outputStyle}
                    onChange={(e) => setForm({ ...form, outputStyle: e.target.value })}
                    className="input-glass"
                    placeholder="如：专业详细、简洁有力、幽默风趣"
                  />
                </div>
              </div>

              {/* 弹窗底部按钮 */}
              <div className="flex gap-4 mt-8">
                <button
                  onClick={handleSave}
                  className="btn-aurora flex-1 !py-3 text-center"
                >
                  {edit ? '保存修改' : '创建 Agent'}
                </button>
                <button
                  onClick={() => setShow(false)}
                  className="btn-ghost flex-1 !py-3 text-center"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
