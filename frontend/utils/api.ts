import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const fetchArticles = async (filters: {
  page?: number
  per_page?: number
  category?: string
  source?: string
  search?: string
  minCredibility?: number
}) => {
  const params = new URLSearchParams()
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '' && value !== null) {
      params.append(key, value.toString())
    }
  })

  const response = await api.get(`/api/articles?${params.toString()}`)
  return response.data
}

export const fetchCategories = async () => {
  const response = await api.get('/api/articles/categories')
  return response.data
}

export const fetchSources = async () => {
  const response = await api.get('/api/articles/sources')
  return response.data
}

export const fetchTrendingTopics = async () => {
  const response = await api.get('/api/articles/trending/topics')
  return response.data
}

export const refreshNews = async () => {
  const response = await api.post('/api/articles/refresh')
  return response.data
}