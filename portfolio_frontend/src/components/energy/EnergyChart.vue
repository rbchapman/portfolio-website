<template>
  <div class="h-full w-full p-4 flex flex-col">
    <div class="flex-1 min-h-0">
      <Line :data="chartData" :options="chartOptions" class="h-full" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { useEnergyStore } from '@/stores/energyStore'
import { computed, onMounted } from 'vue'

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const energyStore = useEnergyStore()

onMounted(() => {
  energyStore.initializeData()
})

const chartData = computed(() => {
  if (!energyStore.chartData?.hourly_data) return { labels: [], datasets: [] }
    
  const data = energyStore.chartData.hourly_data
  const netLoad = data.map(d => d.demand - (d.wind + d.solar))
    
  return {
    labels: data.map(d => d.hour),
    datasets: [
      {
        label: 'Net Load',
        data: netLoad,
        backgroundColor: 'rgba(6, 182, 212, 0.5)',  // Just solid cyan
        borderColor: '#06b6d4',
        borderWidth: 2,
        fill: 'origin',
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: '#06b6d4'
      },
      {
        label: 'Total Demand',
        data: data.map(d => d.demand),
        borderColor: '#9ca3af',
        borderDash: [5, 5],
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#9ca3af'
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false
  },
  plugins: {
    title: {
      display: true,
      text: 'NET LOAD: RESIDUAL DEMAND AFTER VARIABLE RENEWABLES',
      color: 'rgba(245, 245, 245, 0.9)',
      font: {
        size: 16,
        weight: 'normal' as const
      },
      padding: {
        top: 5,
        bottom: 10
      }
    },
    legend: {
      position: 'bottom' as const,
      labels: {
        color: '#e5e7eb',
        font: {
          size: 12
        },
        padding: 10,
        usePointStyle: true
      }
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      titleColor: '#f3f4f6',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1,
      padding: 12,
      callbacks: {
        title: function(context: any) {
          return context[0].label
        },
        label: function(context: any) {
          const hourData = energyStore.chartData?.hourly_data[context.dataIndex]
          if (!hourData) return ''
          
          if (context.datasetIndex === 0) {
            const netLoad = hourData.demand - (hourData.wind + hourData.solar)
            let status = ''
            if (netLoad < 3) status = ' (Very tight - minimal headroom)'
            else if (netLoad < 8) status = ' (Moderate flexibility available)'
            return `Net Load: ${netLoad.toFixed(1)}GW${status}`
          } else {
            return `Total Demand: ${hourData.demand.toFixed(1)}GW`
          }
        },
        afterLabel: function(context: any) {
          if (context.datasetIndex === 0) {
            const hourData = energyStore.chartData?.hourly_data[context.dataIndex]
            if (!hourData) return ''
            return [
              `Wind: ${hourData.wind.toFixed(1)}GW`,
              `Solar: ${hourData.solar.toFixed(1)}GW`,
              `VRE Total: ${(hourData.wind + hourData.solar).toFixed(1)}GW`
            ]
          }
          return ''
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#9ca3af'
      },
      grid: {
        color: 'rgba(156, 163, 175, 0.1)'
      }
    },
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'GW',
        color: '#e5e7eb'
      },
      ticks: {
        color: '#9ca3af'
      },
      grid: {
        color: 'rgba(156, 163, 175, 0.1)'
      }
    }
  }
}
</script>