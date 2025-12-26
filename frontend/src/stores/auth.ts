/**
 * Authentication store using Pinia
 *
 * Manages user authentication state, login/logout, and token storage.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface User {
  id: number
  username: string
  email?: string
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userInitials = computed(() => {
    if (!user.value) return 'TN'
    return user.value.username.substring(0, 2).toUpperCase()
  })

  // Actions
  async function register(username: string, password: string, email?: string) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post<AuthResponse>(`${API_URL}/api/auth/register`, {
        username,
        password,
        email
      })

      token.value = response.data.access_token
      user.value = response.data.user

      // Store token in localStorage
      localStorage.setItem('auth_token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))

      // Set axios default header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`

      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(username: string, password: string) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post<AuthResponse>(`${API_URL}/api/auth/login`, {
        username,
        password
      })

      token.value = response.data.access_token
      user.value = response.data.user

      // Store token in localStorage
      localStorage.setItem('auth_token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))

      // Set axios default header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`

      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      // Call logout endpoint (optional, since JWT is stateless)
      await axios.post(`${API_URL}/api/auth/logout`)
    } catch (err) {
      // Ignore logout endpoint errors
    } finally {
      // Clear state
      token.value = null
      user.value = null
      error.value = null

      // Clear localStorage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')

      // Remove axios default header
      delete axios.defaults.headers.common['Authorization']
    }
  }

  async function checkAuth() {
    // Try to restore session from localStorage
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`

      // Verify token is still valid by fetching current user
      try {
        const response = await axios.get<User>(`${API_URL}/api/auth/me`)
        user.value = response.data
      } catch (err) {
        // Token is invalid, clear auth state
        await logout()
      }
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    user,
    token,
    loading,
    error,

    // Computed
    isAuthenticated,
    userInitials,

    // Actions
    register,
    login,
    logout,
    checkAuth,
    clearError
  }
})
