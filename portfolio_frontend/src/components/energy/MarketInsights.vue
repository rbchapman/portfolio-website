<template>
  <div class="h-full my-4 flex flex-col">
    <!-- Sticky Date Picker Section -->
    <div class="sticky top-0 z-10 bg-custom-dark bg-opacity-90 backdrop-blur-sm border-b border-custom-grey py-4">
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

      <div class="flex justify-between gap-2 mt-3">
        <button 
          @click="previousDay"
          :disabled="energyStore.loading || localSelectedDate <= minDate"
          class="w-24 h-8 flex items-center justify-center bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded text-white text-sm hover:bg-opacity-80 focus:outline-none transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ←
        </button>
        <div class="text-xs text-custom-text text-center">
          Market data from Red Eléctrica de España via ESIOS API
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
          <div class="text-2xl font-light text-white">€{{ avgPrice }}</div>
          <div class="text-xs text-custom-text">Average Market Price</div>
        </div>
        <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <div class="text-2xl font-light text-white">{{ volatility }}</div>
          <div class="text-xs text-custom-text">Price Volatility (σ)</div>
        </div>
      </div>

      <!-- Market Summary -->
      <div v-if="energyStore.chartData?.hourly_data" class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
        <h4 class="text-sm font-medium text-white mb-2">Market Summary</h4>
        <ul class="space-y-2 text-xs text-custom-text">
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-yellow-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Intraday range: €{{ intradayRange }}/MWh
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Negative price hours: {{ negativeHours }}h ({{ negativePct }}%)
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-purple-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Price–VRE correlation: {{ correlationVRE }}
          </li>
          <li class="flex items-start">
            <span class="w-1.5 h-1.5 bg-green-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
            Arbitrage potential: €{{ arbitrageOpportunity }}/MWh
          </li>
        </ul>
      </div>

      <!-- Project Overview -->
      <div class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
        <h3 class="text-lg font-medium text-white mb-3">Understanding Daily Price Dynamics</h3>
        <p class="text-custom-text text-sm leading-relaxed">
          This view summarizes how Spain’s wholesale market prices fluctuate over the day. 
          High volatility reflects grid stress and balancing challenges, while price troughs indicate hours of renewable oversupply. 
          When prices are low or negative, storage assets and interconnections capture surplus renewable energy, later discharging during high-price peaks. 
          The price–VRE correlation helps gauge how strongly renewables are driving market conditions — 
          a key insight for evaluating the value of flexibility resources such as BESS and demand response.
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

const prices = computed(() => energyStore.chartData?.hourly_data?.map(d => d.price) || [])

const avgPrice = computed(() => {
  if (!prices.value.length) return '0.00'
  const avg = prices.value.reduce((a, b) => a + b, 0) / prices.value.length
  return avg.toFixed(2)
})

const volatility = computed(() => {
  if (!prices.value.length) return '0.00'
  const mean = prices.value.reduce((a, b) => a + b, 0) / prices.value.length
  const variance = prices.value.reduce((acc, p) => acc + Math.pow(p - mean, 2), 0) / prices.value.length
  return Math.sqrt(variance).toFixed(2)
})

const intradayRange = computed(() => {
  if (!prices.value.length) return '0.00'
  const range = Math.max(...prices.value) - Math.min(...prices.value)
  return range.toFixed(2)
})

const negativeHours = computed(() => prices.value.filter(p => p < 0).length)
const negativePct = computed(() => ((negativeHours.value / (prices.value.length || 1)) * 100).toFixed(1))

// Price-VRE correlation
const correlationVRE = computed(() => {
  if (!energyStore.chartData?.hourly_data) return '0.00'
  const data = energyStore.chartData.hourly_data
  const priceArr = data.map(d => d.price)
  const vreArr = data.map(d => d.vre_total)
  const meanP = priceArr.reduce((a, b) => a + b, 0) / priceArr.length
  const meanV = vreArr.reduce((a, b) => a + b, 0) / vreArr.length
  const numerator = priceArr.reduce((acc, p, i) => acc + (p - meanP) * (vreArr[i] - meanV), 0)
  const denom = Math.sqrt(priceArr.reduce((acc, p) => acc + Math.pow(p - meanP, 2), 0) * vreArr.reduce((acc, v) => acc + Math.pow(v - meanV, 2), 0))
  return (numerator / denom).toFixed(2)
})

const arbitrageOpportunity = computed(() => {
  if (!prices.value.length) return '0.00'
  return (Math.max(...prices.value) - Math.min(...prices.value)).toFixed(2)
})

// Navigation
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
  if (!energyStore.chartData) energyStore.fetchChartData()
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>
