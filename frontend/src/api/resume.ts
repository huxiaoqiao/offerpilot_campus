import api from './index'
import { getCurrentUserId } from '../lib/userId'
import type { ResumeRewrite } from '../types/resume'

export const resumeApi = {
  generate: (jobId: string): Promise<ResumeRewrite> =>
    api.post(`/resume/${jobId}?user_id=${getCurrentUserId()}`),
  get: (jobId: string): Promise<ResumeRewrite> =>
    api.get(`/resume/${jobId}?user_id=${getCurrentUserId()}`),
  versions: (jobId: string): Promise<ResumeRewrite[]> =>
    api.get(`/resume/${jobId}/versions?user_id=${getCurrentUserId()}`),
  htmlPreview: (jobId: string): Promise<string> =>
    api.get(`/resume/${jobId}/html?user_id=${getCurrentUserId()}`, { responseType: 'text' }),
  delete: (jobId: string): Promise<void> =>
    api.delete(`/resume/${jobId}?user_id=${getCurrentUserId()}`),
}
