import { create } from 'zustand'
import { dashboardApi } from '../api/dashboard'
import type { Application, ApplicationCreate, BoardStats } from '../types/dashboard'

interface DashboardState {
  applications: Application[]
  stats: BoardStats | null
  loading: boolean
  error: string | null
  selectedApp: Application | null
  fetchApplications: () => Promise<void>
  fetchStats: () => Promise<void>
  createApplication: (data: ApplicationCreate) => Promise<void>
  updateApplication: (id: string, data: Partial<Application>) => Promise<void>
  deleteApplication: (id: string) => Promise<void>
  selectApp: (app: Application | null) => void
  clearError: () => void
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  applications: [],
  stats: null,
  loading: false,
  error: null,
  selectedApp: null,

  fetchApplications: async () => {
    set({ loading: true, error: null })
    try {
      const applications = await dashboardApi.listApplications()
      set({ applications, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  fetchStats: async () => {
    try {
      const stats = await dashboardApi.getStats()
      set({ stats })
    } catch (e: any) {
      set({ error: e.message })
    }
  },

  createApplication: async (data) => {
    set({ loading: true, error: null })
    try {
      await dashboardApi.createApplication(data)
      await get().fetchApplications()
      await get().fetchStats()
    } catch (e: any) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  updateApplication: async (id, data) => {
    set({ loading: true, error: null })
    try {
      await dashboardApi.updateApplication(id, data)
      await get().fetchApplications()
      await get().fetchStats()
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  deleteApplication: async (id) => {
    set({ loading: true, error: null })
    try {
      await dashboardApi.deleteApplication(id)
      await get().fetchApplications()
      await get().fetchStats()
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  selectApp: (app) => set({ selectedApp: app }),
  clearError: () => set({ error: null }),
}))
