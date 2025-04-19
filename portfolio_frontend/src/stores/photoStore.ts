import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/axios'
import type { PhotoShoot, Photo } from '../types/models'
import type { AxiosResponse } from 'axios'
import { useUiStore } from './uiStore' // Import the UI store for loading states

const CLOUDINARY_BASE_URL = import.meta.env.VITE_CLOUDINARY_BASE_URL

export const usePhotoStore = defineStore('photo', () => {
  const uiStore = useUiStore()
  
  // Photo data state
  const carouselPhotos = ref<Photo[]>([])
  const displayPhotos = ref<Photo[]>([])
  const allPhotos = ref<Photo[]>([])
  
  // PhotoShoot data state (keeping for compatibility)
  const photoShoots = ref<PhotoShoot[]>([])
  const isPhotoShootsLoading = ref<boolean>(false)
  
  // Error tracking
  const hasError = ref<boolean>(false)
  
  // Computed properties
  const featuredPhoto = computed(() => displayPhotos.value[0] || null)
  const gridPhotos = computed(() => displayPhotos.value.slice(1) || [])

  // Helper function to ensure image URLs are complete
  function getFullUrl(photos: Photo[]): Photo[] {
    return photos.map(photo => ({
      ...photo,
      image: photo.image.includes('http') ? photo.image : `${CLOUDINARY_BASE_URL}/${photo.image}`
    }));
  }

  // Utility: Preload a single image and return a promise
  function preloadImage(url: string): Promise<void> {
    return new Promise((resolve) => {
      const img = new Image()
      img.src = url

      if (img.complete) {
        resolve()
      } else {
        img.onload = () => resolve()
        img.onerror = () => {
          console.warn(`Failed to preload: ${url}`)
          resolve() // Resolve anyway to not block loading
        }
      }
    })
  }

  // Utility: Preload a batch of images without waiting (background)
  function preloadImagesInBackground(urls: string[]): void {
    urls.forEach((url) => {
      const img = new Image()
      img.src = url
    })
  }

  // PRIORITY 1: Fetch and load carousel photos
  async function fetchCarouselPhotos() {
    try {
      const response: AxiosResponse<Photo[]> = await api.get('/photos/?carousel=true')
      const photos = getFullUrl(response.data)
      
      // Wait for carousel images to fully load before setting state
      await Promise.all(photos.map(photo => preloadImage(photo.image)))
      
      carouselPhotos.value = photos
      uiStore.setCarouselLoaded(true)
      return photos
    } catch (error) {
      console.error('Error loading carousel photos:', error)
      hasError.value = true
      uiStore.setCarouselLoaded(true) // Still mark as loaded to not block UI
      return []
    }
  }

  // PRIORITY 2: Fetch and load display photos (featured + grid)
  async function fetchDisplayPhotos() {
    try {
      // Get all non-photographer photos (modeling portfolio)
      const response: AxiosResponse<Photo[]> = await api.get('/photos/?photographer_id__ne=1')
      const photos = getFullUrl(response.data)
      
      // Load the featured image first (most important)
      if (photos.length > 0) {
        await preloadImage(photos[0].optimized_images?.featured || photos[0].image)
      }
      
      // Then load the initial grid images
      await Promise.all(photos.slice(1, 5).map(photo => 
        preloadImage(photo.optimized_images?.grid || photo.image)
      ))
      
      displayPhotos.value = photos
      uiStore.setDisplayPhotosLoaded(true)
      
      // Start loading the remaining grid images in the background
      if (photos.length > 5) {
        preloadImagesInBackground(
          photos.slice(5).map(photo => photo.optimized_images?.grid || photo.image)
        )
      }
      
      // Start preloading modal images in background
      preloadModalImages(photos)
      
      return photos
    } catch (error) {
      console.error('Error loading display photos:', error)
      hasError.value = true
      uiStore.setDisplayPhotosLoaded(true) // Still mark as loaded to not block UI
      return []
    }
  }

  // PRIORITY 3: Background loading of high-res modal images
  function preloadModalImages(photos: Photo[]) {
    try {
      // Use the 'full' optimized image URLs from the backend
      const modalUrls = photos.map(photo => 
        photo.optimized_images?.full || photo.image
      )
      
      // Load in background - don't wait for completion
      preloadImagesInBackground(modalUrls)
    } catch (error) {
      console.error('Error preloading modal images:', error)
    }
  }

  // Fetch all photos if needed
  async function fetchAllPhotos() {
    try {
      const response: AxiosResponse<Photo[]> = await api.get('/photos/')
      const photos = getFullUrl(response.data)
      allPhotos.value = photos
      return photos
    } catch (error) {
      console.error('Error fetching all photos:', error)
      hasError.value = true
      return []
    }
  }

  // KEEPING UNTOUCHED: Existing PhotoShoot loading function but updating to use getFullUrl
  async function fetchAllPhotoShoots() {
    isPhotoShootsLoading.value = true
    try {
      const response: AxiosResponse<PhotoShoot[]> = await api.get('/photo-shoots/')
      
      photoShoots.value = response.data.map((shoot) => ({
        ...shoot,
        photos: getFullUrl(shoot.photos)
      }))
  
      // Wait for first image of each photoshoot to load (medium priority)
      const indexImages = photoShoots.value
        .map((shoot) => shoot.photos?.[0]?.image)
        .filter(Boolean) as string[]
  
      await Promise.all(indexImages.map((url) => preloadImage(url)))
  
      // Preload remaining images in background (low priority)
      const remainingImages = photoShoots.value.flatMap((shoot) =>
        shoot.photos.slice(1).map((photo) => photo.image)
      )
  
      preloadImagesInBackground(remainingImages)
    } catch (error) {
      console.error('Error loading photo shoots:', error)
      hasError.value = true
    } finally {
      isPhotoShootsLoading.value = false
    }
  }

  // Main loading sequence function for modeling portfolio
  async function loadPortfolioData() {
    uiStore.resetLoadingState()
    try {
      // Priority 1: Carousel - wait for completion
      await fetchCarouselPhotos()
      
      // Priority 2: Display photos - wait for initial completion
      await fetchDisplayPhotos()
      
      // Priority 3 happens automatically in the background
    } catch (error) {
      console.error('Error in portfolio data loading sequence:', error)
      hasError.value = true
    }
  }

  // For compatibility with existing code that expects this function
  const getPortfolioDisplayPhotos = (
    isIndex: boolean,
    params: Record<string, string> = {}
  ) => {
    if (isIndex) {
      // For index page: first photo of each photoshoot
      return photoShoots.value.map((shoot) => shoot.photos[0]).filter(Boolean)
    } else if (params.order) {
      // For specific photoshoot: all photos in that shoot
      const shoot = photoShoots.value.find(
        (s) => s.order === Number(params.order)
      )
      return shoot?.photos || []
    }

    return []
  }

  return {
    // State
    carouselPhotos,
    displayPhotos,
    allPhotos,
    photoShoots,
    isPhotoShootsLoading,
    hasError,
    
    // Computed
    featuredPhoto,
    gridPhotos,
    
    // Actions - Modeling portfolio
    loadPortfolioData,
    fetchCarouselPhotos,
    fetchDisplayPhotos,
    fetchAllPhotos,
    
    // Actions - PhotoShoot (kept untouched)
    fetchAllPhotoShoots,
    getPortfolioDisplayPhotos
  }
})