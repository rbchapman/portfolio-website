<template>
  <dl class="flex ml-6 flex-col justify-start">
    <div class="-mt-1">
      <dt class="inline text-white/70 uppercase text-xs">Photo by:</dt>
      <dd class="inline ml-1 text-white/90 font-medium text-xs uppercase">
        {{ photo.photographer.name }}
      </dd>
    </div>
    <div>
      <dt class="inline text-white/70 uppercase text-xs">Website:</dt>
      <dd class="inline ml-1 text-white/90 font-medium text-xs uppercase">
        <a
          class="text-white/90 uppercase font-medium text-xs hover:text-white cursor-pointer hover:underline transition-colors duration-200"
          :href="photo.photographer.website"
          target="_blank"
        >
          {{ photo.photographer.website_display }}
        </a>
      </dd>
    </div>
    <div>
      <dt class="inline text-white/70 uppercase text-xs">Instagram:</dt>
      <dd class="inline ml-1 text-white/90 font-medium text-xs uppercase">
        <a
          class="text-white/90 uppercase font-medium text-xs hover:text-white cursor-pointer hover:underline transition-colors duration-200"
          :href="`https://www.instagram.com/${photo.photographer.instagram}/`"
          target="_blank"
        >
          @{{ photo.photographer.instagram }}
        </a>
      </dd>
    </div>
    <div>
      <dt class="inline text-white/70 uppercase text-xs">Date:</dt>
      <dd class="inline ml-1 text-white/90 font-medium text-xs uppercase">
        {{ photo.shoot_year }}
      </dd>
    </div>
    <!-- <div class="mt-auto">
      <router-link
        :to="`/photoshoot/${photo.shoot_order + 1}`"
        class="flex items-center text-white/70 -mb-2 hover:text-white transition-colors"
        @click="uiStore.clearHover"
      >
        <div v-if="uiStore.isModalOpen && !uiStore.isHome || uiStore.isPortfolioIndex && !uiStore.isModalOpen" @click="updateStore()">
          <span class="text-xs hover:underline uppercase underline-offset-4">
            Full Shoot
          </span>
          <span class="text-lg ml-1">→</span>
        </div>
      </router-link>
    </div> -->
  </dl>
</template>

<script setup lang="ts">
  import type { Photo } from '../types/models'
  import { useUiStore } from '@/stores/uiStore'

  const uiStore = useUiStore()

  const updateStore = () => {
    uiStore.clearHover()
    uiStore.closeModal()
  }

  defineProps<{
    photo: Photo
  }>()
</script>
