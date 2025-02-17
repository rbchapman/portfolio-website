import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'
import type { PhotoShoot, Photo } from '../types'
import type { AxiosResponse } from 'axios'

export const usePhotoShootStore = defineStore('photoshoot', () => {
    const isLoading = ref<boolean>(true)
    const photoShoots = ref<PhotoShoot[]>([])
    const carouselPhotos = ref<Photo[]>([])
    const hasError = ref<boolean>(false)
    async function fetchPhotoShoots() {
      try {
        hasError.value = false

        const response: AxiosResponse<PhotoShoot[]> = await api.get('http://localhost:8000/api/photo-shoots/')
          photoShoots.value = response.data

        const carouselResponse: AxiosResponse<Photo[]> = await api.get('http://localhost:8000/api/photos/?carousel=true')
          carouselPhotos.value = carouselResponse.data

        // Preload all images
        const imagePromises = photoShoots.value
          .flatMap(shoot => shoot.photos)
          .map(photo => new Promise((resolve, reject) => {
            const img = new Image()
            img.onload = resolve
            img.onerror = reject
            img.src = photo.image
          }))
        
        await Promise.all(imagePromises)
      } catch (error) {
        console.error('Error loading photo shoots:', error)
        hasError.value = true
      } finally {
        isLoading.value = false
      }
    }

  return {
    photoShoots,
    carouselPhotos,
    isLoading,
    hasError,
    fetchPhotoShoots
  }
})