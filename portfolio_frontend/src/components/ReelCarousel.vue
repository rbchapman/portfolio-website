<template>
  <div class="w-full relative">
    <div
      class="scroll-track"
      :style="{ animationPlayState: uiStore.isPaused ? 'paused' : 'running' }"
      ref="scrollTrack"
    >
      <div class="flex">
        <div
          v-for="photo in photos"
          :key="photo.id"
          class="max-w-4xl mr-4 shadow-lg relative cursor-pointer"
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
          <!-- Overlay with photo details -->
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
    <!-- <PhotoModal
      v-if="uiStore.selectedPhoto"
      v-model="uiStore.selectedPhoto"
      :photos="photos"
      @close="uiStore.closeModal"
    /> -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// import PhotoModal from '../components/PhotoModal.vue'
import PhotoDetails from './PhotoDetails.vue'
import { useUiStore } from '@/stores/uiStore'
import type { Photo } from '@/types/models'

defineProps<{
  photos: Photo[]
}>()

const uiStore = useUiStore()
const scrollTrack = ref<HTMLElement | null>(null)
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
  -webkit-animation: slide-from-right 100s linear infinite;
  will-change: transform;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
}

.scroll-track::-webkit-scrollbar {
  display: none;
}

.scroll-track {
  scrollbar-width: none;
}
</style>