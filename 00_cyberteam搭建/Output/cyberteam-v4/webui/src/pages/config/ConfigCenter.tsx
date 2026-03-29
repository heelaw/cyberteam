import { useEffect, useState } from 'react';

const API = '/api';

interface SystemMetrics {
  total_tasks: number; active_tasks: number;
  state_machine_enabled: boolean; rbac_enabled: boolean;
}

export default function ConfigCenter() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      const [sm, rbac, tasks] = await Promise.all([
        fetch(`${API}/config/state-machine`).then(r => r.json()),
        fetch(`${API}/config/rbac`).then(r => r.json()),
        fetch(`${API}/tasks`).then(r => r.json()),
      ]);
      setMetrics({
        total_tasks: tasks.total || 0,
        active_tasks: tasks.tasks?.filter((t: any) => !['done', 'cancelled'].includes(t.state)).length || 0,
        state_machine_enabled: sm.enabled, rbac_enabled: rbac.enabled,
      });
    } catch (e) { console.error('Failed to fetch metrics:', e); } finally { setLoading(false); }
  };

  useEffect(() => { fetchMetrics(); }, []);

  const toggleConfig = async (type: 'state-machine' | 'rbac', enabled: boolean) => {
    setToggling(type);
    try {
      await fetch(`${API}/config/${type}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      fetchMetrics();
    } catch (e) { console.error('Failed to toggle config:', e); } finally { setToggling(null); }
  };

  const configCards = [
    { id: 'state-machine', title: '状态机配置', description: '三省六部任务状态流转控制',
      enabled: metrics?.state_machine_enabled ?? false, stats: '11 状态 · 严格流转校验',
      gradient: 'from-indigo-500 to-blue-500', icon: 'SM', link: '/config/state-machine' },
    { id: 'rbac', title: '权限矩阵配置', description: 'Agent 通信白名单控制',
      enabled: metrics?.rbac_enabled ?? false, stats: '22 Agent · 白名单机制',
      gradient: 'from-purple-500 to-violet-500', icon: 'RB', link: '/config/rbac' },
    { id: 'agents', title: 'Agent 配置', description: 'Agent 角色与数量管理',
      enabled: true, stats: '角色分配 · 数量调整',
      gradient: 'from-emerald-500 to-teal-500', icon: 'AG', link: '/agents' },
    { id: 'prompts', title: '提示词模板', description: 'CEO/COO/专家提示词编辑',
      enabled: true, stats: '模板编辑 · 版本管理',
      gradient: 'from-amber-500 to-orange-500', icon: 'PT', link: '/config/prompts' },
    { id: 'execution', title: '执行控制面板', description: '任务执行实时监控与控制',
      enabled: true, stats: `${metrics?.active_tasks || 0} 活跃任务`,
      gradient: 'from-rose-500 to-pink-500', icon: 'EX', link: '/execute' },
  ];

  return (
    <div className="p-8 min-h-full">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">配置中心</h1>
        <p className="text-slate-500 text-sm mt-1">CyberTeam V4 系统配置与状态监控</p>
      </div>

      {/* 系统概览 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: '总任务数', value: metrics?.total_tasks || 0, color: 'text-white' },
          { label: '活跃任务', value: metrics?.active_tasks || 0, color: 'text-emerald-400' },
          { label: '状态机', value: metrics?.state_machine_enabled ? 'ON' : 'OFF', color: metrics?.state_machine_enabled ? 'text-emerald-400' : 'text-slate-600', dot: metrics?.state_machine_enabled },
          { label: '权限矩阵', value: metrics?.rbac_enabled ? 'ON' : 'OFF', color: metrics?.rbac_enabled ? 'text-emerald-400' : 'text-slate-600', dot: metrics?.rbac_enabled },
        ].map((stat, i) => (
          <div key={i} className="glass p-5 animate-slide-up" style={{ animationDelay: `${i * 60}ms` }}>
            <div className={`text-2xl font-bold ${stat.color} mb-1`}>
              {stat.dot !== undefined && <span className={`inline-block w-2 h-2 rounded-full mr-2 ${stat.dot ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'bg-slate-700'}`} />}
              {stat.value}
            </div>
            <div className="text-slate-500 text-xs">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* 配置卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
        {configCards.map((card, idx) => (
          <a key={card.id} href={card.link} className="block group animate-slide-up" style={{ animationDelay: `${idx * 80}ms` }}>
            <div className="glass aurora-glow p-6 h-full">
              <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center shadow-glass-sm`}>
                  <span className="text-white text-sm font-bold">{card.icon}</span>
                </div>
                <div className={`px-2.5 py-1 rounded-lg text-[10px] font-semibold ${
                  card.enabled ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-500/10 text-slate-500 border border-slate-500/20'
                }`}>
                  {card.enabled ? '已启用' : '已禁用'}
                </div>
              </div>
              <h3 className="text-white font-bold text-lg mb-2">{card.title}</h3>
              <p className="text-slate-400 text-sm mb-4 leading-relaxed">{card.description}</p>
              <div className="pt-4 border-t border-white/[0.06]">
                <span className="text-slate-500 text-sm">{card.stats}</span>
              </div>
            </div>
          </a>
        ))}
      </div>

      {/* 全局开关 */}
      <div className="glass p-8">
        <h2 className="text-lg font-bold text-white mb-6">全局功能开关</h2>
        <div className="space-y-6">
          {[
            { key: 'state-machine' as const, label: '状态机', desc: '启用三省六部任务状态流转控制', enabled: metrics?.state_machine_enabled },
            { key: 'rbac' as const, label: '权限矩阵', desc: '启用 Agent 通信白名单控制', enabled: metrics?.rbac_enabled },
          ].map(item => (
            <div key={item.key} className="flex items-center justify-between">
              <div>
                <div className="text-white font-medium">{item.label}</div>
                <div className="text-slate-500 text-sm">{item.desc}</div>
              </div>
              <button onClick={() => toggleConfig(item.key, !item.enabled)}
                disabled={toggling === item.key}
                className={`relative w-12 h-7 rounded-full transition-all disabled:opacity-40 ${
                  item.enabled ? 'bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_15px_rgba(99,102,241,0.15)]' : 'bg-white/10'
                }`}>
                <div className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow-sm transition-transform ${
                  item.enabled ? 'translate-x-6' : 'translate-x-1'
                }`} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-[#06080f]/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="text-slate-400 text-sm animate-pulse">加载中...</div>
        </div>
      )}
    </div>
  );
}
