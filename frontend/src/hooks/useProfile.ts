import { useProfileStore } from '../store/profileStore'

/**
 * Re-export store hook for convenience.
 * All profile state management is in profileStore.
 */
export const useProfile = useProfileStore
