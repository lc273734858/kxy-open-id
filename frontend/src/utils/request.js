import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://localhost:5801',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    const res = response.data

    if (res.code === 0) {
      return res
    } else {
      ElMessage.error(res.msg || 'Request failed')
      return Promise.reject(new Error(res.msg || 'Request failed'))
    }
  },
  error => {
    if (error.response && error.response.status === 401) {
      ElMessage.error('Unauthorized. Please login again.')
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    } else {
      ElMessage.error(error.message || 'Network error')
    }
    return Promise.reject(error)
  }
)

export default request
