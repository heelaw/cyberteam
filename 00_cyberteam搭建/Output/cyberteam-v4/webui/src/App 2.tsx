import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Departments from './pages/Departments';
import Agents from './pages/Agents';
import Teams from './pages/Teams';
import Skills from './pages/Skills';
import ConfigCenter from './pages/config/ConfigCenter';
import StateMachineConfig from './pages/config/StateMachineConfig';
import RBACConfig from './pages/config/RBACConfig';
import ExecutionControl from './pages/ExecutionControl';

const NAV = [
  { path: '/', label: '首页', icon: HomeIcon },
  { path: '/departments', label: '部门', icon: DeptIcon },
  { path: '/agents', label: 'Agent', icon: AgentIcon },
  { path: '/teams', label: '团队', icon: TeamIcon },
  { path: '/skills', label: '技能', icon: SkillIcon },
  { path: '/config', label: '配置', icon: ConfigIcon },
  { path: '/execute', label: '执行', icon: ExecIcon },
];

function HomeIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>;
}
function DeptIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>;
}
function AgentIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>;
}
function TeamIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>;
}
function SkillIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>;
}
function ConfigIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>;
}
function ExecIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>;
}

function Layout({ children }: { children: React.ReactNode }) {
  const loc = useLocation();
  return (
    <div className="flex h-screen overflow-hidden">
      {/* 背景网格 */}
      <div className="fixed inset-0 bg-mesh-bg pointer-events-none" />
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none opacity-[0.03]"
        style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)', backgroundSize: '40px 40px' }} />

      {/* 侧边栏 */}
      <aside className="relative w-64 flex flex-col border-r border-white/[0.06] bg-aurora-sidebar z-10 shrink-0">
        {/* Logo 区域 */}
        <div className="px-6 pt-7 pb-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-glow-sm">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            </div>
            <div>
              <h1 className="text-[15px] font-bold text-white tracking-tight">CyberTeam</h1>
              <p className="text-[10px] text-slate-500 font-medium tracking-wider uppercase">Studio</p>
            </div>
          </div>
        </div>

        {/* 导航区 */}
        <nav className="flex-1 px-3 space-y-0.5" role="navigation" aria-label="主导航">
          <div className="px-3 mb-3">
            <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest">导航</span>
          </div>
          {NAV.map((n) => {
            const isActive = loc.pathname === n.path;
            const Icon = n.icon;
            return (
              <Link
                key={n.path}
                to={n.path}
                aria-current={isActive ? 'page' : undefined}
                className={`
                  relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-medium
                  transition-all duration-200 group
                  ${isActive
                    ? 'bg-white/[0.08] text-white'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/[0.04]'
                  }
                `}
              >
                {/* 激活态左侧极光条 */}
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-gradient-to-b from-indigo-400 to-purple-500" />
                )}
                <span className={`transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-600 group-hover:text-slate-400'}`}>
                  <Icon />
                </span>
                <span>{n.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* 底部状态 */}
        <div className="px-5 py-4 border-t border-white/[0.06]">
          <div className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-2 text-slate-500">
              <span className="status-dot online" />
              <span>系统在线</span>
            </div>
            <span className="text-slate-600 font-mono">v4.1.0</span>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto relative z-10" role="main" id="main-content" tabIndex={-1}>
        {children}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/departments" element={<Departments />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/teams" element={<Teams />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/config" element={<ConfigCenter />} />
          <Route path="/config/state-machine" element={<StateMachineConfig />} />
          <Route path="/config/rbac" element={<RBACConfig />} />
          <Route path="/execute" element={<ExecutionControl />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
