import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Photo } from '../types'
import { usePhotoShootStore } from './photoShootStore'
import { useCampaignStore } from './campaignStore'

export const useUiStore = defineStore('ui', () => {
  // Initial load state
  const showLoadScreen = ref(true)

  // Hover and modal states
  const hoveredPhoto = ref<Photo | null>(null)
  const selectedPhoto = ref<Photo | null>(null)
  const isModalOpen = ref(false)
  const showDetails = ref(false)
  const currentPage = ref('')
  const currentPageParams = ref<Record<string, string>>({})

  // Initial load function
  function noLoad() {
    showLoadScreen.value = false
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
    if (event.key === 'Enter' && showLoadScreen.value) {
      noLoad()
    }
  }

  const isPaused = computed(() => {
    return hoveredPhoto.value !== null || isModalOpen.value
  })

  const isPortfolioIndex = computed(
    () => currentPage.value === 'home' && !currentPageParams.value.order
  )

  const isCampaigns = computed(
    () => currentPage.value === 'campaigns'
  )
  const isHome = computed(() => currentPage.value === 'home')

  // NEW COMPUTED PROPERTIES FOR NAVIGATION
  
  // Get store instances
  const photoShootStore = usePhotoShootStore()
  const campaignStore = useCampaignStore()
  
  // Get the total count of photoshoots and campaigns
  const photoShootCount = computed(() => photoShootStore.photoShoots.length)
  const campaignCount = computed(() => campaignStore.campaigns.length)
  
  // Determine which section is active (photoShoot or campaign)
  const currentSection = computed(() => 
    isCampaigns.value ? 'campaigns' : 'photoshoot'
  )
  
  // Get the base path for the current section
  const currentBasePath = computed(() => 
    isCampaigns.value ? '/campaigns' : '/photoshoot'
  )
  
  // Generate navigation routes for the current section
  const navigationRoutes = computed(() => {
    const count = isCampaigns.value ? campaignCount.value : photoShootCount.value
    const basePath = currentBasePath.value
    
    // Generate numbered routes (1, 2, 3, etc.)
    const indexedRoutes = Array.from({ length: count }, (_, i) => ({
      path: `${basePath}/${i + 1}`,
      label: `${i + 1}`
    }))
    
    // For photoshoots, add the "ALL" route (home page)
    if (!isCampaigns.value) {
      return [
        { path: '/', label: 'ALL' },
        ...indexedRoutes
      ]
    }
    
    // For campaigns, just return the numbered routes
    return indexedRoutes
  })
  
  // Determine if a route should be underlined (active)
  const isRouteActive = (label: string | number) => {
    // For home page or "ALL" route
    if (currentPage.value === 'home' && label === 'ALL') {
      return true
    }
    
    // For numbered routes
    return String(label) === String(currentPageParams.value.order)
  }

  return {
    // State
    showLoadScreen,
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
    
    // New navigation properties
    photoShootCount,
    campaignCount,
    navigationRoutes,
    currentSection,
    currentBasePath,
    isRouteActive,

    // Functions
    noLoad,
    setCurrentPage,
    setHover,
    clearHover,
    openModal,
    closeModal,
    setShowDetails
  }
})