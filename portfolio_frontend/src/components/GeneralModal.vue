<!-- src/components/GeneralModal.vue -->
<template>
    <Transition name="modal">
      <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" @click="closeModal">
        <div class="flex min-h-screen items-center justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          <!-- Background overlay -->
          <div class="fixed inset-0 bg-black bg-opacity-75 transition-opacity"></div>
  
          <!-- Modal panel -->
          <div 
            class="inline-block transform overflow-hidden rounded-lg bg-white text-left align-bottom shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl sm:align-middle"
            @click.stop
          >
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <!-- Close button -->
                  <!-- <button 
                    @click="closeModal"
                    class="absolute top-4 right-4 text-gray-400 hover:text-gray-500"
                  >
                    <XMarkIcon class="h-6 w-6" />
                  </button> -->
                  
                  <!-- Modal content -->
                  <div class="mt-2">
                    <img 
                      :src="photo.image" 
                      :alt="photo.title"
                      class="w-full h-auto max-h-[70vh] object-contain"
                    />
                    <h3 class="text-lg font-medium leading-6 text-gray-900 mt-4">
                      {{ photo.title }}
                    </h3>
                    <p class="text-sm text-gray-500 mt-2">
                      {{ photo.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </template>
  
  <script setup lang="ts">
  // import { XMarkIcon } from '@heroicons/vue/24/outline'
  
  interface Props {
    isOpen: boolean
    photo: {
      image: string
      title: string
      description: string
    }
  }
  
  defineProps<Props>()
  const emit = defineEmits<{
    (e: 'close'): void
  }>()
  
  const closeModal = () => {
    emit('close')
  }
  </script>
  
  <style scoped>
  .modal-enter-active,
  .modal-leave-active {
    transition: opacity 0.3s ease;
  }
  
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
  }
  </style>