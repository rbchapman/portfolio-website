<template>
  <div class="h-full my-4 flex flex-col">

    <!-- View Toggle -->
    <!-- <div v-if="energyStore.selectedRegion === 'spain'" class="flex gap-2 mb-4">
      <button
        @click="store.setView('monthly')"
        :class="[
          'flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200',
          store.view === 'monthly'
            ? 'bg-cyan-700 text-white border border-cyan-600'
            : 'bg-custom-grey bg-opacity-30 text-custom-text border border-custom-text border-opacity-30 hover:bg-opacity-80'
        ]"
      >
        Annual
      </button>
      <button
        @click="store.setView('daily')"
        :class="[
          'flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200',
          store.view === 'daily'
            ? 'bg-cyan-700 text-white border border-cyan-600'
            : 'bg-custom-grey bg-opacity-30 text-custom-text border border-custom-text border-opacity-30 hover:bg-opacity-80'
        ]"
      >
        Daily
      </button>
    </div> -->

    <!-- Date picker - only in daily view -->
    <div v-if="store.view === 'daily'" class="sticky top-0 z-10 bg-custom-dark bg-opacity-90 backdrop-blur-sm border-b border-custom-grey py-4 mb-4">
      <div class="relative">
        <input
          type="date"
          v-model="localDate"
          @change="handleDateChange"
          min="2024-01-01"
          max="2025-12-31"
          class="w-full px-4 py-3 bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded-lg text-white focus:outline-none transition-all duration-200 cursor-pointer hover:bg-opacity-80"
          :disabled="store.dailyLoading"
        />
        <div v-if="store.dailyLoading" class="absolute right-3 top-1/2 transform -translate-y-1/2">
          <div class="animate-spin rounded-full h-5 w-5 border-2 border-cyan-500 border-t-transparent"></div>
        </div>
      </div>
      <div class="flex justify-between gap-2 mt-3">
        <button @click="previousDay" :disabled="store.dailyLoading"
          class="w-24 h-8 flex items-center justify-center bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded text-white text-sm hover:bg-opacity-80 disabled:opacity-50">←</button>
        <div class="text-xs text-custom-text text-center">{{ dataSourceText }}</div>
        <button @click="nextDay" :disabled="store.dailyLoading"
          class="w-24 h-8 flex items-center justify-center bg-custom-grey bg-opacity-30 border border-custom-text border-opacity-30 rounded text-white text-sm hover:bg-opacity-80 disabled:opacity-50">→</button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar space-y-4">

      <!-- ANNUAL VIEW -->
      <template v-if="store.view === 'monthly'">

        <!-- Headline stat cards -->
        <div v-if="store.annual2024 && store.annual2025" class="grid grid-cols-2 gap-3">
          <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20 col-span-2">
            <div class="text-xs text-custom-text mb-1">2024 → 2025 Curtailment Growth</div>
            <div class="text-2xl font-light text-orange-400">+{{ growthPct }}%</div>
            <div class="text-xs text-custom-text mt-1">curtailed volume year-over-year</div>
          </div>
          <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
            <div class="text-xs text-custom-text mb-1">2024 Total</div>
            <div class="text-xl font-light text-white">{{ fmt(store.annual2024.total_curtailed_mwh / 1000, 1) }} GWh</div>
            <div class="text-xs text-cyan-400 mt-1">€{{ fmtM(store.annual2024.total_revenue_lost_eur) }}M lost</div>
          </div>
          <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
            <div class="text-xs text-custom-text mb-1">2025 Total</div>
            <div class="text-xl font-light text-white">{{ fmt(store.annual2025.total_curtailed_mwh / 1000, 1) }} GWh</div>
            <div class="text-xs text-orange-400 mt-1">€{{ fmtM(store.annual2025.total_revenue_lost_eur) }}M lost</div>
          </div>
        </div>

        <!-- Transmission vs distribution -->
        <div v-if="latestMonth" class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <h4 class="text-sm font-medium text-white mb-2">{{ copyStore.get('curtailment_breakdown_title', 'Constraint Type Breakdown') }}</h4>
          <ul class="space-y-2 text-xs text-custom-text">
            <li class="flex justify-between">
              <span class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-orange-400 rounded-full"></span>
                Transmission (RTT)
              </span>
              <span class="text-white">{{ fmt(latestMonth.transmission_curtailment_pct, 2) }}%</span>
            </li>
            <li class="flex justify-between">
              <span class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-cyan-400 rounded-full"></span>
                Distribution (RTD)
              </span>
              <span class="text-white">{{ fmt(latestMonth.distribution_curtailment_pct, 3) }}%</span>
            </li>
          </ul>
          <p class="text-xs text-custom-text mt-3 opacity-70">{{ copyStore.get('curtailment_breakdown_note', 'Monthly avg · transmission constraints dominate by ~10x') }}</p>
        </div>

        <!-- Explainer -->
        <div class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
          <h3 class="text-lg font-medium text-white mb-3">{{ copyStore.get('curtailment_annual_title', 'Renewable Curtailment and System Flexibility') }}</h3>
          <p class="text-custom-text text-sm leading-relaxed mb-3">
            {{ copyStore.get('curtailment_annual_body_problem', 'Curtailment occurs when available renewable generation cannot be fully used, either because grid constraints limit where the power can be delivered or because supply exceeds what the system can absorb at that time. In Spain, congestion on the high-voltage network is a major source of curtailment, while periods of very low or negative prices can also reflect excess renewable supply. Both show a mismatch between renewable output and the system’s ability to move or use that energy when it is available.') }}
          </p>
          <p class="text-custom-text text-sm leading-relaxed">
            {{ copyStore.get('curtailment_annual_body_solution', 'Storage and flexible demand can help reduce this mismatch by shifting electricity use toward hours with abundant renewable generation. Batteries, EV charging, thermal loads, and other controllable resources can absorb surplus energy and reduce demand during tighter periods. Used alongside transmission upgrades and other grid investments, these resources can help the power system make better use of the renewable generation already available.') }}
          </p>
        </div>
      </template>

      <!-- DAILY VIEW -->
      <template v-else-if="store.view === 'daily' && store.dailyData">
        <!-- Quick stats -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
            <div class="text-2xl font-light text-orange-400">{{ fmtMwh(store.dailyData.daily_insights.total_curtailed_mwh) }}</div>
            <div class="text-xs text-custom-text">MWh Curtailed</div>
          </div>
          <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
            <div class="text-2xl font-light text-white">{{ currency }}{{ fmt(revenueLost, 0) }}</div>
            <div class="text-xs text-custom-text">Lost Spot Value</div>
          </div>
        </div>

        <!-- Daily insights -->
        <div class="bg-custom-grey bg-opacity-30 rounded-lg p-4 border border-custom-text border-opacity-20">
          <h4 class="text-sm font-medium text-white mb-2">{{ copyStore.get('curtailment_daily_summary_title', 'Day Summary') }}</h4>
          <ul class="space-y-2 text-xs text-custom-text">
            <li class="flex items-start">
              <span class="w-1.5 h-1.5 bg-orange-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
              Peak curtailment: {{ fmtMwh(store.dailyData.daily_insights.peak_curtailment_mwh) }} MWh at {{ store.dailyData.daily_insights.peak_curtailment_hour }}
            </li>
            <li class="flex items-start">
              <span class="w-1.5 h-1.5 bg-cyan-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
              Active curtailment in {{ store.dailyData.daily_insights.curtailment_hours }} of 24 hours
            </li>
            <li class="flex items-start">
              <span class="w-1.5 h-1.5 bg-red-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
              {{ store.dailyData.daily_insights.negative_price_hours }}h of negative spot prices — {{ fmtMwh(store.dailyData.daily_insights.negative_price_curtailed_mwh) }} MWh curtailed during zero/negative price periods
            </li>
          </ul>
        </div>

        <!-- Explainer -->
        <div class="bg-custom-grey bg-opacity-50 rounded-lg p-6 border border-custom-text border-opacity-20">
          <h3 class="text-lg font-medium text-white mb-3">{{ copyStore.get('curtailment_daily_title', 'What the Hourly Pattern Shows') }}</h3>
          <p class="text-custom-text text-sm leading-relaxed mb-3">
            {{ copyStore.get('curtailment_daily_body_problem', 'This view pairs hourly curtailment with wholesale prices to show when renewable generation is going unused and under what market conditions. Curtailment during low or negative-price hours often coincides with surplus generation, while curtailment at higher prices can indicate local constraints that prevent available power from reaching demand.') }}
          </p>
          <p class="text-custom-text text-sm leading-relaxed">
            {{ copyStore.get('curtailment_daily_body_solution', 'For storage and controllable demand, these hours can point to useful windows for shifting energy consumption. Flexible resources can increase load or charge during periods of surplus generation, then reduce consumption or discharge during tighter and more expensive hours. This can improve renewable utilization while also supporting grid balancing.') }}
          </p>
          <div class="mt-4 pt-4 border-t border-custom-text border-opacity-30 text-xs text-custom-text italic">
            {{ copyStore.get('curtailment_methodology_note', 'Methodology: Curtailment volumes are paired with hourly spot prices. Lost spot value is calculated only for curtailed energy during positive-price hours, using curtailed MWh × hourly price. It is an illustrative market-value estimate and does not account for contracts, settlements, congestion pricing differences, or other compensation.') }}
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCurtailmentStore } from '@/stores/curtailmentStore'
import { useEnergyStore } from '@/stores/energyStore'
import { useSiteCopyStore } from '@/stores/siteCopyStore'

