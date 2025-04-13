<template>
  <Transition name="fade">
    <div
      v-if="uiStore.showLoadScreen && !uiStore.isPhotography"
      class="fixed z-[51] inset-0 bg-custom-dark flex flex-col justify-between"
    >
      <!-- Title section -->
      <div class="flex flex-col items-center">
        <PageTitle boldText="RileyBenjamin" italicText="Chapman" />
        
        <!-- Pulsating enter text -->
        <div class="text-center">
          <div
            @click="uiStore.noLoad()"
            class="inline-block cursor-pointer transition-all duration-300 pulsate-text"
          >
            <span>ENTER</span>
          </div>
        </div>
      </div>
      
      <!-- Carousel at bottom -->
      <ReelCarousel
        class="w-full"
        :photos="photoShootStore.carouselPhotos"
      />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import ReelCarousel from './ReelCarousel.vue'
import { usePhotoShootStore } from '@/stores/photoShootStore'
import PageTitle from './PageTitle.vue'
import { useUiStore } from '@/stores/uiStore'


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
const uiStore = useUiStore()

const onOpenPortfolio = () => {
  emit('openPortfolio')
}

onMounted(() => {
  // Auto-hide the load screen after 10 seconds (adjust time as needed)
  setTimeout(() => {
    uiStore.noLoad()
  }, 10000) // 10 seconds
})
</script>

<style scoped>
.pulsate-text {
  animation: textPulsate 3s infinite ease-in-out;
}

@keyframes textPulsate {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

/* Transition styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.7s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>