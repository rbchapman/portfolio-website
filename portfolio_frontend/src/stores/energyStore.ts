import { defineStore } from 'pinia'
import api from '@/utils/axios'
import { useCurtailmentStore } from './curtailmentStore'

interface HourlyData {
    hour: string
    demand: number
    solar: number
    wind: number
    vre_total: number
    solar_pct: number
    wind_pct: number
    vre_pct: number
    net_load: number
    price: number
  }
  
  interface DailyInsights {
    peak_vre_pct: number
    peak_vre_hour: string
    avg_vre_pct: number
    peak_demand: number
    peak_vre: number
    min_vre_pct: number
    min_vre_hour: string
    optimal_shift_amount: number
    shift_from_hour: string
    shift_to_hour: string
    shift_from_vre_pct: number
    shift_to_vre_pct: number
    high_vre_window_hours: number
    flexibility_window_start: string | null
    flexibility_window_end: string | null

    max_ramp_gw: number
    ramp_window: string
    load_balancing_gap_hours: number
  }

  interface BESSConfig {
    power_mw: number
    duration_hours: 2 | 4 | 6
  }

  interface BESSDecision {
    hour: string
    action: 'CHARGE' | 'DISCHARGE' | 'HOLD'
    price: number
    price_percentile: number
    net_load: number
    vre_pct: number
    energy_mwh: number
    cost_eur: number
    soc_before: number
    soc_after: number
    reasoning: string[]
  }
  interface BESSPerformance {
    gross_profit_eur: number
    revenue_eur: number
    cost_eur: number
    energy_charged_mwh: number
    energy_discharged_mwh: number
    avg_charge_price: number
    avg_discharge_price: number
    cycles_completed: number
    charge_hours: number
    discharge_hours: number
    utilization_pct: number
  }
  interface BESSAnalysis {
    date: string
    config: {
      power_mw: number
      duration_hours: number
      capacity_mwh: number
      efficiency: number
      c_rate: number
      min_soc: number
      max_soc: number
    }
    hourly_decisions: BESSDecision[]
    daily_performance: BESSPerformance
    data_source: string
  }
  interface ChartData {
    date: string
    hourly_data: HourlyData[]
    daily_insights: DailyInsights
    data_quality?: { 
      complete: boolean
      total_hours: number
      generation_hours: number
      issues: string[]
    }
  }
  
  export const useEnergyStore = defineStore('energy', {
    state: () => ({
      chartData: null as ChartData | null,
      loading: false,
      selectedDate: '2024-06-16',
      selectedRegion: 'california' as 'california' | 'spain',

      bessConfig: {
        power_mw: 100,
        duration_hours: 4 as 2 | 4 | 6
      } as BESSConfig,
      bessAnalysis: null as BESSAnalysis | null,
      bessLoading: false
    }),

  getters: {
    // Helper to format the currently selected date
    formattedDate: (state) => {
      const date = new Date(state.selectedDate)
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      })
    },

    // Check if we have data for the currently selected date
    hasDataForSelectedDate: (state) => {
      return state.chartData?.date === state.selectedDate
    }
  },

  actions: {
    // Main method to fetch data - now properly handles date parameter
    async fetchChartData(date?: string): Promise<void> {
      // If no date provided, use the currently selected date
      const targetDate = date || this.selectedDate
      
      // Don't refetch if we already have data for this date
      if (this.chartData?.date === targetDate && !this.loading) {
        return
      }

      this.loading = true
      
      try {
        const response = await api.get(`/energy/chart_data/?date=${targetDate}&region=${this.selectedRegion}`)
        this.chartData = response.data
        
        // Update selectedDate only after successful fetch
        this.selectedDate = targetDate
        
      } catch (error) {
        console.error('Failed to fetch chart data:', error)
      } finally {
        this.loading = false
      }      
    },

    async setRegion(region: 'california' | 'spain'): Promise<void> {
      this.selectedRegion = region
      // Refetch data for new region
      this.chartData = null  // Clear old data

      const curtailmentStore = useCurtailmentStore()
      curtailmentStore.dailyData = null
      
      await this.fetchChartData(this.selectedDate)
      await curtailmentStore.refreshForRegionChange()

    },

    // Method to change date (called from components)
    async setSelectedDate(date: string): Promise<void> {
      // Basic date validation for 2024
      const selectedYear = new Date(date).getFullYear()
      if (selectedYear !== 2024) {
        console.warn('Only 2024 data is available')
        return
      }

      await this.fetchChartData(date)

      if (this.bessAnalysis) {
        await this.fetchBessAnalysis()
      }
    },

    // Helper to get default/initial data on app load
    async initializeData(): Promise<void> {
      // Only fetch if we don't already have data
      if (!this.chartData) {
        await this.fetchChartData(this.selectedDate)
      }
      await this.fetchBessAnalysis()
    },

    async fetchBessAnalysis(): Promise<void> {
      this.bessLoading = true
      
      try {
        const response = await api.get('/energy/bess_analysis/', {
          params: {
            date: this.selectedDate,
            power_mw: this.bessConfig.power_mw,
            duration_hours: this.bessConfig.duration_hours
          }
        })
        
        this.bessAnalysis = response.data
        
      } catch (error) {
        console.error('Failed to fetch BESS analysis:', error)
      } finally {
        this.bessLoading = false
      }
    },

    // Update BESS config and re-run analysis
    async updateBessConfig(config: Partial<BESSConfig>): Promise<void> {
      this.bessConfig = { ...this.bessConfig, ...config }
      await this.fetchBessAnalysis()
    },
  }
})