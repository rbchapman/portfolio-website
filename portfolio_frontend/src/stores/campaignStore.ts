import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'
import type { Campaign } from '../types'
import type { AxiosResponse } from 'axios'

export const useCampaignStore = defineStore('campaign', () => {
    const campaigns = ref<Campaign[]>([])
    const hasError = ref<boolean>(false)
    const isLoading = ref<boolean>(true)

    async function fetchCampaigns() {
        try {
            const response: AxiosResponse<Campaign[]> = await api.get('http://localhost:8000/api/campaigns/')
            campaigns.value = response.data
        } catch(error) {
            console.error('Error loading campaigns:', error)
            hasError.value = true
        } finally {
            isLoading.value = false
        }
    }

    return {
        campaigns,
        hasError,
        isLoading,
        fetchCampaigns
    }
})