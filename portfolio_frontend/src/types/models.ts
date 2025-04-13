export interface Photographer {
  id: number
  name: string
  instagram: string
  website: string
  website_display: string
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
  shoot_order: number
  is_portrait: boolean
  photo_shoot_order: number
  carousel_order: number | null
  show: boolean
  shoot_date: string
  shoot_year: string
  photo_count: number
  created_at: string
  updated_at: string
  optimized_images: OptimizedImages
  shoot_location: string
  date: string
}

export interface OptimizedImages {
  grid: string
  medium: string
  large: string
  full: string
}

export interface PhotoDetailItem {
  field: string
  linkField?: string
  isInstagram?: boolean
}

export type PhotoDetailConfig = Record<string, PhotoDetailItem[]>

