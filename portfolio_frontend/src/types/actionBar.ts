import type { ComputedRef } from 'vue'
import type { RouteLocationNormalizedLoaded } from 'vue-router'

// Define types for different section formats
export type KeyValueSection = {
  type: 'keyValue'
  items: Record<string, string>
}

export type LinkSection = {
    type: 'links'
    baseRoute: string
    items: ComputedRef<Array<Record<string, any>>> | Array<Record<string, any>>
    paramKey: string
    valueKey: string 
    displayKey?: string
    activePath: string | null
  }

export type ListSection = {
  type: 'list'
  items: string[]
}

// Union type for all section formats
export type ActionBarSection = KeyValueSection | LinkSection | ListSection

// Navigation link configuration
export interface NavigationLink {
  to: string
  label: string
  activeWhen: (route: RouteLocationNormalizedLoaded) => boolean
}

// Complete action bar configuration for a route
export interface ActionBarConfig {
  label: string
  section: ActionBarSection
  rightLinks: NavigationLink[]
}

// Configuration map type
export type ActionBarConfigMap = Record<string, ActionBarConfig>