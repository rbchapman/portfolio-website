import axios from 'axios'

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL}/api/`,
  headers: {
    'Content-Type': 'application/json',
  }
})

export default api