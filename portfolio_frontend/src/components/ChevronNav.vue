<template>
  <div class="fixed inset-0 pointer-events-none z-10">
    <button
      class="fixed mb-24 left-4 top-1/2 font-thin translate-y-8 p-4 text-white/70 hover:text-white transition-colors z-20 pointer-events-auto text-4xl font-light"
      aria-label="Previous photo"
      @click="$emit('previous')"
    >
      ‹
    </button>
    
    <button
      class="fixed right-4 top-1/2 font-thin translate-y-8 p-4 text-white/70 hover:text-white transition-colors z-20 pointer-events-auto text-4xl font-light"
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