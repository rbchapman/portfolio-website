<template>
  <div class="h-full flex items-center">
    <div :class="[
      'h-full mx-6 gap-6',
      siteConfig.isEnergy ? 'flex w-full' : 'max-w-[1500px] grid grid-cols-2'
    ]">
      <!-- Left side - Chart/Featured Photo -->
      <div :class="siteConfig.isEnergy ? 'flex-1' : 'h-full'">
        <EnergyChart v-if="siteConfig.isEnergy" />
        <FeaturedPhoto
          v-else-if="photoStore.featuredPhoto"
          :photo="photoStore.featuredPhoto"
        />
      </div>

      <!-- Right side - Panel/Photo grid -->
      <div :class="[
        'h-full overflow-y-auto custom-scrollbar',
        siteConfig.isEnergy ? 'w-85 overflow-y-hidden' : ''
      ]">
        <DashboardPanel v-if="siteConfig.isEnergy" />
        <PhotoGrid v-else :photos="photoStore.gridPhotos" />
      </div>
    </div>

    <!-- Photo Modal -->
    <PhotoModal
      v-if="uiStore.isModalOpen"
      v-model="uiStore.selectedPhoto"
      :photos="photoStore.displayPhotos"
      @close="uiStore.closeModal"
    />
  </div>
</template>

<script setup lang="ts">
  import PhotoModal from '../components/PhotoModal.vue'
  import FeaturedPhoto from '@/components/FeaturedPhoto.vue'
  import PhotoGrid from '@/components/PhotoGrid.vue'
  import EnergyChart from '@/components/EnergyChart.vue'
  import DashboardPanel from '@/components/DashboardPanel.vue'
  import { usePhotoStore } from '@/stores/photoStore'
  import { useUiStore } from '@/stores/uiStore'
  import { useRoute } from 'vue-router'
  import { watch, onMounted } from 'vue'
  import { siteConfig } from '@/utils/siteConfig'

  const photoStore = usePhotoStore()
  const uiStore = useUiStore()
  const route = useRoute()

  function updateDisplayPhotos() {
    const locationParam = route.params.location
    const location =
      typeof locationParam === 'string' ? locationParam : undefined

    const photos = photoStore.getCollectionPhotos(!location, {
      location: location || ''
    })
    photoStore.displayPhotos = photos
  }

  onMounted(() => {
    updateDisplayPhotos()
  })

  // Watch for route param changes to update photos
  watch(
    () => route.params.location,
    () => {
      updateDisplayPhotos()
    }
  )
</script>

<style scoped>
  .custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
    padding-right: 10px;
    margin-right: -8px;
    -webkit-overflow-scrolling: touch;
  }
</style>
