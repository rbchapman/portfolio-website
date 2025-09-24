<template>
  <div class="h-full my-4 flex flex-col">
    <!-- Sticky Date Picker Section -->
    <div class="sticky top-0 z-10 bg-custom-dark bg-opacity-90 backdrop-blur-sm border-b border-custom-grey py-4">
      
      <!-- Custom Date Picker -->
      <div class="relative">
        <input
          type="date"
          v-model="localSelectedDate"
          @change="handleDateChange"
          :min="minDate"
          :max="maxDate"
          class="w-full px-4 py-3 bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded-lg text-white placeholder-custom-text focus:outline-none  focus:border-transparent transition-all duration-200 cursor-pointer hover:bg-opacity-80"
          :disabled="energyStore.loading"
        />
        <!-- Loading indicator -->
        <div v-if="energyStore.loading" class="absolute right-3 top-1/2 transform -translate-y-1/2">
          <div class="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent"></div>
        </div>
      </div>
      
      <!-- Navigation buttons -->
      <div class="flex justify-between gap-2 mt-3">
        <button 
          @click="previousDay"
          :disabled="energyStore.loading || localSelectedDate <= minDate"
          class="w-24 h-8 flex items-center justify-center bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded text-white text-sm hover:bg-opacity-80 focus:outline-none  transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ←
        </button>
         <div class="text-xs text-custom-text text-center">
          Grid data from Rede Elétrica de España via ESIOS API
        </div>
        <button 
          @click="nextDay"
          :disabled="energyStore.loading || localSelectedDate >= maxDate"
          class="w-24 h-8 flex items-center justify-center bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded text-white text-sm hover:bg-opacity-80 focus:outline-none  transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          →
        </button>
      </div>
    </div>

    <!-- Content Section -->
    <div class="flex-1 overflow-y-auto custom-scrollbar space-y-4">

    <div v-if="dataQualityMessage" class="bg-amber-500 bg-opacity-20 border border-amber-500 rounded-lg p-3">
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-amber-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-amber-200 text-sm">{{ dataQualityMessage }}</p>
        </div>
      </div>
    </div>
     
      <!-- Quick Stats -->
      <div v-if="energyStore.chartData" class="grid grid-cols-2 gap-4">
        <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <div class="text-2xl font-light text-white">{{ peakVRE }}</div>
          <div class="text-xs text-custom-text">Peak VRE Penetration</div>
        </div>
        <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <div class="text-2xl font-light text-white">{{ averageVRE }}</div>
          <div class="text-xs text-custom-text">Average VRE Penetration</div>
        </div>
      </div>

      <!-- Analysis Notes -->
      <div v-if="energyStore.chartData?.daily_insights" class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
        <h4 class="text-sm font-medium text-white mb-2">Grid Flexibility Insights</h4>
        <ul class="space-y-2 text-xs text-custom-text">
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Load Balancing Gap: Shift {{ energyStore.chartData.daily_insights.optimal_shift_amount }}GW from {{ energyStore.chartData.daily_insights.shift_from_hour }} ({{ energyStore.chartData.daily_insights.shift_from_vre_pct }}% VRE) to {{ energyStore.chartData.daily_insights.shift_to_hour }} ({{ energyStore.chartData.daily_insights.shift_to_vre_pct }}% VRE)
          </li>
          <li class="flex items-start" v-if="energyStore.chartData.daily_insights.flexibility_window_start">
            <span class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Sustained High VRE: {{ energyStore.chartData.daily_insights.high_vre_window_hours }}-hour window ({{ energyStore.chartData.daily_insights.flexibility_window_start }}-{{ energyStore.chartData.daily_insights.flexibility_window_end }}) ideal for flexible loads
          </li>
          <!-- <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            System Stress Signal: Peak generation at {{ energyStore.chartData.daily_insights.peak_vre_hour }}, peak demand at {{ energyStore.chartData.daily_insights.shift_from_hour }} ({{ energyStore.chartData.daily_insights.shift_from_vre_pct }}% VRE at demand peak)
          </li> -->
        </ul>
      </div>

      <!-- Project Overview -->
      <div class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
        <h3 class="text-lg font-medium text-white mb-3">Project Motivation</h3>
        <p class="text-custom-text text-sm leading-relaxed">
          This project builds on my master's thesis focused on international energy markets, where I aimed to understand the sector's mechanisms in order to contribute to the further integration of renewable energy sources and drive the energy transition forward. 
          I chose Spain as a case study because of its excellent renewable resources (especially solar PV) and the increasing occurrence of negative prices. 
          This market signal is a quintessential example of the limitations of the legacy system and infrastructure that wasn't designed to handle intermittent generation patterns and highlights the need for more sophisticated grid management. 
          The objective is to incrementally introduce more ESIOS energy indicators to better capture the true complexity of this multifaceted puzzle that the grid represents, ultimately delivering valuable insights for achieving net-zero electricity supply.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useEnergyStore } from '@/stores/energyStore'

