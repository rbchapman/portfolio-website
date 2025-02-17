<template>
  <div class="min-h-screen flex flex-col">
    <LoadScreen :is-loading="photoShootStore.isLoading" />
    <div
      class="flex-1 flex flex-col transition-opacity duration-700 ease-in-out"
      :class="isLoading ? 'opacity-0' : 'opacity-100'"
    >
      <NavMenu class="z-50" />
      <PageTitle title="Riley Benjamin Chapman" />
      <main class="flex-1 justify-center">
        <RouterView />
      </main>
      <PageFooter />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { RouterView } from 'vue-router'
  import NavMenu from './components/NavMenu.vue'
  import PageTitle from './components/PageTitle.vue'
  import PageFooter from './components/PageFooter.vue'
  import LoadScreen from './components/LoadScreen.vue'
  import { onMounted } from 'vue'
  import { usePhotoShootStore } from './stores/photoShootStore'
  import { useCampaignStore } from './stores/campaignStore'
  import { storeToRefs } from 'pinia'

  const photoShootStore = usePhotoShootStore()
  const campaignStore = useCampaignStore()
  const { isLoading } = storeToRefs(photoShootStore)

  onMounted(async () => {
    await photoShootStore.fetchPhotoShoots()
    await campaignStore.fetchCampaigns()
  })
</script>
