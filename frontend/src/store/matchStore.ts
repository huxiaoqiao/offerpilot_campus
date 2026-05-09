import { create } from 'zustand'
import { matchApi } from '../api/match'
import type { MatchResult } from '../types/match'

interface MatchState {
  currentResult: MatchResult | null
  compareResults: MatchResult[]
  loading: boolean
  error: string | null
  runMatch: (jobId: string) => Promise<void>
  fetchMatch: (jobId: string) => Promise<void>
  compare: (jobIds: string[]) => Promise<void>
  deleteMatch: (jobId: string) => Promise<void>
  clearResult: () => void
  clearError: () => void
}

export const useMatchStore = create<MatchState>((set) => ({
  currentResult: null,
  compareResults: [],
  loading: false,
  error: null,

  runMatch: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const result = await matchApi.run(jobId)
      set({ currentResult: result, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  fetchMatch: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const result = await matchApi.get(jobId)
      set({ currentResult: result, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  compare: async (jobIds) => {
    set({ loading: true, error: null })
    try {
      const results = await matchApi.compare(jobIds)
      set({ compareResults: results, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  deleteMatch: async (jobId) => {
    set({ loading: true, error: null })
    try {
      await matchApi.delete(jobId)
      set({ currentResult: null, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  clearResult: () => set({ currentResult: null }),
  clearError: () => set({ error: null }),
}))
