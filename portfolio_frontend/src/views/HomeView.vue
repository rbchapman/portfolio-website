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
  import { computed, onMounted } from 'vue'
  import PhotoModal from '../components/PhotoModal.vue'
  import FeaturedPhoto from '@/components/FeaturedPhoto.vue'
  import PhotoGrid from '@/components/PhotoGrid.vue'
  import { usePhotoShootStore } from '@/stores/photoShootStore'
  import { useUiStore } from '@/stores/uiStore'

  const photoShootStore = usePhotoShootStore()
  const uiStore = useUiStore()

  onMounted(() => {
  photoShootStore.fetchAllPhotos()
})

  // Get all display photos for the current page
  const displayPhotos = computed(() => photoShootStore.allPhotos)

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
