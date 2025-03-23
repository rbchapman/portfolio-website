<template>
  <div class="flex-1 mr-6 relative max-w-[45vw] h-[60vh] sticky top-0" v-if="props.photo">
    <!-- Index page version -->
    <RouterLink
      v-if="isPortfolioIndex"
      :to="`/portfolio/${props.photo.photo_shoot_order}`"
      class="relative block h-full"
      @mouseenter="uiStore.setHover(props.photo)"
      @mouseleave="uiStore.clearHover()"
    >
      <img
        loading="eager"
        :src="props.photo.optimized_images.full"
        :alt="props.photo.title || ''"
        class="w-full h-full object-cover content-transition transition-opacity duration-300"
      />

      <!-- Overlay with PhotoDetails -->
      <div
        v-show="uiStore.hoveredPhoto?.id === props.photo.id && !uiStore.isModalOpen"
        class="absolute inset-0 bg-black bg-opacity-60 transition-opacity duration-200"
      >
        <PhotoDetails :photo="props.photo" class="z-10 mt-6" />
      </div>
    </RouterLink>

    <!-- Detail page version -->
    <div
      v-else
      class="cursor-pointer relative h-full"
      @click="uiStore.openModal(props.photo)"
    >
      <img
        loading="eager"
        :src="props.photo.optimized_images.full"
        :alt="props.photo.title || ''"
        class="w-full h-full object-cover content-transition transition-opacity duration-300"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/uiStore';
import PhotoDetails from './PhotoDetails.vue';
import type { Photo } from '@/types';

// Props
const props = defineProps<{
  photo: Photo;
  isPortfolioIndex: boolean;
}>();

// Store
const uiStore = useUiStore();
</script>