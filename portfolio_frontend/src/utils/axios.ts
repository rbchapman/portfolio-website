import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})
console.log('debug', import.meta.env.VITE_DEBUG)
console.log('api base ', import.meta.env.VITE_API_BASE_URL)
export default api