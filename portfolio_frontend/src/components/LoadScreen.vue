<template>
  <Transition name="fade">
    <div
      v-if="uiStore.showLoadScreen && !uiStore.isPhotography"
      class="fixed z-[51] inset-0 bg-custom-dark flex flex-col justify-between outline-none"
      @keydown.enter="handleEnterKey"
      tabindex="0"
      ref="loadScreenRef"
    >
      <!-- Title section -->
      <div class="flex flex-col items-center">
        <PageTitle boldText="RileyBenjamin" italicText="Chapman" />
        
        <!-- Text container with fixed dimensions -->
        <div class="text-center h-8 relative">
          <transition name="text-fade" mode="out-in">
            <div 
              v-if="!isLoaded" 
              key="loading"
              class="pulsate-text"
            >
              loading...
            </div>
            <div
              v-else
              key="enter"
              @click="uiStore.noLoad()"
              class="cursor-pointer text-white/70 hover:text-white opacity-100 underline-offset-4 hover:underline decoration-[0.25px]"
            >
              ENTER
            </div>
          </transition>
        </div>
      </div>
      
      <!-- Carousel at bottom -->
      <ReelCarousel
        v-if="uiStore.carouselLoaded"
        class="w-full"
        :photos="photoStore.carouselPhotos"
      />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import ReelCarousel from './ReelCarousel.vue'
import { usePhotoStore } from '@/stores/photoStore'
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

const loadScreenRef = ref<HTMLDivElement | null>(null)
const minTimeElapsed = ref(false)
const photoStore = usePhotoStore()
const uiStore = useUiStore()

// Computed property to determine when to show the ENTER button
// Will only be true when both minimum time has passed AND carousel is loaded
const isLoaded = computed(() => 
  minTimeElapsed.value && uiStore.carouselLoaded
)

function handleEnterKey() {
  if (isLoaded.value) {
    uiStore.noLoad()
  }
}

onMounted(() => {
  // Start loading the portfolio data
  photoStore.loadPortfolioData()
  
  // Focus the load screen to capture keydown events
  if (loadScreenRef.value) {
    loadScreenRef.value.focus()
  }
  
  // Set minimum time flag after 2 seconds
  setTimeout(() => {
    minTimeElapsed.value = true
  }, 2000)
  
  // Auto-hide the load screen after 10 seconds
  setTimeout(() => {
    uiStore.noLoad()
  }, 10000)
})
</script>

<style scoped>
.pulsate-text {
  animation: textPulsate 2s infinite ease-in-out;
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