<template>
  <div>
    <ActionBar :action="campaignsNav" />
    <div class="flex items-center justify-center pt-8">
      <div class="flex justify-start">
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
          <p class="text-white/90 -mb-1 ml-2 uppercase font-medium text-m">
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
  import ActionBar from '../components/ActionBar.vue'
  import { computed } from 'vue'
  import type { NavigationAction } from '../types'
  import { useCampaignStore } from '@/stores/campaignStore'
  import { useRoute } from 'vue-router'

  const campaignStore = useCampaignStore()
  const campaigns = computed(() => campaignStore.campaigns)
  const route = useRoute()

  const currentCampaign = computed(() => {
    return campaigns.value.find(
      (campaign) => campaign.order + 1 === Number(route.params.order)
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
</script>
