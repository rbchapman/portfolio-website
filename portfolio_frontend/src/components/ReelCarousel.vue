<!-- Updated template section with the typewriter effect -->
<template>
  <div class="overflow-hidden w-full relative">
    <div
      class="scroll-track"
      :style="{ animationPlayState: uiStore.isPaused ? 'paused' : 'running' }"
      ref="scrollTrack"
    >
      <div class="flex">
        <!-- This div now contains the typewriter animation -->
        <div class="w-[100vw] flex items-center justify-center">
          <div class="typewriter">
            <p>Loading...</p>
          </div>
        </div>
        
        <div
          v-for="photo in carouselPhotos"
          :key="photo.id + '-' + photo.duplicateIndex"
          class="max-w-4xl mr-6 shadow-lg overflow-hidden relative cursor-pointer"
          @mouseenter="uiStore.setHover(photo)"
          @mouseleave="uiStore.clearHover()"
          @click="uiStore.openModal(photo)"
        >
          <img
            :src="photo.optimized_images.full"
            :alt="photo.title"
            loading="eager"
            :class="[
              !photo?.is_portrait
                ? 'h-auto max-h-[60vh]'
                : 'w-auto max-h-[60vh] max-w-3xl'
            ]"
          />
          <!-- Overlay with photo details, only shown when this specific photo is hovered -->
          <div
            v-show="uiStore.hoveredPhoto?.id === photo.id"
            class="absolute inset-0 bg-black bg-opacity-60 transition-opacity duration-200"
          >
            <PhotoDetails
              v-if="uiStore.hoveredPhoto?.id === photo.id"
              :photo="uiStore.hoveredPhoto"
              class="mt-6"
            />
          </div>
        </div>
      </div>
    </div>
    <PhotoModal
      v-if="uiStore.selectedPhoto"
      v-model="uiStore.selectedPhoto"
      :photos="photoShootStore.carouselPhotos"
      @close="uiStore.closeModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import PhotoModal from '../components/PhotoModal.vue'
import PhotoDetails from './PhotoDetails.vue'
import { usePhotoShootStore } from '@/stores/photoShootStore'
import { useUiStore } from '@/stores/uiStore'

const photoShootStore = usePhotoShootStore()
const uiStore = useUiStore()
const scrollTrack = ref<HTMLElement | null>(null)

// Clone the photos for continuous scrolling effect
const carouselPhotos = computed(() => {
  return [
    ...photoShootStore.carouselPhotos,
    ...photoShootStore.carouselPhotos
  ].map((photo, index) => ({
    ...photo,
    duplicateIndex: index < photoShootStore.carouselPhotos.length ? 0 : 1
  }))
})

onMounted(() => {
  if (photoShootStore.carouselPhotos.length === 0) {
    photoShootStore.fetchCarouselPhotos()
  }
})
</script>

<style>
@keyframes slide-from-right {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-100%);
  }
}

.scroll-track {
  display: flex;
  width: max-content;
  animation: slide-from-right 200s linear infinite;
}

.scroll-track::-webkit-scrollbar {
  display: none;
}

.scroll-track {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

/* Typewriter effect styles */
.typewriter p {
  overflow: hidden;
  border-right: 0.15em solid #666;
  white-space: nowrap;
  margin: 0 auto;
  letter-spacing: 0.15em;
  color: #333;
  font-size: 1.5rem;
  animation: 
    typing 3.5s steps(30, end) infinite,
    blink-caret 0.75s step-end infinite;
}

/* The typing effect */
@keyframes typing {
  0% { width: 0 }
  50% { width: 100% }
  90% { width: 100% }
  100% { width: 0 }
}

/* The typewriter cursor effect */
@keyframes blink-caret {
  from, to { border-color: transparent }
  50% { border-color: #666 }
}
</style>