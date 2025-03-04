<template>
  <LoadScreen :is-loading="!uiStore.hasCompletedInitialLoad" />
  <div class="min-h-screen flex flex-col">
    <div class="flex-1 flex flex-col">
      <NavMenu class="z-40" />
      <PageTitle title="Riley Benjamin Chapman" />
      <main class="flex-1 justify-center overflow-hidden">
        <RouterView v-slot="{ Component, route }">
          <transition
            name="slide-transition"
            mode="out-in"
          >
            <component 
              :is="Component" 
              :key="getTransitionKey(route)" 
            />
          </transition>
        </RouterView>
      </main>
      <PageFooter />
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import LoadScreen from './components/LoadScreen.vue'
import NavMenu from './components/NavMenu.vue'
import PageTitle from './components/PageTitle.vue'
import PageFooter from './components/PageFooter.vue'
import type { RouteLocationNormalized } from 'vue-router'
import { usePhotoShootStore } from '@/stores/photoShootStore'
import { useUiStore } from '@/stores/uiStore'
import { onMounted } from 'vue'

const uiStore = useUiStore()
const photoShootStore = usePhotoShootStore()


function getTransitionKey(route: RouteLocationNormalized) {
  if (route.name === 'campaigns') {
    return `campaign-${route.params.id}`
  }
  if (route.name === 'portfolio') {
    return `portfolio-${route.params.id}`
  }
  return route.path
}

onMounted(async () => {
  if (uiStore.hasCompletedInitialLoad) return

  await photoShootStore.fetchCarouselPhotos() // Ensure carousel loads first

  setTimeout(() => {
    uiStore.completeInitialLoad()
    photoShootStore.fetchAllPhotoShoots() // Continue loading in background
  }, 1000)
})
</script>

<style>
.slide-transition-enter-active,
.slide-transition-leave-active {
  transition: opacity 0.6s ease, transform 0.7s ease;
}

.slide-transition-enter-from {
  opacity: 0.8;
  transform: translateX(15px); 
}

.slide-transition-leave-to {
  opacity: 0;
  transform: translateX(-15px); 
}
</style>