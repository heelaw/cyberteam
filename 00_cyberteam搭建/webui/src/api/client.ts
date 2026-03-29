const API_BASE = '/api'

async function fetchApi(endpoint: string, options?: RequestInit) {
  // 从 zustand persist 存储中读取 token（与 authStore 保持一致）
  let token: string | null = null
  try {
    const persisted = localStorage.getItem('cyberteam-auth')
    if (persisted) {
      const parsed = JSON.parse(persisted)
      token = parsed?.state?.token || null
    }
  } catch {
    // Fallback: 尝试旧 key
    token = localStorage.getItem('auth_token')
  }
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers,
    ...options,
  })
  if (!res.ok) throw new Error(`API Error: ${res.status}`)
  return res.json()
}

export const api = {
  // Generic HTTP methods
  get: (endpoint: string) => fetchApi(endpoint),
  post: (endpoint: string, data?: unknown) =>
    fetchApi(endpoint, { method: 'POST', body: data ? JSON.stringify(data) : undefined }),
  put: (endpoint: string, data?: unknown) =>
    fetchApi(endpoint, { method: 'PUT', body: data ? JSON.stringify(data) : undefined }),
  delete: (endpoint: string) =>
    fetchApi(endpoint, { method: 'DELETE' }),

  // Departments
  getDepartments: () => fetchApi('/departments'),
  createDepartment: (data: unknown) => fetchApi('/departments', { method: 'POST', body: JSON.stringify(data) }),
  updateDepartment: (id: string, data: unknown) => fetchApi(`/departments/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteDepartment: (id: string) => fetchApi(`/departments/${id}`, { method: 'DELETE' }),

  // Agents (built-in from YAML)
  getAgents: () => fetchApi('/agents'),
  getAgentProfile: (name: string) => fetchApi(`/agents/${name}`),

  // Custom Agents (user-created)
  getCustomAgents: () => fetchApi('/agents/custom'),
  createCustomAgent: (data: unknown) => fetchApi('/agents', { method: 'POST', body: JSON.stringify(data) }),
  updateCustomAgent: (id: string, data: unknown) => fetchApi(`/agents/custom/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCustomAgent: (id: string) => fetchApi(`/agents/custom/${id}`, { method: 'DELETE' }),

  // Teams
  getTeams: () => fetchApi('/teams'),
  createTeam: (data: unknown) => fetchApi('/teams', { method: 'POST', body: JSON.stringify(data) }),
  updateTeam: (id: string, data: unknown) => fetchApi(`/teams/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTeam: (id: string) => fetchApi(`/teams/${id}`, { method: 'DELETE' }),

  // Templates
  getTemplates: () => fetchApi('/templates'),
  createTemplate: (data: unknown) => fetchApi('/templates', { method: 'POST', body: JSON.stringify(data) }),
  updateTemplate: (id: string, data: unknown) => fetchApi(`/templates/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTemplate: (id: string) => fetchApi(`/templates/${id}`, { method: 'DELETE' }),

  // Skills
  getSkills: () => fetchApi('/skills'),
  createSkill: (data: unknown) => fetchApi('/skills', { method: 'POST', body: JSON.stringify(data) }),
  updateSkill: (id: string, data: unknown) => fetchApi(`/skills/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteSkill: (id: string) => fetchApi(`/skills/${id}`, { method: 'DELETE' }),

  // Chat (CyberTeam core)
  getConversations: () => fetchApi('/chat'),
  createConversation: (data?: unknown) => fetchApi('/chat', { method: 'POST', body: JSON.stringify(data || {}) }),
  getConversation: (id: string) => fetchApi(`/chat/${id}`),
  deleteConversation: (id: string) => fetchApi(`/chat/${id}`, { method: 'DELETE' }),
  getMessages: (convId: string) => fetchApi(`/chat/${convId}/messages`),
  sendMessage: (convId: string, data: unknown) => fetchApi(`/chat/${convId}/messages`, { method: 'POST', body: JSON.stringify(data) }),

  // Agents (CyberTeam core)
  getAgentProfiles: () => fetchApi('/agents'),
  runAgent: (name: string, data: unknown) => fetchApi(`/agents/${name}/run`, { method: 'POST', body: JSON.stringify(data) }),
}
