<template>
  <div class="h-full flex flex-col">
    <!-- Sticky Date Picker Section -->
    <div class="sticky top-0 z-10 bg-custom-dark bg-opacity-90 backdrop-blur-sm border-b border-custom-grey py-4 mb-4">
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
          Grid data from Red Eléctrica de España via ESIOS API
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

    <!-- Battery Configuration Header -->
     <div class="overflow-y-auto">

         <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20 mb-4">
           <h4 class="text-sm font-medium text-white mb-3">Battery System Configuration</h4>
           
           <!-- Power Selection -->
           <div class="mb-4">
             <label class="text-xs text-custom-text block mb-2">Rated Power (MW)</label>
             <select
               v-model.number="localConfig.power_mw"
               @change="handleConfigChange"
               class="w-full px-4 py-2 bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500 transition-all duration-200 cursor-pointer hover:bg-opacity-80"
               :disabled="energyStore.bessLoading"
             >
               <option :value="50">50 MW</option>
               <option :value="100">100 MW</option>
               <option :value="150">150 MW</option>
               <option :value="200">200 MW</option>
             </select>
           </div>
     
           <!-- Duration Selection -->
           <div class="mb-4">
             <label class="text-xs text-custom-text block mb-2">Storage Duration (hours)</label>
             <div class="flex gap-2">
               <button
                 v-for="duration in [2, 4, 6]"
                 :key="duration"
                 @click="selectDuration(duration)"
                 :disabled="energyStore.bessLoading"
                 :class="[
        'flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200',
        localConfig.duration_hours === duration
          ? 'bg-cyan-700 text-white border border-cyan-600'
          : 'bg-custom-grey bg-opacity-30 text-custom-text border border-custom-text border-opacity-30 hover:bg-opacity-80',
        energyStore.bessLoading && 'opacity-50 cursor-not-allowed'
      ]"
               >
                 {{ duration }}h
               </button>
             </div>
           </div>
     
           <!-- Run Analysis Button -->
           <button
            @click="runAnalysis"
            :disabled="energyStore.bessLoading"
            class="w-full py-3 bg-cyan-700 hover:bg-cyan-600 disabled:bg-custom-grey disabled:opacity-50 text-white rounded-lg font-medium text-sm transition-all duration-200 flex items-center justify-center"
          >
            <span v-if="!energyStore.bessLoading">Run BESS Analysis</span>
            <div v-else class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
              Analyzing...
            </div>
          </button>
         </div>
     
         <!-- System Specs (only show after analysis) -->
         <div v-if="energyStore.bessAnalysis" class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20 mb-4">
           <h4 class="text-sm font-medium text-white mb-2">System Specifications</h4>
           <ul class="space-y-2 text-xs text-custom-text">
             <li class="flex justify-between">
               <span>Energy Capacity:</span>
               <span class="text-white font-medium">{{ energyStore.bessAnalysis.config.capacity_mwh }} MWh</span>
             </li>
             <li class="flex justify-between">
               <span>Round-trip Efficiency:</span>
               <span class="text-white font-medium">{{ (energyStore.bessAnalysis.config.efficiency * 100).toFixed(0) }}%</span>
             </li>
             <li class="flex justify-between">
               <span>C-Rate:</span>
               <span class="text-white font-medium">{{ energyStore.bessAnalysis.config.c_rate }}C</span>
             </li>
             <li class="flex justify-between">
               <span>Usable Range (10-90%):</span>
               <span class="text-white font-medium">{{ (energyStore.bessAnalysis.config.capacity_mwh * 0.8).toFixed(0) }} MWh</span>
             </li>
           </ul>
         </div>
     
         <!-- Market Eligibility -->
         <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20 mb-4">
           <h4 class="text-sm font-medium text-white mb-2">Market Eligibility</h4>
           <ul class="space-y-2 text-xs text-custom-text">
             <li class="flex items-start">
               <span class="w-1.5 h-1.5 bg-green-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
               Energy Arbitrage (Day-Ahead)
             </li>
             <li class="flex items-start opacity-50">
               <span class="w-1.5 h-1.5 bg-custom-text rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
               FCR (Post-PICASSO May 2025)
             </li>
             <li class="flex items-start opacity-50">
               <span class="w-1.5 h-1.5 bg-custom-text rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
               aFRR (Future Enhancement)
             </li>
           </ul>
         </div>
     
         <!-- Daily Performance (only show after analysis) -->
         <div v-if="energyStore.bessAnalysis" class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
           <h3 class="text-lg font-medium text-white mb-3">Daily Performance</h3>
           
           <!-- Main metrics -->
           <div class="grid grid-cols-2 gap-4 mb-4">
             <div class="bg-custom-grey bg-opacity-30 rounded-lg p-3 border border-custom-text border-opacity-20">
               <div class="text-xl font-light text-green-400">€{{ energyStore.bessAnalysis.daily_performance.gross_profit_eur.toLocaleString() }}</div>
               <div class="text-xs text-custom-text">Gross Profit</div>
             </div>
             <div class="bg-custom-grey bg-opacity-30 rounded-lg p-3 border border-custom-text border-opacity-20">
               <div class="text-xl font-light text-white">{{ energyStore.bessAnalysis.daily_performance.cycles_completed.toFixed(2) }}</div>
               <div class="text-xs text-custom-text">Cycles Completed</div>
             </div>
           </div>
     
           <!-- Detailed stats -->
           <ul class="space-y-2 text-xs text-custom-text">
             <li class="flex justify-between">
               <span>Energy Charged:</span>
               <span class="text-white">{{ energyStore.bessAnalysis.daily_performance.energy_charged_mwh.toFixed(1) }} MWh @ €{{ energyStore.bessAnalysis.daily_performance.avg_charge_price.toFixed(2) }}</span>
             </li>
             <li class="flex justify-between">
               <span>Energy Discharged:</span>
               <span class="text-white">{{ energyStore.bessAnalysis.daily_performance.energy_discharged_mwh.toFixed(1) }} MWh @ €{{ energyStore.bessAnalysis.daily_performance.avg_discharge_price.toFixed(2) }}</span>
             </li>
             <li class="flex justify-between">
               <span>Capacity Utilization:</span>
               <span class="text-white">{{ energyStore.bessAnalysis.daily_performance.utilization_pct.toFixed(1) }}%</span>
             </li>
             <li class="flex justify-between">
               <span>Active Hours:</span>
               <span class="text-white">{{ energyStore.bessAnalysis.daily_performance.charge_hours }}h charge / {{ energyStore.bessAnalysis.daily_performance.discharge_hours }}h discharge</span>
             </li>
           </ul>
     
           <!-- Disclaimer -->
           <div class="mt-4 pt-4 border-t border-custom-text border-opacity-20">
             <p class="text-xs text-custom-text italic">
                ⚠️ Illustrative values only. Excludes: Degradation, O&M, transaction fees, imbalance charges, 
                and primary revenue streams (FCR, aFRR). Real BESS economics require revenue stacking.
              </p>
           </div>
         </div>
     </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useEnergyStore } from '@/stores/energyStore'

