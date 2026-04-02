import { useState } from 'react'
import { useApp, type ApiProvider } from '@/contexts/AppContext'
import { cn } from '@/utils/cn'
import {
  Settings,
  Key,
  Globe,
  Cpu,
  TestTube,
  Save,
  RotateCcw,
  CheckCircle,
  XCircle,
  Loader2,
} from 'lucide-react'

const PROVIDER_OPTIONS: { value: ApiProvider; label: string; models: string[] }[] = [
  {
    value: 'anthropic',
    label: 'Anthropic',
    models: ['claude-opus-4-6', 'claude-sonnet-4-6', 'claude-haiku-4-5'],
  },
  {
    value: 'minimax',
    label: 'MiniMax',
    models: ['MiniMax-Text-01', 'MiniMax-Reasoning'],
  },
  {
    value: 'openai',
    label: 'OpenAI',
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'],
  },
]

export default function SettingsPage() {
  const { config, updateConfig, testConnection } = useApp()
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null)
  const [saving, setSaving] = useState(false)

  const currentProvider = PROVIDER_OPTIONS.find((p) => p.value === config.apiProvider)
  const models = currentProvider?.models || []

  const handleProviderChange = (provider: ApiProvider) => {
    const newBaseUrl = provider === 'anthropic'
      ? 'https://api.anthropic.com'
      : provider === 'minimax'
      ? 'https://api.minimax.chat'
      : 'https://api.openai.com'
    updateConfig({
      apiProvider: provider,
      baseUrl: newBaseUrl,
      model: PROVIDER_OPTIONS.find((p) => p.value === provider)?.models[0] || '',
    })
  }

  const handleTestConnection = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const success = await testConnection()
      setTestResult(success ? 'success' : 'error')
    } catch {
      setTestResult('error')
    } finally {
      setTesting(false)
    }
  }

  const handleSave = () => {
    setSaving(true)
    // 保存配置到 localStorage
    localStorage.setItem('cyberteam_config', JSON.stringify(config))
    setTimeout(() => setSaving(false), 500)
  }

  const handleReset = () => {
    updateConfig({
      apiProvider: 'anthropic',
      apiKey: '',
      baseUrl: 'https://api.anthropic.com',
      model: 'claude-opus-4-6',
      connected: false,
    })
    setTestResult(null)
  }

  return (
    <div className="h-full overflow-auto p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-[var(--color-bg-tertiary)]">
            <Settings className="w-5 h-5 text-[var(--color-accent)]" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-[var(--color-text-primary)]">系统设置</h1>
            <p className="text-sm text-[var(--color-text-secondary)]">配置 API 连接和模型参数</p>
          </div>
        </div>

        {/* Settings Card */}
        <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border)] overflow-hidden">
          {/* API Provider Section */}
          <div className="p-5 border-b border-[var(--color-border)]">
            <div className="flex items-center gap-2 mb-4">
              <Globe className="w-4 h-4 text-[var(--color-text-secondary)]" />
              <h2 className="text-sm font-medium text-[var(--color-text-primary)]">API Provider</h2>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {PROVIDER_OPTIONS.map((provider) => (
                <button
                  key={provider.value}
                  onClick={() => handleProviderChange(provider.value)}
                  className={cn(
                    'px-4 py-2.5 rounded-lg text-sm font-medium transition-all',
                    config.apiProvider === provider.value
                      ? 'bg-[var(--color-accent)] text-white'
                      : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
                  )}
                >
                  {provider.label}
                </button>
              ))}
            </div>
          </div>

          {/* API Key Section */}
          <div className="p-5 border-b border-[var(--color-border)]">
            <div className="flex items-center gap-2 mb-4">
              <Key className="w-4 h-4 text-[var(--color-text-secondary)]" />
              <h2 className="text-sm font-medium text-[var(--color-text-primary)]">API Key</h2>
            </div>
            <div className="relative">
              <input
                type="password"
                value={config.apiKey}
                onChange={(e) => updateConfig({ apiKey: e.target.value })}
                placeholder="sk-ant-..."
                className="w-full px-4 py-2.5 bg-[var(--color-bg-tertiary)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent)] transition-colors"
              />
            </div>
          </div>

          {/* Base URL Section */}
          <div className="p-5 border-b border-[var(--color-border)]">
            <div className="flex items-center gap-2 mb-4">
              <Globe className="w-4 h-4 text-[var(--color-text-secondary)]" />
              <h2 className="text-sm font-medium text-[var(--color-text-primary)]">Base URL</h2>
            </div>
            <input
              type="text"
              value={config.baseUrl}
              onChange={(e) => updateConfig({ baseUrl: e.target.value })}
              placeholder="https://api.anthropic.com"
              className="w-full px-4 py-2.5 bg-[var(--color-bg-tertiary)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent)] transition-colors"
            />
          </div>

          {/* Model Section */}
          <div className="p-5 border-b border-[var(--color-border)]">
            <div className="flex items-center gap-2 mb-4">
              <Cpu className="w-4 h-4 text-[var(--color-text-secondary)]" />
              <h2 className="text-sm font-medium text-[var(--color-text-primary)]">Model</h2>
            </div>
            <select
              value={config.model}
              onChange={(e) => updateConfig({ model: e.target.value })}
              className="w-full px-4 py-2.5 bg-[var(--color-bg-tertiary)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent)] transition-colors cursor-pointer"
            >
              {models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>

          {/* Test Connection */}
          <div className="p-5 border-b border-[var(--color-border)]">
            <div className="flex items-center gap-3">
              <button
                onClick={handleTestConnection}
                disabled={testing || !config.apiKey}
                className={cn(
                  'flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all',
                  testing || !config.apiKey
                    ? 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)] cursor-not-allowed'
                    : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-primary)] hover:bg-[var(--color-border)]'
                )}
              >
                {testing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <TestTube className="w-4 h-4" />
                )}
                测试连接
              </button>

              {testResult && (
                <div className="flex items-center gap-2">
                  {testResult === 'success' ? (
                    <>
                      <CheckCircle className="w-4 h-4 text-[var(--color-success)]" />
                      <span className="text-sm text-[var(--color-success)]">连接成功</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-4 h-4 text-[var(--color-error)]" />
                      <span className="text-sm text-[var(--color-error)]">连接失败</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="p-5 flex items-center gap-3">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-5 py-2.5 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white rounded-lg text-sm font-medium transition-colors"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              保存
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-5 py-2.5 bg-[var(--color-bg-tertiary)] hover:bg-[var(--color-border)] text-[var(--color-text-secondary)] rounded-lg text-sm font-medium transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              重置
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
