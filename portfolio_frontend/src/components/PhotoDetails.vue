<template>
  <dl class="flex ml-6 flex-col gap-1 justify-start">
    <div v-for="(item, index) in detailsToShow" :key="index">
      <!-- Regular text field -->
      <dd v-if="!item.linkField && !item.isInstagram" class="text-white/90 font-medium text-xs uppercase">
        {{ getFieldValue(item.field) }}
      </dd>
      
      <!-- Website link -->
      <dd v-else-if="item.linkField" class="text-white/90 font-medium text-xs uppercase">
        
          <a class="text-white/90 uppercase font-medium text-xs hover:text-white hover:underline transition-colors duration-200"
          :href="getFieldValue(item.linkField)"
          target="_blank"
        >
          {{ getFieldValue(item.field) }}
        </a>
      </dd>
      
      <!-- Instagram link -->
      <dd v-else-if="item.isInstagram" class="text-white/90 font-medium text-xs uppercase">
        
          <a class="text-white/90 uppercase font-medium text-xs hover:text-white hover:underline transition-colors duration-200"
          :href="`https://www.instagram.com/${getFieldValue(item.field)}/`"
          target="_blank"
        >
          @{{ getFieldValue(item.field) }}
        </a>
      </dd>
    </div>
    
    <!-- Show link to location page when on photography index page -->
    <div v-if="!siteConfig.isPortfolio && uiStore.isHome">
      <router-link
        :to="`/${photo.shoot_location}`"
        class="flex items-center text-white/70 -mb-2 hover:text-white transition-colors"
        @click="uiStore.clearHover"
      >
        <div>
          <span class="text-xs hover:underline uppercase underline-offset-4">
            photos
          </span>
          <span class="text-lg ml-1">→</span>
        </div>
      </router-link>
    </div>
  </dl>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Photo, PhotoDetailItem } from '../types/models'
import { useUiStore } from '@/stores/uiStore'
import { siteConfig } from '@/utils/siteConfig'

const uiStore = useUiStore()

const props = defineProps<{
  photo: Photo
}>()

// Simple config object directly in the component
const photoDetailConfigs: Record<string, PhotoDetailItem[]> = {
  home: [
    { field: "photographer.name" },
    { field: "photographer.website_display", linkField: "photographer.website" },
    { field: "photographer.instagram", isInstagram: true }
  ],
  photography: [
    { field: "shoot_location" },
    { field: "photoshoot.description" },
    { field: "shoot_year" }
  ]
}

// Get the fields to display based on current route
const detailsToShow = computed(() => {
  // Use your uiStore to determine the current route
  if (!siteConfig.isPortfolio) {
    return photoDetailConfigs.photography
  } else {
    return photoDetailConfigs.home
  }
})

// Helper to get field values
const getFieldValue = (field: string) => {
  const parts = field.split('.')
  let value: any = props.photo
  
  for (const part of parts) {
    if (value && value[part] !== undefined) {
      value = value[part]
    } else {
      return undefined
    }
  }
  
  return value
}
</script>