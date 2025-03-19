<template>
  <div class="absolute inset-0 flex flex-col justify-center items-center">
    <div class="absolute inset-0 bg-black opacity-50"></div>
    <div class="absolute top-4 right-4 z-10">
      <div v-if="route.path === '/portfolio'">
        <span
            class="text-sm mt-10 hover:underline uppercase underline-offset-4"
          >
            Full Shoot
          </span>
          <span class="text-lg mt-10 hover:none ml-1">→</span>
      </div>
      <div v-else>
        <ArrowsPointingOutIcon class="h-6 w-6 stroke-[.75] text-white/70 hover:text-white" />
      </div>
    </div>
    <div class="relative text-white text-center p-4">
      <h3 class="text-l leading-none uppercase">
        {{ photo.photographer.name }}
      </h3>
      <a
        class="text-white/70 leading-none underline-offset-4 hover:text-white underline-offset-4 text-xs hover:underline transition-colors duration-200"
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
  import { ArrowsPointingOutIcon } from '@heroicons/vue/24/outline'
  import { useRoute } from 'vue-router'

  const route = useRoute()

  defineProps<{
    photo: Photo
  }>()
</script>