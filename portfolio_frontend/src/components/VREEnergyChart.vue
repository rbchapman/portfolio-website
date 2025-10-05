<template>
  <div class="h-full w-full p-4 flex flex-col">
    <!-- <h3 class="text-white text-base font-normal mb-2 ml-12">
      VARIABLE RENEWABLE GENERATION & DEMAND
    </h3> -->
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
    
  return {
    labels: data.map(d => d.hour),
    datasets: [
      {
        label: 'Solar PV',
        data: data.map(d => d.solar),
        backgroundColor: 'rgba(251, 191, 36, 0.6)',
        borderColor: '#fbbf24',
        fill: 'origin',
        tension: 0.4
      },
      {
        label: 'Wind',
        data: data.map(d => d.wind + d.solar),
        backgroundColor: 'rgba(16, 185, 129, 0.6)',
        borderColor: '#10b981',
        fill: '-1',
        tension: 0.4
      },
      {
        label: 'Demand',
        data: data.map(d => d.demand),
        borderColor: '#3b82f6',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'VARIABLE RENEWABLE GENERATION & DEMAND',
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
        color: '#ffffff',
        font: {
          size: 12
        },
        padding: 10,
        usePointStyle: true
      }
    },
    tooltip: {
      callbacks: {
        title: function() {
          return '' // Remove hour display
        },
        label: function(context: any) {
          const hourData = energyStore.chartData?.hourly_data[context.dataIndex]
          if (!hourData) return ''
          
          if (context.datasetIndex === 0) { // Solar
            return `Solar: ${hourData.solar}GW`
          } else if (context.datasetIndex === 1) { // Wind
            return `Wind: ${hourData.wind}GW`
          } else { // Demand
            return `Demand: ${hourData.demand}GW`
          }
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#ffffff70'
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'GW',
        color: '#ffffff'
      },
      ticks: {
        color: '#ffffff70'
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  }
}
</script>