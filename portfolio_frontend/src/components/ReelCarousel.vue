<!-- Updated template section with the typewriter effect -->
<template>
  <div class="w-full relative">
    <div
      class="scroll-track"
      :style="{ animationPlayState: uiStore.isPaused ? 'paused' : 'running' }"
      ref="scrollTrack"
    >
      <div class="flex">
        
        <div
          v-for="photo in carouselPhotos"
          :key="photo.id + '-' + photo.duplicateIndex"
          class="max-w-4xl mr-4 shadow-lg relative"
          @mouseenter="uiStore.setHover(photo)"
          @mouseleave="uiStore.clearHover()"
        >
          <img
            :src="photo.image"
            :alt="photo.title"
            loading="eager"
            :class="[
              !photo?.is_portrait
                ? 'h-auto max-h-[70vh]'
                : 'w-auto max-h-[70vh] max-w-3xl'
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
import { usePhotoStore } from '@/stores/photoStore'
import { useUiStore } from '@/stores/uiStore'
const uiStore = useUiStore()

const photoShootStore = usePhotoStore()
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
  animation: slide-from-right 100s linear infinite;
  -webkit-animation: slide-from-right 100s linear infinite; /* Safari needs this */
  will-change: transform; /* Performance hint */
  transform: translateZ(0); /* Force hardware acceleration */
  -webkit-transform: translateZ(0);
}

/* Hide scrollbars across browsers */
.scroll-track::-webkit-scrollbar {
  display: none;
}

.scroll-track {
  scrollbar-width: none;

}
</style>