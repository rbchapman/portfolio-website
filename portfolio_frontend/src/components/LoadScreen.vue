<template>
  <div
    class="fixed z-[51] inset-0 bg-black flex flex-col justify-between transition-opacity duration-700 ease-in-out"
    :class="isLoading ? 'opacity-100' : 'opacity-0 pointer-events-none'"
  >
    <!-- Title section with loading text -->
    <div class="pt-10 flex flex-col items-center">
      <h1
        class="text-6xl w-full text-center text-white/90 font-serif scale-y-110 uppercase font-light transform"
      >
        {{ props.title }}
      </h1>
      
      <!-- Pulsating loading text -->
      <div 
        v-if="isLoading" 
        class="loading-text text-white/80 text-xl font-serif mt-4"
      >
        LOADING
      </div>
      
      <!-- Open Portfolio button (when not loading) -->
      <button
        v-else
        @click="onOpenPortfolio"
        class="open-portfolio-btn mt-6"
      >
        OPEN PORTFOLIO
      </button>
    </div>
    
    <!-- Carousel at bottom -->
    <ReelCarousel
      class="w-full pb-8"
      :photos="photoShootStore.carouselPhotos"
    />
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import ReelCarousel from './ReelCarousel.vue'
import { usePhotoShootStore } from '@/stores/photoShootStore'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: true
  },
  title: {
    type: String,
    default: 'Riley Benjamin Chapman'
  }
})

const emit = defineEmits(['openPortfolio'])
const photoShootStore = usePhotoShootStore()

const onOpenPortfolio = () => {
  emit('openPortfolio')
}
</script>

<style scoped>
.loading-text {
  animation: pulse 2s infinite;
  letter-spacing: 3px;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

.open-portfolio-btn {
  padding: 0.75rem 1.5rem;
  background-color: transparent;
  color: white;
  border: 1px solid white;
  font-family: serif;
  letter-spacing: 3px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.open-portfolio-btn:hover {
  background-color: white;
  color: black;
}
</style>