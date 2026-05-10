import api from './index'
import { getCurrentUserId } from '../lib/userId'
import type { JobPost, JobCreate } from '../types/job'

export const jobsApi = {
  create: (data: JobCreate): Promise<JobPost> =>
    api.post(`/jobs?user_id=${getCurrentUserId()}`, data),
  batch: (jobs: JobCreate[]): Promise<JobPost[]> =>
    api.post(`/jobs/batch?user_id=${getCurrentUserId()}`, { jobs }),
  importCsv: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/jobs/import-csv?user_id=${getCurrentUserId()}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: (params?: Record<string, any>): Promise<{ items: JobPost[]; total: number }> =>
    api.get('/jobs', { params: { user_id: getCurrentUserId(), ...params } }),
  get: (id: string): Promise<JobPost> => api.get(`/jobs/${id}`),
  delete: (id: string): Promise<void> => api.delete(`/jobs/${id}`),
  reparse: (id: string): Promise<JobPost> => api.post(`/jobs/${id}/reparse`),
}
