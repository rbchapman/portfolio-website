import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
})
console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL);
export default api