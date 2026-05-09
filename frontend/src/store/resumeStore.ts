import { create } from 'zustand'
import { resumeApi } from '../api/resume'
import type { ResumeRewrite } from '../types/resume'

interface ResumeState {
  currentResume: ResumeRewrite | null
  versions: ResumeRewrite[]
  htmlPreview: string
  loading: boolean
  error: string | null
  generate: (jobId: string) => Promise<void>
  fetchResume: (jobId: string) => Promise<void>
  fetchVersions: (jobId: string) => Promise<void>
  fetchHtmlPreview: (jobId: string) => Promise<void>
  deleteResume: (jobId: string) => Promise<void>
  clear: () => void
  clearError: () => void
}

export const useResumeStore = create<ResumeState>((set) => ({
  currentResume: null,
  versions: [],
  htmlPreview: '',
  loading: false,
  error: null,

  generate: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const result = await resumeApi.generate(jobId)
      set({ currentResume: result, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  fetchResume: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const result = await resumeApi.get(jobId)
      set({ currentResume: result, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  fetchVersions: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const result = await resumeApi.versions(jobId)
      set({ versions: result, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  fetchHtmlPreview: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const html = await resumeApi.htmlPreview(jobId)
      set({ htmlPreview: html, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  deleteResume: async (jobId) => {
    set({ loading: true, error: null })
    try {
      await resumeApi.delete(jobId)
      set({ currentResume: null, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  clear: () => set({ currentResume: null, versions: [], htmlPreview: '' }),
  clearError: () => set({ error: null }),
}))
