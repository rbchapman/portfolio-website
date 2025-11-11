
<template>
  <div class="h-full w-full p-4 flex flex-col">
    <div class="flex-1 min-h-0">
      <Bar v-if="energyStore.bessAnalysis" :data="chartData" :options="chartOptions" class="h-full" />
      <div v-else class="h-full flex items-center justify-center text-custom-text text-sm">
        Configure battery system and run analysis to see operational decisions
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { 
  Chart, 
  CategoryScale, 
  LinearScale, 
  BarElement,
  LineElement,
  PointElement,
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js'
import { useEnergyStore } from '@/stores/energyStore'
import { computed } from 'vue'

Chart.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend)

const energyStore = useEnergyStore()

const chartData = computed(() => {
  if (!energyStore.bessAnalysis?.hourly_decisions) return { labels: [], datasets: [] }
  
  const decisions = energyStore.bessAnalysis.hourly_decisions
  const hours = decisions.map(d => d.hour)
  
  // Separate charge and discharge into different datasets for stacking
  const chargeData = decisions.map(d => d.action === 'CHARGE' ? d.energy_mwh : 0)
  const dischargeData = decisions.map(d => d.action === 'DISCHARGE' ? -d.energy_mwh : 0)
  const prices = decisions.map(d => d.price)
  
  return {
    labels: hours,
    datasets: [
      // Price line (on secondary axis)
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
        order: 1
      },
      // Charge bars (green, going up)
      {
        type: 'bar',
        label: 'Charging',
        data: chargeData,
        backgroundColor: 'rgba(34, 197, 94, 0.7)',
        borderColor: '#22c55e',
        borderWidth: 1,
        yAxisID: 'y-energy',
        order: 2
      },
      // Discharge bars (red, going down)
      {
        type: 'bar',
        label: 'Discharging',
        data: dischargeData,
        backgroundColor: 'rgba(239, 68, 68, 0.7)',
        borderColor: '#ef4444',
        borderWidth: 1,
        yAxisID: 'y-energy',
        order: 2
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false
  },
  plugins: {
    title: {
      display: true,
      text: 'BESS Operations: Price Dynamics & Battery Actions',
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
      display: true,
      position: 'bottom' as const,
      labels: {
        color: '#e5e7eb',
        font: {
          size: 12
        },
        padding: 15,
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
    displayColors: false,
    callbacks: {
      title: (context: any) => {
        const decision = energyStore.bessAnalysis?.hourly_decisions[context[0].dataIndex]
        const actionEmoji = decision?.action === 'CHARGE' ? '🟢' : decision?.action === 'DISCHARGE' ? '🔴' : '⚪'
        return `${actionEmoji} ${decision?.hour} - ${decision?.action}`
      },
      label: (context: any) => {
        const decision = energyStore.bessAnalysis?.hourly_decisions[context.dataIndex]
        
        if (context.dataset.label !== 'Market Price') {
          return null
        }
        
        return [
          `Price: €${decision?.price.toFixed(2)}/MWh`,
          `SoC: ${decision?.soc_before.toFixed(1)}% → ${decision?.soc_after.toFixed(1)}%`,
          decision?.energy_mwh > 0 ? `Energy: ${decision.energy_mwh.toFixed(1)} MWh` : ''
        ].filter(Boolean)
      },
      // afterLabel: (context: any) => {
      //   const decision = energyStore.bessAnalysis?.hourly_decisions[context.dataIndex]
        
      //   if (context.dataset.label === 'Market Price' && decision?.reasoning) {
      //     return [
      //       '',
      //       ...decision.reasoning
      //     ]
      //   }
      //   return ''
      // }
    }
  }
  },
  scales: {
    x: {
      stacked: true,
      title: {
        display: true,
        text: 'Hour of Day',
        color: '#e5e7eb',
        font: { size: 13 }
      },
      ticks: {
        color: '#9ca3af',
        maxRotation: 45,
        minRotation: 45
      },
      grid: {
        color: 'rgba(156, 163, 175, 0.1)'
      }
    },
    'y-energy': {
      stacked: true,
      position: 'left' as const,
      title: {
        display: true,
        text: 'Energy Flow (MWh)',
        color: '#e5e7eb',
        font: { size: 13, weight: 'bold' as const }
      },
      ticks: {
        color: '#9ca3af',
        callback: function(value: any) {
          return value + ' MWh'
        }
      },
      grid: {
        color: 'rgba(156, 163, 175, 0.1)'
      }
    },
    'y-price': {
      position: 'right' as const,
      title: {
        display: true,
        text: 'Price (€/MWh)',
        color: '#fbbf24',
        font: { size: 13, weight: 'bold' as const }
      },
      ticks: {
        color: '#fbbf24',
        callback: function(value: any) {
          return '€' + value.toFixed(0)
        }
      },
      grid: {
        display: false
      }
    }
  }
}))
</script>