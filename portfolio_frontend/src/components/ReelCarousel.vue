<template>
  <div class="overflow-hidden w-full relative">
    <div
      @mouseover="pauseAnimation"
      @mouseout="unPauseAnimation"
      class="scroll-track"
      :style="{ animationPlayState: isPaused ? 'paused' : 'running' }"
      ref="scrollTrack"
    >
      <!-- First set of photos -->
      <div class="flex">
        <PhotoCard
          v-for="photo in props.photos"
          :key="photo.id"
          :photo="photo"
          class="flex-shrink-0"
          @click="() => handlePhotoSelect(photo)"
        />
      </div>
      <!-- Clone set for smooth looping -->
      <div class="flex">
        <PhotoCard
          v-for="photo in props.photos"
          :key="photo.id"
          :photo="photo"
          class="flex-shrink-0"
          @click="() => handlePhotoSelect(photo)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import PhotoCard from '@/components/PhotoCard.vue'
  import type { Photo } from '../types'

  const props = defineProps<{
    photos: Photo[]
  }>()

  const emit = defineEmits<{
    photoSelect: [photo: Photo]
  }>()

  const isPaused = ref<boolean>(false)
  const scrollTrack = ref<HTMLElement | null>(null)

  const handlePhotoSelect = (photo: Photo) => {
    emit('photoSelect', photo)
  }

  const pauseAnimation = () => {
    isPaused.value = true
  }

  const unPauseAnimation = () => {
    isPaused.value = false
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