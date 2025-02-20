<template>
  <div class="w-full h-40 flex items-center">
    <router-link :to="{ name: 'home' }"
      class="text-6xl w-full cursor-crosshair text-center text-white/90 font-serif scale-y-110 uppercase"
    >
      {{ title }}
    </router-link>
  </div>
</template>

<script setup lang="ts">
  defineProps({
    title: {
      type: String,
      required: true
    }
  })
</script>
