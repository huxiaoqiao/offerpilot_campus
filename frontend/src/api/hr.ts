import api from './index'
import { getCurrentUserId } from '../lib/userId'
import type { HRSimulation } from '../types/hr'

export const hrApi = {
  run: (jobId: string): Promise<HRSimulation> =>
    api.post(`/hr/${jobId}?user_id=${getCurrentUserId()}`),
  get: (jobId: string): Promise<HRSimulation> =>
    api.get(`/hr/${jobId}?user_id=${getCurrentUserId()}`),
  delete: (jobId: string): Promise<void> =>
    api.delete(`/hr/${jobId}?user_id=${getCurrentUserId()}`),
}
