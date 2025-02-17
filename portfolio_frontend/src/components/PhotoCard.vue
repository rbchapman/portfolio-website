<template>
  <div
    v-memo="[
      photo.id,
      photo.image,
      photo.is_portrait,
      photo.photographer.name,
      photo.photographer.instagram
    ]"
    class="max-w-4xl max-h-2xl shadow-lg overflow-hidden relative group"
  >
    <div
      class="absolute inset-0 bg-black opacity-0 group-hover:opacity-50 transition-opacity duration-300"
    ></div>
    <div
      class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
    >
      <div class="text-white text-center p-4">
        <h3 class="text-l leading-none uppercase">
          {{ photo.photographer.name }}
        </h3>
        <a
          class="text-white/70 leading-none hover:text-white text-xs hover:underline transition-colors duration-200"
          :href="`https://www.instagram.com/${photo.photographer.instagram}/`"
          target="_blank"
        >
          @{{ photo.photographer.instagram }}
        </a>
      </div>
    </div>
    <img
      :src="photo.image"
      :alt="photo.title"
      loading="eager"
      class="w-full h-auto max-h-[60vh]"
      :class="!photo?.is_portrait ? 'h-[85vh] w-auto' : 'max-w-3xl'"
    />
  </div>
</template>

<script setup lang="ts">
  import type { Photo } from '../types'

  defineProps<{
    photo: Photo
  }>()
</script>
