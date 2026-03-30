import { useEffect, useState, useRef } from 'react';

const API = '/api';

interface TaskInfo {
  task_id: string; trace_id: string; state: string; title: string; description: string;
  transitions: Array<{ from_state: string; to_state: string; reason: string; triggered_by: string; timestamp: string; }>;
  created_at: string; updated_at: string; score?: number;
}

const STATE_STYLES: Record<string, { gradient: string; label: string }> = {
  pending:   { gradient: 'from-slate-500 to-slate-600', label: '待处理' },
  taizi:     { gradient: 'from-indigo-500 to-blue-500', label: '太子分拣' },
  zhongshu:  { gradient: 'from-blue-500 to-cyan-500', label: '中书审核' },
  menxia:    { gradient: 'from-purple-500 to-violet-500', label: '门下审议' },
  assigned:  { gradient: 'from-pink-500 to-rose-500', label: '已分配' },
  doing:     { gradient: 'from-orange-500 to-amber-500', label: '执行中' },
  review:    { gradient: 'from-yellow-500 to-amber-500', label: '审核中' },
  done:      { gradient: 'from-emerald-500 to-green-500', label: '已完成' },
  cancelled: { gradient: 'from-rose-600 to-red-600', label: '已取消' },
  failed:    { gradient: 'from-red-600 to-rose-700', label: '已失败' },
};

