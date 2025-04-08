<template>
  <div
    class="fixed modal-container inset-0 z-40"
    tabindex="0"
    @keyup.escape="emitClose"
    ref="modalRef"
  >
    <!-- Overlay -->
    <div
      class="absolute -m-5 inset-0 bg-black bg-opacity-96 z-40"
      @click.self="emitClose"
    ></div>

    <div class="fixed flex flex-col top-4 right-6 uppercase z-[60]">
      <button
        @click="emitClose"
        class="uppercase hover:underline fixed text-sm top-4 right-6 underline-offset-4 z-60 text-white/70 hover:text-white transition-colors"
        aria-label="Close modal"
      >
        close
      </button>
    </div>
    
    <!-- Modal content with Swiper -->
    <div class="relative h-screen overflow-y-auto flex flex-col items-center justify-start z-50 p-6">
      <swiper
        :modules="modules"
        :slides-per-view="1"
        :space-between="0"
        :initial-slide="initialSlideIndex"
        :loop="true"
        :speed="300"
        :keyboard="{ enabled: true }"
        @slideChange="handleSlideChange"
        @swiper="onSwiperInit"
        class="w-full h-full"
      >
        <swiper-slide v-for="photo in photos" :key="photo.id" class="h-auto overflow-y-auto">
          <div class="flex items-end justify-center">
            <div class="max-w-[80%] overflow-y-auto">
              <img
                :src="photo.image"
                :alt="photo.title"
                class="max-h-full w-auto object-contain"
              />
            </div>
            <div class="w-[20%] sticky bottom-0">
              <PhotoDetails :photo="photo" />
            </div>
          </div>
        </swiper-slide>
      </swiper>
      
      <!-- Custom Navigation using Swiper instance directly -->
      <!-- <ChevronNav
        class="z-60"
        @previous="swiperInstance?.slidePrev()"
        @next="swiperInstance?.slideNext()"
      /> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Keyboard, A11y } from 'swiper/modules'
import type { Swiper as SwiperInstance } from 'swiper'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/keyboard'

import ChevronNav from './ChevronNav.vue'
import PhotoDetails from './PhotoDetails.vue'
import type { Photo } from '../types'

const modules = [Navigation, Keyboard, A11y]
const modalRef = ref<HTMLElement | null>(null)
const swiperInstance = ref<SwiperInstance | null>(null)

const props = defineProps<{
  modelValue: Photo | null
  photos: Photo[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Photo): void
  (e: 'close'): void
}>()

const emitClose = () => {
  console.log('Emitting close event')
  emit('close')
}

const initialSlideIndex = computed(() => {
  const modelId = props.modelValue?.id
  
  const index = props.photos.findIndex(photo => photo.id === modelId)
  return index >= 0 ? index : 0
})

onMounted(() => {
  nextTick(() => {
    modalRef.value?.focus()
  })
})

const onSwiperInit = (swiper: SwiperInstance) => {
  swiperInstance.value = swiper
  nextTick(() => {
    swiper.update()
  })
}

const handleSlideChange = (swiper: SwiperInstance) => {
  const currentPhoto = props.photos[swiper.realIndex]
  emit('update:modelValue', currentPhoto)
}

</script>