<template>
  <div class="overflow-hidden w-full relative">
    <div
      class="scroll-track"
      :style="{ animationPlayState: isPaused ? 'paused' : 'running' }"
      ref="scrollTrack"
    >
      <!-- First set of photos -->
      <div class="flex">
        <div
          v-for="photo in photoShootStore.carouselPhotos"
          :key="photo.id"
          class="max-w-4xl max-h-2xl shadow-lg overflow-hidden relative cursor-crosshair"
          @mouseenter="handleMouseEnter(photo)"
          @mouseleave="handleMouseLeave()"
          @click="openModal(photo)"
        >
          <img
            :src="photo.image"
            :alt="photo.title"
            loading="eager"
            :class="[
              !photo?.is_portrait
                ? 'h-auto w-auto max-h-[60vh]'
                : 'w-auto h-auto max-h-[60vh] max-w-3xl'
            ]"
          />
          <HoverInfo 
            v-if="showHoverInfo?.id === photo.id" 
            :photo="photo" 
          />
        </div>
      </div>
      <!-- Clone set for smooth looping -->
      <div class="flex">
        <div
          v-for="photo in photoShootStore.carouselPhotos"
          :key="photo.id"
          class="max-w-4xl max-h-2xl shadow-lg overflow-hidden relative cursor-crosshair"
          @mouseenter="handleMouseEnter(photo)"
          @mouseleave="handleMouseLeave()"
          @click="openModal(photo)"
        >
          <img
            :src="photo.image"
            :alt="photo.title"
            loading="eager"
            :class="[
              !photo?.is_portrait
                ? 'h-auto w-auto max-h-[60vh]'
                : 'w-auto h-auto max-h-[60vh] max-w-3xl'
            ]"
          />
          <HoverInfo 
            v-if="showHoverInfo?.id === photo.id" 
            :photo="photo" 
          />
        </div>
      </div>
    </div>
    <PhotoModal
      v-if="selectedPhoto"
      v-model="selectedPhoto"
      :photos="photoShootStore.carouselPhotos"
      @close="closeModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PhotoModal from '../components/PhotoModal.vue'
import HoverInfo from './HoverInfo.vue'
import type { Photo } from '../types'
import { usePhotoShootStore } from '@/stores/photoShootStore'

const photoShootStore = usePhotoShootStore()
const selectedPhoto = ref<Photo | null>(null)
const isModalOpen = ref<boolean>(false)
const scrollTrack = ref<HTMLElement | null>(null)
const showHoverInfo = ref<Photo | null>(null)

const isPaused = computed(() => {
  return showHoverInfo.value !== null || isModalOpen.value
})

const closeModal = () => {
  selectedPhoto.value = null
  isModalOpen.value = false
}

const openModal = (photo: Photo) => {
  isModalOpen.value = true
  selectedPhoto.value = photo
}

const handleMouseEnter = (photo: Photo) => {
  showHoverInfo.value = photo
}

const handleMouseLeave = () => {
  showHoverInfo.value = null
}
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