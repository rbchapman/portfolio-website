<template>
  <div
    class="fixed inset-0 z-50"
    tabindex="0"
    @keyup.escape="closeModal"
    @keyup.left="previousPhoto"
    @keyup.right="nextPhoto"
    ref="modalRef"
  >
    <!-- Overlay -->
    <div
      class="absolute inset-0 bg-black bg-opacity-95 z-50"
      @click.self="closeModal"
    ></div>

    <div class="fixed flex flex-col top-4 right-6 uppercase z-[51]">
      <div v-if="route.path === '/'">
        <router-link
          :to="`/portfolio/${currentPhoto.shoot_slug}`"
          class="flex items-center text-white/70 hover:text-white transition-colors"
        >
          <span class="text-sm hover:underline underline-offset-4">
            View Full Shoot
          </span>
          <span class="text-lg ml-1">→</span>
        </router-link>
      </div>
      <button
        @click="closeModal"
        :class="[
          'uppercase hover:underline underline-offset-4 z-[51] text-white/70 hover:text-white transition-colors',
          route.path === '/'
            ? 'fixed bottom-4 text-xs left-6'
            : 'fixed text-sm top-4 right-6'
        ]"
        aria-label="Close modal"
      >
        close
      </button>
    </div>
    <!-- Modal content -->
    <div class="relative h-screen flex items-center justify-center p-24">
      <!-- Navigation buttons -->
      <ChevronNav class="z-[51]" @previous="previousPhoto" @next="nextPhoto" />

      <div class="flex items-end z-50">
        <div class="relative">
          <img
            v-if="currentPhoto"
            :src="currentPhoto.image"
            :alt="currentPhoto.title"
            :class="currentPhoto?.is_portrait ? 'h-[85vh] w-auto' : 'max-w-3xl'"
          />
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
import { useRoute } from 'vue-router'
import ChevronNav from './ChevronNav.vue'
import type { Photo } from '../types'

const route = useRoute()

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
  const prevIndex = (currentIndex - 1 + props.photos.length) % props.photos.length
  currentPhoto.value = props.photos[prevIndex]
  emit('update:modelValue', currentPhoto.value)
}
</script>