import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useSiteCopyStore } from '@/stores/siteCopyStore'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const siteCopyStore = useSiteCopyStore(pinia)
void siteCopyStore.fetchCopy()

app.mount('#app')
