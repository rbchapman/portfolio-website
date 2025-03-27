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
  const showDetails = ref(false)
  const currentPage = ref('')
  const currentPageParams = ref<Record<string, string>>({})

  // Initial load function
  function completeInitialLoad() {
    setTimeout(() => {
      hasCompletedInitialLoad.value = true
    }, 5000)
  }

  function setCurrentPage(
    routeName: string,
    params: Record<string, string> = {}
  ) {
    currentPage.value = routeName
    currentPageParams.value = params
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

  const isPortfolioIndex = computed(
    () => currentPage.value === 'portfolio' && !currentPageParams.value.order
  )

  const isCampaigns = computed(
    () => currentPage.value === 'campaigns'
  )
  const isHome = computed(() => currentPage.value === 'home')

  return {
    // State
    hasCompletedInitialLoad,
    currentPage,
    currentPageParams,
    isPortfolioIndex,
    isCampaigns,
    isHome,
    showDetails,
    selectedPhoto,
    isModalOpen,
    isPaused,
    hoveredPhoto,

    // Functions
    completeInitialLoad,
    setCurrentPage,
    setHover,
    clearHover,
    openModal,
    closeModal,
    setShowDetails
  }
})
