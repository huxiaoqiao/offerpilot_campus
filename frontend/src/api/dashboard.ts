import api from './index'
import type { Application, ApplicationCreate, BoardStats } from '../types/dashboard'

export const dashboardApi = {
  createApplication: (data: ApplicationCreate): Promise<Application> =>
    api.post('/dashboard/applications', data),
  listApplications: (): Promise<Application[]> =>
    api.get('/dashboard/applications'),
  getApplication: (id: string): Promise<Application> =>
    api.get(`/dashboard/applications/${id}`),
  updateApplication: (id: string, data: Partial<Application>): Promise<Application> =>
    api.put(`/dashboard/applications/${id}`, data),
  deleteApplication: (id: string): Promise<void> =>
    api.delete(`/dashboard/applications/${id}`),
  getStats: (): Promise<BoardStats> => api.get('/dashboard/stats'),
}
