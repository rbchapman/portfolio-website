<template>
  <ActionBar :action="photoShootsNav" />
  <!-- index of photo shoot instances -->
  <div v-if="!selectedShoot" class="flex px-8 pt-2 pb-8">
    <!-- Left side - large photo -->
    <div class="flex-1 pr-8 border-r border-r-white/70 border-r-[0.5px]">
      <RouterLink
        v-if="photoShoots.length && photoShoots[0]?.photos?.length"
        :to="`/portfolio/${photoShoots[0].order}`"
      >
        <img
          v-if="photoShoots.length && photoShoots[0].photos?.length"
          loading="eager"
          :src="photoShoots[0].photos[0].image"
          :alt="photoShoots[0].photos[0].title || ''"
          class="w-full h-full object-cover"
        />
      </RouterLink>
    </div>

    <!-- Right side - photo grid -->
    <div class="pl-8">
      <div class="grid grid-cols-2 gap-8">
        <div
          v-for="shoot in photoShoots.slice(1)"
          :key="shoot.id"
          v-memo="[shoot.id, shoot.photos[0].image]"
          class="aspect-[4/5] max-h-[350px] overflow-hidden"
        >
          <RouterLink
            v-if="shoot.photos?.length"
            :to="`/portfolio/${shoot.order}`"
          >
            <img
              loading="eager"
              v-if="shoot.photos?.length"
              :src="shoot.photos[0].image"
              :alt="shoot.photos[0].title || ''"
              class="w-full h-full object-cover"
            />
          </RouterLink>
        </div>
      </div>
    </div>
  </div>

  <!-- show for selected photo shoot -->
  <div v-else class="flex px-8 pt-2 pb-8">
    <!-- Left side - large photo -->
    <div
      v-memo="[selectedShoot?.id, selectedShoot?.photos?.[0]?.image]"
      class="flex-1 pr-8 border-r border-r-white/70 border-r-[0.5px]"
    >
      <img
        v-if="selectedShoot.photos?.length"
        loading="eager"
        :src="selectedShoot.photos[0].image"
        :alt="selectedShoot.photos[0].title || ''"
        class="w-full h-full object-cover"
      />
    </div>

    <!-- Right side - photo grid -->
    <div class="pl-8">
      <div class="grid grid-cols-2 gap-8">
        <div
          v-for="photo in selectedShoot.photos.slice(1)"
          v-memo="[photo.id, photo.image]"
          :key="photo.id"
          class="aspect-[4/5] max-h-[350px] overflow-hidden"
        >
          <img
            loading="eager"
            :src="photo.image"
            :alt="photo.title || ''"
            class="w-full h-full object-cover"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import ActionBar from '../components/ActionBar.vue'
  import { computed } from 'vue'
  import { useRoute } from 'vue-router'
  import type { NavigationAction } from '../types'
  import { usePhotoShootStore } from '@/stores/photoShootStore'

  const route = useRoute()
  const photoShootStore = usePhotoShootStore()
  const photoShoots = computed(() => photoShootStore.photoShoots)
  const photoShootsNav: NavigationAction = {
    title: 'Photo Shoots',
    type: 'navigation',
    basePath: 'portfolio',
    count: photoShoots.value.length,
    showBasePath: true
  }

  const selectedShoot = computed(() => {
    if (!route.params.order) return null
    return photoShoots.value.find(
      (shoot) => shoot.order === Number(route.params.order)
    )
  })
</script>
