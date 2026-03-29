import axios from 'axios'

const browserHost =
  typeof window !== 'undefined' && window.location.hostname
    ? window.location.hostname
    : '127.0.0.1'

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || `http://${browserHost}:8000`

const API = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export default API
