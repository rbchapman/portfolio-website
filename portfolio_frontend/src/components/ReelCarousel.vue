<template>
  <div class="overflow-hidden carousel-container w-full relative">
    <div
      class="scroll-track"
      :style="{ animationPlayState: uiStore.isPaused ? 'paused' : 'running' }"
      ref="scrollTrack"
    >
      <div class="flex">
        <div
          v-for="photo in carouselPhotos"
          :key="photo.id + '-' + photo.duplicateIndex"
          class="max-w-4xl max-h-2xl mr-6 shadow-lg overflow-hidden relative cursor-pointer"
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
                ? 'h-auto w-auto max-h-[60vh]'
                : 'w-auto h-auto max-h-[60vh] max-w-3xl'
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

<style scoped>
  @keyframes scroll {
    0% {
      transform: translateX(0);
    }
    100% {
      transform: translateX(-50%);
    }
  }

  .scroll-track {
    display: flex;
    width: max-content;
    animation: scroll 100s linear infinite;
  }

  .scroll-track::-webkit-scrollbar {
    display: none;
  }

  .scroll-track {
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
</style>