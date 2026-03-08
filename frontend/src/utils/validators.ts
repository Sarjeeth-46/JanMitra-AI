/**
 * Validation utility functions
 */

import type { UserProfile } from '../types'

/**
 * Validate user profile data
 */
export const validateUserProfile = (profile: Partial<UserProfile>): string[] => {
  const errors: string[] = []

  if (!profile.name || profile.name.trim().length === 0) {
    errors.push('Name is required')
  }

  if (!profile.age || profile.age < 0 || profile.age > 150) {
    errors.push('Age must be between 0 and 150')
  }

  if (profile.income !== undefined && profile.income < 0) {
    errors.push('Income cannot be negative')
  }

  if (!profile.state || profile.state.trim().length === 0) {
    errors.push('State is required')
  }

  if (!profile.occupation || profile.occupation.trim().length === 0) {
    errors.push('Occupation is required')
  }

  if (!profile.category || profile.category.trim().length === 0) {
    errors.push('Category is required')
  }

  if (profile.land_size !== undefined && profile.land_size < 0) {
    errors.push('Land size cannot be negative')
  }

  return errors
}

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (Indian format)
 */
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^[6-9]\d{9}$/
  return phoneRegex.test(phone.replace(/\s+/g, ''))
}

/**
 * Validate file type
 */
export const isValidFileType = (file: File, allowedTypes: string[]): boolean => {
  return allowedTypes.some((type) => file.type.includes(type))
}

/**
 * Validate file size (in MB)
 */
export const isValidFileSize = (file: File, maxSizeMB: number): boolean => {
  const maxSizeBytes = maxSizeMB * 1024 * 1024
  return file.size <= maxSizeBytes
}
