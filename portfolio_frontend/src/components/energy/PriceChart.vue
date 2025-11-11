  <template>
    <div class="h-full w-full p-4 flex flex-col">
      <div class="flex-1 min-h-0">
        <Scatter :data="chartData" :options="chartOptions" class="h-full" />
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { Scatter } from 'vue-chartjs'
  import { Chart, LinearScale, PointElement, Title, Tooltip, Legend } from 'chart.js'
  import type { TooltipItem } from 'chart.js'
  import { useEnergyStore } from '@/stores/energyStore'
  import { computed, onMounted } from 'vue'

  Chart.register(LinearScale, PointElement, Title, Tooltip, Legend)

  // ADD THIS INTERFACE
  interface ScatterPoint {
    x: number
    y: number
    hour: string
    vre_pct: number
  }

  const energyStore = useEnergyStore()

  onMounted(() => {
    energyStore.initializeData()
  })

  const chartData = computed(() => {
    if (!energyStore.chartData?.hourly_data) return { datasets: [] }
      
    const data = energyStore.chartData.hourly_data
    
    // Create scatter points: { x: net_load, y: price }
    const scatterPoints = data.map(d => ({
      x: d.net_load,
      y: d.price,
      hour: d.hour,
      vre_pct: d.vre_pct
    }))
    
    // Color points based on VRE penetration
    const colors = scatterPoints.map(point => {
      if (point.vre_pct > 80) return 'rgba(34, 197, 94, 0.7)' // Green - high VRE
      if (point.vre_pct > 60) return 'rgba(251, 191, 36, 0.7)' // Yellow - medium VRE
      return 'rgba(239, 68, 68, 0.7)' // Red - low VRE
    })
      
    return {
      datasets: [{
        label: 'Hourly Price vs Net Load',
        data: scatterPoints,
        backgroundColor: colors,
        borderColor: colors.map(c => c.replace('0.7', '1')),
        borderWidth: 1,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    }
  })

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'PRICE vs NET LOAD',
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
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#f3f4f6',
        bodyColor: '#d1d5db',
        borderColor: '#374151',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          title: function(context: TooltipItem<'scatter'>[]) {
            const point = context[0].raw as ScatterPoint
            return `Hour: ${point.hour}`
          },
          label: function(context: TooltipItem<'scatter'>) {
            const point = context.raw as ScatterPoint
            return [
              `Net Load: ${point.x.toFixed(1)} GW`,
              `Price: €${point.y.toFixed(2)}/MWh`,
              `VRE Penetration: ${point.vre_pct.toFixed(1)}%`
            ]
          },
          afterLabel: function(context: TooltipItem<'scatter'>) {
            const point = context.raw as ScatterPoint
            const price = point.y
            if (price < 0) return 'Negative price - paid to consume!'
            if (price < 10) return 'Very low price - charge window'
            if (price > 50) return 'High price - discharge window'
            return ''
          }
        }
      }
    },
    scales: {
      x: {
        type: 'linear' as const,
        title: {
          display: true,
          text: 'Net Load (GW)',
          color: '#e5e7eb',
          font: {
            size: 13
          }
        },
        ticks: {
          color: '#9ca3af'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.1)'
        }
      },
      y: {
        type: 'linear' as const,
        title: {
          display: true,
          text: 'Price (EUR/MWh)',
          color: '#e5e7eb',
          font: {
            size: 13
          }
        },
        ticks: {
          color: '#9ca3af',
          callback: function(value: number | string) {
            return '€' + value
          }
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.1)'
        }
      }
    }
  }
  </script>