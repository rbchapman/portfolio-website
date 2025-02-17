<template>
  <div
    class="fixed inset-0 bg-black flex items-center justify-center transition-opacity duration-700 ease-in-out"
    :class="isLoading ? 'opacity-100' : 'opacity-0 pointer-events-none'"
  >
    <h1
      class="text-6xl w-full text-center text-white/70 font-serif scale-y-110 uppercase font-light"
    >
      {{ title }}
    </h1>
  </div>
</template>

<script setup lang="ts">
  defineProps({
    isLoading: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: 'Riley Benjamin Chapman'
    }
  })
</script>
