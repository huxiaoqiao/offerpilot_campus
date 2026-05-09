import { create } from 'zustand'
import { hrApi } from '../api/hr'
import type { HRSimulation } from '../types/hr'

interface HRState {
  simulation: HRSimulation | null
  loading: boolean
  error: string | null
  runSimulation: (jobId: string) => Promise<void>
  fetchSimulation: (jobId: string) => Promise<void>
  deleteSimulation: (jobId: string) => Promise<void>
  clear: () => void
  clearError: () => void
}

export const useHRStore = create<HRState>((set) => ({
  simulation: null,
  loading: false,
  error: null,

  runSimulation: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const result = await hrApi.run(jobId)
      set({ simulation: result, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  fetchSimulation: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const result = await hrApi.get(jobId)
      set({ simulation: result, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  deleteSimulation: async (jobId) => {
    set({ loading: true, error: null })
    try {
      await hrApi.delete(jobId)
      set({ simulation: null, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  clear: () => set({ simulation: null }),
  clearError: () => set({ error: null }),
}))
