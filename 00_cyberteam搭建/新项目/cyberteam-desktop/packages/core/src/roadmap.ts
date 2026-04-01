export interface RoadmapPhase {
  id: string
  name: string
  status: 'done' | 'in-progress' | 'next' | 'planned'
  goal: string
  proof: string
  question: string
  sortOrder?: number
  createdAt?: string
  updatedAt?: string
}

export function createRoadmap(): RoadmapPhase[] {
  return [
    {
      id: 'phase-0',
      sortOrder: 0,
      name: '本地桌面骨架',
      status: 'done',
      goal: 'Electron + Next.js + SQLite 跑通',
      proof: '可以启动、浏览页面、读取种子态。',
      question: '如果没有桌面壳，这个系统还剩什么？',
    },
    {
      id: 'phase-1',
      sortOrder: 1,
      name: '运行时闭环',
      status: 'done',
      goal: 'IPC / preload / runtime snapshot 打通',
      proof: '前端已能读写 SQLite，页面能刷新实时状态。',
      question: '系统的单一事实源在哪里？',
    },
    {
      id: 'phase-2',
      sortOrder: 2,
      name: '组织与对话协作',
      status: 'in-progress',
      goal: '把组织、聊天、Playground 串成工作流',
      proof: '组织页、聊天页、Playground 页已存在并写回数据库。',
      question: '任务从输入到审核，是否形成了闭环？',
    },
    {
      id: 'phase-3',
      sortOrder: 3,
      name: '质量门控',
      status: 'next',
      goal: '把验证、审核、回滚和日志变成默认路径',
      proof: '当前已有构建验证，但还缺产品内质量仪表盘。',
      question: '当结果不可信时，系统如何自动拦下？',
    },
    {
      id: 'phase-4',
      sortOrder: 4,
      name: '能力扩展',
      status: 'planned',
      goal: '把更多 Agent、Skill、模板接到市场层',
      proof: '市场页已显示种子资源，后续可继续增长。',
      question: '新能力是怎么被发现、分发和复用的？',
    },
  ]
}
