import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (response) => {
    const body = response.data
    // 后端统一返回 { code, message, data } 格式
    // 分页接口返回 { code, message, data, total, page, page_size }
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code !== 0) {
        throw new Error(body.message || '请求失败')
      }
      // 分页接口：返回 { items, total }
      if ('total' in body) {
        return { items: body.data || [], total: body.total || 0 }
      }
      // 普通接口：返回 data 字段
      return body.data
    }
    return body
  },
  (error) => {
    const message = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

export default api
