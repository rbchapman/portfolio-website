<template>
  <footer class="flex justify-between mt-auto py-2 px-8">
    <div>
      <div v-if="siteConfig.isEnergy" class="uppercase text-xs text-white/70 space-x-3">
        <a href="https://github.com/rbchapman/portfolio-website" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="footer-link hover:text-white transition-colors">
          GitHub
        </a>
        <span class="opacity-50">|</span>
        <a href="https://www.linkedin.com/in/rileychapman/" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="footer-link hover:text-white transition-colors">
          LinkedIn
        </a>
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
