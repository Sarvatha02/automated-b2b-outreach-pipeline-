import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(msg))
  }
)

// Pipeline
export const startPipeline = (domain) =>
  api.post('/pipeline/start', { domain })

export const getPipelineStatus = (id) =>
  api.get(`/pipeline/status/${id}`)

export const getPipelineSummary = (id) =>
  api.get(`/pipeline/summary/${id}`)

export const listPipelines = () =>
  api.get('/pipeline/list')

export const approvePipeline = (pipeline_id, approved) =>
  api.post('/pipeline/approve', { pipeline_id, approved })

// Results
export const getCompanies = (id) =>
  api.get(`/results/${id}/companies`)

export const getContacts = (id) =>
  api.get(`/results/${id}/contacts`)

export const getEmailPreview = (id) =>
  api.get(`/results/${id}/email-preview`)

// Email logs
export const getEmailLogs = (id, params = {}) =>
  api.get(`/emails/${id}/logs`, { params })

// Export
export const exportContactsCsv = (id) =>
  window.open(`/api/export/${id}/contacts/csv`, '_blank')

export const exportContactsJson = (id) =>
  window.open(`/api/export/${id}/contacts/json`, '_blank')

export const exportEmailLogsCsv = (id) =>
  window.open(`/api/export/${id}/email-logs/csv`, '_blank')

export const exportFullJson = (id) =>
  window.open(`/api/export/${id}/full/json`, '_blank')
