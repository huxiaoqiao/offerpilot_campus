import { create } from 'zustand'
import { profileApi } from '../api/profile'
import type { Profile, ProfileCreate, ProfileUpdate } from '../types/profile'

interface ProfileState {
  profile: Profile | null
  loading: boolean
  error: string | null
  fetchProfile: (id: string) => Promise<void>
  createProfile: (data: ProfileCreate) => Promise<string>
  updateProfile: (id: string, data: ProfileUpdate) => Promise<void>
  uploadResume: (id: string, file: File) => Promise<void>
  reparse: (id: string) => Promise<void>
  updateSkillRatings: (id: string, ratings: Record<string, number>) => Promise<void>
  clearError: () => void
}

export const useProfileStore = create<ProfileState>((set) => ({
  profile: null,
  loading: false,
  error: null,

  fetchProfile: async (id) => {
    set({ loading: true, error: null })
    try {
      const profile = await profileApi.get(id)
      set({ profile, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  createProfile: async (data) => {
    set({ loading: true, error: null })
    try {
      const profile = await profileApi.create(data)
      set({ profile, loading: false })
      return profile.id
    } catch (e: any) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  updateProfile: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const profile = await profileApi.update(id, data)
      set({ profile, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  uploadResume: async (id, file) => {
    set({ loading: true, error: null })
    try {
      await profileApi.uploadResume(id, file)
      const profile = await profileApi.get(id)
      set({ profile, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  reparse: async (id) => {
    set({ loading: true, error: null })
    try {
      const profile = await profileApi.reparse(id)
      set({ profile, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  updateSkillRatings: async (id, ratings) => {
    set({ loading: true, error: null })
    try {
      const profile = await profileApi.updateSkillRatings(id, ratings)
      set({ profile, loading: false })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
