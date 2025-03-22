import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { Photo } from '../types'

export const useUiStore = defineStore('ui', () => {
  // Get current route to watch for changes
  const route = useRoute()
  
  // Initial load state
  const hasCompletedInitialLoad = ref(false)
  
  // Hover and modal states
  const hoveredPhoto = ref<Photo | null>(null)
  const selectedPhoto = ref<Photo | null>(null)
  const isModalOpen = ref(false)
  const showDetails = ref(false)
  
  // Previous route path to detect changes
  const previousRoutePath = ref(route.path)
  
  // Watch for route changes to close modal
  watch(() => route.path, (newPath) => {
    if (newPath !== previousRoutePath.value) {
      // Route has changed, close modal and reset hover state
      if (isModalOpen.value) {
        closeModal()
      }
      if (showDetails.value) {
        setShowDetails(false)
      }
      previousRoutePath.value = newPath
    }
  })
  
  // Initial load function
  function completeInitialLoad() {
    hasCompletedInitialLoad.value = true
  }
  
  // Hover functions
  function setHover(photo: Photo) {
    hoveredPhoto.value = photo
  }
  
  function clearHover() {
    hoveredPhoto.value = null
  }
  
  // Modal functions
  function openModal(photo: Photo) {
    selectedPhoto.value = photo
    isModalOpen.value = true
    // When modal is opened, set event listeners for ESC key
    document.addEventListener('keydown', handleKeyDown)
  }
  
  function setShowDetails(value: boolean) {
    showDetails.value = value
  }

  function closeModal() {
    selectedPhoto.value = null
    isModalOpen.value = false
    
    // When modal is closed, remove event listeners
    document.removeEventListener('keydown', handleKeyDown)
  }
  
  // Handle keyboard events for modal
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Escape' && isModalOpen.value) {
      closeModal()
    }
  }
  
  const isPaused = computed(() => {
    return hoveredPhoto.value !== null || isModalOpen.value
  })
  
  return {
    // State
    hasCompletedInitialLoad,
    showDetails,
    selectedPhoto,
    isModalOpen,
    isPaused,
    hoveredPhoto,
    
    // Functions
    completeInitialLoad,
    setHover,
    clearHover,
    openModal,
    closeModal,
    setShowDetails
  }
})