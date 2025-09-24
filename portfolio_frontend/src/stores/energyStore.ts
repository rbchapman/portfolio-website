import { defineStore } from 'pinia'
import api from '@/utils/axios'

interface HourlyData {
    hour: string
    demand: number
    solar: number
    wind: number
    vre_total: number
    solar_pct: number
    wind_pct: number
    vre_pct: number
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
      selectedDate: '2024-05-02' 
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
        const response = await api.get(`/energy-data/chart_data/?date=${targetDate}`)
        this.chartData = response.data
        
        // Update selectedDate only after successful fetch
        this.selectedDate = targetDate
        
      } catch (error) {
        console.error('Failed to fetch chart data:', error)
      } finally {
        this.loading = false
      }
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
    },

    // Helper to get default/initial data on app load
    async initializeData(): Promise<void> {
      // Only fetch if we don't already have data
      if (!this.chartData) {
        await this.fetchChartData()
      }
    }
  }
})