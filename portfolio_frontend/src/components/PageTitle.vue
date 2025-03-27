<template>
  <div class="w-full flex justify-center items-center pb-8">
    <div class="w-full max-w-5xl mx-auto px-8">
      <router-link
        :to="{ name: 'home' }"
        class="block text-6xl md:text-6xl lg:text-8xl text-white"
        @click.prevent="navigateToHome"
      >
        <span class="font-['Inter'] font-medium tracking-tight">RileyBenjamin</span><!--
        --><span class="font-['Cormorant'] text-9xl font-light normal-case italic">Chapman</span>
      </router-link>
    </div>
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