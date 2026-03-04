<template>
  <div class="h-full w-full p-4 flex flex-col">
    <div class="flex-1 min-h-0">
      <!-- California - not available yet -->
      <div v-if="energyStore.selectedRegion === 'california'" class="h-full w-360 flex flex-col items-center justify-center">
        <div class="text-center">
          <div class="text-2xl font-light text-white mb-3">BESS Analysis</div>
          <div class="text-lg text-white/60 mb-2">Coming soon for CAISO</div>
          <div class="text-sm text-white/40">Currently available for Spanish market (REE)</div>
        </div>
      </div>
      <!-- Loading state -->
      <!-- <div v-else-if="energyStore.bessLoading" class="h-full flex flex-col items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-2 border-cyan-500 border-t-transparent mb-3"></div>
        <span class="text-custom-text text-sm">Analyzing market data...</span>
      </div> -->
      
      <!-- Chart when ready -->
      <Chart 
        v-else-if="energyStore.bessAnalysis" 
        type="bar"
        :data="chartData" 
        :options="chartOptions" 
        class="h-full" 
      />
      
      <div v-else class="h-full flex items-center justify-center text-custom-text text-sm">
        Select a date to analyze BESS opportunities
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Chart } from 'vue-chartjs'
import { Chart as ChartJS, registerables, type ChartData, type ChartOptions, type TooltipItem } from 'chart.js'
import { useEnergyStore } from '@/stores/energyStore'
import { computed } from 'vue'

ChartJS.register(...registerables)

const energyStore = useEnergyStore()

const chartData = computed((): ChartData<'bar' | 'line'> => {
  if (!energyStore.bessAnalysis?.hourly_decisions) return { labels: [], datasets: [] }

  const decisions = energyStore.bessAnalysis.hourly_decisions
  const hours = decisions.map(d => d.hour)

  const chargeData = decisions.map(d => (d.action === 'CHARGE' ? Number(d.energy_mwh) : 0))
  const dischargeData = decisions.map(d => (d.action === 'DISCHARGE' ? -Number(d.energy_mwh) : 0))
  const prices = decisions.map(d => Number(d.price))

  return {
    labels: hours,
    datasets: [
      {
        type: 'line',
        label: 'Market Price',
        data: prices,
        borderColor: '#fbbf24',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.3,
        yAxisID: 'y-price',
        order: 1,
      },
      {
        type: 'bar',
        label: 'Charging',
        data: chargeData,
        backgroundColor: 'rgba(34, 197, 94, 0.7)',
        borderColor: '#22c55e',
        borderWidth: 1,
        yAxisID: 'y-energy',
        order: 2,
      },
      {
        type: 'bar',
        label: 'Discharging',
        data: dischargeData,
        backgroundColor: 'rgba(239, 68, 68, 0.7)',
        borderColor: '#ef4444',
        borderWidth: 1,
        yAxisID: 'y-energy',
        order: 2,
      },
    ],
  }
})

const chartOptions = computed((): ChartOptions<'bar' | 'line'> => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    title: {
      display: true,
      text: 'BESS Operations: Price Dynamics & Battery Actions',
      color: 'rgba(245, 245, 245, 0.9)',
      font: { size: 16, weight: 'normal' },
      padding: { top: 5, bottom: 10 },
    },
    legend: {
      display: true,
      position: 'bottom',
      labels: {
        color: '#e5e7eb',
        font: { size: 12 },
        padding: 15,
        usePointStyle: true,
      },
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      titleColor: '#f3f4f6',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1,
      padding: 12,
      callbacks: {
        title: (context: TooltipItem<'bar' | 'line'>[]) => {
          const decision = energyStore.bessAnalysis?.hourly_decisions[context[0].dataIndex]
          const actionEmoji =
            decision?.action === 'CHARGE'
              ? '🟢'
              : decision?.action === 'DISCHARGE'
              ? '🔴'
              : '⚪'
          return `${actionEmoji} ${decision?.hour} - ${decision?.action ?? 'IDLE'}`
        },
        label: (context: TooltipItem<'bar' | 'line'>) => {
          const decision = energyStore.bessAnalysis?.hourly_decisions[context.dataIndex]

          if (context.dataset.label === 'Market Price') {
            const price = Number(decision?.price ?? 0)
            return `Price: €${price.toFixed(2)}/MWh`
          }

          if (decision?.action === 'CHARGE' || decision?.action === 'DISCHARGE') {
            const socBefore = Number(decision.soc_before ?? 0)
            const socAfter = Number(decision.soc_after ?? 0)
            const energy = Math.abs(Number(decision.energy_mwh ?? 0))
            return [
              `Energy: ${energy.toFixed(1)} MWh`,
              `SoC: ${socBefore.toFixed(1)}% → ${socAfter.toFixed(1)}%`,
            ]
          }

          const soc = Number(decision?.soc_after ?? 0)
          return `No action (${soc.toFixed(1)}% SoC)`
        },
      },
    },
  },
  scales: {
    x: {
      stacked: true,
      title: {
        display: true,
        text: 'Hour of Day',
        color: '#e5e7eb',
        font: { size: 13 },
      },
      ticks: { color: '#9ca3af', maxRotation: 45, minRotation: 45 },
      grid: { color: 'rgba(156, 163, 175, 0.1)' },
    },
    'y-energy': {
      stacked: true,
      position: 'left',
      title: {
        display: true,
        text: 'Energy Flow (MWh)',
        color: '#e5e7eb',
        font: { size: 13, weight: 'bold' },
      },
      ticks: {
        color: '#9ca3af',
        callback: (value: number | string) => `${value} MWh`,
      },
      grid: { color: 'rgba(156, 163, 175, 0.1)' },
    },
    'y-price': {
      position: 'right',
      title: {
        display: true,
        text: 'Price (€/MWh)',
        color: '#fbbf24',
        font: { size: 13, weight: 'bold' },
      },
      ticks: {
        color: '#fbbf24',
        callback: (value: number | string) => '€' + Number(value).toFixed(0),
      },
      grid: { display: false },
    },
  },
}))
</script>