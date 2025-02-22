<template>
  <div class="fixed top-4 right-4 z-50">
    <button
      v-if="!isOpen"
      class="relative text-white/70 text-sm cursor-crosshair bg-transparent border-none p-0 z-50 hover:text-white transition-colors duration-300"
      @click="toggleMenu"
      aria-label="Menu"
    >
      MENU
    </button>
    <button
      v-else
      class="relative opacity-70 hover:text-white text-2xl bg-transparent border-none cursor-crosshair p-0 z-50 hover:text-white transition-colors duration-300"
      @click="toggleMenu"
      aria-label="Close Menu"
    >
      <XMarkIcon class="w-5 h-5" style="stroke-width: 0.4" />
    </button>

    <!-- Overlay -->
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-30"
      @click="closeMenu"
    ></div>

    <!-- Navigation Menu -->
    <nav
      ref="menuRef"
      class="fixed top-0 right-0 h-screen w-[160px] pt-7 px-4 items-start transition-[right] duration-300 ease-in-out flex flex-col z-40 text-sm focus:outline-none focus-visible:ring-1 focus-visible:ring-white/20"
      :class="isOpen ? 'right-0' : '-right-full'"
      @keyup.escape="closeMenu"
      @click="closeMenu"
      tabindex="0"
      v-if="isOpen"
    >
      <RouterLink
        v-for="(item, index) in menuItems"
        :key="index"
        :to="item.path"
        class="uppercase no-underline text-white/50 text-s duration-300 hover:text-white hover:underline focus:outline-none focus-visible:ring-1 focus-visible:ring-white/20 rounded"
        @click="handleNavigation"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
  import { ref, nextTick } from 'vue'
  import { RouterLink } from 'vue-router'
  import { XMarkIcon } from '@heroicons/vue/24/outline'

  const isOpen = ref(false)
  const menuRef = ref<HTMLElement | null>(null)

  const menuItems = [
    {
      label: 'HOME',
      path: '/'
    },
    {
      label: 'Portfolio',
      path: '/portfolio'
    },
    {
      label: 'Campaigns',
      path: '/campaigns/1'
    },
  ]

  const toggleMenu = () => {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      nextTick(() => {
        menuRef.value?.focus()
      })
    }
  }

  const closeMenu = () => {
    isOpen.value = false
  }

  const handleNavigation = () => {
    nextTick(() => {
      closeMenu()
    })
  }
</script>
