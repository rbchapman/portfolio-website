<template>
  <div
    class="fixed inset-0 z-40"
    tabindex="0"
    @keyup.escape="closeModal"
    @keyup.left="previousPhoto"
    @keyup.right="nextPhoto"
    ref="modalRef"
  >
    <!-- Overlay -->
    <div
      class="absolute inset-0 bg-black bg-opacity-95 z-40"
      @click.self="closeModal"
    ></div>

    <!-- Modal content -->
    <div class="relative h-screen flex items-center justify-center p-24">
      <!-- Navigation buttons -->
      <button
        class="absolute left-4 top-1/2 -translate-y-1/2 p-4 text-white/70 hover:text-white transition-colors z-50 text-4xl font-light"
        aria-label="Previous photo"
        @click="previousPhoto"
      >
        ‹
      </button>

      <button
        class="absolute right-4 top-1/2 -translate-y-1/2 p-4 text-white/70 hover:text-white transition-colors z-50 text-4xl font-light"
        aria-label="Next photo"
        @click="nextPhoto"
      >
        ›
      </button>

      <div class="flex items-end z-50">
        <div class="relative">
          <img
            v-if="currentPhoto"
            :src="currentPhoto.image"
            :alt="currentPhoto.title"
            :class="currentPhoto?.is_portrait ? 'h-[85vh] w-auto' : 'max-w-3xl'"
          />
          <button
            class="absolute bottom-4 left-4 flex items-center gap-2 text-white/90 hover:text-white px-4 py-2 bg-black/30 backdrop-blur-sm rounded"
          >
            <span class="uppercase text-sm">View Full Shoot</span>
            <span class="text-lg">→</span>
          </button>
        </div>

        <!-- Photographer side bar -->
        <div
          class="flex ml-6 flex-col border-l h-36 border-white/70 justify-end"
        >
          <a
            class="text-white/90 -mb-1 ml-2 cursor-crosshair leading-none uppercase font-medium hover:text-white text-m cursor-crosshair hover:underline transition-colors duration-200"
            :href="`https://www.instagram.com/${currentPhoto.photographer.instagram}/`"
            target="_blank"
          >
            {{ currentPhoto.photographer.name }}
          </a>
          <a
            class="text-white/70 ml-2 pt-2 leading-none cursor-default text-xs"
            tabindex="0"
          >
            Photographer
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, nextTick } from 'vue'
  import type { Photo } from '../types'

  // Define props
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

  const closeModal = () => {
    emit('close')
  }

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
