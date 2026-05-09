import { create } from 'zustand'
import { interviewApi } from '../api/interview'
import type { InterviewData } from '../types/interview'

interface InterviewState {
  data: InterviewData | null
  loading: boolean
  error: string | null
  selectedQuestionId: string | null
  generate: (jobId: string) => Promise<void>
  fetchData: (jobId: string) => Promise<void>
  deleteData: (jobId: string) => Promise<void>
  selectQuestion: (id: string | null) => void
  clear: () => void
  clearError: () => void
}

export const useInterviewStore = create<InterviewState>((set) => ({
  data: null,
  loading: false,
  error: null,
  selectedQuestionId: null,

  generate: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const data = await interviewApi.generate(jobId)
      set({ data, loading: false, selectedQuestionId: data.questions[0]?.id || null })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  fetchData: async (jobId) => {
    set({ loading: true, error: null })
    try {
      const data = await interviewApi.get(jobId)
      set({ data, loading: false, selectedQuestionId: data.questions[0]?.id || null })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  deleteData: async (jobId) => {
    set({ loading: true, error: null })
    try {
      await interviewApi.delete(jobId)
      set({ data: null, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  selectQuestion: (id) => set({ selectedQuestionId: id }),
  clear: () => set({ data: null, selectedQuestionId: null }),
  clearError: () => set({ error: null }),
}))
