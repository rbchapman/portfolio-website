<!-- OverlayInfo.vue -->
<template>
  <div class="absolute inset-0 flex flex-col justify-center items-center">
    <div class="absolute inset-0 bg-black opacity-50"></div>
    <div class="relative text-white text-center p-4">
      
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
</template>

<script setup lang="ts">
import type { Photo } from '../types'

defineProps<{
  photo: Photo
}>();
</script>