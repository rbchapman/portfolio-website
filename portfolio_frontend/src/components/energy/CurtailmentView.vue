<template>
  <div class="h-full w-full p-4 flex flex-col">
    <div class="flex-1 min-h-0">
      <Bar v-if="store.view === 'monthly' && energyStore.selectedRegion === 'spain' && monthlyChartData" :data="monthlyChartData" :options="monthlyOptions" class="h-full" />
      <ChartJS type="bar" v-else-if="store.view === 'daily' && dailyChartData" :data="dailyChartData" :options="dailyOptions" class="h-full" />
      <div v-else class="h-full flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Chart, BarController, BarElement, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { Bar, Chart as ChartJS } from 'vue-chartjs'
import { useCurtailmentStore } from '@/stores/curtailmentStore'
import { useEnergyStore } from '@/stores/energyStore'

Chart.register(BarController, BarElement, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend)

const store = useCurtailmentStore()
const energyStore = useEnergyStore()

onMounted(async () => {
  await store.initializeData()
})

// --- Monthly chart ---
const monthlyChartData = computed(() => {
  if (!store.monthlyData) return null
  const m2024 = store.monthlyData.monthly_data.filter(m => m.year === 2024)
  const m2025 = store.monthlyData.monthly_data.filter(m => m.year === 2025)
  const labels = m2024.map(m => new Date(m.year, m.month - 1).toLocaleString('en', { month: 'short' }))

  return {
    labels,
    datasets: [
      {
        label: '2024 Curtailed (GWh)',
        data: m2024.map(m => +(m.total_curtailed_mwh / 1000).toFixed(2)),
        backgroundColor: 'rgba(6, 182, 212, 0.6)',
        borderColor: 'rgba(6, 182, 212, 1)',
        borderWidth: 1,
      },
      {
        label: '2025 Curtailed (GWh)',
        data: m2025.map(m => +(m.total_curtailed_mwh / 1000).toFixed(2)),
        backgroundColor: 'rgba(251, 146, 60, 0.6)',
        borderColor: 'rgba(251, 146, 60, 1)',
        borderWidth: 1,
      }
    ]
  }
})

const monthlyOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'RENEWABLE CURTAILMENT: 2024 vs 2025',
      color: 'rgba(245, 245, 245, 0.9)',
      font: { size: 16, weight: 'normal' as const },
      padding: { top: 5, bottom: 10 }
    },
    legend: {
      position: 'bottom' as const,
      labels: { color: '#e5e7eb', font: { size: 12 }, padding: 10, usePointStyle: true }
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      titleColor: '#f3f4f6',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1,
      callbacks: {
        label: (ctx: any) => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} GWh`
      }
    }
  },
  scales: {
    x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(156, 163, 175, 0.1)' } },
    y: {
      ticks: { color: '#9ca3af', callback: (v: any) => `${v} GWh` },
      grid: { color: 'rgba(156, 163, 175, 0.1)' },
      title: { display: true, text: 'GWh', color: '#e5e7eb' }
    }
  }
}
const currency = computed(() => energyStore.selectedRegion === 'california' ? '$' : '€')

// --- Daily chart ---
const dailyChartData = computed(() => {
  if (!store.dailyData) return null
  const currentCurrency = currency.value
  const hourly = store.dailyData.hourly_data

  return {
    labels: hourly.map(h => h.hour),
    datasets: [
      {
        type: 'bar' as const,
        label: 'Curtailed (MWh)',
        data: hourly.map(h => h.curtailed_mwh),
        backgroundColor: 'rgba(251, 146, 60, 0.6)',
        borderColor: 'rgba(251, 146, 60, 1)',
        borderWidth: 1,
        yAxisID: 'y',
        order: 2
      },
      {
        type: 'line' as const,
        label: `Spot Price (${currentCurrency}/MWh)`,
        data: hourly.map(h => h.spot_price),
        borderColor: 'rgba(6, 182, 212, 1)',
        backgroundColor: 'transparent',
        pointRadius: 2,
        tension: 0.3,
        yAxisID: 'y1',
        order: 1
      }
    ]
  }
})

const dailyOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index' as const, intersect: false },
  plugins: {
    title: {
      display: true,
      text: 'HOURLY CURTAILMENT & SPOT PRICE',
      color: 'rgba(245, 245, 245, 0.9)',
      font: { size: 16, weight: 'normal' as const },
      padding: { top: 5, bottom: 10 }
    },
    legend: {
      position: 'bottom' as const,
      labels: { color: '#e5e7eb', font: { size: 12 }, padding: 10, usePointStyle: true }
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      titleColor: '#f3f4f6',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1,
      callbacks: {
        label: (ctx: any) => ctx.dataset.label?.includes('Price')
          ? ` ${ctx.parsed.y.toFixed(2)} ${currency.value}/MWh`
          : ` ${ctx.parsed.y.toFixed(1)} MWh curtailed`
      }
    }
  },
  scales: {
    x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(156, 163, 175, 0.1)' } },
    y: {
      ticks: { color: '#9ca3af' },
      grid: { color: 'rgba(156, 163, 175, 0.1)' },
      title: { display: true, text: 'MWh', color: '#e5e7eb' }
    },
    y1: {
      position: 'right' as const,
      ticks: { color: 'rgba(6,182,212,0.8)', callback: (v: any) => `${currency.value}${v}` },
      grid: { drawOnChartArea: false },
      title: { display: true, text: `${currency.value}/MWh`, color: 'rgba(6,182,212,0.8)' }
    }
  }
}))
</script>