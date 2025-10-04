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
          class="w-full px-4 py-3 bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded-lg text-white placeholder-custom-text focus:outline-none focus:border-transparent transition-all duration-200 cursor-pointer hover:bg-opacity-80"
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
          class="w-24 h-8 flex items-center justify-center bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded text-white text-sm hover:bg-opacity-80 focus:outline-none transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ←
        </button>
         <div class="text-xs text-custom-text text-center">
          Grid data from Rede Elétrica de España via ESIOS API
        </div>
        <button 
          @click="nextDay"
          :disabled="energyStore.loading || localSelectedDate >= maxDate"
          class="w-24 h-8 flex items-center justify-center bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded text-white text-sm hover:bg-opacity-80 focus:outline-none transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          →
        </button>
      </div>
    </div>

    <!-- Content Section -->
    <div class="flex-1 overflow-y-auto custom-scrollbar space-y-4">
      <!-- Quick Stats -->
      <div v-if="energyStore.chartData" class="grid grid-cols-2 gap-4">
        <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <div class="text-2xl font-light text-white">{{ peakVREOutput }}</div>
          <div class="text-xs text-custom-text">Peak Combined VRE Output ({{ peakVRE }} penetration)</div>
        </div>
        <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <div class="text-2xl font-light text-white">{{ minConventionalNeed }}</div>
          <div class="text-xs text-custom-text">Minimum Conventional Generation Required</div>
        </div>
      </div>

      <!-- Grid Balance Summary -->
      <div v-if="energyStore.chartData?.hourly_data" class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
        <h4 class="text-sm font-medium text-white mb-2">Grid Balance Summary</h4>
        <ul class="space-y-2 text-xs text-custom-text">
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Tightest operating hour: {{ tightestHour }} ({{ minConventionalNeed }} conventional capacity needed)
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Largest VRE swing: {{ largestVRESwing }} ({{ vreSwingWindow }})
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Hours with VRE providing >70% of demand: {{ highVREHours }}h
          </li>
        </ul>
      </div>

      <!-- Project Overview -->
      <div class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
        <h3 class="text-lg font-medium text-white mb-3">Project Motivation</h3>
        <p class="text-custom-text text-sm leading-relaxed">
          This project builds on my master's thesis focused on international energy markets, where I aimed to understand the sector's mechanisms in order to contribute to the further integration of renewable energy sources and drive the energy transition forward. 
          I chose Spain as a case study because of its excellent renewable resources (especially solar PV) and the increasing occurrence of negative prices. 
          This market signal is a quintessential example of the limitations of the legacy system. Today's infrastructure wasn't designed to handle intermittent generation patterns and highlights the need for more sophisticated grid management. 
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

// Date constraints
const minDate = '2020-01-01'
const maxDate = new Date().toISOString().split('T')[0]

// Computed values for dynamic stats
const peakVRE = computed(() => {
  if (!energyStore.chartData?.daily_insights) return '0%'
  return `${energyStore.chartData.daily_insights.peak_vre_pct}%`
})
const peakVREOutput = computed(() => {
  if (!energyStore.chartData?.hourly_data) return '0GW'
  const maxVRE = Math.max(...energyStore.chartData.hourly_data.map(d => d.wind + d.solar))
  return `${maxVRE.toFixed(1)}GW`
})

const minConventionalNeed = computed(() => {
  if (!energyStore.chartData?.hourly_data) return '0GW'
  const minGap = Math.min(...energyStore.chartData.hourly_data.map(d => d.demand - (d.wind + d.solar)))
  return `${minGap.toFixed(1)}GW`
})

const tightestHour = computed(() => {
  if (!energyStore.chartData?.hourly_data) return '00:00'
  const hourlyData = energyStore.chartData.hourly_data
  const gaps = hourlyData.map(d => d.demand - (d.wind + d.solar))
  const minIdx = gaps.indexOf(Math.min(...gaps))
  return hourlyData[minIdx].hour
})

const largestVRESwing = computed(() => {
  if (!energyStore.chartData?.hourly_data) return '0GW'
  const vreData = energyStore.chartData.hourly_data.map(d => d.wind + d.solar)
  const swings = []
  for (let i = 1; i < vreData.length; i++) {
    swings.push(Math.abs(vreData[i] - vreData[i-1]))
  }
  return `${Math.max(...swings).toFixed(1)}GW`
})

const vreSwingWindow = computed(() => {
  if (!energyStore.chartData?.hourly_data) return ''
  const vreData = energyStore.chartData.hourly_data.map(d => d.wind + d.solar)
  let maxSwing = 0
  let maxIdx = 0
  for (let i = 1; i < vreData.length; i++) {
    const swing = Math.abs(vreData[i] - vreData[i-1])
    if (swing > maxSwing) {
      maxSwing = swing
      maxIdx = i
    }
  }
  const startHour = energyStore.chartData.hourly_data[maxIdx - 1].hour
  const endHour = energyStore.chartData.hourly_data[maxIdx].hour
  return `${startHour}-${endHour}`
})

const highVREHours = computed(() => {
  if (!energyStore.chartData?.hourly_data) return '0'
  return energyStore.chartData.hourly_data.filter(d => {
    const vre = d.wind + d.solar
    return (vre / d.demand) > 0.7
  }).length
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
  if (document.activeElement?.tagName === 'INPUT') return
  
  if (event.key === 'ArrowLeft' || event.key === 'l' || event.key === 'L') {
    event.preventDefault()
    previousDay()
  } else if (event.key === 'ArrowRight' || event.key === 'r' || event.key === 'R') {
    event.preventDefault()
    nextDay()
  }
}

const handleDateChange = async () => {
  if (localSelectedDate.value !== energyStore.selectedDate) {
    await energyStore.fetchChartData(localSelectedDate.value)
  }
}

watch(() => energyStore.selectedDate, (newDate) => {
  localSelectedDate.value = newDate
})

onMounted(() => {
  if (!energyStore.chartData) {
    energyStore.fetchChartData()
  }
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>