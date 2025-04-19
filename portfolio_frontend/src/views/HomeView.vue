<template>
  <div class="h-full flex items-center">
    <div class="max-w-[1500px] h-full mx-8 grid grid-cols-2 gap-6">
      <!-- Left side - Featured Photo -->
      <div class="h-full">
        <FeaturedPhoto
          v-if="photoStore.featuredPhoto"
          :photo="photoStore.featuredPhoto"
        />
      </div>
      
      <!-- Right side - Photo grid -->
      <div class="h-full overflow-y-auto custom-scrollbar">
        <PhotoGrid
          :photos="photoStore.gridPhotos"
        />
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
  import { onMounted } from 'vue'
  import PhotoModal from '../components/PhotoModal.vue'
  import FeaturedPhoto from '@/components/FeaturedPhoto.vue'
  import PhotoGrid from '@/components/PhotoGrid.vue'
  import { usePhotoStore } from '@/stores/photoStore'
  import { useUiStore } from '@/stores/uiStore'
  
  const photoStore = usePhotoStore()
  const uiStore = useUiStore()
  
  onMounted(() => {
    // Use the optimized loading sequence from the photoStore
    // instead of just fetching all photos
    if (photoStore.displayPhotos.length === 0) {
      photoStore.fetchDisplayPhotos()
    }
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