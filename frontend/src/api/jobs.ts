import api from './index'
import type { JobPost, JobCreate } from '../types/job'

export const jobsApi = {
  create: (data: JobCreate): Promise<JobPost> => api.post('/jobs', data),
  batch: (jobs: JobCreate[]): Promise<JobPost[]> =>
    api.post('/jobs/batch', { jobs }),
  importCsv: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/jobs/import-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: (params?: {
    sort_by?: string
    order?: string
    city?: string
    industry?: string
    min_score?: number
    page?: number
    page_size?: number
  }): Promise<{ items: JobPost[]; total: number }> => api.get('/jobs', { params }),
  get: (id: string): Promise<JobPost> => api.get(`/jobs/${id}`),
  delete: (id: string): Promise<void> => api.delete(`/jobs/${id}`),
  reparse: (id: string): Promise<JobPost> => api.post(`/jobs/${id}/reparse`),
}
