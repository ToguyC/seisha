import axios from 'axios'

const baseURL = "http://localhost:8000"

const api = axios.create({
  baseURL,
  timeout: 10000,
})

export default api

