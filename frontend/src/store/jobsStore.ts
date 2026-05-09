import { create } from 'zustand'
import { jobsApi } from '../api/jobs'
import type { JobPost, JobCreate } from '../types/job'

interface JobsState {
  jobs: JobPost[]
  total: number
  loading: boolean
  error: string | null
  currentPage: number
  pageSize: number
  filters: {
    sort_by?: string
    order?: string
    city?: string
    industry?: string
    min_score?: number
  }
  fetchJobs: (params?: Record<string, any>) => Promise<void>
  createJob: (data: JobCreate) => Promise<void>
  batchCreate: (jobs: JobCreate[]) => Promise<void>
  importCsv: (file: File) => Promise<void>
  deleteJob: (id: string) => Promise<void>
  reparse: (id: string) => Promise<void>
  setPage: (page: number) => void
  setFilters: (filters: Record<string, any>) => void
  clearError: () => void
}

export const useJobsStore = create<JobsState>((set, get) => ({
  jobs: [],
  total: 0,
  loading: false,
  error: null,
  currentPage: 0,
  pageSize: 20,
  filters: {},

  fetchJobs: async (extraParams) => {
    set({ loading: true, error: null })
    try {
      const { currentPage, pageSize, filters } = get()
      const params = {
        page: currentPage + 1,
        page_size: pageSize,
        ...filters,
        ...extraParams,
      }
      const result = await jobsApi.list(params)
      set({ jobs: result.items || result as any, total: result.total || 0, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  createJob: async (data) => {
    set({ loading: true, error: null })
    try {
      await jobsApi.create(data)
      await get().fetchJobs()
    } catch (e: any) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  batchCreate: async (jobs) => {
    set({ loading: true, error: null })
    try {
      await jobsApi.batch(jobs)
      await get().fetchJobs()
    } catch (e: any) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  importCsv: async (file) => {
    set({ loading: true, error: null })
    try {
      await jobsApi.importCsv(file)
      await get().fetchJobs()
    } catch (e: any) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  deleteJob: async (id) => {
    set({ loading: true, error: null })
    try {
      await jobsApi.delete(id)
      await get().fetchJobs()
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  reparse: async (id) => {
    set({ loading: true, error: null })
    try {
      await jobsApi.reparse(id)
      await get().fetchJobs()
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  setPage: (page) => {
    set({ currentPage: page })
    get().fetchJobs()
  },

  setFilters: (filters) => {
    set({ filters: { ...get().filters, ...filters }, currentPage: 0 })
    get().fetchJobs()
  },

  clearError: () => set({ error: null }),
}))