const energyStore = useEnergyStore()

// Date picker state
const localSelectedDate = ref(energyStore.selectedDate)
const minDate = '2024-01-01'
const maxDate = '2024-12-31'

// BESS config state
const localConfig = ref({
  power_mw: energyStore.bessConfig.power_mw,
  duration_hours: energyStore.bessConfig.duration_hours as 2 | 4 | 6
})

// Date navigation
const previousDay = async () => {
  if (localSelectedDate.value <= minDate || energyStore.loading) return
  const currentDate = new Date(localSelectedDate.value)
  currentDate.setDate(currentDate.getDate() - 1)
  localSelectedDate.value = currentDate.toISOString().split('T')[0]
  await energyStore.setSelectedDate(localSelectedDate.value)
}

const nextDay = async () => {
  if (localSelectedDate.value >= maxDate || energyStore.loading) return
  const currentDate = new Date(localSelectedDate.value)
  currentDate.setDate(currentDate.getDate() + 1)
  localSelectedDate.value = currentDate.toISOString().split('T')[0]
  await energyStore.setSelectedDate(localSelectedDate.value)
}

const handleDateChange = async () => {
  if (localSelectedDate.value !== energyStore.selectedDate) {
    await energyStore.setSelectedDate(localSelectedDate.value)
  }
}

// BESS config
const selectDuration = (duration: number) => {
  if (energyStore.bessLoading) return
  localConfig.value.duration_hours = duration as 2 | 4 | 6
}

const handleConfigChange = () => {
  // Update happens when user clicks "Run Analysis"
}

const runAnalysis = async () => {
  if (energyStore.bessLoading) return
  await energyStore.updateBessConfig(localConfig.value)
}

// Watch for date changes from store
watch(() => energyStore.selectedDate, (newDate) => {
  localSelectedDate.value = newDate
})

onMounted(() => {
  
  if (!energyStore.chartData) energyStore.initializeData()
})
</script>