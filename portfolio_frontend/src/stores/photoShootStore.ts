import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'
import type { PhotoShoot, Photo } from '../types'
import type { AxiosResponse } from 'axios'

const CLOUDINARY_BASE_URL = import.meta.env.VITE_CLOUDINARY_BASE_URL

export const usePhotoShootStore = defineStore('photoshoot', () => {
    const isLoading = ref<boolean>(true)
    const photoShoots = ref<PhotoShoot[]>([])
    const carouselPhotos = ref<Photo[]>([])
    const hasError = ref<boolean>(false)
    async function fetchPhotoShoots() {
      try {
        hasError.value = false

        const response: AxiosResponse<PhotoShoot[]> = await api.get('/photo-shoots/')
        photoShoots.value = response.data.map(shoot => ({
          ...shoot,
          photos: shoot.photos.map(photo => ({
            ...photo,
            image: `${CLOUDINARY_BASE_URL}/${photo.image}`
          }))
        }))

        const carouselResponse: AxiosResponse<Photo[]> = await api.get('/photos/?carousel=true')
        carouselPhotos.value = carouselResponse.data.map(photo => ({
          ...photo,
          image: `${CLOUDINARY_BASE_URL}/${photo.image}`
        }))

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