<template>
  <div class="w-full h-40 border-b border-b-white/70 border-b-[0.5px] flex items-center justify-center">
    <router-link 
      :to="{ name: 'home' }"
      class="text-6xl cursor-default hover:cursor-crosshair text-center text-white font-serif scale-y-110 uppercase inline-block"
      @click.prevent="navigateToHome"
    >
      {{ props.title }}
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    required: true
  }
})

const router = useRouter()

const navigateToHome = () => {
  router.push({ name: 'home' })
}
</script>