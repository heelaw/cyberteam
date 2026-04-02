import { useState, useEffect } from 'react'
import type { ApiProvider } from '../../types/electron.d'

const PROVIDER_PRESETS = [
  { name: 'Anthropic', provider_type: 'anthropic', protocol: 'anthropic', base_url: 'https://api.anthropic.com' },
  { name: 'MiniMax', provider_type: 'minimax', protocol: 'openai-compatible', base_url: 'https://api.minimax.chat/v1' },
  { name: 'OpenRouter', provider_type: 'openrouter', protocol: 'openrouter', base_url: 'https://openrouter.ai/api/v1' },
  { name: 'Moonshot', provider_type: 'moonshot', protocol: 'openai-compatible', base_url: 'https://api.moonshot.cn/v1' },
]

const PROTOCOLS = [
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'openai-compatible', label: 'OpenAI Compatible' },
  { value: 'bedrock', label: 'AWS Bedrock' },
  { value: 'vertex', label: 'Google Vertex' },
  { value: 'google', label: 'Google AI' },
]

export default function SettingsPage() {
  const [providers, setProviders] = useState<ApiProvider[]>([])
  const [selectedProvider, setSelectedProvider] = useState<ApiProvider | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle')
  const [testError, setTestError] = useState('')
  const [headers, setHeaders] = useState<{ key: string; value: string }[]>([])
  const [models, setModels] = useState<string[]>([])

  useEffect(() => {
    loadProviders()
  }, [])

  async function loadProviders() {
    try {
      const list = await window.electronAPI.providers.list()
      setProviders(list || [])
      // Load first provider or default
      if (list.length > 0 && !selectedProvider) {
        const active = list.find(p => p.is_active) || list[0]
        setSelectedProvider(active)
        loadProviderConfig(active)
      }
    } catch (err) {
      console.error('Failed to load providers:', err)
    }
  }

  function loadProviderConfig(provider: ApiProvider) {
    try {
      const h = JSON.parse(provider.headers_json || '{}')
      setHeaders(Object.entries(h).map(([key, value]) => ({ key, value: value as string })))
      const m = JSON.parse(provider.role_models_json || '[]')
      setModels(Array.isArray(m) ? m : [])
    } catch {
      setHeaders([])
      setModels([])
    }
  }

  async function createProvider(data: Partial<ApiProvider>) {
    try {
      const provider = await window.electronAPI.providers.create(data)
      setProviders([...providers, provider])
      setSelectedProvider(provider)
      setIsEditing(false)
    } catch (err) {
      console.error('Failed to create provider:', err)
    }
  }

  async function updateProvider(id: string, data: Record<string, unknown>) {
    try {
      // Serialize headers and models
      const headersObj: Record<string, string> = {}
      headers.forEach(({ key, value }) => {
        if (key.trim()) headersObj[key.trim()] = value
      })

      const provider = await window.electronAPI.providers.update(id, {
        ...data,
        headers_json: JSON.stringify(headersObj),
        role_models_json: JSON.stringify(models.filter(m => m.trim())),
      })
      if (provider) {
        setProviders(providers.map((p) => (p.id === id ? provider : p)))
        setSelectedProvider(provider)
      }
      setIsEditing(false)
    } catch (err) {
      console.error('Failed to update provider:', err)
    }
  }

  async function deleteProvider(id: string) {
    try {
      await window.electronAPI.providers.delete(id)
      setProviders(providers.filter((p) => p.id !== id))
      if (selectedProvider?.id === id) {
        setSelectedProvider(null)
      }
    } catch (err) {
      console.error('Failed to delete provider:', err)
    }
  }

  async function testProvider(id: string) {
    setTestStatus('testing')
    setTestError('')
    try {
      const result = await window.electronAPI.providers.test(id)
      setTestStatus(result.success ? 'success' : 'error')
      if (!result.success) {
        setTestError(result.error || 'Connection failed')
      }
    } catch (err) {
      setTestStatus('error')
      setTestError(String(err))
    }
    setTimeout(() => setTestStatus('idle'), 3000)
  }

  function applyPreset(preset: typeof PROVIDER_PRESETS[0]) {
    if (!selectedProvider) return
    setSelectedProvider({
      ...selectedProvider,
      ...preset,
    })
  }

  function handleSave() {
    if (!selectedProvider) return
    updateProvider(selectedProvider.id, { ...selectedProvider })
  }

  function setDefaultProvider() {
    if (!selectedProvider) return
    // Set all providers to inactive, then set selected to active
    providers.forEach(async (p) => {
      if (p.id === selectedProvider.id) {
        await window.electronAPI.providers.update(p.id, { is_active: 1 })
      } else if (p.is_active) {
        await window.electronAPI.providers.update(p.id, { is_active: 0 })
      }
    })
    setProviders(providers.map(p => ({
      ...p,
      is_active: p.id === selectedProvider.id ? 1 : 0
    })))
  }

  function addHeader() {
    setHeaders([...headers, { key: '', value: '' }])
  }

  function removeHeader(index: number) {
    setHeaders(headers.filter((_, i) => i !== index))
  }

  function updateHeader(index: number, field: 'key' | 'value', value: string) {
    const newHeaders = [...headers]
    newHeaders[index][field] = value
    setHeaders(newHeaders)
  }

  function addModel() {
    setModels([...models, ''])
  }

  function removeModel(index: number) {
    setModels(models.filter((_, i) => i !== index))
  }

  function updateModel(index: number, value: string) {
    const newModels = [...models]
    newModels[index] = value
    setModels(newModels)
  }

  return (
    <div className="flex h-full">
      {/* 左侧 Provider 列表 */}
      <div className="w-72 bg-[#111118] border-r border-[#2a2a3a] flex flex-col">
        <div className="p-4 border-b border-[#2a2a3a]">
          <h2 className="text-white font-semibold">API Providers</h2>
        </div>

        <div className="flex-1 overflow-y-auto">
          {providers.map((provider) => (
            <div
              key={provider.id}
              onClick={() => {
                setSelectedProvider(provider)
                setIsEditing(false)
                loadProviderConfig(provider)
              }}
              className={`p-4 cursor-pointer border-b border-[#2a2a3a] transition-colors ${
                selectedProvider?.id === provider.id
                  ? 'bg-[#1a1a24]'
                  : 'hover:bg-[#1a1a24]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-white font-medium">{provider.name}</span>
                {provider.is_active ? (
                  <span className="status-dot online" />
                ) : (
                  <span className="status-dot offline" />
                )}
              </div>
              <div className="text-xs text-[#606070] mt-1">
                {provider.protocol || provider.provider_type}
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-[#2a2a3a]">
          <button
            onClick={() => {
              setSelectedProvider(null)
              setIsEditing(true)
            }}
            className="w-full btn btn-primary text-sm"
          >
            + 添加 Provider
          </button>
        </div>
      </div>

      {/* 右侧编辑区 */}
      <div className="flex-1 overflow-y-auto p-6">
        {selectedProvider || isEditing ? (
          <div className="max-w-2xl">
            <h3 className="text-white text-lg font-semibold mb-6">
              {isEditing ? '新建 Provider' : '编辑 Provider'}
            </h3>

            {/* 快速预设 */}
            {!isEditing && (
              <div className="mb-6">
                <label className="block text-sm text-[#a0a0b0] mb-2">快速预设</label>
                <div className="flex gap-2">
                  {PROVIDER_PRESETS.map((preset) => (
                    <button
                      key={preset.name}
                      onClick={() => applyPreset(preset)}
                      className="btn btn-secondary text-xs"
                    >
                      {preset.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* 默认 Provider */}
            {!isEditing && (
              <div className="mb-6 p-4 bg-[#1a1a24] rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">默认 Provider</p>
                    <p className="text-xs text-[#606070] mt-1">用于新会话的默认 API 提供者</p>
                  </div>
                  {selectedProvider?.is_active ? (
                    <span className="text-[#22c55e] text-sm">✓ 当前默认</span>
                  ) : (
                    <button onClick={setDefaultProvider} className="btn btn-secondary text-sm">
                      设为默认
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* 表单 */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">名称</label>
                <input
                  type="text"
                  value={selectedProvider?.name || ''}
                  onChange={(e) =>
                    setSelectedProvider({ ...selectedProvider!, name: e.target.value })
                  }
                  className="w-full"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[#a0a0b0] mb-1">Protocol</label>
                  <select
                    value={selectedProvider?.protocol || ''}
                    onChange={(e) =>
                      setSelectedProvider({ ...selectedProvider!, protocol: e.target.value })
                    }
                    className="w-full"
                  >
                    {PROTOCOLS.map(p => (
                      <option key={p.value} value={p.value}>{p.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-[#a0a0b0] mb-1">Provider Type</label>
                  <input
                    type="text"
                    value={selectedProvider?.provider_type || ''}
                    onChange={(e) =>
                      setSelectedProvider({ ...selectedProvider!, provider_type: e.target.value })
                    }
                    className="w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">Base URL</label>
                <input
                  type="text"
                  value={selectedProvider?.base_url || ''}
                  onChange={(e) =>
                    setSelectedProvider({ ...selectedProvider!, base_url: e.target.value })
                  }
                  className="w-full"
                  placeholder="https://api.example.com/v1"
                />
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">API Key</label>
                <input
                  type="password"
                  value={selectedProvider?.api_key || ''}
                  onChange={(e) =>
                    setSelectedProvider({ ...selectedProvider!, api_key: e.target.value })
                  }
                  className="w-full"
                  placeholder="sk-..."
                />
                {selectedProvider?.api_key && (
                  <p className="text-xs text-[#606070] mt-1">
                    已保存 {selectedProvider.api_key.slice(0, 8)}...
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm text-[#a0a0b0] mb-1">备注</label>
                <textarea
                  value={selectedProvider?.notes || ''}
                  onChange={(e) =>
                    setSelectedProvider({ ...selectedProvider!, notes: e.target.value })
                  }
                  className="w-full h-20 resize-none"
                />
              </div>

              {/* 自定义 Headers */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-[#a0a0b0]">自定义 Headers</label>
                  <button onClick={addHeader} className="text-xs text-[#6366f1] hover:text-[#818cf8]">
                    + 添加 Header
                  </button>
                </div>
                {headers.map((header, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={header.key}
                      onChange={(e) => updateHeader(index, 'key', e.target.value)}
                      placeholder="Header Name"
                      className="flex-1"
                    />
                    <input
                      type="text"
                      value={header.value}
                      onChange={(e) => updateHeader(index, 'value', e.target.value)}
                      placeholder="Header Value"
                      className="flex-1"
                    />
                    <button onClick={() => removeHeader(index)} className="text-[#ef4444] hover:text-[#dc2626]">
                      ✕
                    </button>
                  </div>
                ))}
                {headers.length === 0 && (
                  <p className="text-xs text-[#606070]">无自定义 Headers</p>
                )}
              </div>

              {/* 支持的 Models */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-[#a0a0b0]">支持的 Models</label>
                  <button onClick={addModel} className="text-xs text-[#6366f1] hover:text-[#818cf8]">
                    + 添加 Model
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {models.map((model, index) => (
                    <div key={index} className="flex items-center gap-1 bg-[#1a1a24] rounded px-2 py-1">
                      <input
                        type="text"
                        value={model}
                        onChange={(e) => updateModel(index, e.target.value)}
                        placeholder="model-name"
                        className="bg-transparent text-white text-sm w-32"
                      />
                      <button onClick={() => removeModel(index)} className="text-[#606070] hover:text-[#ef4444]">
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
                {models.length === 0 && (
                  <p className="text-xs text-[#606070]">留空则使用默认模型列表</p>
                )}
              </div>

              <div className="flex items-center gap-4 pt-4">
                <button onClick={handleSave} className="btn btn-primary">
                  保存
                </button>

                {!isEditing && (
                  <>
                    <button
                      onClick={() => testProvider(selectedProvider!.id)}
                      disabled={testStatus === 'testing'}
                      className="btn btn-secondary"
                    >
                      {testStatus === 'testing' ? '测试中...' : '测试连接'}
                    </button>

                    {testStatus === 'success' && (
                      <span className="text-[#22c55e] text-sm">✓ 连接成功</span>
                    )}
                    {testStatus === 'error' && (
                      <span className="text-[#ef4444] text-sm">✗ {testError}</span>
                    )}

                    <button
                      onClick={() => deleteProvider(selectedProvider!.id)}
                      className="btn btn-danger ml-auto"
                    >
                      删除
                    </button>
                  </>
                )}

                {isEditing && (
                  <button
                    onClick={() => {
                      if (selectedProvider) {
                        createProvider(selectedProvider)
                      } else {
                        createProvider({
                          name: 'New Provider',
                          provider_type: 'anthropic',
                          protocol: 'anthropic',
                          base_url: '',
                          api_key: '',
                        })
                      }
                    }}
                    className="btn btn-primary"
                  >
                    创建
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-[#606070]">
            <p className="text-lg mb-2">⚙️ 选择一个 Provider</p>
            <p className="text-sm">或创建一个新的 Provider</p>
          </div>
        )}
      </div>
    </div>
  )
}
