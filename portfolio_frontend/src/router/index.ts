import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

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

export default router
