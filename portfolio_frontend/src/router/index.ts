import { createRouter, createWebHistory } from 'vue-router'
// import { usePhotoStore } from '@/stores/photoStore'
// import { useUiStore } from '@/stores/uiStore'
// import { useCampaignStore } from '@/stores/campaignStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    // {
    //   path: '/campaigns/:client?',
    //   name: 'campaigns',
    //   component: () => import('../views/CampaignView.vue')
    // },
    {
      // Location route (using same component)
      path: '/:location',
      name: 'location',
      component: () => import('../views/HomeView.vue'),
      props: true
    }
  ]
})

// Add navigation guard for data loading and transitions
// router.beforeEach(async (to, from, next) => {
//   const uiStore = useUiStore()
//   const photoShootStore = usePhotoStore()
//   const campaignStore = useCampaignStore()
  
//   if (from.name === 'home' || from.name === 'photoshoot') {
//     uiStore.clearHover()
//   }
  
//   uiStore.setCurrentPage(to.name as string, to.params as Record<string, string>)
//   try {
//     // Load data based on route
//     if (to.name === 'home' && photoShootStore.carouselPhotos.length === 0) {
//       // await photoShootStore.fetchCarouselPhotos()
//     }
//     if (
//       (to.name === 'home' || to.name === 'photoshoot') &&
//       photoShootStore.photoShoots.length === 0
//     ) {
//       // await photoShootStore.fetchAllCollections()
//     }

//     if (to.name === 'photography' && photoShootStore.photoShoots.length === 0) {
//       // await photoShootStore.fetchAllCollections()
//     }
    
//     // Handle campaigns route
//     if (to.name === 'campaigns') {
//       // Fetch campaigns if they haven't been loaded yet
//       if (campaignStore.campaigns.length === 0) {
//         await campaignStore.fetchCampaigns()
//       }
      
//       // If no client param is specified and we have campaigns, redirect to first campaign
//       if (!to.params.client && campaignStore.campaigns.length > 0) {
//         return next({
//           path: `/campaigns/${campaignStore.campaigns[0].client}`
//         })
//       }
//     }
    
//     next()
//   } catch (error) {
//     console.error('Error during route navigation:', error)
//     next()
//   }
// })

export default router