<template>
  <div>
    <!-- <ActionBar :action="toggleBar" /> -->
    <ReelCarousel
      class="pt-6"
      :photos="photoShootStore.carouselPhotos"
    />
  </div>
</template>

<script setup lang="ts">
  import ReelCarousel from '../components/ReelCarousel.vue'
  import ActionBar from '../components/ActionBar.vue'
  import type { ToggleAction } from '../types'
  import { usePhotoShootStore } from '@/stores/photoShootStore'

  const photoShootStore = usePhotoShootStore()
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

</script>
