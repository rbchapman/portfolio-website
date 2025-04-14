<template>
  <div class="w-full h-full">
    <div class="grid grid-cols-2 gap-6 pb-6">
      <!-- Index page grid items -->
      <template v-if="uiStore.isPhotography && !uiStore.currentPageParams.location"
      >
        <RouterLink
          v-for="photo in props.photos"
          :key="photo.id"
          :to="`/photography/${photo.shoot_location}`"
          class="h-[50vh] overflow-hidden relative"
          @mouseenter="uiStore.setHover(photo)"
          @mouseleave="uiStore.clearHover()"
        >
          <img
            loading="eager"
            :src="photo.optimized_images.grid"
            :alt="photo.title || ''"
            class="w-full h-full object-cover transition-opacity duration-300"
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
          class="h-[50vh] overflow-hidden cursor-pointer relative"
          @click="uiStore.openModal(photo)" 
        >
          <img
            loading="eager"
            :src="photo.optimized_images.grid"
            :alt="photo.title || ''"
            class="w-full h-full object-cover transition-opacity duration-300"
          />
        </div>
      </template>
    </div>
  </div>
</template>
  
  <script setup lang="ts">
  import { useUiStore } from '@/stores/uiStore';
  import PhotoDetails from './PhotoDetails.vue';
  import type { Photo } from '@/types/models';
  
  // Props
  const props = defineProps<{
    photos: Photo[];
  }>();
  
  // Store
  const uiStore = useUiStore();
  </script>