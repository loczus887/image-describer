import React, { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import Register from './components/Register'
import ImageUploader from './components/ImageUploader'
import DescriptionViewer from './components/DescriptionViewer'
import AudioPlayer from './components/AudioPlayer'
import HistoryPanel from './components/HistoryPanel'
import SettingsPanel from './components/SettingsPanel'
import './App.css'

function MainApp() {
  const { user, loading: authLoading, isAuthenticated, logout, authenticatedFetch } = useAuth()
  const [showAuthForm, setShowAuthForm] = useState('login')

  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [highContrast, setHighContrast] = useState(false)
  const [fontSize, setFontSize] = useState('medium')
  const [audioEnabled, setAudioEnabled] = useState(true)
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    if (highContrast) {
      document.body.classList.add('high-contrast')
    } else {
      document.body.classList.remove('high-contrast')
    }

    document.body.className = document.body.className.replace(/font-\w+/g, '')
    document.body.classList.add(`font-${fontSize}`)
  }, [highContrast, fontSize])

  useEffect(() => {
    if (isAuthenticated) {
      loadHistory()
    }
  }, [isAuthenticated])

  const loadHistory = async () => {
    try {
      const response = await authenticatedFetch('/api/history?limit=10')
      if (response.ok) {
        const data = await response.json()
        setHistory(data)
      }
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  const clearHistory = async () => {
    try {
      const response = await authenticatedFetch('/api/history', {
        method: 'DELETE'
      })
      if (response.ok) {
        setHistory([])
        setDescription('')
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to clear history')
      }
    } catch (err) {
      console.error('Failed to clear history:', err)
      setError(`Failed to clear history: ${err.message}`)
    }
  }

  const opiszObraz = async (file) => {
    setLoading(true)
    setLoadingMessage('Wysyłanie obrazu...')
    setError(null)
    setDescription('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      console.log('Sending image to API...', file.name, file.size, 'bytes')

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 300000)

      setLoadingMessage('Przetwarzanie obrazu... (może to zająć kilka minut przy pierwszym uruchomieniu)')

      const response = await authenticatedFetch('/api/describe', {
        method: 'POST',
        body: formData,
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      console.log('Response status:', response.status, response.statusText)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        throw new Error(`Server error: ${response.status} - ${errorText}`)
      }

      setLoadingMessage('Generowanie opisu...')
      const data = await response.json()
      console.log('Response data:', data)

      if (data.success) {
        setDescription(data.description)
        loadHistory()
        setLoadingMessage('')
      } else {
        setError(data.error || 'Failed to generate description')
        setLoadingMessage('')
      }
    } catch (err) {
      console.error('Error in opiszObraz:', err)
      if (err.name === 'AbortError') {
        setError('Timeout: Przetwarzanie trwa zbyt długo. Spróbuj ponownie.')
      } else {
        setError(`Error: ${err.message}`)
      }
      setLoadingMessage('')
    } finally {
      setLoading(false)
    }
  }

  if (authLoading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="spinner" />
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="app">
        {showAuthForm === 'login' ? (
          <Login onSwitchToRegister={() => setShowAuthForm('register')} />
        ) : (
          <Register onSwitchToLogin={() => setShowAuthForm('login')} />
        )}
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Image Describer</h1>
        <div className="header-controls">
          <span className="user-info">Welcome, {user?.username}</span>
          <button
            className="settings-toggle"
            onClick={() => setShowSettings(!showSettings)}
            aria-label="Toggle settings"
          >
            ⚙️
          </button>
          <button
            className="logout-button"
            onClick={logout}
            aria-label="Logout"
          >
            Logout
          </button>
        </div>
      </header>

      {showSettings && (
        <SettingsPanel
          highContrast={highContrast}
          fontSize={fontSize}
          audioEnabled={audioEnabled}
          onHighContrastChange={setHighContrast}
          onFontSizeChange={setFontSize}
          onAudioEnabledChange={setAudioEnabled}
          onClose={() => setShowSettings(false)}
        />
      )}

      <main className="app-main">
        <div className="upload-section">
          <ImageUploader onUpload={opiszObraz} loading={loading} loadingMessage={loadingMessage} />
          {error && <div className="error-message" role="alert">{error}</div>}
        </div>

        {description && (
          <div className="description-section">
            <DescriptionViewer description={description} />
            {audioEnabled && <AudioPlayer text={description} />}
          </div>
        )}

        <HistoryPanel
          history={history}
          onSelectItem={(item) => setDescription(item.description)}
          onClearHistory={clearHistory}
        />
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  )
}

export default App
