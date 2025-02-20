<template>
  <div
    ref="containerRef"
    @keyup.left="navigateCampaign(-1)"
    @keyup.right="navigateCampaign(1)"
    tabindex="0"
    class="focus:outline-none"
  >
    <ActionBar :action="campaignsNav" />
    <ChevronNav @previous="navigateCampaign(-1)" @next="navigateCampaign(1)" />
    <div class="flex items-center justify-center">
      <div class="flex p-8 justify-start">
        <iframe
          width="750"
          height="422"
          :src="currentCampaign?.video_url"
          title="YouTube video player"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          referrerpolicy="strict-origin-when-cross-origin"
          allowfullscreen
        ></iframe>
        <div
          class="h-24 border-l border-white/70 border-l-[0.5px] flex flex-col ml-6"
        >
          <p
            class="text-white/90 -mb-1 ml-2 uppercase font-medium text-m w-40 truncate"
          >
            {{ currentCampaign?.client }}
          </p>
          <p
            class="text-white/70 -mb-1 ml-2 mt-1 cursor-default text-xs"
            tabindex="0"
          >
            {{ campaignYear }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onMounted, ref, nextTick } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import ActionBar from '../components/ActionBar.vue'
  import ChevronNav from '../components/ChevronNav.vue'
  import type { NavigationAction } from '../types'
  import { useCampaignStore } from '@/stores/campaignStore'

  const containerRef = ref<HTMLElement | null>(null)
  const campaignStore = useCampaignStore()
  const campaigns = computed(() => campaignStore.campaigns)
  const route = useRoute()
  const router = useRouter()

  const currentCampaign = computed(() => {
    return campaigns.value.find(
      (campaign) => campaign.order === Number(route.params.order)
    )
  })

  const campaignYear = computed(() => {
    if (!currentCampaign.value?.date) return 'N/A'
    return new Date(currentCampaign.value.date).getFullYear()
  })

  const campaignsNav: NavigationAction = {
    title: 'Campaigns',
    type: 'navigation',
    basePath: 'campaigns',
    count: campaigns.value.length,
    showBasePath: false
  }

  const navigateCampaign = (direction: number) => {
    if (campaigns.value.length === 0) return

    const currentIndex = campaigns.value.findIndex(
      (campaign) => campaign.order === Number(route.params.order)
    )
    const newIndex =
      (currentIndex + direction + campaigns.value.length) %
      campaigns.value.length
    router.push(`/campaigns/${campaigns.value[newIndex].order}`)
  }

  onMounted(async () => {
    await campaignStore.fetchCampaigns()
    nextTick(() => {
      containerRef.value?.focus()
    })
  })
</script>
