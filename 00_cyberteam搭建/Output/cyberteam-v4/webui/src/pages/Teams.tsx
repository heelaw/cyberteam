import { useEffect, useState } from 'react';

const API = '/api';

interface Team {
  id: string; name: string; description: string;
  agentIds: string[]; coordinationMode: string; reportingCycle: string;
}
interface Agent { id: string; name: string; role: string; departmentId: string; }

async function api(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    ...(opts.body ? { body: JSON.stringify(opts.body) } : {}),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

const COORDINATION_LABELS: Record<string, { label: string; color: string }> = {
  sequential: { label: '顺序协作', color: 'from-blue-500 to-cyan-500' },
  parallel: { label: '并行协作', color: 'from-emerald-500 to-teal-500' },
  hierarchical: { label: '层级协作', color: 'from-purple-500 to-indigo-500' },
};

const CYCLE_LABELS: Record<string, string> = {
  daily: '每日汇报',
  weekly: '每周汇报',
  monthly: '每月汇报',
};

export default function Teams() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [depts, setDepts] = useState<{id: string; name: string}[]>([]);
  const [show, setShow] = useState(false);
  const [edit, setEdit] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{msg: string; type: 'success'|'error'} | null>(null);
  const [form, setForm] = useState({
    name: '', description: '', agentIds: [] as string[],
    coordinationMode: 'sequential', reportingCycle: 'daily'
  });

  const showToast = (msg: string, type: 'success'|'error') => {
    setToast({msg, type});
    setTimeout(() => setToast(null), 3000);
  };

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [t, a, d] = await Promise.all([api('/teams'), api('/agents'), api('/departments')]);
      setTeams(Array.isArray(t) ? t : (t.teams || []));
      setAgents((a.agents || a || []).map((ag: any) => ({ ...ag, id: ag.agent_id || ag.id, departmentId: ag.department_id || ag.departmentId })));
      setDepts((d.departments || d || []).map((dept: any) => ({ ...dept, id: dept.department_id || dept.id })));
    } catch (e) { showToast('加载数据失败', 'error'); } finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleSave = async () => {
    if (!form.name.trim()) { showToast('请输入团队名称', 'error'); return; }
    try {
      const id = edit?.id || `team-${Date.now()}`;
      if (edit) {
        await api(`/teams/${id}`, { method: 'PUT', body: { ...form, id } });
        showToast('团队更新成功', 'success');
      } else {
        await api('/teams', { method: 'POST', body: { ...form, id } });
        showToast('团队创建成功', 'success');
      }
      setShow(false); setEdit(null);
      setForm({ name: '', description: '', agentIds: [], coordinationMode: 'sequential', reportingCycle: 'daily' });
      fetchAll();
    } catch (e) { showToast('保存失败', 'error'); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除此团队？')) return;
    try { await api(`/teams/${id}`, { method: 'DELETE' }); showToast('删除成功', 'success'); fetchAll(); }
    catch (e) { showToast('删除失败', 'error'); }
  };

  const openEdit = (t: Team) => {
    setEdit(t);
    setForm({ name: t.name, description: t.description || '', agentIds: t.agentIds || [], coordinationMode: t.coordinationMode || 'sequential', reportingCycle: t.reportingCycle || 'daily' });
    setShow(true);
  };

  const openAdd = () => {
    setEdit(null);
    setForm({ name: '', description: '', agentIds: [], coordinationMode: 'sequential', reportingCycle: 'daily' });
    setShow(true);
  };

  const toggleAgent = (agentId: string) => {
    setForm(prev => ({
      ...prev,
      agentIds: prev.agentIds.includes(agentId) ? prev.agentIds.filter(id => id !== agentId) : [...prev.agentIds, agentId]
    }));
  };

  const getAgentName = (id: string) => agents.find(a => a.id === id)?.name || id;
  const getDeptName = (id: string) => depts.find(d => d.id === id)?.name || '未知';

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

      {/* 头部 */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">团队管理</h1>
          <p className="text-slate-500 text-sm mt-1">组建 Agent 团队，设置协作模式和汇报周期</p>
        </div>
        <button onClick={openAdd} className="btn-aurora flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          创建团队
        </button>
      </div>

      {/* 提示 */}
      <div className="bg-indigo-500/[0.06] border border-indigo-500/15 rounded-2xl p-4 mb-8 animate-fade-in">
        <p className="text-indigo-300/80 text-sm">
          团队由多个 Agent 组成，定义好协作模式和汇报周期后，可以将团队保存为模板复用。
        </p>
      </div>

      {/* 团队卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {teams.map((t, idx) => {
          const coord = COORDINATION_LABELS[t.coordinationMode] || { label: t.coordinationMode, color: 'from-slate-500 to-slate-600' };
          return (
            <div key={t.id} className="glass aurora-glow p-6 animate-slide-up" style={{ animationDelay: `${idx * 60}ms` }}>
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-white font-semibold text-lg">{t.name}</h3>
                <span className={`text-[10px] px-2.5 py-1 rounded-lg bg-gradient-to-r ${coord.color} text-white font-medium`}>
                  {coord.label}
                </span>
              </div>
              <p className="text-slate-400 text-sm mb-4 leading-relaxed">{t.description || '暂无描述'}</p>

              {/* 团队成员 */}
              <div className="mb-4">
                <p className="text-xs text-slate-500 mb-2">成员 ({t.agentIds?.length || 0})</p>
                <div className="flex flex-wrap gap-1.5">
                  {(t.agentIds || []).slice(0, 5).map(id => (
                    <span key={id} className="tag text-indigo-300 bg-indigo-500/[0.08] border-indigo-500/15">
                      {getAgentName(id)}
                    </span>
                  ))}
                  {(t.agentIds?.length || 0) > 5 && (
                    <span className="tag text-slate-500">+{t.agentIds.length - 5}</span>
                  )}
                  {(!t.agentIds || t.agentIds.length === 0) && (
                    <span className="text-xs text-slate-600">暂无成员</span>
                  )}
                </div>
              </div>

              {/* 汇报周期 */}
              <p className="text-xs text-slate-600 mb-4">{CYCLE_LABELS[t.reportingCycle] || t.reportingCycle}</p>

              <div className="flex gap-3 pt-4 border-t border-white/[0.06]">
                <button onClick={() => openEdit(t)} className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">编辑</button>
                <button onClick={() => handleDelete(t.id)} className="text-sm text-rose-400/60 hover:text-rose-400 transition-colors">删除</button>
              </div>
            </div>
          );
        })}
        {teams.length === 0 && !loading && (
          <div className="col-span-3 text-center py-20 animate-fade-in">
            <p className="text-slate-500 mb-4">暂无团队</p>
            <button onClick={openAdd} className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">
              点击创建第一个团队
            </button>
          </div>
        )}
      </div>

      {/* 弹窗 */}
      {show && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass p-8 w-full max-w-lg max-h-[90vh] overflow-auto animate-slide-up shadow-glass">
            <h2 className="text-xl font-bold text-white mb-6">{edit ? '编辑团队' : '创建新团队'}</h2>
            <div className="space-y-5">
              <div>
                <label className="block text-slate-400 text-sm mb-2">团队名称 <span className="text-indigo-400">*</span></label>
                <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                  className="input-glass" placeholder="如：618大促运营团队" />
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">团队描述</label>
                <input value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                  className="input-glass" placeholder="描述团队目标和职责" />
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">选择团队成员</label>
                <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-3 bg-white/[0.02] rounded-2xl border border-white/[0.06]">
                  {agents.map((a) => (
                    <button key={a.id} onClick={() => toggleAgent(a.id)}
                      className={`text-xs px-3 py-1.5 rounded-xl border transition-all ${
                        form.agentIds.includes(a.id)
                          ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                          : 'bg-white/[0.03] border-white/[0.06] text-slate-400 hover:border-white/[0.12]'
                      }`}>
                      {a.name}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-slate-600 mt-2">已选 {form.agentIds.length} 人</p>
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">协作模式</label>
                <select value={form.coordinationMode} onChange={e => setForm({ ...form, coordinationMode: e.target.value })}
                  className="input-glass">
                  <option value="sequential">顺序协作</option>
                  <option value="parallel">并行协作</option>
                  <option value="hierarchical">层级协作</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">汇报周期</label>
                <select value={form.reportingCycle} onChange={e => setForm({ ...form, reportingCycle: e.target.value })}
                  className="input-glass">
                  <option value="daily">每日汇报</option>
                  <option value="weekly">每周汇报</option>
                  <option value="monthly">每月汇报</option>
                </select>
              </div>
            </div>
            <div className="flex gap-4 mt-8">
              <button onClick={handleSave} className="btn-aurora flex-1 py-3">{edit ? '保存修改' : '创建团队'}</button>
              <button onClick={() => setShow(false)} className="btn-ghost flex-1 py-3">取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
