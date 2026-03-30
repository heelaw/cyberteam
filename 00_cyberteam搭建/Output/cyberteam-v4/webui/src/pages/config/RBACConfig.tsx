import { useEffect, useState } from 'react';

const API = '/api';

interface AgentInfo {
  id: string;
  label: string;
  layer: string;
  role: string;
  duty: string;
  allow_agents: string[];
}

interface LayerInfo {
  value: string;
  name: string;
  agents: AgentInfo[];
}

const LAYER_COLORS: Record<string, string> = {
  taizi: 'bg-blue-500',
  zhongshu: 'bg-indigo-500',
  menxia: 'bg-purple-500',
  shangshu: 'bg-pink-500',
  bingbu: 'bg-orange-500',
  xingbu: 'bg-yellow-500',
  libu: 'bg-teal-500',
  hubu: 'bg-cyan-500',
  gongbu: 'bg-green-500',
  libu_hr: 'bg-emerald-500',
  user: 'bg-gray-500',
};

const LAYER_GLOW: Record<string, string> = {
  taizi: 'shadow-blue-500/30',
  zhongshu: 'shadow-indigo-500/30',
  menxia: 'shadow-purple-500/30',
  shangshu: 'shadow-pink-500/30',
  bingbu: 'shadow-orange-500/30',
  xingbu: 'shadow-yellow-500/30',
  libu: 'shadow-teal-500/30',
  hubu: 'shadow-cyan-500/30',
  gongbu: 'shadow-green-500/30',
  libu_hr: 'shadow-emerald-500/30',
  user: 'shadow-gray-500/30',
};

