import api from './index'
import type { HRSimulation } from '../types/hr'

export const hrApi = {
  run: (jobId: string): Promise<HRSimulation> => api.post(`/hr/${jobId}`),
  get: (jobId: string): Promise<HRSimulation> => api.get(`/hr/${jobId}`),
  delete: (jobId: string): Promise<void> => api.delete(`/hr/${jobId}`),
}
