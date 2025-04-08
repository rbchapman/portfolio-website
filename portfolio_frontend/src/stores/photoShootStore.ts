import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/axios'
import type { PhotoShoot, Photo } from '../types'
import type { AxiosResponse } from 'axios'

const CLOUDINARY_BASE_URL = import.meta.env.VITE_CLOUDINARY_BASE_URL

// PhotoShootStore with priority-based loading
export const usePhotoShootStore = defineStore('photoshoot', () => {
  const isCarouselLoading = ref<boolean>(false)
  const isPhotoShootsLoading = ref<boolean>(false)
  const isLoading = computed(
    () => isCarouselLoading.value || isPhotoShootsLoading.value
  )
  const photoShoots = ref<PhotoShoot[]>([])
  const carouselPhotos = ref<Photo[]>([])
  const hasError = ref<boolean>(false)
  const allPhotos = ref<Photo[]>([])

  // Preload a single image and return a promise
  function preloadImage(url: string): Promise<void> {
    return new Promise((resolve) => {
      const img = new Image()
      img.src = url

      // If image is already loaded/cached
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

  // Preload a batch of images without waiting (background)
  function preloadImagesInBackground(urls: string[]): void {
    urls.forEach((url) => {
      const img = new Image()
      img.src = url
    })
  }

  // Fetch carousel photos (priority 1)
  async function fetchCarouselPhotos() {
    isCarouselLoading.value = true
    try {
      const carouselResponse: AxiosResponse<Photo[]> = await api.get(
        '/photos/?carousel=true'
      )
      carouselPhotos.value = carouselResponse.data.map((photo) => ({
        ...photo,
        image: `${CLOUDINARY_BASE_URL}/${photo.image}`
      }))

      // Wait for carousel images to load (high priority)
      const carouselUrls = carouselPhotos.value.map((photo) => photo.image)
      await Promise.all(carouselUrls.map((url) => preloadImage(url)))
    } catch (error) {
      console.error('Error loading carousel photos:', error)
      hasError.value = true
    } finally {
      isCarouselLoading.value = false
    }
  }

  async function fetchAllPhotos() {
    try {
      const response: AxiosResponse<Photo[]> =
        await api.get('/photos/')
        allPhotos.value = response.data.map((photo: Photo) => ({
          ...photo,
          image: `${CLOUDINARY_BASE_URL}/${photo.image}`
        }))
    }catch (error) {
      console.error('Error fetching photos:', error)
    }
    
  }

  // Fetch all photo shoots
  async function fetchAllPhotoShoots() {
    isPhotoShootsLoading.value = true
    try {
      const response: AxiosResponse<PhotoShoot[]> =
        await api.get('/photo-shoots/')
      photoShoots.value = response.data.map((shoot) => ({
        ...shoot,
        photos: shoot.photos.map((photo) => ({
          ...photo,
          image: `${CLOUDINARY_BASE_URL}/${photo.image}`
        }))
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

  // Load specific photoshoot images with priority
  async function prioritizePhotoShoot(shootId: number) {
    const shoot = photoShoots.value.find(
      (s) => s.id === shootId || s.order === shootId
    )
    if (shoot?.photos?.length) {
      const imageUrls = shoot.photos.map((photo) => photo.image)
      await Promise.all(imageUrls.slice(0, 3).map((url) => preloadImage(url)))
      preloadImagesInBackground(imageUrls.slice(3))
    }
  }

  // Centralized initial data loader
  async function fetchInitialData(currentRoute = '') {
    try {
      // Fetch and preload high-priority content
      await Promise.all([fetchCarouselPhotos(), fetchAllPhotoShoots()])

      // If on a specific photoshoot page, prioritize those images
      if (currentRoute.includes('photoshoot/')) {
        const shootId = currentRoute.split('/').pop()
        if (shootId && !isNaN(Number(shootId))) {
          await prioritizePhotoShoot(Number(shootId))
        }
      }

      console.log(
        'Priority images loaded, remaining images loading in background'
      )
    } catch (error) {
      console.error('Error in initial data load:', error)
      hasError.value = true
    }
  }

  return {
    allPhotos,
    photoShoots,
    carouselPhotos,
    isCarouselLoading,
    isPhotoShootsLoading,
    isLoading,
    hasError,
    fetchCarouselPhotos,
    fetchAllPhotos,
    fetchAllPhotoShoots,
    prioritizePhotoShoot,
    fetchInitialData,
    getPortfolioDisplayPhotos
  }
})