export default function RBACConfig() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [enabled, setEnabled] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<AgentInfo | null>(null);
  const [matrix, setMatrix] = useState<Record<string, Record<string, boolean>>>({});
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [agentsRes, configRes, matrixRes] = await Promise.all([
        fetch(`${API}/config/rbac/agents`).then(r => r.json()),
        fetch(`${API}/config/rbac/config`).then(r => r.json()),
        fetch(`${API}/config/rbac/matrix`).then(r => r.json()),
      ]);
      setAgents(agentsRes.agents || []);
      setEnabled(configRes.enabled);
      setMatrix(matrixRes.matrix || {});
    } catch (e) {
      console.error('Failed to fetch data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const toggleEnabled = async () => {
    try {
      await fetch(`${API}/config/rbac`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !enabled }),
      });
      setEnabled(!enabled);
    } catch (e) {
      console.error('Failed to toggle:', e);
    }
  };

  const getAgentsByLayer = () => {
    const layers: Record<string, AgentInfo[]> = {};
    agents.forEach(agent => {
      if (!layers[agent.layer]) {
        layers[agent.layer] = [];
      }
      layers[agent.layer].push(agent);
    });
    return layers;
  };

  const layers = getAgentsByLayer();

  const canCommunicate = (from: string, to: string) => {
    return matrix[from]?.[to] ?? false;
  };

  return (
    <div className="p-6 min-h-full">
      {/* 页面标题 */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">权限矩阵配置</h1>
          <p className="text-slate-500 text-sm mt-1">Agent 通信白名单可视化配置</p>
        </div>
        <button
          onClick={toggleEnabled}
          className={`px-5 py-2.5 rounded-2xl font-medium transition-all duration-300 ${
            enabled
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/25'
              : 'bg-white/[0.06] text-slate-400 border border-white/[0.07] hover:bg-white/[0.08]'
          }`}
        >
          {enabled ? '权限矩阵已启用' : '权限矩阵已禁用'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent 层级列表 */}
        <div className="glass p-6">
          <h2 className="text-lg font-bold text-white mb-4">Agent 层级</h2>
          <div className="space-y-5">
            {Object.entries(layers).map(([layer, layerAgents]) => (
              <div key={layer}>
                <div className="text-slate-500 text-xs uppercase tracking-wider mb-2 font-medium">{layer}</div>
                <div className="space-y-1.5">
                  {layerAgents.map(agent => (
                    <button
                      key={agent.id}
                      onClick={() => setSelectedAgent(agent)}
                      className={`w-full text-left p-3 rounded-2xl transition-all duration-200 ${
                        selectedAgent?.id === agent.id
                          ? 'bg-indigo-500/10 border border-indigo-500/30'
                          : 'bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.05] hover:border-white/[0.1]'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-xl ${LAYER_COLORS[agent.layer] || 'bg-slate-500'} flex items-center justify-center text-white text-sm font-medium shadow-lg ${LAYER_GLOW[agent.layer] || ''}`}>
                          {agent.label.charAt(0)}
                        </div>
                        <div>
                          <div className="text-slate-100 text-sm font-medium">{agent.label}</div>
                          <div className="text-slate-600 text-xs">{agent.role}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 权限详情 */}
        <div className="glass p-6">
          <h2 className="text-lg font-bold text-white mb-4">权限详情</h2>
          {selectedAgent ? (
            <div>
              <div className="flex items-center gap-4 mb-5">
                <div className={`w-14 h-14 rounded-2xl ${LAYER_COLORS[selectedAgent.layer] || 'bg-slate-500'} flex items-center justify-center text-white text-xl font-bold shadow-lg ${LAYER_GLOW[selectedAgent.layer] || ''}`}>
                  {selectedAgent.label.charAt(0)}
                </div>
                <div>
                  <div className="text-white font-bold text-lg">{selectedAgent.label}</div>
                  <div className="text-slate-400 text-sm">{selectedAgent.role} · {selectedAgent.layer}</div>
                </div>
              </div>
              <p className="text-slate-400 text-sm mb-5 leading-relaxed">{selectedAgent.duty}</p>

              <div className="mb-5">
                <div className="text-slate-500 text-xs uppercase tracking-wider mb-2.5 font-medium">可通信目标 ({selectedAgent.allow_agents.length})</div>
                <div className="flex flex-wrap gap-2">
                  {selectedAgent.allow_agents.map(targetId => {
                    const target = agents.find(a => a.id === targetId);
                    return (
                      <span key={targetId} className="tag">
                        {target?.label || targetId}
                      </span>
                    );
                  })}
                  {selectedAgent.allow_agents.length === 0 && (
                    <span className="text-slate-600 text-sm">无</span>
                  )}
                </div>
              </div>

              <div className="pt-4 border-t border-white/[0.06]">
                <div className="text-slate-500 text-xs uppercase tracking-wider mb-2.5 font-medium">可接收消息来源</div>
                <div className="flex flex-wrap gap-2">
                  {agents
                    .filter(a => a.allow_agents.includes(selectedAgent.id))
                    .map(source => (
                      <span key={source.id} className="tag" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderColor: 'rgba(255,255,255,0.06)' }}>
                        {source.label}
                      </span>
                    ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-500 py-16">
              <svg className="w-16 h-16 mx-auto mb-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
              </svg>
              <p>选择左侧 Agent 查看权限详情</p>
            </div>
          )}
        </div>

        {/* 权限矩阵热力图 */}
        <div className="glass p-6">
          <h2 className="text-lg font-bold text-white mb-4">权限热力图</h2>
          <div className="overflow-auto max-h-96">
            <table className="w-full text-xs">
              <thead>
                <tr>
                  <th className="text-left text-slate-500 p-1.5"></th>
                  {agents.slice(0, 8).map(agent => (
                    <th key={agent.id} className="text-center text-slate-500 p-1.5">
                      <div className="w-10 truncate text-xs">{agent.label}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {agents.slice(0, 8).map(rowAgent => (
                  <tr key={rowAgent.id}>
                    <td className="text-left text-slate-400 p-1.5 font-medium">{rowAgent.label}</td>
                    {agents.slice(0, 8).map(colAgent => (
                      <td key={colAgent.id} className="text-center p-1.5">
                        <div className={`w-5 h-5 mx-auto rounded-md transition-colors ${
                          canCommunicate(rowAgent.id, colAgent.id)
                            ? 'bg-emerald-500 shadow-sm shadow-emerald-500/40'
                            : canCommunicate(colAgent.id, rowAgent.id)
                            ? 'bg-amber-500/80 shadow-sm shadow-amber-500/30'
                            : 'bg-white/[0.04]'
                        }`} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-5 pt-4 border-t border-white/[0.06] flex items-center gap-5 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3.5 h-3.5 rounded bg-emerald-500 shadow-sm shadow-emerald-500/40" />
              <span className="text-slate-400">可发送</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3.5 h-3.5 rounded bg-amber-500/80 shadow-sm shadow-amber-500/30" />
              <span className="text-slate-400">可接收</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3.5 h-3.5 rounded bg-white/[0.04]" />
              <span className="text-slate-400">无权限</span>
            </div>
          </div>
        </div>
      </div>

      {/* 三层架构说明 */}
      <div className="mt-6 glass p-6">
        <h2 className="text-lg font-bold text-white mb-5">权限架构说明</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/[0.02] rounded-2xl p-5 border border-white/[0.05]">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-blue-400 shadow-sm shadow-blue-400/50" />
              <div className="text-blue-400 font-bold text-sm">决策层</div>
            </div>
            <p className="text-slate-300 text-sm font-mono">taizi → zhongshu → menxia ↔ shangshu</p>
            <p className="text-slate-600 text-xs mt-3 leading-relaxed">CEO路由、COO协调、CEO审核、PM调度</p>
          </div>
          <div className="bg-white/[0.02] rounded-2xl p-5 border border-white/[0.05]">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-purple-400 shadow-sm shadow-purple-400/50" />
              <div className="text-purple-400 font-bold text-sm">协调层 (部门总监)</div>
            </div>
            <p className="text-slate-300 text-sm font-mono">growth_bg, product_bg, tech_bg...</p>
            <p className="text-slate-600 text-xs mt-3 leading-relaxed">受PM调度，协调执行层</p>
          </div>
          <div className="bg-white/[0.02] rounded-2xl p-5 border border-white/[0.05]">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-orange-400 shadow-sm shadow-orange-400/50" />
              <div className="text-orange-400 font-bold text-sm">执行层 (部门)</div>
            </div>
            <p className="text-slate-300 text-sm font-mono">bingbu, xingbu, libu, hubu...</p>
            <p className="text-slate-600 text-xs mt-3 leading-relaxed">只与PM调度通信，不能跨部门直接沟通</p>
          </div>
        </div>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-[#06080f]/90 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass p-8 flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <div className="text-slate-200">加载中...</div>
          </div>
        </div>
      )}
    </div>
  );
}
