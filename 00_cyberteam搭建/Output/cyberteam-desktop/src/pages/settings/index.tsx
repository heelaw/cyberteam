import { invoke } from '@tauri-apps/api/core'

interface SettingsProps {
  claudePath: string
  setClaudePath: (path: string) => void
  apiKey: string
  setApiKey: (key: string) => void
}

export default function Settings({ claudePath, setClaudePath, apiKey, setApiKey }: SettingsProps) {
  const handleSave = async () => {
    try {
      await invoke('set_setting', { key: 'claude_path', value: claudePath })
      await invoke('set_setting', { key: 'api_key', value: apiKey })
      alert('设置已保存')
    } catch (e) {
      console.error('Failed to save settings:', e)
      alert('保存失败: ' + String(e))
    }
  }

  return (
    <div className="h-full overflow-auto p-6">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6">设置</h2>

        <div className="space-y-6">
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-4">Claude Code CLI</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Claude CLI 路径
                </label>
                <input
                  type="text"
                  value={claudePath}
                  onChange={(e) => setClaudePath(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="/opt/homebrew/bin/claude"
                />
                <p className="mt-1 text-xs text-slate-400">
                  Claude Code CLI 的安装路径
                </p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-4">API 配置</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="sk-ant-api03-..."
                />
                <p className="mt-1 text-xs text-slate-400">
                  Anthropic API Key，用于 Claude Code CLI 认证
                </p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-4">会话管理</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white">自动保存会话</p>
                  <p className="text-xs text-slate-400">自动保存所有 Claude Code 会话</p>
                </div>
                <input type="checkbox" defaultChecked className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white">SSE 流式输出</p>
                  <p className="text-xs text-slate-400">实时显示 Claude 输出</p>
                </div>
                <input type="checkbox" defaultChecked className="w-5 h-5" />
              </div>
            </div>
          </div>

          <button
            onClick={handleSave}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            保存设置
          </button>
        </div>
      </div>
    </div>
  )
}
