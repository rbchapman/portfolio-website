<template>
  <div class="h-full flex flex-col">
    <!-- Sticky Date Picker Section -->
    <div class="sticky top-0 z-10 bg-custom-dark bg-opacity-90 backdrop-blur-sm border-b border-custom-grey p-4">
      
      <!-- Custom Date Picker -->
      <div class="relative">
        <input
          type="date"
          v-model="localSelectedDate"
          @change="handleDateChange"
          :min="minDate"
          :max="maxDate"
          class="w-full px-4 py-3 bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded-lg text-white placeholder-custom-text focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 cursor-pointer hover:bg-opacity-80"
          :disabled="energyStore.loading"
        />
        <!-- Loading indicator -->
        <div v-if="energyStore.loading" class="absolute right-3 top-1/2 transform -translate-y-1/2">
          <div class="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent"></div>
        </div>
      </div>
      <div class="flex items-center text-m text-custom-text mt-2">
        <!-- <span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span> -->
        Data available for 2024 from Rede Elétrica de España (REE) via ESIOS API - some days are lacking data
      </div>
    </div>

    <!-- Content Section -->
    <div class="flex-1 overflow-y-auto custom-scrollbar space-y-4">
      <div class="text-center border-custom-text border-opacity-10">
        <span class="text-xs text-custom-text opacity-75">↓ Scroll for analysis details</span>
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
            Flexibility Gap: {{ energyStore.chartData.daily_insights.optimal_shift_amount }}GW from {{ energyStore.chartData.daily_insights.shift_from_hour }} ({{ energyStore.chartData.daily_insights.shift_from_vre_pct }}% VRE) to {{ energyStore.chartData.daily_insights.shift_to_hour }} ({{ energyStore.chartData.daily_insights.shift_to_vre_pct }}% VRE)
          </li>
          <li class="flex items-start" v-if="energyStore.chartData.daily_insights.flexibility_window_start">
            <span class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Sustained High VRE: {{ energyStore.chartData.daily_insights.high_vre_window_hours }}-hour window ({{ energyStore.chartData.daily_insights.flexibility_window_start }}-{{ energyStore.chartData.daily_insights.flexibility_window_end }}) ideal for flexible loads
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            System Stress Signal: Peak generation at {{ energyStore.chartData.daily_insights.peak_vre_hour }}, peak demand at {{ energyStore.chartData.daily_insights.shift_from_hour }} ({{ energyStore.chartData.daily_insights.shift_from_vre_pct }}% VRE at demand peak)
          </li>
        </ul>
      </div>

            <!-- Project Overview -->
      <div class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
        <h3 class="text-lg font-medium text-white mb-3">Energy Sector Analysis</h3>
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
import { ref, computed, watch, onMounted } from 'vue'
import { useEnergyStore } from '@/stores/energyStore'

const energyStore = useEnergyStore()

// Local reactive date for the input
const localSelectedDate = ref(energyStore.selectedDate)

// Date constraints for 2024
const minDate = '2024-01-01'
const maxDate = '2024-12-31'

// Computed values for dynamic stats
const peakVRE = computed(() => {
  if (!energyStore.chartData?.daily_insights) return '0%'
  return `${energyStore.chartData.daily_insights.peak_vre_pct}%`
})

const averageVRE = computed(() => {
  if (!energyStore.chartData?.daily_insights) return '0%'
  return `${energyStore.chartData.daily_insights.avg_vre_pct}%`
})

// Format date for display
const formatDisplayDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

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

// Initialize on mount
onMounted(() => {
  // Ensure we have initial data
  if (!energyStore.chartData) {
    energyStore.fetchChartData()
  }
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