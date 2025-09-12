import type { ActionBarConfig, ActionBarConfigMap } from '@/types/actionBar'

export const actionBarConfigs: ActionBarConfigMap = {
  portfolio: {
    label: 'MEASUREMENTS',
    section: {
      type: 'keyValue',
      items: {
        'HEIGHT': '180CM',
        'SUIT': '48',
        'SHOES': '42',
        'HAIR': 'RED',
        'EYES': 'BLUE'
      }
    },
    rightLinks: [
      // {
      //   to: '/',
      //   label: 'PHOTOS',
      //   activeWhen: (route) => route.name === 'home' && !route.path.includes('/photography')
      // },
      // {
      //   to: '/campaigns',
      //   label: 'CAMPAIGNS',
      //   activeWhen: (route) => route.name === 'campaigns'
      // }
    ]
  },
  
  home: {
    label: 'Categories',
    section: {
      type: 'links',
      baseRoute: '/',
      items: [],
      paramKey: 'location',
      valueKey: 'location',
      activePath: null
    },
    rightLinks: [
      // {
      //   to: '/photography',
      //   label: 'PHOTOGRAPHY',
      //   activeWhen: (route) => route.path.includes('/photography')
      // }
    ]
  },
  
  dev: {
    label: 'TECH STACK',
    section: {
      type: 'list',
      items: ['Python', 'Django', 'Vue', 'TypeScript', 'Cloudinary']
    },
    rightLinks: [
      {
        to: '/dev',
        label: 'DEV',
        activeWhen: (route) => route.name === 'dev'
      }
    ]
  }
}

// Helper function to get config based on current route
export function getActionBarConfig(routeName: string): ActionBarConfig {
  return actionBarConfigs[routeName] || actionBarConfigs.home
}