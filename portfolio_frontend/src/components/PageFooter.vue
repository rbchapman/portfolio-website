<template>
  <footer class="flex justify-between mt-auto py-3 px-8">
    <div>
      <span class="text-white/70 text-sm uppercase">agency:</span>
      <a
        :href="agencyUrl"
        class="text-sm hover:underline uppercase cursor-crosshair bg-transparent transition-all duration-500 text-white/70 hover:text-white"
      >
        {{ agencyName }}
      </a>
    </div>
    <div>
      <span class="uppercase text-sm text-white/70">{{ contactEmail }}</span>
    </div>
  </footer>
</template>

<script setup lang="ts">
  defineProps({
    agencyUrl: {
      type: String,
      default: 'https://www.elitelisbon.com/en/riley-chapman/'
    },
    agencyName: {
      type: String,
      default: 'Elite Lisbon'
    },
    contactEmail: {
      type: String,
      default: 'contact@rileybc.net'
    }
  })
</script>
