import { useEffect, useState } from 'react';

const API = '/api';

interface Dept {
  id: string; name: string; parentId: string | null;
  description: string; level: number; rules?: string;
}

async function api(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    ...(opts.body ? { body: JSON.stringify(opts.body) } : {}),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

const LEVEL_STYLES: Record<number, { gradient: string; label: string; color: string }> = {
  1: { gradient: 'from-indigo-500 to-blue-500', label: 'CEO', color: 'text-blue-400' },
  2: { gradient: 'from-purple-500 to-indigo-500', label: '总监', color: 'text-indigo-400' },
  3: { gradient: 'from-pink-500 to-purple-500', label: '专家', color: 'text-purple-400' },
  4: { gradient: 'from-orange-500 to-amber-500', label: '专员', color: 'text-amber-400' },
};

export default function Departments() {
  const [depts, setDepts] = useState<Dept[]>([]);
  const [show, setShow] = useState(false);
  const [edit, setEdit] = useState<Dept | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{msg: string; type: 'success'|'error'} | null>(null);
  const [form, setForm] = useState({ name: '', description: '', parentId: '', level: 1, rules: '' });

  const showToast = (msg: string, type: 'success'|'error') => {
    setToast({msg, type});
    setTimeout(() => setToast(null), 3000);
  };

  const fetchDepts = async () => {
    try {
      setLoading(true);
      const data = await api('/departments');
      const deptList = data.departments || data || [];
      const mappedDepts = deptList.map((d: any) => ({
        ...d,
        id: d.department_id || d.id,
        parentId: d.parentId || null,
        level: d.level || 1,
      }));
      setDepts(mappedDepts);
    } catch (e) {
      showToast('加载部门失败', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDepts(); }, []);

  const buildTree = (items: Dept[], parentId: string | null = null): Dept[] =>
    items.filter(d => d.parentId === parentId);

  const handleSave = async () => {
    if (!form.name.trim()) { showToast('请输入部门名称', 'error'); return; }
    try {
      const id = edit?.id || `dept-${Date.now()}`;
      const payload = {
        id, name: form.name, description: form.description,
        parentId: form.parentId || null, level: form.level, rules: form.rules,
      };
      if (edit) {
        await api(`/departments/${id}`, { method: 'PUT', body: payload });
        showToast('部门更新成功', 'success');
      } else {
        await api('/departments', { method: 'POST', body: payload });
        showToast('部门创建成功', 'success');
      }
      setShow(false); setEdit(null);
      setForm({ name: '', description: '', parentId: '', level: 1, rules: '' });
      fetchDepts();
    } catch (e) {
      showToast('保存失败', 'error');
    }
  };

  const handleEdit = (d: Dept) => {
    setEdit(d);
    setForm({ name: d.name, description: d.description || '', parentId: d.parentId || '', level: d.level || 1, rules: d.rules || '' });
    setShow(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除此部门？')) return;
    try {
      await api(`/departments/${id}`, { method: 'DELETE' });
      showToast('删除成功', 'success');
      fetchDepts();
    } catch (e) { showToast('删除失败', 'error'); }
  };

  const getDeptName = (id: string) => depts.find(d => d.id === id)?.name || '未知';

  const renderTree = (items: Dept[], level = 0) => items.map(d => {
    const ls = LEVEL_STYLES[d.level] || LEVEL_STYLES[1];
    const childDepts = buildTree(depts, d.id);
    return (
      <div key={d.id} style={{ marginLeft: level * 20 }} className="animate-fade-in">
        <div className="glass flex items-center justify-between py-3.5 px-5 mb-2 group cursor-pointer hover:aurora-glow"
          onClick={() => handleEdit(d)}>
          <div className="flex items-center gap-4">
            {/* 左边极光色条 */}
            <div className={`w-1 h-10 rounded-full bg-gradient-to-b ${ls.gradient} opacity-60`} />
            <div>
              <div className="flex items-center gap-2">
                <span className="text-white font-medium">{d.name}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-md bg-gradient-to-r ${ls.gradient} text-white font-medium`}>
                  {ls.label}
                </span>
              </div>
              {d.description && <p className="text-xs text-slate-500 mt-0.5">{d.description}</p>}
              {d.parentId && <p className="text-xs text-indigo-400/70 mt-0.5">上级: {getDeptName(d.parentId)}</p>}
            </div>
          </div>
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={(e) => { e.stopPropagation(); handleEdit(d); }}
              className="px-3 py-1.5 text-xs text-indigo-400 hover:text-white hover:bg-indigo-500/20 rounded-lg transition-colors">
              编辑
            </button>
            <button onClick={(e) => { e.stopPropagation(); handleDelete(d.id); }}
              className="px-3 py-1.5 text-xs text-rose-400 hover:text-white hover:bg-rose-500/20 rounded-lg transition-colors">
              删除
            </button>
          </div>
        </div>
        {childDepts.length > 0 && renderTree(childDepts, level + 1)}
      </div>
    );
  });

  return (
    <div className="p-8 min-h-full relative">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-6 right-6 px-5 py-3 rounded-2xl z-50 backdrop-blur-xl border-l-[3px] animate-slide-in ${
          toast.type === 'success'
            ? 'bg-emerald-500/10 border-l-emerald-400 text-emerald-300'
            : 'bg-rose-500/10 border-l-rose-400 text-rose-300'
        }`}>
          {toast.msg}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="absolute inset-0 bg-[#06080f]/80 backdrop-blur-sm flex items-center justify-center z-40">
          <div className="text-slate-400 text-sm animate-pulse">加载中...</div>
        </div>
      )}

      {/* 头部 */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">部门管理</h1>
          <p className="text-slate-500 text-sm mt-1">管理公司组织架构，调整部门层级关系</p>
        </div>
        <button onClick={() => { setEdit(null); setForm({ name: '', description: '', parentId: '', level: 1, rules: '' }); setShow(true); }}
          className="btn-aurora flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加部门
        </button>
      </div>

      {/* 提示框 */}
      <div className="bg-indigo-500/[0.06] border border-indigo-500/15 rounded-2xl p-4 mb-8 animate-fade-in">
        <p className="text-indigo-300/80 text-sm">
          点击部门卡片可以编辑，可以修改上级部门来调整组织架构。每个部门可以配置专属的规章制度。
        </p>
      </div>

      {/* 统计 */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: '总部门数', value: depts.length },
          { label: '一级部门', value: depts.filter(d => !d.parentId).length },
          { label: '子部门', value: depts.filter(d => d.parentId).length },
          { label: '组织层级', value: Math.max(...depts.map(d => d.level), 0) + ' 层' },
        ].map((stat, i) => (
          <div key={i} className="glass p-5 text-center animate-slide-up" style={{ animationDelay: `${i * 60}ms` }}>
            <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
            <div className="text-xs text-slate-500">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* 树形列表 */}
      <div className="animate-fade-in">
        {depts.length > 0 ? renderTree(buildTree(depts)) : (
          <div className="text-center py-20">
            <p className="text-slate-500 mb-4">暂无部门</p>
            <button onClick={() => setShow(true)} className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">
              点击添加第一个部门
            </button>
          </div>
        )}
      </div>

      {/* 弹窗 */}
      {show && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 overflow-auto">
          <div className="glass p-8 w-full max-w-lg max-h-[90vh] overflow-auto animate-slide-up shadow-glass">
            <h2 className="text-xl font-bold text-white mb-6">{edit ? '编辑部门' : '添加新部门'}</h2>
            <div className="space-y-5">
              <div>
                <label className="block text-slate-400 text-sm mb-2">部门名称 <span className="text-indigo-400">*</span></label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="input-glass" placeholder="如：运营部、营销部" />
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">上级部门</label>
                <select value={form.parentId} onChange={(e) => setForm({ ...form, parentId: e.target.value })}
                  className="input-glass">
                  <option value="">作为一级部门</option>
                  {depts.filter(d => !edit || d.id !== edit.id).map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">部门级别</label>
                <select value={form.level} onChange={(e) => setForm({ ...form, level: parseInt(e.target.value) })}
                  className="input-glass">
                  <option value="1">L1 - CEO（最高决策层）</option>
                  <option value="2">L2 - 总监（管理层）</option>
                  <option value="3">L3 - 专家（专业层）</option>
                  <option value="4">L4 - 专员（执行层）</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">部门描述</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="input-glass" placeholder="简单描述部门职责" />
              </div>
              <div>
                <label className="block text-slate-400 text-sm mb-2">部门规章制度</label>
                <textarea value={form.rules} onChange={(e) => setForm({ ...form, rules: e.target.value })}
                  rows={4} className="input-glass resize-none" placeholder="输入部门规章、工作流程、考核标准等..." />
              </div>
            </div>
            <div className="flex gap-4 mt-8">
              <button onClick={handleSave} className="btn-aurora flex-1 py-3">
                {edit ? '保存修改' : '创建部门'}
              </button>
              <button onClick={() => setShow(false)} className="btn-ghost flex-1 py-3">取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
