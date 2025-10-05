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
          <div class="text-2xl font-light text-white">{{ netLoadRange }}</div>
          <div class="text-xs text-custom-text">Net Load Range</div>
        </div>
        <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <div class="text-2xl font-light text-white">{{ maxRampRate }}</div>
          <div class="text-xs text-custom-text">Steepest Hourly Ramp</div>
        </div>
      </div>

      <!-- Flexibility Requirements -->
      <div v-if="energyStore.chartData?.hourly_data" class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
        <h4 class="text-sm font-medium text-white mb-2">Operational Flexibility Challenge</h4>
        <ul class="space-y-2 text-xs text-custom-text">
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Duck curve depth: Net load dropped to {{ minNetLoad }} at {{ minNetLoadHour }} - a {{ duckCurveDepth }} reduction from morning baseline
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-sky-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Evening ramp: Conventional generation ramped {{ eveningRamp }} in {{ rampDuration }} as solar dropped and demand peaked
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Baseload constraint: {{ tightHours }} with net load 8GW - limited capacity for inflexible generation
          </li>
        </ul>
      </div>

      <!-- What Net Load Shows -->
      <div class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
        <h3 class="text-lg font-medium text-white mb-3">Understanding Net Load</h3>
        <p class="text-custom-text text-sm leading-relaxed mb-3">
          Net load (also called residual load) represents the demand that must be met by dispatchable generation after variable renewables contribute. 
          It's calculated as: <span class="text-white font-mono">Net Load = Total Demand - Wind - Solar</span>
        </p>
        <p class="text-custom-text text-sm leading-relaxed">
          This metric reveals the operational flexibility challenge: when net load is negative, the grid has oversupply and must curtail generation. 
          When net load ramps steeply, conventional plants must respond quickly. 
          Low net load values indicate tight operating margins where forecast accuracy becomes critical.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
  import { useEnergyStore } from '@/stores/energyStore'

  const energyStore = useEnergyStore()

  const localSelectedDate = ref(energyStore.selectedDate)

  const minDate = '2020-01-01'
  const maxDate = new Date().toISOString().split('T')[0]

  const netLoadRange = computed(() => {
    if (!energyStore.chartData?.hourly_data) return '0GW'
    const netLoads = energyStore.chartData.hourly_data.map(d => d.demand - (d.wind + d.solar))
    const min = Math.min(...netLoads)
    const max = Math.max(...netLoads)
    return `${min.toFixed(1)}GW → ${max.toFixed(1)}GW`
  })

  const minNetLoadValue = computed(() => {
    if (!energyStore.chartData?.hourly_data) return 0
    const netLoads = energyStore.chartData.hourly_data.map(d => d.demand - (d.wind + d.solar))
    return Math.min(...netLoads)
  })

  const minNetLoad = computed(() => {
    return `${minNetLoadValue.value.toFixed(1)}GW`
  })

  const minNetLoadHour = computed(() => {
    if (!energyStore.chartData?.hourly_data) return '00:00'
    const netLoads = energyStore.chartData.hourly_data.map(d => d.demand - (d.wind + d.solar))
    const minIdx = netLoads.indexOf(Math.min(...netLoads))
    return energyStore.chartData.hourly_data[minIdx].hour
  })
  const duckCurveDepth = computed(() => {
    if (!energyStore.chartData?.hourly_data) return '0GW'
    const netLoads = energyStore.chartData.hourly_data.map(d => d.demand - (d.wind + d.solar))
    // Morning baseline (6-8am average)
    const morningAvg = (netLoads[6] + netLoads[7]) / 2
    const minLoad = Math.min(...netLoads)
    return `${(morningAvg - minLoad).toFixed(1)}GW`
  })

  const eveningRamp = computed(() => {
    if (!energyStore.chartData?.hourly_data) return '0GW'
    const netLoads = energyStore.chartData.hourly_data.map(d => d.demand - (d.wind + d.solar))
    // Find ramp between 17:00-21:00
    const eveningStart = 17
    const eveningEnd = 21
    const ramp = netLoads[eveningEnd] - netLoads[eveningStart]
    return `${ramp.toFixed(1)}GW`
  })

  const rampDuration = computed(() => {
    return '4h (17:00-21:00)'
  })

  const tightHours = computed(() => {
    if (!energyStore.chartData?.hourly_data) return '0h'
    const count = energyStore.chartData.hourly_data.filter(d => {
      const netLoad = d.demand - (d.wind + d.solar)
      return netLoad < 8
    }).length
    return `${count}h`
  })

  const maxRampRate = computed(() => {
    if (!energyStore.chartData?.hourly_data) return '0GW/h'
    const netLoads = energyStore.chartData.hourly_data.map(d => d.demand - (d.wind + d.solar))
    let maxRamp = 0
    for (let i = 1; i < netLoads.length; i++) {
      const ramp = Math.abs(netLoads[i] - netLoads[i-1])
      if (ramp > maxRamp) maxRamp = ramp
    }
    return `${maxRamp.toFixed(1)}GW/h`
  })

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

<style scoped>
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

input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}
</style>