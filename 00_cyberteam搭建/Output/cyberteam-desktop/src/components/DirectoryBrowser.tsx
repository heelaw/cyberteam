import { useState, useEffect } from 'react'

interface DirEntry {
  name: string
  path: string
}

interface BrowseResult {
  current: string
  parent: string | null
  directories: DirEntry[]
  error: string | null
}

interface DirectoryBrowserProps {
  initialPath?: string
  onSelect: (path: string) => void
  onCancel: () => void
}

export default function DirectoryBrowser({ initialPath, onSelect, onCancel }: DirectoryBrowserProps) {
  const [currentPath, setCurrentPath] = useState(initialPath || '')
  const [result, setResult] = useState<BrowseResult | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    browseDirectory(currentPath)
  }, [])

  async function browseDirectory(path: string) {
    setIsLoading(true)
    setError('')
    try {
      const data = await window.electronAPI.files.browse(path)
      setResult(data)
      setCurrentPath(data.current)
    } catch (err) {
      setError(String(err))
    } finally {
      setIsLoading(false)
    }
  }

  function navigateTo(path: string) {
    browseDirectory(path)
  }

  function navigateUp() {
    if (result?.parent) {
      navigateTo(result.parent)
    }
  }

  function navigateHome() {
    window.electronAPI.system.getHomeDirectory().then(home => {
      browseDirectory(home)
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#111118] border border-[#2a2a3a] rounded-lg w-[600px] max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-[#2a2a3a] flex items-center justify-between">
          <h3 className="text-white font-semibold">选择工作目录</h3>
          <button onClick={onCancel} className="text-[#606070] hover:text-white">✕</button>
        </div>

        {/* Path bar */}
        <div className="p-3 border-b border-[#2a2a3a] flex items-center gap-2">
          <button onClick={navigateHome} className="btn btn-secondary text-xs" title="主目录">
            🏠
          </button>
          <button onClick={navigateUp} className="btn btn-secondary text-xs" disabled={!result?.parent} title="上级目录">
            ⬆️
          </button>
          <div className="flex-1 bg-[#1a1a24] rounded px-3 py-1.5 text-sm text-white truncate">
            {currentPath || '/'}
          </div>
        </div>

        {/* Directory list */}
        <div className="flex-1 overflow-y-auto p-2">
          {isLoading && (
            <div className="flex items-center justify-center h-32 text-[#606070]">
              加载中...
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-32 text-[#ef4444]">
              {error}
            </div>
          )}

          {result?.error && !error && (
            <div className="flex items-center justify-center h-32 text-[#ef4444]">
              {result.error}
            </div>
          )}

          {result && !result.error && result.directories.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-32 text-[#606070]">
              <p>空目录</p>
              <button
                onClick={() => onSelect(currentPath)}
                className="mt-2 btn btn-primary text-sm"
              >
                选择此目录
              </button>
            </div>
          )}

          {result && !result.error && result.directories.map((dir) => (
            <div
              key={dir.path}
              onClick={() => navigateTo(dir.path)}
              className="flex items-center gap-2 px-3 py-2 rounded hover:bg-[#1a1a24] cursor-pointer text-white"
            >
              <span>📁</span>
              <span className="flex-1 truncate">{dir.name}</span>
              <span className="text-[#606070] text-xs">→</span>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#2a2a3a] flex items-center justify-between">
          <div className="text-xs text-[#606070]">
            {result?.directories.length || 0} 个子目录
          </div>
          <div className="flex gap-2">
            <button onClick={onCancel} className="btn btn-secondary">
              取消
            </button>
            <button
              onClick={() => onSelect(currentPath)}
              className="btn btn-primary"
              disabled={!currentPath}
            >
              选择此目录
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
