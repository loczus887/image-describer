import React, { createContext, useState, useContext, useEffect } from 'react'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('auth_token'))
  const [loading, setLoading] = useState(true)

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('auth_token')
      if (storedToken) {
        try {
          const response = await fetch('/api/me', {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          })

          if (response.ok) {
            const userData = await response.json()
            setUser(userData)
            setToken(storedToken)
          } else {
            // Token invalid, clear it
            localStorage.removeItem('auth_token')
            setToken(null)
            setUser(null)
          }
        } catch (error) {
          console.error('Auth check failed:', error)
          localStorage.removeItem('auth_token')
          setToken(null)
          setUser(null)
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (username, password) => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      localStorage.setItem('auth_token', data.access_token)
      setToken(data.access_token)

      // Fetch user data
      const userResponse = await fetch('/api/me', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      })

      if (userResponse.ok) {
        const userData = await userResponse.json()
        setUser(userData)
      }

      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message }
    }
  }

  const register = async (username, email, password) => {
    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }

      // Auto-login after registration
      return await login(username, password)
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
  }

  // Helper function to make authenticated requests
  const authenticatedFetch = async (url, options = {}) => {
    if (!token) {
      throw new Error('Not authenticated')
    }

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }

    const response = await fetch(url, { ...options, headers })

    if (response.status === 401) {
      // Token expired or invalid
      logout()
      throw new Error('Session expired. Please login again.')
    }

    return response
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    register,
    logout,
    authenticatedFetch
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
