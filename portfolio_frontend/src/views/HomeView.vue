<template>
  <div>
    <ActionBar :action="toggleBar" />
    <ReelCarousel
      class="pt-4"
      :photos="photoShootStore.carouselPhotos"
      @photoSelect="selectPhoto"
    />
    <PhotoModal
      v-if="selectedPhoto"
      v-model="selectedPhoto"
      :photos="photoShootStore.carouselPhotos"
      @close="closeModal"
    />
  </div>
</template>

<script setup lang="ts">
  import ReelCarousel from '../components/ReelCarousel.vue'
  import ActionBar from '../components/ActionBar.vue'
  import PhotoModal from '../components/PhotoModal.vue'
  import { ref } from 'vue'
  import type { Photo, ToggleAction } from '../types'
  import { usePhotoShootStore } from '@/stores/photoShootStore'

  const photoShootStore = usePhotoShootStore()
  const selectedPhoto = ref<Photo | null>(null)
  const toggleBar: ToggleAction = {
    title: 'Measurements',
    type: 'toggle',
    content: {
      HEIGHT: '180CM',
      WAIST: '71CM',
      SHOES: '42',
      HAIR: 'RED',
      EYES: 'BLUE'
    }
  }

  const selectPhoto = (photo: Photo) => {
    selectedPhoto.value = photo
  }

  const closeModal = () => {
    selectedPhoto.value = null
  }
</script>
