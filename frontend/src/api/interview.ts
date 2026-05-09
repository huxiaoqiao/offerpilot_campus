import api from './index'
import type { InterviewData } from '../types/interview'

export const interviewApi = {
  generate: (jobId: string): Promise<InterviewData> =>
    api.post(`/interview/${jobId}`),
  get: (jobId: string): Promise<InterviewData> =>
    api.get(`/interview/${jobId}`),
  delete: (jobId: string): Promise<void> =>
    api.delete(`/interview/${jobId}`),
}