export default function ExecutionControl() {
  const [tasks, setTasks] = useState<TaskInfo[]>([]);
  const [selectedTask, setSelectedTask] = useState<TaskInfo | null>(null);
  const [logs, setLogs] = useState<Array<{ time: string; message: string; type: string }>>([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [creating, setCreating] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const fetchTasks = async () => {
    try {
      const res = await fetch(`${API}/config/state-machine/tasks`);
      const data = await res.json();
      setTasks(data.tasks || []);
    } catch (e) { console.error('Failed to fetch tasks:', e); }
  };

  useEffect(() => {
    fetchTasks();
    if (autoRefresh) { const iv = setInterval(fetchTasks, 5000); return () => clearInterval(iv); }
  }, [autoRefresh]);

  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  const addLog = (message: string, type: string = 'info') => {
    setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message, type }]);
  };

  const createTask = async () => {
    if (!newTaskTitle.trim()) return;
    setCreating(true);
    try {
      const res = await fetch(`${API}/config/state-machine/tasks`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTaskTitle, description: '', user_input: newTaskTitle, priority: '中' }),
      });
      const data = await res.json();
      addLog(`任务创建成功: ${data.title || data.task_id}`, 'success');
      setNewTaskTitle(''); fetchTasks();
      if (data.task_id) {
        setTimeout(async () => {
          await fetch(`${API}/config/state-machine/tasks/${data.task_id}/transition`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to_state: 'taizi', reason: 'prince_received', triggered_by: 'user' }),
          });
          addLog('任务进入太子分拣阶段', 'info'); fetchTasks();
        }, 1000);
      }
    } catch (e) { addLog(`任务创建失败: ${e}`, 'error'); } finally { setCreating(false); }
  };

  const transitionTask = async (taskId: string, toState: string) => {
    try {
      await fetch(`${API}/config/state-machine/tasks/${taskId}/transition`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_state: toState, reason: 'system', triggered_by: 'user' }),
      });
      addLog(`任务 ${taskId} 转换到 ${toState}`, 'success'); fetchTasks();
    } catch (e) { addLog(`状态转换失败: ${e}`, 'error'); }
  };

  const getNextStates = (currentState: string): string[] => {
    const flow = ['pending', 'taizi', 'zhongshu', 'menxia', 'assigned', 'doing', 'review', 'done'];
    const idx = flow.indexOf(currentState);
    if (idx === -1 || idx >= flow.length - 1) return [];
    return [flow[idx + 1]];
  };

  const activeTasks = tasks.filter(t => !['done', 'cancelled', 'failed'].includes(t.state));
  const completedTasks = tasks.filter(t => ['done', 'cancelled', 'failed'].includes(t.state));

  return (
    <div className="p-8 min-h-full">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">执行控制面板</h1>
          <p className="text-slate-500 text-sm mt-1">任务执行实时监控与控制</p>
        </div>
        <label className="flex items-center gap-3 cursor-pointer group">
          <div className={`relative w-11 h-6 rounded-full transition-colors ${autoRefresh ? 'bg-gradient-to-r from-indigo-500 to-purple-500' : 'bg-white/10'}`}
            onClick={() => setAutoRefresh(!autoRefresh)}>
            <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${autoRefresh ? 'translate-x-6' : 'translate-x-1'}`} />
          </div>
          <span className="text-slate-400 text-sm group-hover:text-slate-300 transition-colors">自动刷新</span>
        </label>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 任务列表 */}
        <div className="glass p-6">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
            任务列表 <span className="text-indigo-400 ml-1">{activeTasks.length}</span>
          </h2>

          <div className="flex gap-2 mb-4">
            <input value={newTaskTitle} onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="输入任务标题..." className="input-glass flex-1"
              onKeyDown={(e) => e.key === 'Enter' && createTask()} />
            <button onClick={createTask} disabled={creating || !newTaskTitle.trim()}
              className="btn-aurora disabled:opacity-40">新建</button>
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {activeTasks.map(task => {
              const ss = STATE_STYLES[task.state] || { gradient: 'from-slate-500 to-slate-600', label: task.state };
              return (
                <button key={task.task_id} onClick={() => setSelectedTask(task)}
                  className={`w-full text-left p-3.5 rounded-xl transition-all ${
                    selectedTask?.task_id === task.task_id
                      ? 'bg-indigo-500/[0.1] border border-indigo-500/25'
                      : 'bg-white/[0.02] hover:bg-white/[0.04] border border-transparent'
                  }`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${ss.gradient} flex items-center justify-center shrink-0`}>
                      <span className="text-white text-xs font-bold">{ss.label[0]}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-white text-sm font-medium truncate">{task.title || task.task_id}</div>
                      <div className="text-slate-500 text-xs">{ss.label}</div>
                    </div>
                  </div>
                </button>
              );
            })}
            {activeTasks.length === 0 && <div className="text-center text-slate-600 py-10 text-sm">暂无活跃任务</div>}
          </div>
        </div>

        {/* 任务详情 */}
        <div className="glass p-6">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">任务详情</h2>
          {selectedTask ? (
            <div className="animate-fade-in">
              <div className="flex items-center gap-4 mb-6">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${STATE_STYLES[selectedTask.state]?.gradient || 'from-slate-500 to-slate-600'} flex items-center justify-center`}>
                  <span className="text-white text-2xl font-bold">{(STATE_STYLES[selectedTask.state]?.label || '?')[0]}</span>
                </div>
                <div>
                  <div className="text-white font-bold text-lg">{selectedTask.title || selectedTask.task_id}</div>
                  <div className="text-slate-400 text-sm">{STATE_STYLES[selectedTask.state]?.label || selectedTask.state}</div>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <div className="text-slate-500 text-xs uppercase tracking-wider mb-3">流转历史</div>
                  <div className="space-y-2.5 max-h-36 overflow-y-auto">
                    {selectedTask.transitions.map((t, idx) => {
                      const fromS = STATE_STYLES[t.from_state]?.label || t.from_state;
                      const toS = STATE_STYLES[t.to_state]?.label || t.to_state;
                      return (
                        <div key={idx} className="flex items-center gap-2.5 text-sm">
                          <span className="text-slate-600 text-xs font-mono">{new Date(t.timestamp).toLocaleTimeString()}</span>
                          <span className="text-slate-400">{fromS}</span>
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-indigo-400"><polyline points="9 18 15 12 9 6"/></svg>
                          <span className="text-emerald-400">{toS}</span>
                        </div>
                      );
                    })}
                    {selectedTask.transitions.length === 0 && <div className="text-slate-600 text-sm">暂无流转记录</div>}
                  </div>
                </div>

                <div>
                  <div className="text-slate-500 text-xs uppercase tracking-wider mb-3">执行控制</div>
                  <div className="flex flex-wrap gap-2">
                    {getNextStates(selectedTask.state).map(nextState => (
                      <button key={nextState} onClick={() => transitionTask(selectedTask.task_id, nextState)}
                        className="btn-aurora text-sm">
                        推进到 {STATE_STYLES[nextState]?.label || nextState}
                      </button>
                    ))}
                    <button onClick={() => transitionTask(selectedTask.task_id, 'cancelled')}
                      className="btn-ghost text-sm text-rose-400 border-rose-500/20 hover:bg-rose-500/10">
                      取消
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-600 py-16 text-sm">选择任务查看详情</div>
          )}
        </div>

        {/* 日志 */}
        <div className="glass p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">实时日志</h2>
            <button onClick={() => setLogs([])} className="text-xs text-slate-600 hover:text-slate-400 transition-colors">清空</button>
          </div>
          <div className="bg-black/30 rounded-xl p-4 h-80 overflow-y-auto font-mono text-xs leading-relaxed border border-white/[0.04]">
            {logs.map((log, idx) => (
              <div key={idx} className={`${
                log.type === 'success' ? 'text-emerald-400' : log.type === 'error' ? 'text-rose-400' : 'text-slate-500'
              }`}>
                <span className="text-slate-700">[{log.time}]</span> {log.message}
              </div>
            ))}
            {logs.length === 0 && <div className="text-slate-700">等待日志...</div>}
            <div ref={logsEndRef} />
          </div>
        </div>
      </div>

      {/* 已完成 */}
      {completedTasks.length > 0 && (
        <div className="glass p-6 mt-6 animate-fade-in">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
            已完成 <span className="text-slate-600 ml-1">{completedTasks.length}</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {completedTasks.slice(0, 8).map(task => {
              const ss = STATE_STYLES[task.state] || { gradient: 'from-slate-500 to-slate-600' };
              return (
                <div key={task.task_id} className="p-3 bg-white/[0.02] rounded-xl border border-white/[0.04]">
                  <div className="flex items-center gap-2">
                    <div className={`w-6 h-6 rounded-md bg-gradient-to-br ${ss.gradient} flex items-center justify-center`}>
                      <span className="text-white text-[10px] font-bold">{(STATE_STYLES[task.state]?.label || '?')[0]}</span>
                    </div>
                    <div className="text-white text-sm truncate">{task.title || task.task_id}</div>
                  </div>
                  <div className="text-slate-600 text-xs mt-1.5">{STATE_STYLES[task.state]?.label} · {task.transitions.length} 次流转</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
