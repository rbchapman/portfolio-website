<template>
    <div>
      <div class="grid grid-cols-2 gap-6">
        <!-- Index page grid items -->
        <template v-if="uiStore.isPortfolioIndex">
          <RouterLink
            v-for="photo in props.photos"
            :key="photo.id"
            :to="`/portfolio/${photo.photo_shoot_order}`"
            class="aspect-[9/10] max-h-[350px] overflow-hidden relative"
            @mouseenter="uiStore.setHover(photo)"
            @mouseleave="uiStore.clearHover()"
          >
            <img
              loading="eager"
              :src="photo.optimized_images.large"
              :alt="photo.title || ''"
              class="w-full h-full object-cover content-transition transition-opacity duration-300"
            />
  
            <!-- Overlay for grid photos -->
            <div
              v-show="uiStore.hoveredPhoto?.id === photo.id && !uiStore.isModalOpen"
              class="absolute inset-0 bg-black bg-opacity-60 transition-opacity duration-200 flex"
            >
              <PhotoDetails :photo="photo" class="z-10 mt-6" />
            </div>
          </RouterLink>
        </template>
  
        <!-- Detail page grid items -->
        <template v-else>
          <div
            v-for="photo in props.photos"
            :key="photo.id"
            class="aspect-[9/10] max-h-[350px] overflow-hidden cursor-pointer relative"
            @click="uiStore.openModal(photo)" 
          >
            <img
              loading="eager"
              :src="photo.optimized_images.large"
              :alt="photo.title || ''"
              class="w-full h-full object-cover content-transition transition-opacity duration-300"
            />
          </div>
        </template>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { useUiStore } from '@/stores/uiStore';
  import PhotoDetails from './PhotoDetails.vue';
  import type { Photo } from '@/types';
  
  // Props
  const props = defineProps<{
    photos: Photo[];
  }>();
  
  // Store
  const uiStore = useUiStore();
  </script>