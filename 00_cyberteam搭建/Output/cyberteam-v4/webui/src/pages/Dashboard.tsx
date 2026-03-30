import { useEffect, useState } from 'react';
import { apiRequest, ApiError } from '../api/client';

interface Dept {
  id: string;
  name: string;
  parentId: string | null;
  level: number;
  description: string;
}

interface Agent {
  id: string;
  name: string;
  role: string;
  departmentId: string;
  level: number;
  skills: any[];
}

const LEVEL_GRADIENTS: Record<number, string> = {
  1: 'from-indigo-500 to-blue-500',
  2: 'from-purple-500 to-indigo-500',
  3: 'from-pink-500 to-purple-500',
  4: 'from-orange-500 to-amber-500',
};
const LEVEL_LABELS: Record<number, string> = { 1: 'CEO', 2: '总监', 3: '专家', 4: '专员' };

interface TreeNode {
  dept: Dept;
  children: TreeNode[];
}

function buildTree(depts: Dept[]): TreeNode[] {
  const map = new Map<string, TreeNode>();
  depts.forEach(d => map.set(d.id, { dept: d, children: [] }));
  const roots: TreeNode[] = [];
  depts.forEach(d => {
    const node = map.get(d.id)!;
    if (d.parentId && map.has(d.parentId)) {
      map.get(d.parentId)!.children.push(node);
    } else {
      roots.push(node);
    }
  });
  return roots;
}

