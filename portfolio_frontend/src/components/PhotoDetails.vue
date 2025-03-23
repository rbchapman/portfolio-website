<template>
  <dl class="flex ml-6 flex-col h-44 justify-start">
    <div class="-mt-1">
      <dt class="inline text-white/70 uppercase text-xs">Photographer:</dt>
      <dd class="inline ml-1">
        <a
          class="text-white/90 uppercase font-medium text-xs hover:text-white cursor-pointer hover:underline transition-colors duration-200"
          :href="`https://www.instagram.com/${photo.photographer.instagram}/`"
          target="_blank"
        >
          {{ photo.photographer.name }}
        </a>
      </dd>
    </div>

    <div>
      <dt class="inline text-white/70 uppercase text-xs">Location:</dt>
      <dd class="inline ml-1 text-white/90 font-medium text-xs uppercase">
        {{ photo.shoot_location }}
      </dd>
    </div>

    <div>
      <dt class="inline text-white/70 uppercase text-xs">Date:</dt>
      <dd class="inline ml-1 text-white/90 font-medium text-xs uppercase">
        {{ photo.shoot_date }}
      </dd>
    </div>

    <div>
      <dt class="inline text-white/70 uppercase text-xs">Photo:</dt>
      <dd class="inline ml-1 text-white/90 font-medium text-xs uppercase">
        {{ photo.photo_shoot_order }}/ {{photo.photo_count}}
      </dd>
    </div>
    <div class="mt-auto">
      <router-link
        :to="`/portfolio/${photo.shoot_order}`"
        class="flex items-center text-white/70 -mb-2 hover:text-white transition-colors"
        @click="uiStore.clearHover"
      >
        <div v-if="uiStore.isModalOpen && uiStore.isHome || uiStore.isPortfolioIndex && !uiStore.isModalOpen" @click="updateStore()">
          <span class="text-xs hover:underline uppercase underline-offset-4">
            Full Shoot
          </span>
          <span class="text-lg ml-1">→</span>
        </div>
    </router-link>
    <div
      v-if="!uiStore.isModalOpen && uiStore.isHome"
      class="flex hover:text-white items-center"
    >
      <span
        class="text-xs hover:underline uppercase underline-offset-4"
        @click="updateStore()"
      >
        FULL SIZE
      </span>
      <ArrowsPointingOutIcon
        class="h-4 w-4 ml-2 text-white/70 hover:text-white"
      />
    </div>
    </div>
  </dl>
</template>

<script setup lang="ts">
  import type { Photo } from '../types'
  import { useUiStore } from '@/stores/uiStore'
  import { ArrowsPointingOutIcon } from '@heroicons/vue/24/outline'

  const uiStore = useUiStore()

  const updateStore = () => {
    uiStore.clearHover()
    uiStore.closeModal()
  }

  defineProps<{
    photo: Photo
  }>()
</script>
