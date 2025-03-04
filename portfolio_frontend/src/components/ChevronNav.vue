<template>
    <div class="absolute mt-32 inset-0 pointer-events-none z-10">
      <button
        class="absolute left-4 top-1/2 -translate-y-1/2 p-4 text-white/70 hover:text-white transition-colors z-20 pointer-events-auto text-4xl font-light"
        aria-label="Previous photo"
        @click="$emit('previous')"
      >
        ‹
      </button>
      
      <button
        class="absolute right-4 top-1/2 -translate-y-1/2 p-4 text-white/70 hover:text-white transition-colors z-20 pointer-events-auto text-4xl font-light"
        aria-label="Next photo"
        @click="$emit('next')"
      >
        ›
      </button>
    </div>
  </template>
  
  <script setup lang="ts">
  defineEmits(['previous', 'next']);
  </script>