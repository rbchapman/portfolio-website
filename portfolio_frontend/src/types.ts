export interface Photographer {
  id: number
  name: string
  instagram: string
  website: string
}

export interface PhotoShoot {
  id: number
  title: string
  date: string
  photographer: Photographer
  description: string
  location: string
  show: boolean
  order: number
  photos: Photo[]
  campaign: Campaign
  created_at: string
  updated_at: string
}

export interface Campaign {
  id: number
  title: string
  client: string
  description: string
  type: CampaignType
  video_url: string
  web_url: string
  order: number
  date: string
  photo_shoot: PhotoShoot
  created_at: string
  updated_at: string
}

export enum CampaignType {
  FILM = 'FILM',
  PHOTO = 'PHOTO',
  BOTH = 'BOTH'
}

export interface Photo {
  id: number
  image: string
  title: string
  description: string
  photographer: Photographer
  photo_shoot: PhotoShoot
  shoot_slug: number
  is_portrait: boolean
  photo_shoot_order: number
  carousel_order: number | null
  show: boolean
  created_at: string
  updated_at: string
}

export type ToggleAction = {
  type: 'toggle'
  title: string
  content: Record<string, string>
}

export type NavigationAction = {
  type: 'navigation'
  title: string
  basePath: string
  count: number
  showBasePath: boolean
}

export type ActionType = ToggleAction | NavigationAction