const store = useCurtailmentStore()
const energyStore = useEnergyStore()
const copyStore = useSiteCopyStore()
const localDate = ref(energyStore.selectedDate)

const dataSourceText = computed(() => {
  return energyStore.selectedRegion === 'california' 
    ? 'CAISO via gridstatus' 
    : 'Red Eléctrica de España via ESIOS'
})

const currency = computed(() => energyStore.selectedRegion === 'california' ? '$' : '€')

const revenueLost = computed(() => {
  const insights = store.dailyData?.daily_insights
  if (!insights) return 0
  return insights.estimated_revenue_lost_usd ?? insights.estimated_revenue_lost ?? 0
})

// Helpers
const fmt  = (v: number | null | undefined, d: number) => v != null ? v.toFixed(d) : '—'
const fmtM = (v: number) => (v / 1_000_000).toFixed(1)
const fmtMwh = (v: number | null | undefined) => {
  if (v == null) return '—'
  if (v === 0) return '0'
  if (v < 1) return v.toFixed(2)      // 0.40
  if (v < 100) return v.toFixed(1)    // 45.3
  return v.toFixed(0)                  // 1,234
}

const growthPct = computed(() => {
  if (!store.annual2024 || !store.annual2025) return '—'
  const pct = ((store.annual2025.total_curtailed_mwh - store.annual2024.total_curtailed_mwh) / store.annual2024.total_curtailed_mwh) * 100
  return pct.toFixed(0)
})

// Most recent month with percentage data for constraint breakdown
const latestMonth = computed(() => {
  const months = store.monthlyData?.monthly_data ?? []
  return [...months].reverse().find(m => m.transmission_curtailment_pct != null) ?? null
})

const handleDateChange = () => energyStore.setSelectedDate(localDate.value)

const previousDay = () => {
  const d = new Date(localDate.value)
  d.setDate(d.getDate() - 1)
  localDate.value = d.toISOString().split('T')[0]
  energyStore.setSelectedDate(localDate.value)
}

const nextDay = () => {
  const d = new Date(localDate.value)
  d.setDate(d.getDate() + 1)
  localDate.value = d.toISOString().split('T')[0]
  energyStore.setSelectedDate(localDate.value)
}

watch(() => energyStore.selectedDate, v => { localDate.value = v })
</script>

<style scoped>
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.2) transparent; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.2); border-radius: 3px; }
input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(1); cursor: pointer; }
</style>