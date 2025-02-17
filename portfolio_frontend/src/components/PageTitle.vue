<template>
  <div class="w-full h-40 flex items-center">
    <h1
      class="text-6xl w-full cursor-crosshair text-center text-white/90 font-serif scale-y-110 uppercase"
    >
      {{ title }}
    </h1>
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
