<template>
  <div class="relative w-full h-full" v-if="props.photo">
    <!-- Index page version -->
    <RouterLink
      v-if="uiStore.isHome"
      :to="`/photoshoot/${props.photo.photo_shoot_order +1}`"
      class="relative block w-full h-full"
      @mouseenter="uiStore.setHover(props.photo)"
      @mouseleave="uiStore.clearHover()"
    >
      <img
        loading="eager"
        :src="props.photo.optimized_images.large"
        :alt="props.photo.title || ''"
        class="w-full h-full object-cover transition-opacity duration-300"
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
      class="cursor-pointer relative w-full h-full"
      @click="uiStore.openModal(props.photo)"
    >
      <img
        loading="eager"
        :src="props.photo.optimized_images.large"
        :alt="props.photo.title || ''"
        class="w-full h-full object-cover transition-opacity duration-300"
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
}>();

// Store
const uiStore = useUiStore();
</script>