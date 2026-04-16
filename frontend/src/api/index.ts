import axios from 'axios'

export interface ApiErrorPayload {
  detail?: string
}

const api = axios.create({
  baseURL: 'http://127.0.0.1:8002',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем интерцептор для передачи токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    // В MVP используем заголовок Authorization
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const getApiErrorMessage = (error: unknown, fallback: string) => {
  if (axios.isAxiosError<ApiErrorPayload>(error)) {
    return error.response?.data?.detail || fallback
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}

export default api
