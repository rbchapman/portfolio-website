<template>
  <div class="relative overflow-hidden">
    <ActionBar :action="photoShootsNav" />


    <div class="flex px-16 pt-6">
      <!-- Featured Photo Component -->
      <FeaturedPhoto
        v-if="featuredPhoto"
        :photo="featuredPhoto"
        :isPortfolioIndex="uiStore.isPortfolioIndex"
      />

      <!-- Right side - photo grid with scrollable container -->
      <div class="flex-1 overflow-y-auto custom-scrollbar h-[60vh]">
        <PhotoGrid
          :photos="gridPhotos"
          :isPortfolioIndex="uiStore.isPortfolioIndex"
        />
      </div>
    </div>

    <!-- Photo Modal -->
    <PhotoModal
      v-if="uiStore.selectedPhoto"
      v-model="uiStore.selectedPhoto"
      :photos="selectedShoot?.photos || []"
      @close="uiStore.closeModal"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import { useRoute } from 'vue-router'
  import ActionBar from '../components/ActionBar.vue'
  import PhotoModal from '../components/PhotoModal.vue'
  import FeaturedPhoto from '@/components/FeaturedPhoto.vue'
  import PhotoGrid from '@/components/PhotoGrid.vue'
  import type { NavigationAction } from '../types'
  import { usePhotoShootStore } from '@/stores/photoShootStore'
  import { useUiStore } from '@/stores/uiStore'

  const route = useRoute()
  const photoShootStore = usePhotoShootStore()
  const uiStore = useUiStore()
  const photoShoots = computed(() => photoShootStore.photoShoots)

  const photoShootsNav: NavigationAction = {
    title: 'Portfolio',
    type: 'navigation',
    basePath: 'portfolio',
    count: photoShoots.value.length,
    showBasePath: true
  }

  const selectedShoot = computed(() => {
    if (!route.params.order) return null
    return photoShoots.value.find(
      (shoot) => shoot.order === Number(route.params.order)
    )
  })

  const featuredPhoto = computed(() => {
    const photos = photoShootStore.getPortfolioDisplayPhotos(
      uiStore.isPortfolioIndex,
      uiStore.currentPageParams
    )
    return photos.length > 0 ? photos[0] : null
  })

  const gridPhotos = computed(() => {
    const photos = photoShootStore.getPortfolioDisplayPhotos(
      uiStore.isPortfolioIndex,
      uiStore.currentPageParams
    )
    return photos.slice(1)
  })
</script>
<style scoped>
.custom-scrollbar {
  scrollbar-width: thin; /* For Firefox */
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent; /* For Firefox */
}

.custom-scrollbar::-webkit-scrollbar {
  width: 2px; /* Slightly wider for the circular feel */
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px; /* Full rounded edges to simulate a circle */
  height: 60px; /* Make the thumb shorter */
  min-height: 60px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>