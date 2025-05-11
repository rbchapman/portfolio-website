import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/axios'
import type { PhotoShoot, Photo } from '../types/models'
import type { AxiosResponse } from 'axios'
import { useUiStore } from './uiStore'

const CLOUDINARY_BASE_URL = import.meta.env.VITE_CLOUDINARY_BASE_URL

export const usePhotoStore = defineStore('photo', () => {
  const uiStore = useUiStore()

  // Photo data state
  const carouselPhotos = ref<Photo[]>([])
  const collectionIndexPhotos = ref<Photo[]>([])
  const displayPhotos = ref<Photo[]>([])
  const allPhotos = ref<Photo[]>([])
  const collections = ref<PhotoShoot[]>([])
  const isLoadComplete = ref<boolean>(false)

  // Error tracking
  const hasError = ref<boolean>(false)

  // Computed properties
  const featuredPhoto = computed(() => displayPhotos.value[0] || null)
  const gridPhotos = computed(() => displayPhotos.value.slice(1) || [])

  // Domain detection - more robust implementation
  function isDomainPortfolio(): boolean {
    if (
      typeof window === 'undefined' ||
      !window.location ||
      !window.location.hostname
    ) {
      return false // Default value when window is not available
    }
    return (
      window.location.hostname.includes('portfolio')
    )
  }

  // Helper function to ensure image URLs are complete
  function getFullUrl(photos: Photo[]): Photo[] {
    return photos.map((photo) => {
      if (!photo) return photo

      return {
        ...photo,
        image: photo?.image
          ? photo.image.includes('http')
            ? photo.image
            : `${CLOUDINARY_BASE_URL}/${photo.image}`
          : '',
        optimized_images: photo.optimized_images || {} // Ensure optimized_images always exists as an object
      }
    })
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
      if (!url) return
      const img = new Image()
      img.src = url
    })
  }

  // PRIORITY 1: Fetch and load carousel photos for modeling portfolio
  async function fetchCarouselPhotos() {
    try {
      const response: AxiosResponse<Photo[]> = await api.get(
        '/photos/?carousel=true'
      )
      const photos = getFullUrl(response.data)

      // Wait for carousel images to fully load before setting state
      await Promise.all(photos.map((photo) => preloadImage(photo.image)))

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

  // Fetch collection index with only first photo from each collection for Photography section
  async function fetchCollectionIndex() {
    try {
      uiStore.setCarouselLoaded(false)

      // Use the first_photo_only parameter
      const response: AxiosResponse<PhotoShoot[]> = await api.get(
        '/photo-shoots/?first_photo_only=true'
      )
      const collectionData = response.data

      // Extract the first photo from each collection for the carousel
      const indexPhotos = collectionData
        .map((collection) => collection.photos?.[0])
        .filter(Boolean)

      // Process photos to ensure they have complete URLs
      const processedPhotos = getFullUrl(indexPhotos)

      // Wait for these photos to load
      await Promise.all(
        processedPhotos.map((photo) => preloadImage(photo.image))
      )

      // Store the collections and set carousel photos for photography section
      collections.value = collectionData.map((collection) => ({
        ...collection,
        photos: collection.photos ? getFullUrl(collection.photos) : []
      }))

      // collectionIndexPhotos.value = processedPhotos
      carouselPhotos.value = processedPhotos
      displayPhotos.value = processedPhotos
      uiStore.setCarouselLoaded(true)

      // Start loading full collection data in background
      fetchAllCollections()

      return collections.value
    } catch (error) {
      console.error('Error loading collection index:', error)
      hasError.value = true
      uiStore.setCarouselLoaded(true) // Still mark as loaded to not block UI
      return []
    }
  }

  // PRIORITY 2: Fetch and load display photos (featured + grid) for modeling portfolio
  async function fetchDisplayPhotos() {
    try {
      // Get all non-photographer photos (modeling portfolio)
      const response: AxiosResponse<Photo[]> = await api.get('/photos/')
      const photos = getFullUrl(response.data)

      // Load the featured image first (most important)
      if (photos.length > 0) {
        await preloadImage(
          photos[0].optimized_images?.featured || photos[0].image
        )
      }

      // Then load the initial grid images
      await Promise.all(
        photos
          .slice(1, 5)
          .map((photo) =>
            preloadImage(photo.optimized_images?.grid || photo.image)
          )
      )

      displayPhotos.value = photos
      uiStore.setDisplayPhotosLoaded(true)

      // Start loading the remaining grid images in the background
      if (photos.length > 5) {
        preloadImagesInBackground(
          photos
            .slice(5)
            .map((photo) => photo.optimized_images?.grid || photo.image)
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
      const modalUrls = photos.map(
        (photo) => photo.optimized_images?.full || photo.image
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
      isLoadComplete.value = true
      return photos
    } catch (error) {
      console.error('Error fetching all photos:', error)
      hasError.value = true
      isLoadComplete.value = true
      return []
    }
  }

  async function fetchAllCollections() {
    try {
      const response: AxiosResponse<PhotoShoot[]> =
        await api.get('/photo-shoots/')

      collections.value = response.data.map((collection) => ({
        ...collection,
        photos: getFullUrl(collection.photos)
      }))

      // Wait for first image of each collection to load (medium priority)
      const indexImages = collections.value
        .map((collection) => collection.photos?.[0]?.image)
        .filter(Boolean) as string[]

      await Promise.all(indexImages.map((url) => preloadImage(url)))

      // Preload remaining images in background (low priority)
      const remainingImages = collections.value.flatMap((collection) =>
        collection.photos.slice(1).map((photo) => photo.image)
      )

      preloadImagesInBackground(remainingImages)
      uiStore.setDisplayPhotosLoaded(true)
    } catch (error) {
      console.error('Error loading collections:', error)
      hasError.value = true
      uiStore.setDisplayPhotosLoaded(true)
    } finally {
      isLoadComplete.value = true
    }
  }

  // Main loading sequence function for modeling portfolio
  async function loadPortfolioData() {
    uiStore.resetLoadingState()
    isLoadComplete.value = false
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

  // Main loading sequence for photography section
  async function loadPhotographyData() {
    uiStore.resetLoadingState()
    isLoadComplete.value = false
    try {
      // Priority 1: Fetch collection index with first photos
      await fetchCollectionIndex()

      // Priority 2 & 3 happen automatically in background via fetchAllCollections
    } catch (error) {
      console.error('Error in photography data loading sequence:', error)
      hasError.value = true
    }
  }

  // Main initialization function - entry point for the store
  async function fetchInitialPhotos() {
    uiStore.resetLoadingState()
    isLoadComplete.value = false
    try {
      console.log('Checking domain:', window.location.hostname)
      const portfolio = isDomainPortfolio()
      console.log('Is portfolio domain?', portfolio)

      if (portfolio) {
        console.log('Loading portfolio data')
        await loadPortfolioData()
      } else {
        console.log('Loading photography data')
        await loadPhotographyData()
      }
    } catch (error) {
      console.error('Error during initial photo fetch:', error)
      hasError.value = true
    }
  }

  // Get photos for display based on context
  const getCollectionPhotos = (
    isIndex: boolean,
    params: Record<string, string> = {}
  ) => {
    if (isIndex) {
      // For index page: first photo of each collection
      return collections.value
        .map((collection) => collection.photos?.[0])
        .filter(Boolean)
    } else if (params.location) {
      // For specific collection: all photos in that collection by location
      const collection = collections.value.find(
        (c) => c.location.toLowerCase() === params.location.toLowerCase()
      )
      return collection?.photos || []
    } else if (params.order) {
      // For backward compatibility: find by order
      const collection = collections.value.find(
        (c) => c.order === Number(params.order)
      )
      return collection?.photos || []
    }

    return []
  }

  return {
    // State
    carouselPhotos,
    collectionIndexPhotos,
    displayPhotos,
    allPhotos,
    collections,
    photoShoots: collections, // Alias for backward compatibility
    isLoadComplete,
    hasError,

    // Computed
    featuredPhoto,
    gridPhotos,

    // Main initialization
    fetchInitialPhotos,

    // Actions - Modeling portfolio
    loadPortfolioData,
    fetchCarouselPhotos,
    fetchDisplayPhotos,
    fetchAllPhotos,

    // Actions - Photography section
    loadPhotographyData,
    fetchCollectionIndex,
    fetchAllCollections,
    getCollectionPhotos
  }
})
