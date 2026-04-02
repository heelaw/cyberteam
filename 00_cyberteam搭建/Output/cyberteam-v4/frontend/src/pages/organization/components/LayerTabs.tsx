/**
 * LayerTabs - 讨论层/执行层切换 Tab
 *
 * 功能：
 * - 切换显示讨论层/执行层/全部
 * - 显示各层级的节点统计
 */
import React, { memo } from 'react'
import { Tabs, Badge } from 'antd'
import type { OrgNode } from '@/types/organization'

// Props 接口
export interface LayerTabsProps {
  activeLayer: 'all' | 'discuss' | 'execute'
  onChange: (layer: 'all' | 'discuss' | 'execute') => void
  discussCount: number
  executeCount: number
}

// LayerTabs 组件
export const LayerTabs: React.FC<LayerTabsProps> = memo(({
  activeLayer,
  onChange,
  discussCount,
  executeCount,
}) => {
  const tabItems = [
    {
      key: 'all',
      label: (
        <span className="flex items-center gap-2">
          全部组织
        </span>
      ),
    },
    {
      key: 'discuss',
      label: (
        <span className="flex items-center gap-2">
          <span>💭</span>
          讨论层
          <Badge count={discussCount} size="small" style={{ backgroundColor: '#8b5cf6' }} />
        </span>
      ),
    },
    {
      key: 'execute',
      label: (
        <span className="flex items-center gap-2">
          <span>⚙️</span>
          执行层
          <Badge count={executeCount} size="small" style={{ backgroundColor: '#10b981' }} />
        </span>
      ),
    },
  ]

  return (
    <Tabs
      activeKey={activeLayer}
      onChange={(key) => onChange(key as 'all' | 'discuss' | 'execute')}
      items={tabItems}
      size="small"
    />
  )
})

LayerTabs.displayName = 'LayerTabs'

export default LayerTabs
