<template>
  <div class="w-full h-[45px] text-sm uppercase tracking-wider">
    <div class="flex text-white/70 items-center h-full justify-between px-8">
      <!-- Left: Section heading -->
      <div class="flex items-center overflow-hidden">
        <h1
          class="bg-transparent cursor-pointer transition-all duration-500  uppercase whitespace-nowrap"
          :class="{
            'text-white opacity-100 cursor-pointer hover:text-white underline-offset-4 underline decoration-[0.25px]': 
              isToggled
          }"
          @click="toggleLeftSection"
        >
          {{ currentConfig.label }}
        </h1>
        
        <!-- Section content with conditional rendering based on type -->
        <div class="flex items-center ml-4 transition-all duration-500 overflow-hidden whitespace-nowrap"
          :class="{
            'opacity-0 max-w-0': !isToggled,
            'opacity-100 max-w-[800px]': isToggled
          }"
        >
          <!-- Key-Value section (measurements) -->
          <template v-if="currentConfig.section.type === 'keyValue'">
            <template v-for="(value, key, index) in (currentConfig.section.items as Record<string, string>)" :key="key">
              <span class="opacity-70">{{ key }} {{ value }}</span>
              <span v-if="index < Object.keys(currentConfig.section.items).length - 1" class="mx-2 opacity-50">|</span>
            </template>
          </template>
          
          <!-- Links section (photography locations) -->
          <template v-else-if="currentConfig.section.type === 'links' && linkSection">
            <!-- ALL link -->
            <div class="flex items-center">
              <router-link 
                :to="linkSection.baseRoute"
                class="hover:text-white transition-opacity duration-200"
                :class="{
                  'text-white': !linkSection.activePath,
                  'opacity-70': linkSection.activePath
                }"
              >
                ALL
              </router-link>
            </div>
            
            <!-- Location links -->
            <template v-for="(item, index) in linkSection.items" :key="index">
              <span class="mx-2 opacity-50">|</span>
              <div class="flex items-center">
                <router-link 
                  :to="`${item[linkSection.valueKey]}`"
                  class="hover:text-white transition-opacity duration-200"
                  :class="{
                    'text-white': 
                      route.params.location === item[linkSection.valueKey],
                    'opacity-70': route.params.location !== item[linkSection.valueKey]
                  }"
                >
                  {{ item[linkSection.displayKey || linkSection.valueKey] }}
                </router-link>
              </div>
            </template>
          </template>
          
          <!-- List section (tech stack) -->
          <template v-else-if="currentConfig.section.type === 'list'">
            <template v-for="(item, index) in (currentConfig.section as ListSection).items" :key="index">
              <span class="opacity-70">{{ item }}</span>
              <span v-if="index < (currentConfig.section as ListSection).items.length - 1" class="mx-2 opacity-50">|</span>
            </template>
          </template>
        </div>
      </div>
      
      <!-- Right: Navigation Links -->
      <div class="flex items-center">
        <template v-for="link in currentConfig.rightLinks" :key="link.to">
          <router-link
            :to="link.to"
            class="pl-2 text-sm hover:text-white"
            :class="{
              'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]': 
                link.activeWhen(route)
            }"
          >
            {{ link.label }}
          </router-link>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import { useUiStore } from '@/stores/uiStore'
  import { usePhotoStore } from '@/stores/photoStore'
  import { actionBarConfigs } from '@/config/actionBarConfig'
  import type { LinkSection, ListSection } from '@/types/actionBar'
  import { siteConfig } from '@/utils/siteConfig'

  const route = useRoute()
  const photoStore = usePhotoStore()

  // Determine the current configuration based on route
  const currentConfig = computed(() => {
    if (siteConfig.isPortfolio) {
    return actionBarConfigs.portfolio
  }
  if (siteConfig.isEnergy) {
    return actionBarConfigs.energy
  }
  const config = actionBarConfigs.home
    // Update dynamic data for photography section
    if (config.section.type === 'links') {
      // Cast to the specific section type for better type safety
      const linkSection = config.section as LinkSection
      
      // Update with actual photoshoots data
      linkSection.items = photoStore.collections
      linkSection.activePath = route.params.location as string || null
    }
    
    return config
  })

  // Add this computed property to access the link section with proper typing
  const linkSection = computed(() => {
    if (currentConfig.value.section.type === 'links') {
      return currentConfig.value.section as LinkSection
    }
    return null
  })

  const isToggled = ref(false)


  const toggleLeftSection = () => {
    isToggled.value = !isToggled.value
  }
</script>