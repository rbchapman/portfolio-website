import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Photo } from '../types'

export const useUiStore = defineStore('ui', () => {
  // Initial load state
  const hasCompletedInitialLoad = ref(false)
  
  // Hover and modal states
  const hoveredPhoto = ref<Photo | null>(null)
  const selectedPhoto = ref<Photo | null>(null)
  const isModalOpen = ref(false)
  
  // Initial load function
  function completeInitialLoad() {
    hasCompletedInitialLoad.value = true
  }
  
  // Hover functions
  function handleMouseEnter(photo: Photo) {
    hoveredPhoto.value = photo
  }
  
  function handleMouseLeave() {
    hoveredPhoto.value = null
  }
  
  // Modal functions
  function openModal(photo: Photo) {
    selectedPhoto.value = photo
    isModalOpen.value = true
  }
  
  function closeModal() {
    selectedPhoto.value = null
    isModalOpen.value = false
  }

  const isPaused = computed(() => {
    return hoveredPhoto.value !== null || isModalOpen.value
  })
  
  return {
    // State
    hasCompletedInitialLoad,
    hoveredPhoto,
    selectedPhoto,
    isModalOpen,
    isPaused,
    
    // Functions
    completeInitialLoad,
    handleMouseEnter,
    handleMouseLeave,
    openModal,
    closeModal
  }
})