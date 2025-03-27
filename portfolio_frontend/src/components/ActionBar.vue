<template>
  <div class="w-full h-[45px] text-sm uppercase tracking-wider">
    <div class="flex text-white/70 items-center h-full relative px-6">
      <!-- Left: Measurements Toggle -->
      <div class="flex items-center">
        <h1
          class="cursor-pointer bg-transparent transition-all duration-700 hover:text-white uppercase mr-2"
          :class="{
            'text-white opacity-100 underline-offset-4 underline decoration-[0.25px]': isMeasurementsOpen,
            'opacity-70': !isMeasurementsOpen
          }"
          @click="toggleMeasurements"
        >
          MEASUREMENTS
        </h1>
        
        <!-- Compact Measurements Display -->
        <div class="overflow-hidden flex items-center">
          <div
            class="transition-all duration-500 flex"
            :class="{
              'opacity-0 max-w-0': !isMeasurementsOpen,
              'opacity-100 max-w-md': isMeasurementsOpen
            }"
          >
            <span v-for="(value, key) in measurementsData" :key="key" class="px-1 text-xs opacity-70">
              {{ key }} 
              <span class="text-white">
                {{ value }}
              </span>
            </span>
          </div>
        </div>
      </div>

      <!-- Center: Navigation Buttons - Fixed Position -->
      <div 
        class="flex justify-center h-full items-center absolute left-1/2 transform -translate-x-1/2 transition-all duration-500 overflow-hidden"
        :class="{
          'opacity-0 max-w-0': isMeasurementsOpen,
          'opacity-100 max-w-md': !isMeasurementsOpen
        }"
      >
        <router-link
          v-for="route in navigationRoutes"
          :key="route.path"
          :to="route.path"
          class="px-2 text-sm hover:text-white opacity-70"
          @mouseleave="uiStore.clearHover()"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': isUnderlined(route.label)
          }"
        >
          {{ route.label }}
        </router-link>
      </div>

      <!-- Right: Always Visible Portfolio and Campaigns Links -->
      <div class="flex items-center absolute right-8">
        <router-link 
          to="/portfolio" 
          class="px-2 text-sm hover:text-white opacity-70"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': !uiStore.isCampaigns
          }"
        >
          PORTFOLIO
        </router-link>
        <router-link 
          to="/campaigns/1" 
          class="px-2 text-sm hover:text-white opacity-70"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': uiStore.isCampaigns
          }"
        >
          CAMPAIGNS
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores/uiStore'

const uiStore = useUiStore()
const route = useRoute()

// State management
const isMeasurementsOpen = ref(false)

// Measurements data
const measurementsData = {
  'HEIGHT': '180CM',
  'WAIST': '71CM',
  'SHOES': '42',
  'HAIR': 'RED',
  'EYES': 'BLUE'
}

// Navigation routes
const navigationRoutes = computed(() => {
  // Base navigation path (portfolio, etc)
  const basePath = 'portfolio'
  // Number of pages
  const count = 4
  
  const indexedRoutes = Array.from({ length: count }, (_, i) => ({
    path: `/${basePath}/${i + 1}`,
    label: `${i + 1}`
  }))
  
  return [
    { path: `/${basePath}`, label: 'ALL' },
    ...indexedRoutes
  ]
})

// Check if a route should be underlined
const isUnderlined = (label: string | number) => {
  if (!route.params.order) {
    return label === 'ALL'
  } else {
    return String(label) === String(route.params.order)
  }
}

// Toggle function for measurements only
const toggleMeasurements = () => {
  isMeasurementsOpen.value = !isMeasurementsOpen.value
}
</script>