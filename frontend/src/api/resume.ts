import api from './index'
import type { ResumeRewrite } from '../types/resume'

export const resumeApi = {
  generate: (jobId: string): Promise<ResumeRewrite> => api.post(`/resume/${jobId}`),
  get: (jobId: string): Promise<ResumeRewrite> => api.get(`/resume/${jobId}`),
  versions: (jobId: string): Promise<ResumeRewrite[]> =>
    api.get(`/resume/${jobId}/versions`),
  htmlPreview: (jobId: string): Promise<string> =>
    api.get(`/resume/${jobId}/html`, { responseType: 'text' }),
  delete: (jobId: string): Promise<void> => api.delete(`/resume/${jobId}`),
}
