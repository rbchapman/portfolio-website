<template>
  <div class="w-full flex justify-center items-center pb-4">
    <div class="text-center">
      <router-link
        :to="{ name: 'home' }"
        class="block text-white"
        :class="{ 'cursor-default': uiStore.isHome }"
        @click.prevent="navigateToHome"
      >
        <span class="font-['Inter'] text-6xl md:text-6xl lg:text-8xl font-medium tracking-tight">{{ boldText }}</span>
        <span class="font-['Cormorant'] text-9xl font-light normal-case italic">{{ italicText }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/uiStore'

const uiStore = useUiStore()

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

const router = useRouter()

const navigateToHome = () => {
  router.push({ name: 'home' })
}
</script>