<template>
  <div
    ref="containerRef"
    @keyup.left="previousCampaign"
    @keyup.right="nextCampaign"
    tabindex="0"
    class="focus:outline-none w-full"
  >
    <!-- Main container with position relative to establish positioning context -->
    <div class="w-full relative">
      <!-- Centered iframe container with responsive sizing -->
      <div class="flex justify-center w-full">
        <div v-if="currentCampaign" :key="currentCampaign.id" class="video-fade-in w-full max-w-[63vw]">
          <!-- Aspect ratio container -->
          <div class="relative w-full aspect-video">
            <iframe
              class="absolute inset-0 w-full h-full"
              :src="currentCampaign.video_url"
              title="YouTube video player"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerpolicy="strict-origin-when-cross-origin"
              allowfullscreen
            ></iframe>
          </div>
        </div>
      </div>
      
      <!-- Campaign client navigation list - right side, absolutely positioned -->
      <div class="absolute top-2 right-0 z-10">
        <div class="space-y-2 min-w-[120px] pr-8">
          <div 
            v-for="campaign in campaigns" 
            :key="campaign.client"
            class="flex items-center justify-end"
          >
            <!-- Active indicator dot -->
            <div
              v-show="currentCampaign?.client === campaign.client"
              class="mr-2"
            >-</div>
            <router-link
              :to="`/campaigns/${campaign.client}`"
              class="uppercase text-sm hover:text-white transition-opacity duration-200"
              :class="{
                'text-white opacity-100': currentCampaign?.client === campaign.client,
                'opacity-70': currentCampaign?.client !== campaign.client
              }"
            >
              {{ campaign.client }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCampaignStore } from '@/stores/campaignStore'
import { useUiStore } from '@/stores/uiStore'

const uiStore = useUiStore()
const containerRef = ref<HTMLElement | null>(null)
const campaignStore = useCampaignStore()
const campaigns = computed(() => campaignStore.campaigns)
const route = useRoute()
const router = useRouter()

// Focus the container on mount for keyboard navigation
onMounted(() => {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.focus()
    }
  })
})

watch(() => route.path, () => {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.focus()
    }
  })
})

// Get the currently selected campaign based on route params
const currentCampaign = computed(() => {
  return campaigns.value.find(
    (campaign) => campaign.client === String(route.params.client)
  )
})

// Campaign year (kept for reference)
const campaignYear = computed(() => {
  if (!currentCampaign.value?.date) return 'N/A'
  return new Date(currentCampaign.value.date).getFullYear()
})

// Navigate to previous campaign
const previousCampaign = () => {
  if (campaigns.value.length === 0) return
  
  const currentIndex = campaigns.value.findIndex(
    (campaign) => campaign.client === String(route.params.client)
  )
  const newIndex = (currentIndex - 1 + campaigns.value.length) % campaigns.value.length
  
  router.push(`/campaigns/${campaigns.value[newIndex].client}`)
}

// Navigate to next campaign
const nextCampaign = () => {
  if (campaigns.value.length === 0) return
  
  const currentIndex = campaigns.value.findIndex(
    (campaign) => campaign.client === String(route.params.client)
  )
  const newIndex = (currentIndex + 1) % campaigns.value.length
  
  router.push(`/campaigns/${campaigns.value[newIndex].client}`)
}
</script>

<style scoped>
/* Simple fade-in animation for iframe */
.video-fade-in {
  opacity: 0;
  animation: iframe-fade-in 0.6s ease-in-out 0.3s forwards;
}

@keyframes iframe-fade-in {
  0% { opacity: 0; }
  100% { opacity: 1; }
}
</style>