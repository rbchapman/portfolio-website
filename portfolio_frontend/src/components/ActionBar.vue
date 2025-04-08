<template>
  <div class="w-full h-[45px] text-sm uppercase tracking-wider">
    <div class="flex text-white/70 items-center h-full relative px-6">
      <!-- Left: Campaigns and Portfolio Links -->
      <div class="flex items-center">
        <router-link 
          to="/campaigns/1" 
          class="px-2 text-sm hover:text-white opacity-70 mr-4"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': uiStore.isCampaigns
          }"
        >
          CAMPAIGNS
        </router-link>
        <router-link 
          to="/" 
          class="px-2 text-sm hover:text-white opacity-70"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': !uiStore.isCampaigns
          }"
        >
          Photos
        </router-link>
      </div>

      <!-- Center: Navigation Buttons - Fixed Position -->
      <div 
        class="flex justify-center h-full items-center absolute left-1/2 transform -translate-x-1/2 transition-all duration-500 overflow-hidden"
        :class="{
          'opacity-0 max-w-0': isMeasurementsOpen,
          'opacity-100 max-w-md': !isMeasurementsOpen
        }"
      >
        <!-- ALL button only for PhotoShoots -->
        <!-- <router-link
          v-if="!uiStore.isCampaigns"
          to="/"
          class="px-2 text-sm hover:text-white opacity-70"
          @mouseleave="uiStore.clearHover()"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': uiStore.isRouteActive('ALL')
          }"
        >
          ALL
        </router-link> -->
        
        <!-- Numbered routes for both PhotoShoots and Campaigns -->
        <!-- <router-link
          v-if="!uiStore.isHome"
          v-for="i in (uiStore.isCampaigns ? uiStore.campaignCount : uiStore.photoShootCount)"
          :key="`${uiStore.currentBasePath}/${i}`"
          :to="`${uiStore.currentBasePath}/${i}`"
          class="px-2 text-sm hover:text-white opacity-70"
          @mouseleave="uiStore.clearHover()"
          :class="{
            'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': uiStore.isRouteActive(i)
          }"
        >
          {{ i }}
        </router-link> -->
      </div>

      <!-- Right: Measurements Toggle with Left Expansion -->
      <div class="flex items-center absolute right-8">
        <!-- Compact Measurements Display (Expands to the left) -->
        <div class="overflow-hidden flex items-center">
          <div
            class="transition-all duration-500 flex flex-row-reverse"
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
        
        <h1
          class="cursor-pointer bg-transparent transition-all duration-700 hover:text-white uppercase ml-2"
          :class="{
            'text-white opacity-100 underline-offset-4 underline decoration-[0.25px]': isMeasurementsOpen,
            'opacity-70': !isMeasurementsOpen
          }"
          @click="toggleMeasurements"
        >
          MEASUREMENTS
        </h1>
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

// Toggle function for measurements only
const toggleMeasurements = () => {
  isMeasurementsOpen.value = !isMeasurementsOpen.value
}
</script>