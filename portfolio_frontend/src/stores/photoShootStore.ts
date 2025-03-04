import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/axios'
import type { PhotoShoot, Photo } from '../types'
import type { AxiosResponse } from 'axios'

const CLOUDINARY_BASE_URL = import.meta.env.VITE_CLOUDINARY_BASE_URL

export const usePhotoShootStore = defineStore('photoshoot', () => {
  const isCarouselLoading = ref<boolean>(false)
  const isPhotoShootsLoading = ref<boolean>(false)
  const isLoading = computed(() => isCarouselLoading.value) // UI loads only until carousel is ready
  const photoShoots = ref<PhotoShoot[]>([])
  const carouselPhotos = ref<Photo[]>([])
  const hasError = ref<boolean>(false)

  async function fetchCarouselPhotos() {
    isCarouselLoading.value = true
    try {
      const carouselResponse: AxiosResponse<Photo[]> = await api.get('/photos/?carousel=true')
      carouselPhotos.value = carouselResponse.data.map(photo => ({
        ...photo,
        image: `${CLOUDINARY_BASE_URL}/${photo.image}`
      }))

      await preloadCarouselImages(carouselPhotos.value) // Ensure carousel is fully loaded before UI unlocks
    } catch (error) {
      console.error('Error loading carousel photos:', error)
      hasError.value = true
    } finally {
      isCarouselLoading.value = false
      fetchAllPhotoShoots() // Start fetching in the background after carousel loads
    }
  }

  function preloadCarouselImages(photos: Photo[]) {
    return Promise.all(photos.map(photo => {
      return new Promise(resolve => {
        const img = new Image()
        img.src = photo.optimized_images.full
        img.onload = resolve 
        img.onerror = resolve
      })
    }))
  }

  async function fetchAllPhotoShoots() {
    isPhotoShootsLoading.value = true
    try {
      const response: AxiosResponse<PhotoShoot[]> = await api.get('/photo-shoots/')
      photoShoots.value = response.data.map(shoot => ({
        ...shoot,
        photos: shoot.photos.map(photo => ({
          ...photo,
          image: `${CLOUDINARY_BASE_URL}/${photo.image}`
        }))
      }))
    } catch (error) {
      console.error('Error loading photo shoots:', error)
      hasError.value = true
    } finally {
      isPhotoShootsLoading.value = false
    }
  }

  function fetchInitialData() {
    fetchCarouselPhotos()
  }

  return {
    photoShoots,
    carouselPhotos,
    isCarouselLoading,
    isPhotoShootsLoading,
    isLoading,
    hasError,
    fetchInitialData,
    fetchCarouselPhotos,
    fetchAllPhotoShoots
  }
})
