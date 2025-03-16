<template>
  <div>
    <ActionBar :action="photoShootsNav" />
    <ChevronNav @previous="previousItem" @next="nextItem" />
    <div
      v-if="!selectedShoot"
      :key="'index-' + $route.fullPath"
      class="flex content-transition px-16 pt-2 pb-8"
    >
      <!-- Left side - large photo -->
      <div class="flex-1 pr-8 border-r border-r-white/70 border-r-[0.5px]">
        <RouterLink
          v-show="photoShoots.length && photoShoots[0]?.photos?.length"
          :to="`/portfolio/${photoShoots[0].order}`"
          class="relative block h-full"
          @mouseenter="handleMouseInteraction(photoShoots[0].photos[0])"
          @mouseleave="handleMouseInteraction(null)"
          @click="handleMouseInteraction(null)"
        >
          <img
            v-show="photoShoots.length && photoShoots[0].photos?.length"
            loading="eager"
            :src="photoShoots[0].photos[0].optimized_images.full"
            :alt="photoShoots[0].photos[0].title || ''"
            class="w-full content-transition h-full object-cover transition-opacity duration-300"
          />
          <HoverInfo
            v-if="showHoverInfo?.id === photoShoots[0].photos[0].id"
            :photo="photoShoots[0].photos[0]"
          />
        </RouterLink>
      </div>

      <!-- Right side - photo grid -->
      <div class="pl-8">
        <div class="grid grid-cols-2 gap-8">
          <div
            v-for="shoot in photoShoots.slice(1)"
            :key="shoot.id"
            v-memo="[shoot.id, shoot.photos[0]?.optimized_images?.large]"
            class="aspect-[4/5] max-h-[350px] overflow-hidden"
          >
            <RouterLink
              v-if="shoot.photos?.length"
              :to="`/portfolio/${shoot.order}`"
              class="relative block h-full"
              @mouseenter="handleMouseInteraction(shoot.photos[0])"
              @mouseleave="handleMouseInteraction(null)"
              @click="handleMouseInteraction(null)"
            >
              <img
                loading="eager"
                v-if="shoot.photos?.length"
                :src="shoot.photos[0].optimized_images.large"
                :alt="shoot.photos[0].title || ''"
                class="w-full h-full object-cover transition-opacity duration-300"
              />
              <HoverInfo
                v-if="showHoverInfo?.id === shoot.photos[0].id"
                :photo="shoot.photos[0]"
              />
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- show for selected photo shoot -->
    <div
      v-else
      :key="'shoot-' + selectedShoot.id + '-' + $route.fullPath"
      class="content-transition flex px-16 pt-2 pb-8"
    >
      <!-- Left side - large photo -->
      <div
        v-memo="[
          selectedShoot?.id,
          selectedShoot?.photos?.[0]?.optimized_images?.large
        ]"
        class="flex-1 pr-8 border-r border-r-white/70 border-r-[0.5px] cursor-pointer relative"
        @mouseenter="handleMouseInteraction(selectedShoot.photos[0])"
        @mouseleave="handleMouseInteraction(null)"
        @click="openModal(selectedShoot.photos[0])"
      >
        <img
          v-if="selectedShoot.photos?.length"
          loading="eager"
          :src="selectedShoot.photos[0].optimized_images.full"
          :alt="selectedShoot.photos[0].title || ''"
          class="w-full h-full object-cover transition-opacity duration-300"
        />
        <HoverInfo
          v-if="showHoverInfo?.id === selectedShoot.photos[0].id"
          :photo="selectedShoot.photos[0]"
        />
      </div>

      <!-- Right side - photo grid -->
      <div class="pl-8">
        <div class="grid grid-cols-2 gap-8">
          <div
            v-for="photo in selectedShoot.photos.slice(1)"
            v-memo="[photo.id, photo.optimized_images?.large]"
            :key="photo.id"
            class="aspect-[4/5] max-h-[350px] overflow-hidden cursor-pointer relative"
            @mouseenter="handleMouseInteraction(photo)"
            @mouseleave="handleMouseInteraction(null)"
            @click="openModal(photo)"
          >
            <img
              loading="eager"
              :src="photo.optimized_images.large"
              :alt="photo.title || ''"
              class="w-full h-full object-cover transition-opacity duration-300"
            />
            <HoverInfo v-if="showHoverInfo?.id === photo.id" :photo="photo" />
          </div>
        </div>
      </div>
    </div>

    <!-- Photo Modal -->
    <PhotoModal
      v-if="selectedPhoto"
      v-model="selectedPhoto"
      :photos="selectedShoot?.photos || []"
      @close="closeModal"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import ActionBar from '../components/ActionBar.vue'
  import PhotoModal from '../components/PhotoModal.vue'
  import HoverInfo from '../components/HoverInfo.vue'
  import ChevronNav from '../components/ChevronNav.vue'
  import type { NavigationAction, Photo } from '../types'
  import { usePhotoShootStore } from '@/stores/photoShootStore'

  const route = useRoute()
  const router = useRouter()
  const photoShootStore = usePhotoShootStore()
  const photoShoots = computed(() => photoShootStore.photoShoots)
  const selectedPhoto = ref<Photo | null>(null)
  const showHoverInfo = ref<Photo | null>(null)

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

  // Navigation functions
  const previousItem = () => {
    if (!route.params.order) {
      // On index page, can't go previous
      return
    }

    const currentIndex = photoShoots.value.findIndex(
      (shoot) => shoot.order === Number(route.params.order)
    )

    if (currentIndex === 0) {
      // First shoot, go to index
      router.push('/portfolio')
    } else if (currentIndex > 0) {
      // Go to previous shoot
      const prevIndex = currentIndex - 1
      router.push(`/portfolio/${photoShoots.value[prevIndex].order}`)
    }
  }

  const nextItem = () => {
    if (!route.params.order) {
      // On index page, go to first shoot if it exists
      if (photoShoots.value.length > 0) {
        router.push(`/portfolio/${photoShoots.value[0].order}`)
      }
      return
    }

    const currentIndex = photoShoots.value.findIndex(
      (shoot) => shoot.order === Number(route.params.order)
    )

    if (currentIndex < photoShoots.value.length - 1) {
      // Go to next shoot
      const nextIndex = currentIndex + 1
      router.push(`/portfolio/${photoShoots.value[nextIndex].order}`)
    } else {
      // Last shoot, wrap to index
      router.push('/portfolio')
    }
  }

  // Mouse interaction and modal functions
  const handleMouseInteraction = (photo: Photo | null) => {
    showHoverInfo.value = photo
  }

  const openModal = (photo: Photo) => {
    selectedPhoto.value = photo
  }

  const closeModal = () => {
    selectedPhoto.value = null
  }
</script>
