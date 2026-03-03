<template>
  <div class="w-full flex justify-center items-center pb-4">
    <div class="text-center">
      <router-link
        :to="{ name: 'home' }"
        class="block text-white"
        :class="{ 'cursor-default': uiStore.isHome }"
        @click.prevent="navigateToHome"
      >
        <span class="font-['Inter'] text-6xl md:text-6xl lg:text-8xl font-medium tracking-tight">{{ displayBoldText }}</span>
        <span class="font-['Cormorant'] text-9xl font-light normal-case italic">{{ displayItalicText }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/uiStore'
import { useEnergyStore } from '@/stores/energyStore'
import { siteConfig } from '@/utils/siteConfig'
import { computed } from 'vue'

const uiStore = useUiStore()
const energyStore = useEnergyStore()

const props = defineProps({
  boldText: {
    type: String,
    required: true
  },
  italicText: {
    type: String,
    required: true
  }
})

const displayBoldText = computed(() => {
  if (!siteConfig.isEnergy) return props.boldText
  return energyStore.selectedRegion === 'california' ? 'California' : 'Spanish'
})

const displayItalicText = computed(() => {
  if (!siteConfig.isEnergy) return props.italicText
  return 'GridAnalysis'
})

const router = useRouter()

const navigateToHome = () => {
  router.push({ name: 'home' })
}
</script>