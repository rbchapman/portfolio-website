<template>
  <div class="w-full h-[45px] text-sm uppercase tracking-wider">
    <div class="flex text-white/70 items-center h-full justify-between px-8">
      <!-- Left: Measurements Section -->
      <div class="flex items-center overflow-hidden">
        <h1
          class="cursor-pointer bg-transparent transition-all duration-500 hover:text-white uppercase whitespace-nowrap"
          :class="{
            'text-white opacity-100 underline-offset-4 underline decoration-[0.25px]': isMeasurementsOpen,
            'opacity-70': !isMeasurementsOpen
          }"
          @click="toggleMeasurements"
        >
          MEASUREMENTS
        </h1>
        
        <!-- Measurements Display -->
        <div class="flex items-center ml-4 transition-all duration-500 overflow-hidden whitespace-nowrap"
          :class="{
            'opacity-0 max-w-0': !isMeasurementsOpen,
            'opacity-100 max-w-[600px]': isMeasurementsOpen
          }"
        >
          <template v-for="(value, key, index) in measurementsData" :key="key">
            <span class="opacity-70">{{ key }} {{ value }}</span>
            <span v-if="index < Object.keys(measurementsData).length - 1" class="mx-2 opacity-50">|</span>
          </template>
        </div>
      </div>
      
      <!-- Right: Campaigns and Photos Links -->
      <div class="flex items-center">
        <router-link 
          to="/"
          class="px-2 text-sm hover:text-white"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': !uiStore.isCampaigns
          }"
        >
          PHOTOS
        </router-link>
        <router-link 
          to="/campaigns"
          class="pl-2 text-sm hover:text-white"
          :class="{
            'underline text-white underline-offset-4 decoration-[0.25px]': uiStore.isCampaigns
          }"
        >
          CAMPAIGNS
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUiStore } from '@/stores/uiStore'

const uiStore = useUiStore()

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

const toggleMeasurements = () => {
  isMeasurementsOpen.value = !isMeasurementsOpen.value
}
</script>