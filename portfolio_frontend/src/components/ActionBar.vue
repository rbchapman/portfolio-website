<template>
  <div
    class="w-full h-[45px] text-sm uppercase tracking-wider"
  >
    <div class="flex text-white/70 justify-between items-center px-8 h-full">
      <!-- Toggle Action Template -->
      <template v-if="props.action.type === 'toggle'">
        <h1
          class="cursor-pointer bg-transparent transition-all duration-500 hover:text-white uppercase "
          :class="{
            'text-white opacity-100 underline-offset-4 underline decoration-[0.25px]': isOpen,
            'opacity-70': !isOpen
          }"
          @click="isOpen = !isOpen"
        >
          {{ props.action.title }}
        </h1>

        <div
          class="mr-16 flex h-full flex-1 items-center justify-center overflow-hidden"
        >
          <div
            class="absolute transition-all duration-500"
            :class="{
              'opacity-0': !isOpen,
              'opacity-100': isOpen
            }"
          >
            <span
              v-for="(value, key) in props.action.content"
              :key="key"
              class="px-2 opacity-70"
            >
              {{ key }} {{ value }}
            </span>
          </div>
        </div>
      </template>

      <!-- Navigation Action Template -->
      <template v-else>
        <h1>
          {{ props.action.title }}
        </h1>

        <div class="flex-1 flex justify-center h-full items-center mr-28">
          <router-link
            v-for="route in routes"
            :key="route.path"
            :to="route.path"
            class="px-2 text-sm hover:text-white opacity-70"
            :class="[
              {
                'underline text-white opacity-100 underline-offset-4 decoration-[0.25px]':
                  isUnderlined(route.label)
              }
            ]"
          >
            {{ route.label }}
          </router-link>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { type ActionType } from '../types'
  import { useRoute } from 'vue-router'

  const route = useRoute()
  const props = defineProps<{
    action: ActionType
  }>()

  const isOpen = ref(false)

  const routes = computed(() => {
    if (props.action.type === 'navigation') {
      const navAction = props.action
      const indexedRoutes = Array.from({ length: navAction.count }, (_, i) => ({
        path: `/${navAction.basePath}/${i + 1}`,
        label: `${i + 1}`
      }))

      if (navAction.showBasePath) {
        return [
          { path: `/${navAction.basePath}`, label: 'ALL' },
          ...indexedRoutes
        ]
      }
      return indexedRoutes
    }
    return []
  })

  const isUnderlined = (label: string | number) => {
    if (!route.params.order) {
      return (
        props.action.type === 'navigation' &&
        props.action.showBasePath &&
        label === 'ALL'
      )
    } else {
      return String(label) === String(route.params.order)
    }
  }
</script>
