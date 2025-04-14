<template>
  <div class="h-full flex items-center">
    <div class="max-w-[1500px] h-full mx-8 grid grid-cols-2 gap-6">
      <!-- Left side - Featured Photo -->
      <div class="h-full">
        <FeaturedPhoto
          v-if="featuredPhoto"
          :photo="featuredPhoto"
        />
      </div>
      
      <!-- Right side - Photo grid -->
      <div class="h-full overflow-y-auto custom-scrollbar">
        <PhotoGrid
          :photos="gridPhotos"
        />
      </div>
    </div>
    
    <!-- Photo Modal -->
    <PhotoModal
      v-if="uiStore.isModalOpen"
      v-model="uiStore.selectedPhoto"
      :photos="displayPhotos"
      @close="uiStore.closeModal"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import PhotoModal from '../components/PhotoModal.vue'
  import FeaturedPhoto from '@/components/FeaturedPhoto.vue'
  import PhotoGrid from '@/components/PhotoGrid.vue'
  import { usePhotoShootStore } from '@/stores/photoShootStore'
  import { useUiStore } from '@/stores/uiStore'
  
  const uiStore = useUiStore()
  const photoShootStore = usePhotoShootStore()
    const isPhotographyIndex = computed(() => 
    uiStore.isPhotography && !uiStore.currentPageParams.location
  )

  // Get the photos to display based on current route
  const displayPhotos = computed(() => {
    if (isPhotographyIndex.value) {
      // For the index page, get only the first photo from each photoshoot
      return photoShootStore.photoShoots.map(shoot => shoot.photos[0]).filter(Boolean)
    } else if (uiStore.isPhotography && uiStore.currentPageParams.location) {
      // For a specific location, find the matching photoshoot and return all its photos
      const location = uiStore.currentPageParams.location
      const matchingShoot = photoShootStore.photoShoots.find(
        shoot => shoot.location.toLowerCase() === location.toLowerCase()
      )
      return matchingShoot ? matchingShoot.photos : []
    }
    
    // Default (shouldn't reach here, but just in case)
    return []
  })

  const featuredPhoto = computed(() => {
    return displayPhotos.value.length > 0 ? displayPhotos.value[0] : null
  })

  const gridPhotos = computed(() => {
    return displayPhotos.value.slice(1)
  })
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
