/**
 * Auth Store — Zustand store for JWT auth state
 * <!--zh
 * 认证状态管理：登录状态、Token 持久化、用户信息
 * -->
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  username: string
  email?: string
  org_id: string
  role: string
  disabled?: boolean
}

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

async function apiLogin(username: string, password: string): Promise<{ access_token: string }> {
  const form = new URLSearchParams({ username, password })
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Login failed' }))
    throw new Error(err.detail || 'Login failed')
  }
  return res.json()
}

async function apiMe(): Promise<User> {
  const token = useAuthStore.getState().token
  const res = await fetch('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('Unauthorized')
  return res.json()
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        const data = await apiLogin(username, password)
        set({ token: data.access_token })
        // Fetch user info after login
        try {
          const user = await apiMe()
          set({ user, isAuthenticated: true })
        } catch {
          // Token stored but user fetch failed — try with new token
          const user = await apiMe()
          set({ user, isAuthenticated: true })
        }
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false })
      },

      fetchUser: async () => {
        const { token } = useAuthStore.getState()
        if (!token) return
        try {
          const user = await apiMe()
          set({ user, isAuthenticated: true })
        } catch {
          // Token expired or invalid
          set({ token: null, user: null, isAuthenticated: false })
        }
      },
    }),
    {
      name: 'cyberteam-auth',
      partialize: (state) => ({ token: state.token }), // Only persist token
    }
  )
)
