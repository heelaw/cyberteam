'use client'

import { useEffect, useState } from 'react'
import { loadRuntimeState, type RuntimeState } from '../lib/runtime-api'

export function RuntimeStatus() {
  const [state, setState] = useState<RuntimeState | null>(null)

  useEffect(() => {
    loadRuntimeState().then(setState)
  }, [])

  if (!state) {
    return null
  }

  const databaseCounts = state.database?.counts ?? {}

  return (
    <div className="panel">
      <h3 className="sectionTitle">运行时状态</h3>
      <div className="timeline">
        <div className="timelineItem">
          <span>Platform</span>
          <span className="subtle">{state.platform} · {state.version}</span>
        </div>
        <div className="timelineItem">
          <span>Database</span>
          <span className="subtle">{state.database?.path ?? 'unknown'}</span>
        </div>
        <div className="timelineItem">
          <span>Companies</span>
          <span className="subtle">{databaseCounts.companies ?? 0}</span>
        </div>
        <div className="timelineItem">
          <span>Messages</span>
          <span className="subtle">{databaseCounts.messages ?? 0}</span>
        </div>
        <div className="timelineItem">
          <span>Claude</span>
          <span className="subtle">{state.claude.installed ? state.claude.status : 'missing'}</span>
        </div>
      </div>
    </div>
  )
}
