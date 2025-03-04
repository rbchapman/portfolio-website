// uiStore.ts - simplified
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  // This is the ONLY state we need to track
  const hasCompletedInitialLoad = ref(false)
  
  // Simple function to mark initial load as complete
  function completeInitialLoad() {
    hasCompletedInitialLoad.value = true
  }
  
  return {
    hasCompletedInitialLoad,
    completeInitialLoad
  }
})