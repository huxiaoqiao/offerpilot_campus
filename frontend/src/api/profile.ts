import api from './index'
import type { Profile, ProfileCreate, ProfileUpdate } from '../types/profile'

export const profileApi = {
  create: (data: ProfileCreate): Promise<Profile> => api.post('/profile', data),
  get: (id: string): Promise<Profile> => api.get(`/profile/${id}`),
  update: (id: string, data: ProfileUpdate): Promise<Profile> => api.put(`/profile/${id}`, data),
  uploadResume: (id: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/profile/${id}/resume/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  updateStructured: (id: string, data: any): Promise<Profile> =>
    api.put(`/profile/${id}/resume/structured`, data),
  updateSkillRatings: (id: string, ratings: Record<string, number>): Promise<Profile> =>
    api.put(`/profile/${id}/skill-ratings`, { skill_ratings: ratings }),
  reparse: (id: string): Promise<Profile> => api.post(`/profile/${id}/resume/reparse`),
}
