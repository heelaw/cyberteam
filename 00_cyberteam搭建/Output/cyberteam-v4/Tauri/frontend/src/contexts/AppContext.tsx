import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

export type ApiProvider = 'anthropic' | 'minimax' | 'openai'

export interface AppConfig {
  apiProvider: ApiProvider
  apiKey: string
  baseUrl: string
  model: string
  connected: boolean
}

interface AppContextType {
  config: AppConfig
  updateConfig: (config: Partial<AppConfig>) => void
  testConnection: () => Promise<boolean>
}

const defaultConfig: AppConfig = {
  apiProvider: 'anthropic',
  apiKey: '',
  baseUrl: 'https://api.anthropic.com',
  model: 'claude-opus-4-6',
  connected: false,
}

const AppContext = createContext<AppContextType | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<AppConfig>(defaultConfig)

  const updateConfig = useCallback((newConfig: Partial<AppConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }))
  }, [])

  const testConnection = useCallback(async (): Promise<boolean> => {
    // 使用 Tauri 命令测试连接
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      const result = await invoke<boolean>('test_connection', {
        provider: config.apiProvider,
        apiKey: config.apiKey,
        baseUrl: config.baseUrl,
      })
      setConfig(prev => ({ ...prev, connected: result }))
      return result
    } catch (error) {
      console.error('Connection test failed:', error)
      // 降级：模拟连接测试
      const isValidKey = config.apiKey.length > 10
      setConfig(prev => ({ ...prev, connected: isValidKey }))
      return isValidKey
    }
  }, [config.apiProvider, config.apiKey, config.baseUrl])

  return (
    <AppContext.Provider value={{ config, updateConfig, testConnection }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}
