import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { usePhotoShootStore } from '@/stores/photoShootStore'
import { useCampaignStore } from '@/stores/campaignStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/campaigns/:order?',
      name: 'campaigns',
      component: () => import('../views/CampaignView.vue'),
    },
    {
      path: '/portfolio/:order?',
      name: 'portfolio',
      component: () => import('../views/PortfolioView.vue'),
    },
  ],
})

// Add navigation guard for data loading and transitions
router.beforeEach(async (to, from, next) => {

  const photoShootStore = usePhotoShootStore()
  const campaignStore = useCampaignStore()
    
  try {
    // Load data based on route
    if (to.name === 'home' && photoShootStore.carouselPhotos.length === 0) {
      await photoShootStore.fetchCarouselPhotos()
    }
    
    if ((to.name === 'portfolio' || to.name === 'photoshoot') && 
        photoShootStore.photoShoots.length === 0) {
      await photoShootStore.fetchAllPhotoShoots()
    }
    
    if (to.name === 'campaigns' && campaignStore.campaigns.length === 0) {
      await campaignStore.fetchCampaigns()
    }
  
    
    next()
  } catch (error) {
    console.error('Error during route navigation:', error)
    next()
  }
})

export default router