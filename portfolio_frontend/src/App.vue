<template>
  <LoadScreen />
  <div class="h-screen flex flex-col">
    <PageTitle boldText="RileyBenjamin" italicText="Chapman" />
    <ActionBar />
    
    <main class="flex-1 flex overflow-hidden">
      <RouterView v-slot="{ Component, route }">
        <transition name="slide-transition" mode="out-in">
          <component :is="Component" :key="getTransitionKey(route)" class="w-full" />
        </transition>
      </RouterView>
    </main>
    <PageFooter />
  </div>
</template>

<script setup lang="ts">
  import { RouterView, useRouter } from 'vue-router'
  import LoadScreen from './components/LoadScreen.vue'
  import ActionBar from './components/ActionBar.vue'
  import PageTitle from './components/PageTitle.vue'
  import PageFooter from './components/PageFooter.vue'
  import type { RouteLocationNormalized } from 'vue-router'
  import { usePhotoStore } from '@/stores/photoStore'
  import { useUiStore } from '@/stores/uiStore'

  const uiStore = useUiStore()
  const photoShootStore = usePhotoStore()
  const router = useRouter()

  function getTransitionKey(route: RouteLocationNormalized) {
    if (route.name === 'campaigns') {
      return `campaign-${route.params.id}`
    }
    if (route.name === 'portfolio') {
      return `portfolio-${route.params.id}`
    }
    return route.path
  }

  // Set up route change detection (outside onMounted to avoid multiple registrations)
  // router.beforeEach((to, from, next) => {
  //   // If navigating to a specific photoshoot
  //   if (to.name === 'portfolio' && to.params.id) {
  //     const shootId = to.params.id
  //     if (shootId && !isNaN(Number(shootId))) {
  //       photoShootStore.prioritizePhotoShoot(Number(shootId))
  //     }
  //   }
  //   next()
  // })
</script>

<style>
  .slide-transition-enter-active,
  .slide-transition-leave-active {
    transition:
      opacity 0.6s ease,
      transform 0.7s ease;
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
