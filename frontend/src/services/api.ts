/**
 * JanMitra AI – Unified API Service
 *
 * Handles:
 * - Auto-fetching anonymous JWT token on first request
 * - Injecting Authorization header on every call
 * - Typed wrappers for every backend endpoint
 */

import axios, { type AxiosInstance } from 'axios'

// ─── Base URL ────────────────────────────────────────────────────────────────
import API_BASE_URL, { apiEndpoints } from '../config/api'
export const API_BASE = API_BASE_URL
console.log('DEBUG: API_BASE initialized as:', API_BASE || '(relative)')

// Stable session ID for the lifetime of this browser tab (voice concurrency control)
export const SESSION_ID = crypto.randomUUID()

// Plain axios instance for public endpoints (login/register) – no auth interceptor
const publicAxios = axios.create({
  baseURL: API_BASE,
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Axios instance ───────────────────────────────────────────────────────────
const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Token management ─────────────────────────────────────────────────────────
let _tokenPromise: Promise<string> | null = null

async function getToken(): Promise<string> {
  const stored = localStorage.getItem('access_token')
  if (stored) return stored

  // Only fetch once even if called concurrently
  if (!_tokenPromise) {
    _tokenPromise = axios
      .get<{ access_token: string }>(apiEndpoints.anonymous_token)
      .then(res => {
        localStorage.setItem('access_token', res.data.access_token)
        _tokenPromise = null
        return res.data.access_token
      })
      .catch(() => {
        _tokenPromise = null
        return ''
      })
  }
  return _tokenPromise
}

// ─── Request interceptor – inject token ───────────────────────────────────────
api.interceptors.request.use(async config => {
  const token = await getToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// ─── Response interceptor – clear token on 401 ───────────────────────────────
api.interceptors.response.use(
  res => res,
  async error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      // Retry once with a fresh token
      const token = await getToken()
      if (token && error.config) {
        error.config.headers['Authorization'] = `Bearer ${token}`
        return api.request(error.config)
      }
    }
    return Promise.reject(error)
  }
)

// ─── Types ────────────────────────────────────────────────────────────────────

export interface EvaluationRequest {
  name: string
  age: number
  income: number
  state: string
  occupation: string
  category: string
  land_size: number
}

export interface EvaluationResult {
  scheme_name: string
  eligible: boolean
  missing_fields: string[]
  failed_conditions: string[]
}

export interface DocumentExtraction {
  status: string
  document_type: string
  data: any
  extracted_fields?: any
}

export interface VoiceQueryResponse {
  transcript: string
  language: string
  response_text: string
  audio_url: string  // base64 encoded audio
}

export interface FeedbackRequest {
  name: string
  email: string
  message: string
}

export interface RegisterRequest {
  name: string
  email: string
  phone: string
  password: string
}

export interface AuthUser {
  name: string
  email: string
  phone: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export interface OTPVerifyRequest {
  mobile: string
  otp: string
  name?: string
}

export interface OTPVerifyResponse {
  token: string
  user: AuthUser
}

export interface ApplicationStatus {
  application_id: string
  status: string
  submitted_date: string
  estimated_approval: string
  scheme_name: string
}

export interface UserApplication {
  application_id: string
  scheme_name: string
  status: string
  submitted_date: string
}

export interface SystemHealth {
  api: string
  s3: string
  textract: string
  transcribe: string
  translate: string
  polly: string
  bedrock: string
  dynamodb: string
}

// ─── API methods ──────────────────────────────────────────────────────────────

/**
 * POST /api/evaluate
 * Evaluate citizen eligibility across all government schemes.
 */
export async function evaluateEligibility(
  profile: EvaluationRequest
): Promise<EvaluationResult[]> {
  const res = await api.post<EvaluationResult[]>('/api/evaluate', profile)
  return res.data
}

export interface DocumentStatus {
  aadhaar: string
  income_certificate: string
}

/**
 * GET /api/documents/status
 * Get the current document verification status for the user.
 */
export async function getDocumentStatus(): Promise<DocumentStatus> {
  const res = await api.get<DocumentStatus>('/api/documents/status')
  return res.data
}

/**
 * POST /api/upload-document (multipart/form-data)
 */
export async function uploadDocument(file: File, type: string): Promise<DocumentExtraction> {
  const formData = new FormData()
  formData.append('document_type', type)
  formData.append('file', file)

  const res = await api.post<DocumentExtraction>('/api/upload-document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

/**
 * POST /api/voice/query  (multipart/form-data)
 * Send audio, receive transcript + AI response + Polly audio.
 */
export async function voiceQuery(audioBlob: Blob, filename = 'voice.webm', lang = 'auto'): Promise<VoiceQueryResponse> {
  const form = new FormData()
  form.append('audio', audioBlob, filename)
  const res = await api.post<VoiceQueryResponse>(`/api/voice/query?lang=${lang}`, form, {
    headers: {
      'Content-Type': 'multipart/form-data',
      'X-Session-Id': SESSION_ID,        // enables server-side session locking
    },
    timeout: 60_000,  // voice pipeline can take up to 60s
  })
  return res.data
}

/**
 * GET /api/system-health
 * Check the status of all AWS services.
 */
export async function getSystemHealth(): Promise<SystemHealth> {
  const res = await api.get<SystemHealth>('/api/system-health')
  return res.data
}

/**
 * GET /api/health
 * Simple liveness check.
 */
export async function ping(): Promise<{ status: string; timestamp: string }> {
  const res = await api.get('/api/health')
  return res.data
}

/**
 * POST /api/feedback
 * Submit user feedback.
 */
export async function submitFeedback(data: FeedbackRequest): Promise<{ message: string }> {
  const res = await api.post<{ message: string }>('/api/feedback', data)
  return res.data
}

/**
 * POST /api/auth/send-otp
 */
export async function sendOTP(mobile: string): Promise<{ success: boolean; message: string }> {
  const res = await publicAxios.post('/api/auth/send-otp', { mobile })
  return res.data
}

/**
 * POST /api/auth/verify-otp
 */
export async function verifyOTP(mobile: string, otp: string, name?: string): Promise<AuthResponse> {
  const res = await publicAxios.post<AuthResponse>('/api/auth/verify-otp', { mobile, otp, name })
  return res.data
}

/**
 * POST /api/auth/login
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await publicAxios.post<AuthResponse>('/api/auth/login', { email, password })
  return res.data
}

/**
 * POST /api/auth/register
 * Create a new user account.
 * Uses plain axios (no auth interceptor) – register is a public endpoint.
 */
export async function register(data: RegisterRequest): Promise<{ message: string }> {
  const res = await publicAxios.post<{ message: string }>('/api/auth/register', data)
  return res.data
}

/**
 * GET /api/application-status
 * Track application status by ID and phone.
 */
export async function getApplicationStatus(id: string, phone: string): Promise<ApplicationStatus> {
  const res = await api.get<ApplicationStatus>(`/api/application-status?id=${encodeURIComponent(id)}&phone=${encodeURIComponent(phone)}`)
  return res.data
}

/**
 * GET /api/user/profile
 * Get current user profile.
 */
export async function getProfile(): Promise<AuthUser> {
  const res = await api.get<AuthUser>('/api/user/profile')
  return res.data
}

/**
 * GET /api/user/applications
 * Get list of applications for current user.
 */
export async function getUserApplications(): Promise<UserApplication[]> {
  const res = await api.get<UserApplication[]>('/api/user/applications')
  return res.data
}

/**
 * POST /api/submit-application
 * Submit a new government scheme application.
 */
export async function submitApplication(data: {
  scheme_id: string
  scheme_name: string
  user_profile: any
}): Promise<ApplicationStatus> {
  const res = await api.post<ApplicationStatus>('/api/submit-application', data)
  return res.data
}

/**
 * GET /api/faqs
 * Returns the list of FAQs.
 */
export async function getFAQs(): Promise<{ faqs: Array<{ id: number; question: string; answer: string }>; total: number }> {
  const res = await api.get('/api/faqs')
  return res.data
}

/**
 * GET /api/services
 * Returns the list of platform services.
 */
export async function getServices(): Promise<{
  services: Array<{ id: string; title: string; description: string; icon: string; link: string; badge: string }>
  total: number
}> {
  const res = await api.get('/api/services')
  return res.data
}

export default api
