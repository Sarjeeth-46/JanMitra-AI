export interface UserProfile {
  name: string
  age: number
  income: number
  state: string
  occupation: string
  category: string
  land_size: number
  aadhaar_number?: string
}

export interface EligibilityRule {
  field: string
  operator: string
  value: string | number
}

export interface Scheme {
  scheme_id: string
  name: string
  description: string
  eligibility_rules: EligibilityRule[]
}

export interface EvaluationResult {
  scheme_name: string
  eligible: boolean
  missing_fields: string[]
  failed_conditions: string[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface HealthResponse {
  status: string
  timestamp: string
}

export interface DocumentUploadResponse {
  status: 'success' | 'error'
  message?: string
  extracted_text?: string
  extracted_fields?: Partial<UserProfile>
}

export interface AudioUploadResponse {
  success: boolean
  transcript: string
  extracted_data?: Partial<UserProfile>
}