export default function Dashboard() {
  const [depts, setDepts] = useState<Dept[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [d, a] = await Promise.all([
          apiRequest<any>('/departments'),
          apiRequest<any>('/agents'),
        ]);
        const deptList: Dept[] = d.departments || d || [];
        const agentList: Agent[] = (a.agents || a || []).map((ag: any) => ({
          ...ag,
          id: ag.agent_id || ag.id,
          departmentId: ag.department_id || ag.departmentId,
          level: typeof ag.level === 'string'
            ? parseInt(ag.level.replace('L', '')) || 3
            : (ag.level || 3),
        }));
        setDepts(deptList);
        setAgents(agentList);
      } catch (e) {
        const message = e instanceof ApiError ? e.message : 'Failed to load data';
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalSkills = agents.reduce((sum, a) => sum + (a.skills?.length || 0), 0);
  const maxLevel = depts.length > 0 ? Math.max(...depts.map(d => d.level), 0) : 0;

  const getDeptName = (id: string) => {
    const d = depts.find(d => d.id === id);
    return d?.name || '未知部门';
  };

  const renderTree = (nodes: TreeNode[], depth = 0): React.ReactNode => (
    <div className={depth > 0 ? 'ml-5 border-l border-white/[0.06] pl-3' : ''}>
      {nodes.map(node => (
        <div key={node.dept.id} className="py-1">
          <div className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-white/[0.04] transition-colors">
            <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${LEVEL_GRADIENTS[node.dept.level] || 'from-slate-500 to-slate-600'}`} />
            <span className="text-slate-300 text-sm">{node.dept.name}</span>
            <span className="text-slate-600 text-xs">L{node.dept.level}</span>
          </div>
          {node.children.length > 0 && renderTree(node.children, depth + 1)}
        </div>
      ))}
    </div>
  );

  const stats = [
    { label: '部门', value: depts.length, icon: 'D', gradient: 'from-blue-400 to-cyan-400' },
    { label: 'Agent', value: agents.length, icon: 'A', gradient: 'from-emerald-400 to-teal-400' },
    { label: '技能', value: totalSkills, icon: 'S', gradient: 'from-amber-400 to-orange-400' },
    { label: '层级', value: maxLevel, icon: 'L', gradient: 'from-purple-400 to-pink-400' },
  ];

  const quickActions = [
    { href: '/departments', label: '部门管理', desc: '组织架构管理' },
    { href: '/agents', label: 'Agent 管理', desc: '角色与能力配置' },
    { href: '/skills', label: '技能配置', desc: '技能定义与编辑' },
    { href: '/config', label: '系统设置', desc: '状态机与权限' },
  ];

  if (loading) {
    return (
      <div className="absolute inset-0 bg-[#06080f]/80 backdrop-blur-xl flex items-center justify-center z-40">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
          <span className="text-slate-400 text-sm">加载中...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 min-h-full flex items-center justify-center">
        <div className="glass p-8 max-w-md text-center animate-fade-in">
          <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-rose-500/10 flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-rose-400">
              <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />
            </svg>
          </div>
          <p className="text-slate-400 text-sm mb-4">数据加载失败</p>
          <p className="text-slate-500 text-xs mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-ghost">刷新页面</button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 min-h-full bg-[#06080f]">
      {/* Hero Banner */}
      <div className="glass p-8 mb-8 animate-fade-in">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-[0_0_20px_rgba(99,102,241,0.2)]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white">
              <polygon points="12 2 2 7 12 12 22 7 12 2" /><polyline points="2 17 12 22 22 17" /><polyline points="2 12 12 17 22 12" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              CyberTeam{' '}
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Studio
              </span>
            </h1>
            <p className="text-slate-500 text-sm mt-0.5">企业级 AI Agent 协作系统</p>
          </div>
        </div>
        <div className="flex gap-3 mt-6 flex-wrap">
          {quickActions.map((item) => (
            <a key={item.href} href={item.href}
              className="glass p-4 flex items-center gap-3 text-sm hover:bg-white/[0.06] hover:border-white/[0.12] transition-all group">
              <span className="text-slate-300 group-hover:text-white transition-colors">{item.label}</span>
              <span className="text-xs text-slate-600">{item.desc}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-slate-600 group-hover:text-indigo-400 transition-colors ml-auto">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </a>
          ))}
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, idx) => (
          <div key={stat.label} className="glass p-5 animate-slide-up" style={{ animationDelay: `${idx * 60}ms` }}>
            <div className="flex items-center gap-3 mb-2">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.gradient} flex items-center justify-center shadow-[0_0_12px_rgba(255,255,255,0.05)]`}>
                <span className="text-white text-xs font-bold">{stat.icon}</span>
              </div>
              <div className="text-white text-3xl font-bold">{stat.value}</div>
            </div>
            <div className="text-slate-500 text-xs ml-[52px]">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Organization & Agents */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Organization Tree */}
        <div>
          <h2 className="text-lg font-medium text-slate-200 mb-3 flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-indigo-400">
              <rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="8" y="14" width="8" height="7" rx="1" />
              <path d="M6.5 10v2M17.5 10v2M12 16v-2" />
            </svg>
            组织架构
          </h2>
          <div className="glass p-4 max-h-[420px] overflow-auto">
            {depts.length > 0 ? renderTree(buildTree(depts)) : (
              <div className="text-center py-8">
                <p className="text-slate-500 mb-2">暂无部门</p>
                <a href="/departments" className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">点击添加第一个部门</a>
              </div>
            )}
          </div>
        </div>

        {/* Agent List */}
        <div>
          <h2 className="text-lg font-medium text-slate-200 mb-3 flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-purple-400">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
            Agent 列表
          </h2>
          <div className="glass p-4 max-h-[420px] overflow-auto space-y-2">
            {agents.length > 0 ? agents.map(a => {
              const levelNum = typeof a.level === 'string' ? parseInt(a.level.replace('L', '')) || 3 : (a.level || 3);
              const gradient = LEVEL_GRADIENTS[levelNum] || LEVEL_GRADIENTS[3];
              const levelLabel = LEVEL_LABELS[levelNum] || `L${levelNum}`;
              return (
                <div key={a.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.04] transition-all">
                  <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center shrink-0`}>
                    <span className="text-white text-xs font-bold">{levelLabel[0]}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-white text-sm font-medium truncate">{a.name}</div>
                    <div className="text-slate-500 text-xs truncate">{a.role || '未定义角色'} · {getDeptName(a.departmentId)}</div>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-md bg-gradient-to-r ${gradient} text-white font-medium shrink-0`}>
                    {levelLabel}
                  </span>
                </div>
              );
            }) : (
              <div className="text-center py-8">
                <p className="text-slate-500 mb-2">暂无 Agent</p>
                <a href="/agents" className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">点击添加第一个 Agent</a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
