import { useEffect, useState } from 'react';

const API = '/api';

interface StateInfo {
  value: string;
  name: string;
  description: string;
  department: string;
}

interface TaskInfo {
  task_id: string;
  state: string;
  title: string;
  transitions: any[];
}

const STATE_COLORS: Record<string, string> = {
  pending: 'bg-slate-500',
  taizi: 'bg-indigo-500',
  zhongshu: 'bg-blue-500',
  menxia: 'bg-purple-500',
  assigned: 'bg-pink-500',
  doing: 'bg-orange-500',
  review: 'bg-yellow-500',
  done: 'bg-emerald-500',
  cancelled: 'bg-red-500',
  failed: 'bg-red-700',
  timeout: 'bg-red-900',
};

const STATE_GLOW: Record<string, string> = {
  pending: 'shadow-slate-500/30',
  taizi: 'shadow-indigo-500/30',
  zhongshu: 'shadow-blue-500/30',
  menxia: 'shadow-purple-500/30',
  assigned: 'shadow-pink-500/30',
  doing: 'shadow-orange-500/30',
  review: 'shadow-yellow-500/30',
  done: 'shadow-emerald-500/30',
  cancelled: 'shadow-red-500/30',
  failed: 'shadow-red-700/30',
};

const STATE_ICONS: Record<string, JSX.Element> = {
  pending: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
  taizi: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>,
  zhongshu: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>,
  menxia: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
  assigned: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>,
  doing: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>,
  review: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
  done: <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>,
};

const FLOW_ORDER = ['pending', 'taizi', 'zhongshu', 'menxia', 'assigned', 'doing', 'review', 'done'];

export default function StateMachineConfig() {
  const [states, setStates] = useState<StateInfo[]>([]);
  const [tasks, setTasks] = useState<TaskInfo[]>([]);
  const [enabled, setEnabled] = useState(true);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statesRes, tasksRes, configRes] = await Promise.all([
        fetch(`${API}/config/state-machine/states`).then(r => r.json()),
        fetch(`${API}/config/state-machine/tasks`).then(r => r.json()),
        fetch(`${API}/config/state-machine/config`).then(r => r.json()),
      ]);
      setStates(statesRes.states || []);
      setTasks(tasksRes.tasks || []);
      setEnabled(configRes.enabled);
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
      await fetch(`${API}/config/state-machine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !enabled }),
      });
      setEnabled(!enabled);
    } catch (e) {
      console.error('Failed to toggle:', e);
    }
  };

  const getStateColor = (value: string) => {
    return STATE_COLORS[value] || 'bg-slate-500';
  };

  const getStateIndex = (value: string) => FLOW_ORDER.indexOf(value);

  return (
    <div className="p-6 min-h-full">
      {/* 页面标题 */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">状态机配置</h1>
          <p className="text-slate-500 text-sm mt-1">公司治理任务状态流转可视化配置</p>
        </div>
        <button
          onClick={toggleEnabled}
          className={`px-5 py-2.5 rounded-2xl font-medium transition-all duration-300 ${
            enabled
              ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/25'
              : 'bg-white/[0.06] text-slate-400 border border-white/[0.07] hover:bg-white/[0.08]'
          }`}
        >
          {enabled ? '状态机已启用' : '状态机已禁用'}
        </button>
      </div>

      {/* 状态流转图 */}
      <div className="glass p-6 mb-6">
        <h2 className="text-lg font-bold text-white mb-6">状态流转图</h2>
        <div className="flex items-center overflow-x-auto pb-4">
          {FLOW_ORDER.map((state, idx) => {
            const stateInfo = states.find(s => s.value === state);
            return (
              <div key={state} className="flex items-center">
                <div className="flex flex-col items-center group">
                  <div className={`w-16 h-16 rounded-2xl ${getStateColor(state)} flex items-center justify-center shadow-lg transition-transform duration-300 group-hover:scale-110 ${STATE_GLOW[state] || ''}`}>
                    {STATE_ICONS[state] || <span className="text-white text-lg">{idx + 1}</span>}
                  </div>
                  <div className="mt-3 text-center">
                    <div className="text-slate-200 text-sm font-medium">{stateInfo?.name || state}</div>
                    <div className="text-slate-600 text-xs mt-0.5">{stateInfo?.department || ''}</div>
                  </div>
                </div>
                {idx < FLOW_ORDER.length - 1 && (
                  <div className="mx-3 flex items-center">
                    <div className="w-6 h-px bg-gradient-to-r from-white/[0.12] to-white/[0.04]" />
                    <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* 图例 */}
        <div className="mt-6 pt-5 border-t border-white/[0.06] flex flex-wrap gap-5 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500/50" />
            <span className="text-slate-400">CEO路由</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500 shadow-sm shadow-blue-500/50" />
            <span className="text-slate-400">COO协调</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-500 shadow-sm shadow-purple-500/50" />
            <span className="text-slate-400">CEO审核</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-pink-500 shadow-sm shadow-pink-500/50" />
            <span className="text-slate-400">PM调度</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500 shadow-sm shadow-orange-500/50" />
            <span className="text-slate-400">部门执行</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500 shadow-sm shadow-yellow-500/50" />
            <span className="text-slate-400">汇总审核</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
            <span className="text-slate-400">任务完成</span>
          </div>
        </div>
      </div>

      {/* 状态详情列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {states.map(state => {
          const stateTasks = tasks.filter(t => t.state === state.value);
          const index = getStateIndex(state.value);
          return (
            <div key={state.value} className="glass p-5 group hover:border-white/[0.12] transition-all duration-300">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-2xl ${getStateColor(state.value)} flex items-center justify-center text-lg shadow-lg ${STATE_GLOW[state.value] || ''}`}>
                  <span className="text-white font-bold text-sm">{index + 1}</span>
                </div>
                <div>
                  <div className="text-slate-100 font-medium">{state.name}</div>
                  <div className="text-slate-600 text-xs">{state.department}</div>
                </div>
              </div>
              <p className="text-slate-400 text-sm mb-3 leading-relaxed">{state.description}</p>
              <div className="text-xs text-slate-500 flex items-center gap-1.5">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                当前任务: <span className="text-slate-200 font-medium">{stateTasks.length}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 当前任务列表 */}
      <div className="glass p-6">
        <h2 className="text-lg font-bold text-white mb-5">当前任务 ({tasks.length})</h2>
        {tasks.length === 0 ? (
          <div className="text-center text-slate-500 py-12">
            <svg className="w-16 h-16 mx-auto mb-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p>暂无任务</p>
            <p className="text-sm mt-2 text-slate-600">创建任务后将在此处显示</p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.slice(0, 10).map(task => (
              <div key={task.task_id} className="flex items-center justify-between bg-white/[0.02] rounded-2xl p-4 border border-white/[0.05] hover:bg-white/[0.04] hover:border-white/[0.08] transition-all duration-200">
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-xl ${getStateColor(task.state)} flex items-center justify-center text-xs text-white font-bold shadow-lg ${STATE_GLOW[task.state] || ''}`}>
                    {getStateIndex(task.state) + 1}
                  </div>
                  <div>
                    <div className="text-slate-100 text-sm font-medium">{task.title || task.task_id}</div>
                    <div className="text-slate-600 text-xs mt-0.5">{task.task_id.slice(0, 12)}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="tag" style={{ backgroundColor: 'rgba(255,255,255,0.04)', color: 'inherit' }}>
                    {states.find(s => s.value === task.state)?.name || task.state}
                  </span>
                  <span className="text-slate-600 text-xs">
                    {task.transitions?.length || 0} 次流转
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
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
