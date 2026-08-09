import { defineStore } from 'pinia'
import api from '@/utils/axios'

export type SiteCopy = Record<string, string>

export const useSiteCopyStore = defineStore('siteCopy', {
  state: () => ({
    copy: {} as SiteCopy,
    loading: false,
    loaded: false,
    error: null as string | null,
  }),

  actions: {
    async fetchCopy(): Promise<void> {
      if (this.loaded || this.loading) return

      this.loading = true
      this.error = null

      try {
        const response = await api.get<SiteCopy>('/site-copy/')
        this.copy = response.data
        this.loaded = true
      } catch (error) {
        console.error('Failed to fetch site copy:', error)
        this.error = 'Failed to load site copy'
      } finally {
        this.loading = false
      }
    },

    get(key: string, fallback = ''): string {
      return this.copy[key] ?? fallback
    },
  },
})
