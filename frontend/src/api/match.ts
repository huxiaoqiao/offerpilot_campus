import api from './index'
import { getCurrentUserId } from '../lib/userId'
import type { MatchResult } from '../types/match'

export const matchApi = {
  run: (jobId: string): Promise<MatchResult> =>
    api.post(`/match/${jobId}?user_id=${getCurrentUserId()}`),
  get: (jobId: string): Promise<MatchResult> =>
    api.get(`/match/${jobId}?user_id=${getCurrentUserId()}`),
  compare: (jobIds: string[]): Promise<MatchResult[]> =>
    api.get('/match/compare', { params: { job_ids: jobIds.join(','), user_id: getCurrentUserId() } }),
  delete: (jobId: string): Promise<void> =>
    api.delete(`/match/${jobId}?user_id=${getCurrentUserId()}`),
}
