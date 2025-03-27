<template>
  <div
    class="fixed modal-container inset-0 z-50"
    tabindex="0"
    @keyup.escape="uiStore.closeModal"
    @keyup.left="previousPhoto"
    @keyup.right="nextPhoto"
    ref="modalRef"
  >
    <!-- Overlay -->
    <div
      class="absolute -m-5 inset-0 bg-black bg-opacity-96 z-50"
      @click.self="uiStore.closeModal"
    ></div>

    <div class="fixed flex flex-col top-4 right-6 uppercase z-[51]">
      <div>
        <button
          @click="uiStore.closeModal"
          class="uppercase hover:underline fixed text-sm top-4 right-6 underline-offset-4 z-[51] text-white/70 hover:text-white transition-colors"
          aria-label="Close modal"
        >
          close
        </button>
      </div>
    </div>
    <!-- Modal content -->
    <div class="relative h-screen flex items-center justify-center p-24">
      <!-- Navigation buttons -->
      <ChevronNav class="z-[51]" @previous="previousPhoto" @next="nextPhoto" />
      <div
        v-show="currentPhoto"
        :key="currentPhoto.id"
        class="flex items-end z-50"
      >
        <div class="relative">
          <img
            :src="currentPhoto.image"
            :alt="currentPhoto.title"
            :class="currentPhoto?.is_portrait ? 'h-[85vh] w-auto' : 'max-w-3xl'"
          />
        </div>
        <div class="flex items-start">
          <!-- Photo Metadata Container - Now using the PhotoDetails component -->
          <PhotoDetails 
            :photo="currentPhoto" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, nextTick } from 'vue'
  import ChevronNav from './ChevronNav.vue'
  import PhotoDetails from './PhotoDetails.vue'
  import type { Photo } from '../types'
  import { useUiStore } from '@/stores/uiStore'

  const uiStore = useUiStore()

  const props = defineProps<{
    modelValue: Photo
    photos: Photo[]
  }>()

  const emit = defineEmits<{
    'update:modelValue': [value: Photo]
    close: []
  }>()

  const modalRef = ref<HTMLElement | null>(null)
  const currentPhoto = ref(props.modelValue)

  nextTick(() => {
    modalRef.value?.focus()
  })

  const nextPhoto = () => {
    const currentIndex = props.photos.findIndex(
      (p) => p.id === currentPhoto.value.id
    )
    const nextIndex = (currentIndex + 1) % props.photos.length
    currentPhoto.value = props.photos[nextIndex]
    emit('update:modelValue', currentPhoto.value)
  }

  const previousPhoto = () => {
    const currentIndex = props.photos.findIndex(
      (p) => p.id === currentPhoto.value.id
    )
    const prevIndex =
      (currentIndex - 1 + props.photos.length) % props.photos.length
    currentPhoto.value = props.photos[prevIndex]
    emit('update:modelValue', currentPhoto.value)
  }
</script>
