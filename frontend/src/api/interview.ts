import api from './index'
import { getCurrentUserId } from '../lib/userId'
import type { InterviewData } from '../types/interview'

export const interviewApi = {
  generate: (jobId: string): Promise<InterviewData> =>
    api.post(`/interview/${jobId}?user_id=${getCurrentUserId()}`),
  get: (jobId: string): Promise<InterviewData> =>
    api.get(`/interview/${jobId}?user_id=${getCurrentUserId()}`),
  delete: (jobId: string): Promise<void> =>
    api.delete(`/interview/${jobId}?user_id=${getCurrentUserId()}`),
}