const energyStore = useEnergyStore()

// Local reactive date for the input
const localSelectedDate = ref(energyStore.selectedDate)

// Date constraints for 2024
const minDate = '2020-01-01'
const maxDate = new Date().toISOString().split('T')[0]

// Computed values for dynamic stats
const peakVRE = computed(() => {
  if (!energyStore.chartData?.daily_insights) return '0%'
  return `${energyStore.chartData.daily_insights.peak_vre_pct}%`
})

const averageVRE = computed(() => {
  if (!energyStore.chartData?.daily_insights) return '0%'
  return `${energyStore.chartData.daily_insights.avg_vre_pct}%`
})

// Navigation functions
const previousDay = async () => {
  if (localSelectedDate.value <= minDate || energyStore.loading) return
  
  const currentDate = new Date(localSelectedDate.value)
  currentDate.setDate(currentDate.getDate() - 1)
  localSelectedDate.value = currentDate.toISOString().split('T')[0]
  await energyStore.fetchChartData(localSelectedDate.value)
}

const nextDay = async () => {
  if (localSelectedDate.value >= maxDate || energyStore.loading) return
  
  const currentDate = new Date(localSelectedDate.value)
  currentDate.setDate(currentDate.getDate() + 1)
  localSelectedDate.value = currentDate.toISOString().split('T')[0]
  await energyStore.fetchChartData(localSelectedDate.value)
}

// Keyboard event handler
const handleKeyPress = (event: KeyboardEvent) => {
  // Only handle if no input is focused
  if (document.activeElement?.tagName === 'INPUT') return
  
  if (event.key === 'ArrowLeft' || event.key === 'l' || event.key === 'L') {
    event.preventDefault()
    previousDay()
  } else if (event.key === 'ArrowRight' || event.key === 'r' || event.key === 'R') {
    event.preventDefault()
    nextDay()
  }
}

const dataQualityMessage = computed(() => {
  const quality = energyStore.chartData?.data_quality
  if (!quality || quality.complete) return null
  
  // Use the issues array to determine message
  const issues = quality.issues
  if (issues.includes('incomplete_hourly')) {
    const hours = quality.total_hours
    return `Limited hourly data available (${hours} hours) - system reporting gaps detected`
  }
  if (issues.includes('no_generation')) {
    return 'Generation data processing in progress - demand data available for analysis'  
  }
  if (issues.includes('sparse_generation')) {
    return 'Partial generation data - some reporting intervals missing'
  }
  return 'Data quality issues detected - please verify results'
})

// Format date for display
// const formatDisplayDate = (dateString: string): string => {
//   const date = new Date(dateString)
//   return date.toLocaleDateString('en-US', { 
//     weekday: 'short', 
//     month: 'short', 
//     day: 'numeric',
//     year: 'numeric'
//   })
// }

// Handle date change
const handleDateChange = async () => {
  if (localSelectedDate.value !== energyStore.selectedDate) {
    await energyStore.fetchChartData(localSelectedDate.value)
  }
}

// Sync local date with store when store updates
watch(() => energyStore.selectedDate, (newDate) => {
  localSelectedDate.value = newDate
})

// Initialize on mount and add keyboard listener
onMounted(() => {
  // Ensure we have initial data
  if (!energyStore.chartData) {
    energyStore.fetchChartData()
  }
  
  // Add keyboard event listener
  window.addEventListener('keydown', handleKeyPress)
})

// Clean up keyboard listener
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<style scoped>
/* Custom scrollbar styling */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

/* Custom date input styling */
input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}
</style>