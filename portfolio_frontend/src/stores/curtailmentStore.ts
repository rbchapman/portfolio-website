import { defineStore } from 'pinia'
import { useEnergyStore } from './energyStore'
import api from '@/utils/axios'

interface HourlyCurtailment {
    hour: string
    curtailed_mwh: number
    redispatch_up: number  // 720 - congestion signal, not curtailment
    spot_price: number
    revenue_lost: number
}

interface DailyCurtailmentInsights {
    total_curtailed_mwh: number
    estimated_revenue_lost?: number
    estimated_revenue_lost_usd?: number
    peak_curtailment_mwh: number
    peak_curtailment_hour: string
    curtailment_hours: number
    negative_price_hours: number
    negative_price_curtailed_mwh: number
}

interface DailyCurtailmentData {
    date: string
    hourly_data: HourlyCurtailment[]
    daily_insights: DailyCurtailmentInsights
    was_cached: boolean
}

interface MonthlyCurtailment {
    year: number
    month: number
    label: string
    total_curtailed_mwh: number
    total_revenue_lost_eur: number
    avg_daily_curtailed_mwh: number
    days_with_curtailment: number
    worst_day: string
    worst_day_mwh: number
    total_curtailment_pct: number | null
    transmission_curtailment_pct: number | null
    distribution_curtailment_pct: number | null
}

interface AnnualTotals {
    [year: number]: {
        total_curtailed_mwh: number
        total_revenue_lost_eur: number
    }
}

interface MonthlyData {
    monthly_data: MonthlyCurtailment[]
    annual_totals: AnnualTotals
}

export const useCurtailmentStore = defineStore('curtailment', {
    state: () => ({
        // Daily view
        selectedDate: '2024-04-15',
        dailyData: null as DailyCurtailmentData | null,
        dailyLoading: false,

        // Monthly/annual view
        monthlyData: null as MonthlyData | null,
        monthlyLoading: false,

        // Toggle between daily chart and monthly chart
        view: 'daily' as 'daily' | 'monthly',
    }),

    getters: {
        formattedDate: (state) => {
            const d = new Date(state.selectedDate)
            return d.toLocaleDateString('en-US', {
                weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
            })
        },

    // Annual totals for headline stat cards
        annual2024: (state) => state.monthlyData?.annual_totals[2024] ?? null,
        annual2025: (state) => state.monthlyData?.annual_totals[2025] ?? null,
    },

    actions: {
        async fetchDailyData(date?: string): Promise<void> {
        const energyStore = useEnergyStore()
        const region = energyStore.selectedRegion
        const targetDate = date || this.selectedDate
        if (this.dailyData?.date === targetDate && !this.dailyLoading) return

        this.dailyLoading = true
        try {
            const response = await api.get(
                `/energy/curtailment_data/?date=${targetDate}&region=${region}`
            )
            this.dailyData = response.data
            this.selectedDate = targetDate
        } catch (e) {
            console.error('Failed to fetch daily curtailment data:', e)
        } finally {
            this.dailyLoading = false
        }
        },

        async fetchMonthlyData(): Promise<void> {
        if (this.monthlyData) return  // already loaded, it's static 2024-2025

        this.monthlyLoading = true
        try {
            const response = await api.get('/energy/curtailment_monthly/')
            this.monthlyData = response.data
        } catch (e) {
            console.error('Failed to fetch monthly curtailment data:', e)
        } finally {
            this.monthlyLoading = false
        }
        },

        async initializeData(): Promise<void> {
        // Always load daily on init - it's the hero chart
        await this.fetchDailyData()
        },

        setView(v: 'daily' | 'monthly') {
        this.view = v
        // Lazy load daily data only when user switches to daily view
        if (v === 'daily' && !this.dailyData) {
            this.fetchDailyData()
        }
        },

        async setSelectedDate(date: string): Promise<void> {
        await this.fetchDailyData(date)
        },

        async refreshForRegionChange(): Promise<void> {
            const energyStore = useEnergyStore()
            this.dailyData = null
            this.monthlyData = null
            
            if (energyStore.selectedRegion === 'california') {
                this.view = 'daily'
                await this.fetchDailyData(this.selectedDate)
            } else if (this.view === 'daily') {
                await this.fetchDailyData(this.selectedDate)
            } else {
                await this.fetchMonthlyData()
            }
        },
    }
})