<template>
  <footer class="flex justify-between mt-auto py-2 px-8">
    <div>
      <div v-if="siteConfig.isEnergy" class="uppercase text-xs text-white/70">
        <a href="https://github.com/rbchapman/portfolio-website" class="footer-link">GitHub</a>
      </div>
    <div v-if="siteConfig.isPortfolio">
      <span class="text-white/70 text-xs uppercase">agency: </span>
      <a :href="agencyUrl" class="footer-link">{{ agencyName }}</a>
    </div>
    </div>
    <div>
      <span class="uppercase text-xs text-white/70">
        {{ siteConfig.isEnergy ? 'chapman.riley@gmail.com' : contactEmail }}
      </span>
    </div>
  </footer>
</template>

<script setup lang="ts">
  import { siteConfig } from '@/utils/siteConfig'

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
