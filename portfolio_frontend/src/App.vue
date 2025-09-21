<template>
  <LoadScreen v-if="!siteConfig.isEnergy"/>
  <div class="h-screen flex flex-col">
    <PageTitle boldText="RileyBenjamin" italicText="Chapman" />
    <ActionBar v-if="!siteConfig.isEnergy"/>
    
    <main class="flex-1 flex overflow-hidden">
      <RouterView v-slot="{ Component }">
        <transition name="slide-transition" mode="out-in">
          <component :is="Component" class="w-full" />
        </transition>
      </RouterView>
    </main>
    <PageFooter />
  </div>
</template>

<script setup lang="ts">
  import { onMounted } from 'vue'
  import { RouterView } from 'vue-router'
  import LoadScreen from './components/LoadScreen.vue'
  import ActionBar from './components/ActionBar.vue'
  import PageTitle from './components/PageTitle.vue'
  import PageFooter from './components/PageFooter.vue'
  import { usePhotoStore } from '@/stores/photoStore'
  import { siteConfig } from '@/utils/siteConfig'
  import { useUiStore } from '@/stores/uiStore'

  const photoStore = usePhotoStore()
  const uiStore = useUiStore()

  onMounted(() => {
    photoStore.fetchInitialPhotos()
  })

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
