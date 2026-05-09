import api from './index'
import type { MatchResult } from '../types/match'

export const matchApi = {
  run: (jobId: string): Promise<MatchResult> => api.post(`/match/${jobId}`),
  get: (jobId: string): Promise<MatchResult> => api.get(`/match/${jobId}`),
  compare: (jobIds: string[]): Promise<MatchResult[]> =>
    api.get('/match/compare', { params: { job_ids: jobIds.join(',') } }),
  delete: (jobId: string): Promise<void> => api.delete(`/match/${jobId}`),
}
